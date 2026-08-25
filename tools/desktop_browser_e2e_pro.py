#!/usr/bin/env python3
"""Source-bound multi-browser E2E evidence for BUNKERFREQUENZ releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile

from build_release import build
import start_a4_acceptance as acceptance

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_NAME = "DESKTOP_BROWSER_E2E_EVIDENCE.json"
SUBGATE_NAME = "SUBGATE_EVIDENCE.json"
REQUIRED_SCENARIOS = (
    "desktop_launcher_contract",
    "clickstart_orchestrator",
    "chromium_dom_ready",
    "firefox_dom_ready",
)
EXPECTED_DESKTOP_EXEC = "Exec=bash -lc 'desktop=\"$1\"; desktop=\"${desktop#file://}\"; cd \"$(dirname \"$desktop\")\" && exec ./START_BUNKERFREQUENZ.sh' _ %k"
EXPECTED_LAUNCHER_EXEC = 'exec "$PYTHON_BIN" tools/start_orchestrator.py "$@"'
FIREFOX_DRIVER_READY_TIMEOUT_SECONDS = 20.0
FIREFOX_SESSION_TIMEOUT_SECONDS = 55.0
FIREFOX_NAVIGATION_TIMEOUT_SECONDS = 20.0
FIREFOX_DOM_READY_TIMEOUT_SECONDS = 40.0
FIREFOX_WEBDRIVER_CALL_TIMEOUT_SECONDS = 8.0


def _canonical_json_bytes(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def source_identity() -> tuple[str, str]:
    dirty_tracked = _git("status", "--porcelain", "--untracked-files=no")
    if dirty_tracked:
        raise RuntimeError("Desktop-Browser-Evidence darf keine geänderten versionierten Quelldateien verwenden")
    return _git("rev-parse", "HEAD"), _git("rev-parse", "HEAD^{tree}")


def _extract(zip_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    root_resolved = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = destination / member.filename
            resolved = target.resolve()
            if resolved != root_resolved and root_resolved not in resolved.parents:
                raise RuntimeError(f"Unsicherer ZIP-Pfad: {member.filename}")
            archive.extract(member, destination)
            if not member.is_dir():
                mode = (member.external_attr >> 16) & 0o777
                target.chmod(mode or 0o644)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError("Entpacktes Release besitzt keinen eindeutigen Produktordner")
    return roots[0]


def _load_prior_subgate(path: Path, source_commit: str, source_tree: str, candidate_sha256: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failure-Containment-Subgate ist nicht lesbar: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise RuntimeError("Failure-Containment-Subgate benötigt schema_version=1")
    if data.get("source_commit") != source_commit or data.get("source_tree") != source_tree:
        raise RuntimeError("Failure-Containment-Subgate gehört nicht zur aktuellen Source")
    if data.get("candidate_sha256") != candidate_sha256:
        raise RuntimeError("Failure-Containment-Subgate gehört nicht zu denselben Release-Bytes")
    gates = data.get("gates")
    if not isinstance(gates, dict):
        raise RuntimeError("Failure-Containment-Subgate besitzt kein gates-Objekt")
    failure = gates.get("failure_containment_pro")
    if not isinstance(failure, dict) or failure.get("status") != "PASS":
        raise RuntimeError("failure_containment_pro muss vor Desktop-Browser-E2E PASS sein")
    evidence_sha = failure.get("evidence_sha256")
    if not isinstance(evidence_sha, str) or len(evidence_sha) != 64:
        raise RuntimeError("failure_containment_pro besitzt keinen gültigen Evidence-SHA-256")
    return data


def _scenario_desktop_launcher_contract(product_root: Path) -> dict[str, object]:
    launcher = product_root / "START_BUNKERFREQUENZ.sh"
    desktop = product_root / "BUNKERFREQUENZ.desktop"
    orchestrator = product_root / "tools" / "start_orchestrator.py"
    for path in (launcher, desktop, orchestrator):
        if not path.is_file():
            raise RuntimeError(f"Pflichtdatei fehlt: {path.name}")
    if not os.access(launcher, os.X_OK):
        raise RuntimeError("START_BUNKERFREQUENZ.sh ist im Release nicht ausführbar")
    if not os.access(desktop, os.X_OK):
        raise RuntimeError("BUNKERFREQUENZ.desktop ist im Release nicht ausführbar")

    desktop_lines = [line.strip() for line in desktop.read_text(encoding="utf-8").splitlines() if line.startswith("Exec=")]
    if desktop_lines != [EXPECTED_DESKTOP_EXEC]:
        raise RuntimeError("Desktop-Datei besitzt nicht exakt den kanonischen Klickstartbefehl")

    launcher_lines = [
        line.strip()
        for line in launcher.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    exec_lines = [line for line in launcher_lines if line.startswith("exec ")]
    if exec_lines != [EXPECTED_LAUNCHER_EXEC] or launcher_lines[-1] != EXPECTED_LAUNCHER_EXEC:
        raise RuntimeError("Startskript besitzt nicht exakt die kanonische Orchestrator-Delegation")
    return {
        "launcher_executable": True,
        "desktop_executable": True,
        "exact_desktop_exec": True,
        "exact_launcher_exec": True,
        "single_orchestrator_path": True,
    }


def _extract_address(output: str) -> str:
    addresses = [line.split("ADRESSE: ", 1)[1].strip() for line in output.splitlines() if line.startswith("ADRESSE: ")]
    if len(addresses) != 1:
        raise RuntimeError("Klickstart lieferte keine eindeutige lokale Serveradresse")
    return addresses[0]


def _extract_owned_evidence(output: str) -> dict[str, object]:
    payloads = [
        line.split(acceptance.OWNED_EVIDENCE_PREFIX, 1)[1].strip()
        for line in output.splitlines()
        if line.startswith(acceptance.OWNED_EVIDENCE_PREFIX)
    ]
    if len(payloads) != 1:
        raise RuntimeError("Runtime-Owned-Evidence lieferte keinen eindeutigen Receipt-Datensatz")
    try:
        receipt = json.loads(payloads[0])
    except json.JSONDecodeError as exc:
        raise RuntimeError("Runtime-Owned-Evidence ist kein gültiges JSON") from exc
    if not isinstance(receipt, dict):
        raise RuntimeError("Runtime-Owned-Evidence ist kein JSON-Objekt")
    if receipt.get("status") != "confirmed" or receipt.get("command_type") != "property.purchase":
        raise RuntimeError("Runtime-Owned-Evidence bestätigt keinen property.purchase")
    location_id = receipt.get("location_id")
    transaction_id = receipt.get("economy_transaction_id")
    property_event_id = receipt.get("property_event_id")
    committed = receipt.get("committed_event_ids")
    if not isinstance(location_id, str) or not location_id:
        raise RuntimeError("Runtime-Owned-Evidence besitzt keine location_id")
    if not isinstance(transaction_id, str) or not transaction_id:
        raise RuntimeError("Runtime-Owned-Evidence besitzt keine Economy-Transaktionsreferenz")
    if not isinstance(property_event_id, str) or not isinstance(committed, list) or property_event_id not in committed:
        raise RuntimeError("Runtime-Owned-Evidence besitzt keine bestätigte Property-Ereignisreferenz")
    if receipt.get("ledger_kind") != "property_purchase":
        raise RuntimeError("Runtime-Owned-Evidence besitzt keine Property-Kaufbuchung")
    return receipt


def _assert_server_stopped(address: str, timeout: float = 3.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(address.rstrip("/") + "/api/health", timeout=0.4) as response:
                response.read(1)
        except (OSError, URLError):
            return
        time.sleep(0.1)
    raise RuntimeError("Klickstart-Server antwortet nach --exit-after-ready weiterhin")


def _scenario_clickstart(product_root: Path, root: Path) -> dict[str, object]:
    save_dir = root / "save"
    state_dir = root / "state"
    env = os.environ.copy()
    env.update(
        {
            "BUNKERFREQUENZ_START_STATE_DIR": str(state_dir),
            "PYTHONPATH": "",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    completed = subprocess.run(
        [
            str(product_root / "START_BUNKERFREQUENZ.sh"),
            "--no-browser",
            "--exit-after-ready",
            "--port",
            "0",
            "--save-dir",
            str(save_dir),
        ],
        cwd=product_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=70,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError("Klickstart scheiterte: " + " | ".join(output.splitlines()[-12:]))
    status_path = state_dir / "START_STATUS.txt"
    if not status_path.is_file():
        raise RuntimeError("Klickstart erzeugte keinen START_STATUS-Nachweis")
    status = status_path.read_text(encoding="utf-8")
    if "[100%]" not in status or "BEREIT" not in status:
        raise RuntimeError("Klickstart erreichte keinen vollständigen BEREIT-Zustand")
    address = _extract_address(output)
    _assert_server_stopped(address)
    return {"exit_code": 0, "ready_100_percent": True, "server_shutdown_after_acceptance": True}


def _scenario_chromium_dom(product_root: Path) -> dict[str, object]:
    env = os.environ.copy()
    env.update({"PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"})
    completed = subprocess.run(
        [sys.executable, str(product_root / "tools" / "start_a4_acceptance.py"), "--require-browser"],
        cwd=product_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=70,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError("Browser-Acceptance scheiterte: " + " | ".join(output.splitlines()[-12:]))
    if "BROWSER OK" not in output or "UI reaktionsfähig" not in output:
        raise RuntimeError("Browser-Acceptance lieferte keinen bestätigten DOM/BEREIT-Nachweis")
    if "RUNTIME-OWNED MAP FIXTURE OK" not in output:
        raise RuntimeError("Browser-Acceptance bestätigte kein Runtime-Owned-Map-Fixture")
    receipt = _extract_owned_evidence(output)
    return {
        "browser": "chromium",
        "real_browser_required": True,
        "dom_ready": True,
        "ui_responsive": True,
        "runtime_owned_map_fixture": True,
        "runtime_owned_evidence_receipt": receipt,
    }


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _webdriver_json(method: str, url: str, payload: object | None = None, timeout: float = 5.0) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("WebDriver lieferte kein JSON-Objekt")
    return data


def _wait_http_ready(url: str, process: subprocess.Popen[bytes], timeout: float = FIREFOX_DRIVER_READY_TIMEOUT_SECONDS) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Geckodriver wurde vor Bereitschaft beendet")
        try:
            _webdriver_json("GET", url, timeout=0.75)
            return
        except (TimeoutError, OSError, URLError, HTTPError, json.JSONDecodeError):
            time.sleep(0.1)
    raise RuntimeError("Geckodriver wurde nicht rechtzeitig bereit")


def _prepare_packaged_owned_map_fixture(product_root: Path, save_dir: Path) -> dict[str, object]:
    completed = subprocess.run(
        [
            sys.executable,
            str(product_root / "tools" / "start_a4_acceptance.py"),
            "--prepare-owned-map-fixture",
            str(save_dir),
        ],
        cwd=product_root,
        env={**os.environ, "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0 or "RUNTIME-OWNED MAP FIXTURE OK" not in output:
        raise RuntimeError(
            "Paketserver konnte Runtime-Owned-Map-Fixture nicht vorbereiten: "
            + " | ".join(output.splitlines()[-10:])
        )
    return _extract_owned_evidence(output)


def _start_packaged_server(product_root: Path, root: Path) -> tuple[subprocess.Popen[str], str, dict[str, object]]:
    save_dir = root / "save"
    receipt = _prepare_packaged_owned_map_fixture(product_root, save_dir)
    process = subprocess.Popen(
        [
            sys.executable,
            "-u",
            str(product_root / "tools" / "start_a4_game_client.py"),
            "--port",
            "0",
            "--no-browser",
            "--save-dir",
            str(save_dir),
        ],
        cwd=product_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**os.environ, "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert process.stdout is not None
    deadline = time.monotonic() + 12.0
    lines: list[str] = []
    while time.monotonic() < deadline:
        line = process.stdout.readline()
        if line:
            clean = line.rstrip()
            lines.append(clean)
            if clean.startswith("ADRESSE: "):
                return process, clean.split("ADRESSE: ", 1)[1].strip(), receipt
        elif process.poll() is not None:
            break
        else:
            time.sleep(0.05)
    process.terminate()
    process.wait(timeout=3)
    raise RuntimeError("Paketserver lieferte keine Adresse: " + " | ".join(lines[-8:]))


def _scenario_firefox_dom(product_root: Path, root: Path) -> dict[str, object]:
    firefox = shutil.which("firefox")
    geckodriver = shutil.which("geckodriver")
    if not firefox or not geckodriver:
        raise RuntimeError("Nativer Firefox und Geckodriver müssen für MULTI-BROWSER-E2E vorhanden sein")

    harness_path = product_root / "web" / "a4" / acceptance.AVATAR_CONTEXT_HARNESS
    if harness_path.exists():
        raise RuntimeError(f"Temporärer Firefox-Harness-Pfad ist bereits belegt: {harness_path}")
    harness_path.write_text(acceptance._avatar_context_harness(), encoding="utf-8")

    server, address, receipt = _start_packaged_server(product_root, root / "server")
    target_url = acceptance._avatar_context_url(address)
    port = _free_loopback_port()
    driver = subprocess.Popen(
        [geckodriver, "--host", "127.0.0.1", "--port", str(port), "--log", "fatal"],
        cwd=product_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    session_id: str | None = None
    base = f"http://127.0.0.1:{port}"
    try:
        _wait_http_ready(base + "/status", driver)
        created = _webdriver_json(
            "POST",
            base + "/session",
            {
                "capabilities": {
                    "alwaysMatch": {
                        "browserName": "firefox",
                        "pageLoadStrategy": "eager",
                        "moz:firefoxOptions": {"binary": firefox, "args": ["-headless"]},
                    }
                }
            },
            timeout=FIREFOX_SESSION_TIMEOUT_SECONDS,
        )
        value = created.get("value")
        if not isinstance(value, dict) or not isinstance(value.get("sessionId"), str):
            raise RuntimeError(f"Firefox-WebDriver lieferte keine Session: {created}")
        session_id = value["sessionId"]
        _webdriver_json(
            "POST",
            f"{base}/session/{session_id}/window/rect",
            {"width": 900, "height": 760},
            timeout=FIREFOX_WEBDRIVER_CALL_TIMEOUT_SECONDS,
        )
        _webdriver_json(
            "POST",
            f"{base}/session/{session_id}/url",
            {"url": target_url},
            timeout=FIREFOX_NAVIGATION_TIMEOUT_SECONDS,
        )

        deadline = time.monotonic() + FIREFOX_DOM_READY_TIMEOUT_SECONDS
        body_text = ""
        while time.monotonic() < deadline:
            if driver.poll() is not None:
                raise RuntimeError("Geckodriver wurde während der Firefox-DOM-Prüfung beendet")
            try:
                result = _webdriver_json(
                    "POST",
                    f"{base}/session/{session_id}/execute/sync",
                    {"script": "return document.body ? document.body.innerText : '';", "args": []},
                    timeout=FIREFOX_WEBDRIVER_CALL_TIMEOUT_SECONDS,
                )
            except (TimeoutError, OSError, URLError, HTTPError, json.JSONDecodeError):
                time.sleep(0.25)
                continue
            body_value = result.get("value")
            body_text = body_value if isinstance(body_value, str) else ""
            if acceptance.AVATAR_CONTEXT_PASS in body_text and "● BEREIT" in body_text and "BUNKERFREQUENZ" in body_text:
                break
            if "AVATAR_CONTEXT_E2E: FAIL" in body_text:
                raise RuntimeError("Firefox Avatar-Context-E2E meldete: " + body_text.strip())
            time.sleep(0.25)
        else:
            raise RuntimeError("Firefox erreichte den bestätigten Avatar-Context-PASS nicht innerhalb der Cold-Start-Grenze")

        health = _webdriver_json(
            "POST",
            f"{base}/session/{session_id}/execute/sync",
            {"script": "return fetch('/api/health').then(r => r.json()).then(x => x.status);", "args": []},
            timeout=FIREFOX_WEBDRIVER_CALL_TIMEOUT_SECONDS,
        )
        if health.get("value") != "ready":
            raise RuntimeError("Firefox konnte /api/health nicht als ready bestätigen")
        return {
            "browser": "firefox",
            "real_browser_required": True,
            "webdriver": "geckodriver",
            "dom_ready": True,
            "ui_responsive": True,
            "health_ready": True,
            "avatar_context_pass": True,
            "runtime_owned_map_fixture": True,
            "runtime_owned_evidence_receipt": receipt,
            "small_viewport": True,
            "high_contrast": True,
        }
    finally:
        harness_path.unlink(missing_ok=True)
        if session_id is not None:
            try:
                _webdriver_json("DELETE", f"{base}/session/{session_id}", timeout=5.0)
            except Exception:
                pass
        if driver.poll() is None:
            driver.terminate()
            try:
                driver.wait(timeout=5)
            except subprocess.TimeoutExpired:
                driver.kill()
                driver.wait(timeout=3)
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=3)
        if server.stdout is not None:
            server.stdout.close()


def _single_run(candidate: Path, root: Path) -> dict[str, dict[str, object]]:
    product_root = _extract(candidate, root / "product")
    calls = (
        ("desktop_launcher_contract", lambda: _scenario_desktop_launcher_contract(product_root)),
        ("clickstart_orchestrator", lambda: _scenario_clickstart(product_root, root / "clickstart")),
        ("chromium_dom_ready", lambda: _scenario_chromium_dom(product_root)),
        ("firefox_dom_ready", lambda: _scenario_firefox_dom(product_root, root / "firefox")),
    )
    scenarios: dict[str, dict[str, object]] = {}
    for name, call in calls:
        try:
            detail = call()
        except Exception as exc:
            scenarios[name] = {"status": "FAIL", "reason": str(exc)}
        else:
            scenarios[name] = {"status": "PASS", "detail": detail}
    return scenarios


def _statuses(run: dict[str, dict[str, object]]) -> dict[str, str]:
    return {name: str(run[name]["status"]) for name in REQUIRED_SCENARIOS}


def evaluate_runs(first: dict[str, dict[str, object]], second: dict[str, dict[str, object]]) -> str:
    first_status = _statuses(first)
    second_status = _statuses(second)
    if first_status != second_status:
        return "FLAKY"
    return "PASS" if all(value == "PASS" for value in first_status.values()) else "FAIL"


def run(output_dir: Path, prior_subgate: Path) -> dict[str, object]:
    source_commit, source_tree = source_identity()
    with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-desktop-browser-e2e-") as temp:
        temp_root = Path(temp)
        candidate, _, summary = build(temp_root / "candidate")
        candidate_sha = _sha256_file(candidate)
        prior = _load_prior_subgate(prior_subgate, source_commit, source_tree, candidate_sha)
        first = _single_run(candidate, temp_root / "run-a")
        second = _single_run(candidate, temp_root / "run-b")
    status = evaluate_runs(first, second)
    evidence = {
        "schema_version": 1,
        "gate": "desktop_browser_e2e_pro",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_sha256": candidate_sha,
        "candidate_size_bytes": summary["size_bytes"],
        "anti_flake_runs": 2,
        "anti_flake_consistent": _statuses(first) == _statuses(second),
        "status": status,
        "coverage": [
            "packaged_desktop_contract",
            "real_clickstart_orchestrator",
            "real_chromium_dom_ready",
            "real_firefox_dom_ready",
            "runtime_owned_map_fixture_from_property_purchase",
            "runtime_owned_evidence_receipt_location_event_ledger",
            "firefox_avatar_context_profile_hud_map_ranking",
            "firefox_avatar_context_high_contrast_small_viewport",
            "same_candidate_sha_across_browsers",
            "post_start_shutdown",
            "anti_flake_quarantine",
        ],
        "runs": [first, second],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = output_dir / EVIDENCE_NAME
    payload = _canonical_json_bytes(evidence)
    evidence_sha = _sha256_bytes(payload)
    evidence_path.write_bytes(payload)
    (output_dir / f"{EVIDENCE_NAME}.sha256").write_text(f"{evidence_sha}  {EVIDENCE_NAME}\n", encoding="utf-8")
    gates = dict(prior["gates"])
    gates["desktop_browser_e2e_pro"] = {"status": status, "evidence_sha256": evidence_sha}
    combined = {
        "schema_version": 1,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_sha256": candidate_sha,
        "gates": gates,
    }
    (output_dir / SUBGATE_NAME).write_bytes(_canonical_json_bytes(combined))
    return {**evidence, "evidence_sha256": evidence_sha, "subgate_file": SUBGATE_NAME}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Multi Browser E2E PRO")
    parser.add_argument("--prior-subgate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "desktop-browser-e2e-dist")
    args = parser.parse_args(argv)
    try:
        evidence = run(args.output_dir.resolve(), args.prior_subgate.resolve())
    except Exception as exc:
        print(f"DESKTOP_BROWSER_E2E_INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
    print(f"DESKTOP_BROWSER_E2E_STATUS: {evidence['status']}")
    if evidence["status"] == "PASS":
        return 0
    return 3 if evidence["status"] == "FLAKY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
