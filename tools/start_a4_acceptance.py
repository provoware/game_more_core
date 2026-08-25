#!/usr/bin/env python3
"""Real start acceptance for the local A4 client."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.error import URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import urlopen

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import start_a4_game_client as game_client  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "tools" / "start_a4_game_client.py"
BROWSER_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
MIN_BROWSER_WALLCLOCK_TIMEOUT = 30.0
BROWSER_VIRTUAL_TIME_BUDGET_MS = 18000
AVATAR_CONTEXT_HARNESS = "__avatar_context_e2e__.html"
AVATAR_CONTEXT_PASS = "AVATAR_CONTEXT_E2E: PASS"
OWNED_EVIDENCE_PREFIX = "ACCEPTANCE_OWNED_EVIDENCE: "


def _json_get(base: str, path: str, timeout: float = 3.0) -> dict:
    with urlopen(base.rstrip("/") + path, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"{path} lieferte HTTP {response.status}")
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} lieferte kein JSON-Objekt")
    return payload


def probe_http(address: str) -> tuple[dict, dict]:
    health = _json_get(address, "/api/health")
    if health.get("status") != "ready":
        raise RuntimeError("/api/health meldet nicht ready")
    state = _json_get(address, "/api/state")
    if state.get("status") != "confirmed" or not isinstance(state.get("state"), dict):
        raise RuntimeError("/api/state liefert keinen bestätigten State")
    return health, state


def find_browser() -> str | None:
    for name in BROWSER_NAMES:
        executable = shutil.which(name)
        if executable:
            return executable
    return None


def prepare_owned_map_fixture(
    save_dir: str | Path,
    *,
    include_evidence: bool = False,
) -> str | dict[str, object]:
    """Create isolated confirmed ownership; optionally expose canonical purchase evidence."""
    runtime = game_client.A4ClientRuntime(Path(save_dir))
    locations = [
        item
        for item in runtime.city_map_manifest.get("locations", ())
        if isinstance(item, dict)
        and item.get("purchasable") is True
        and isinstance(item.get("location_id"), str)
        and isinstance(item.get("purchase_price_cents"), int)
        and item["purchase_price_cents"] >= 0
    ]
    if not locations:
        raise RuntimeError("Avatar-Context-E2E findet keine katalogisierte kaufbare Immobilie")
    location = min(locations, key=lambda item: (item["purchase_price_cents"], item["location_id"]))

    starter_event = runtime.starter.get("event")
    starter_character = runtime.starter.get("character")
    if not isinstance(starter_event, dict) or not isinstance(starter_character, dict):
        raise RuntimeError("Avatar-Context-E2E-Starter besitzt keinen gültigen Event-/Character-State")
    event_id = starter_event.get("event_id")
    character_id = starter_character.get("character_id")
    if not isinstance(event_id, str) or not event_id or not isinstance(character_id, str) or not character_id:
        raise RuntimeError("Avatar-Context-E2E-Starter besitzt keine gültigen Runtime-IDs")

    starter_event["budget_cents"] = location["purchase_price_cents"]
    bootstrap = runtime.bootstrap({"command_id": "acceptance-owned-map-bootstrap"})
    if bootstrap.get("status") != "confirmed":
        raise RuntimeError(f"Avatar-Context-E2E konnte den isolierten Starter nicht bestätigen: {bootstrap}")

    command_id = "acceptance-owned-map-purchase"
    result = runtime.session.dispatch(
        {
            "type": "property.purchase",
            "command_id": command_id,
            "location_id": location["location_id"],
        },
        context=runtime._context(command_id, "event", event_id, character_id),
    )
    if result.status != "confirmed":
        raise RuntimeError(
            "Avatar-Context-E2E konnte Eigentum nicht über property.purchase bestätigen: "
            f"{result.error_code or result.status}"
        )
    if not include_evidence:
        return location["location_id"]

    ownership = (result.metadata or {}).get("property")
    if not isinstance(ownership, dict) or ownership.get("location_id") != location["location_id"]:
        raise RuntimeError("Runtime-Owned-Evidence besitzt keinen bestätigten Property-Ownership-Record")
    transaction_id = ownership.get("economy_transaction_id")
    if not isinstance(transaction_id, str) or not transaction_id:
        raise RuntimeError("Runtime-Owned-Evidence besitzt keine Economy-Transaktionsreferenz")
    state = runtime.session.read_state()
    economy = state.get("economy")
    ledger = economy.get("ledger") if isinstance(economy, dict) else None
    if not isinstance(ledger, list):
        raise RuntimeError("Runtime-Owned-Evidence besitzt kein bestätigtes Economy-Ledger")
    ledger_entry = next(
        (entry for entry in ledger if isinstance(entry, dict) and entry.get("transaction_id") == transaction_id),
        None,
    )
    if not isinstance(ledger_entry, dict) or ledger_entry.get("kind") != "property_purchase":
        raise RuntimeError("Runtime-Owned-Evidence findet keine bestätigte Property-Kaufbuchung")
    expected_item_id = f"property:{location['location_id']}"
    if ledger_entry.get("item_id") != expected_item_id:
        raise RuntimeError("Runtime-Owned-Evidence-Ledger verweist auf eine andere Property")
    confirmed_price = ownership.get("purchase_price_cents")
    if (
        ledger_entry.get("unit_price_cents") != confirmed_price
        or confirmed_price != location["purchase_price_cents"]
    ):
        raise RuntimeError("Runtime-Owned-Evidence-Ledger besitzt einen widersprüchlichen Kaufpreis")
    committed = list(result.committed_event_ids)
    property_event_id = f"{command_id}:property"
    economy_event_id = f"{command_id}:economy"
    if property_event_id not in committed or economy_event_id not in committed:
        raise RuntimeError("Runtime-Owned-Evidence besitzt nicht beide bestätigten Property-/Economy-Ereignisse")

    return {
        "location_id": location["location_id"],
        "command_type": "property.purchase",
        "command_id": command_id,
        "status": result.status,
        "property_event_id": property_event_id,
        "economy_event_id": economy_event_id,
        "committed_event_ids": committed,
        "economy_transaction_id": transaction_id,
        "ledger_kind": ledger_entry.get("kind"),
        "ledger_item_id": ledger_entry.get("item_id"),
        "purchase_price_cents": ledger_entry.get("unit_price_cents"),
        "owner_character_id": ownership.get("owner_character_id"),
        "event_id": ownership.get("event_id"),
    }


def _print_owned_evidence(receipt: dict[str, object]) -> None:
    print(f"ACCEPTANCE: RUNTIME-OWNED MAP FIXTURE OK · {receipt['location_id']}")
    print(OWNED_EVIDENCE_PREFIX + json.dumps(receipt, ensure_ascii=False, sort_keys=True))


def _avatar_context_harness() -> str:
    return """<!doctype html>
<meta charset="utf-8">
<title>BUNKERFREQUENZ Avatar Context E2E</title>
<style>
  html, body { margin: 0; background: #05070a; color: #fff; font-family: sans-serif; }
  #status { padding: 8px; font: 700 14px/1.3 monospace; }
  #app { display: block; width: 760px; height: 680px; border: 0; }
</style>
<div id="status">AVATAR_CONTEXT_E2E: RUNNING</div>
<iframe id="app"></iframe>
<script>
"use strict";
(() => {
  const status = document.getElementById("status");
  const frame = document.getElementById("app");
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const waitFor = async (probe, label, timeout = 9000) => {
    const deadline = performance.now() + timeout;
    while (performance.now() < deadline) {
      const value = probe();
      if (value) return value;
      await sleep(50);
    }
    throw new Error("Timeout: " + label);
  };
  const visible = (node) => Boolean(node && !node.hidden && !node.classList.contains("hidden"));
  const markText = (node) => (node?.textContent || "").trim();

  frame.addEventListener("load", async () => {
    try {
      const w = frame.contentWindow;
      const d = frame.contentDocument;
      await waitFor(() => markText(d.getElementById("connection-status")).includes("BEREIT"), "BEREIT");
      await waitFor(() => !markText(d.getElementById("event-timeline-status")).includes("Timeline wird " + "geladen"), "Timeline");

      if (visible(d.getElementById("first-run"))) {
        throw new Error("Runtime-Owned-Map-Fixture fehlt: First Run ist unerwartet sichtbar");
      }
      await waitFor(() => visible(d.getElementById("profile-panel")), "Profil sichtbar");
      const markInput = await waitFor(() => d.getElementById("crew-identity-mark-input"), "Crew-Editor");
      markInput.value = "E2E";
      markInput.dispatchEvent(new w.Event("input", { bubbles: true }));
      markInput.dispatchEvent(new w.Event("change", { bubbles: true }));
      d.getElementById("save-profile").click();

      const hudMark = await waitFor(() => {
        const host = d.querySelector(".hud-crew-identity");
        const mark = host?.querySelector(".hud-crew-mark");
        return visible(host) && markText(mark) === "E2E" ? mark : null;
      }, "bestätigte HUD-Crew");
      const hallMark = await waitFor(() => {
        const mark = d.querySelector(".hall-local-crew .hud-crew-mark");
        return markText(mark) === "E2E" ? mark : null;
      }, "eigener Ranking-Eintrag");

      const canvas = d.getElementById("berlin-map-canvas");
      await waitFor(() => canvas?.querySelector(".map-marker.owned"), "bestätigter Eigentumsmarker");
      const mapMark = await waitFor(() => {
        const mark = d.querySelector("#berlin-map-canvas .map-marker.owned .map-crew-badge .hud-crew-mark");
        return markText(mark) === "E2E" ? mark : null;
      }, "Map-Crew-Klon");

      if (!w.BunkerUIPrefs || typeof w.BunkerUIPrefs.set !== "function") {
        throw new Error("BunkerUIPrefs fehlt");
      }
      w.BunkerUIPrefs.set("highContrast", true);
      await waitFor(() => d.body.classList.contains("ui-high-contrast"), "Hoher Kontrast");
      await waitFor(() => {
        for (const sheet of d.styleSheets) {
          try {
            const href = new URL(sheet.href || "", d.baseURI).pathname;
            if (href.endsWith("/crew_identity.css") && sheet.cssRules.length > 0) return sheet;
          } catch {
            // Ein fremdes oder noch nicht lesbares Stylesheet ist kein Crew-Stylesheet-Nachweis.
          }
        }
        return null;
      }, "Crew-Stylesheet geladen");

      const profileMark = d.getElementById("crew-identity-mark");
      const contexts = [
        ["Profil", profileMark],
        ["HUD", hudMark],
        ["Ranking", hallMark],
        ["Map", mapMark]
      ];
      const invalidGeometry = contexts.flatMap(([label, node]) => {
        if (!node) return [`${label}=fehlt`];
        const rect = node.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0 ? [] : [`${label}=${rect.width.toFixed(1)}x${rect.height.toFixed(1)}`];
      });
      if (invalidGeometry.length) {
        throw new Error("Crew-Geometrie ungültig: " + invalidGeometry.join(", "));
      }
      const leftOverflow = contexts.flatMap(([label, node]) => {
        const rect = node.getBoundingClientRect();
        return rect.left < -1 ? [`${label}=${rect.left.toFixed(1)}`] : [];
      });
      if (leftOverflow.length) {
        throw new Error("Crew-Marke ragt links heraus: " + leftOverflow.join(", "));
      }
      if (markText(profileMark) !== "E2E") {
        throw new Error("Profilvorschau verlor die bestätigte Kurzmarke");
      }
      const compactMarks = [
        ["HUD", hudMark],
        ["Ranking", hallMark],
        ["Map", mapMark]
      ];
      const rootFontSizePx = Number.parseFloat(w.getComputedStyle(d.documentElement).fontSize);
      if (!Number.isFinite(rootFontSizePx) || rootFontSizePx <= 0) {
        throw new Error("Root-Schriftgröße ist im Browser nicht messbar");
      }
      const minCompactFontSizePx = rootFontSizePx * 0.34;
      const undersizedMarks = compactMarks.flatMap(([label, node]) => {
        const fontSizePx = Number.parseFloat(w.getComputedStyle(node).fontSize);
        if (Number.isFinite(fontSizePx) && fontSizePx + 0.01 >= minCompactFontSizePx) return [];
        const shown = Number.isFinite(fontSizePx) ? fontSizePx.toFixed(2) + "px" : "ungültig";
        return [`${label}=${shown}`];
      });
      if (undersizedMarks.length) {
        throw new Error("Crew-Kurzmarke unter 0.34rem: " + undersizedMarks.join(", "));
      }
      const hudPreview = d.querySelector(".hud-crew-preview");
      const hudStyle = hudPreview ? w.getComputedStyle(hudPreview) : null;
      if (!hudStyle || hudStyle.borderTopStyle === "none" || hudStyle.borderTopWidth === "0px") {
        throw new Error("Crew-Stylesheet wirkt nicht auf die bestätigte HUD-Marke");
      }
      if (hudStyle.borderTopColor !== "rgb(255, 255, 255)") {
        throw new Error("Hoher Kontrast erreicht die bestätigte HUD-Marke nicht");
      }

      document.body.textContent = `AVATAR_CONTEXT_E2E: PASS
● BEREIT
BUNKERFREQUENZ – Control Deck
Profil→HUD→Map→Ranking · Runtime-Eigentum · Hoher Kontrast · kleines Fenster · Kurzmarken ≥ 0.34rem`;
    } catch (error) {
      document.body.textContent = `AVATAR_CONTEXT_E2E: FAIL · ${String(error?.message || error)}`;
    }
  }, { once: true });
  frame.src = "/";
})();
</script>
"""


def _avatar_context_url(address: str) -> str:
    parts = urlsplit(address)
    return urlunsplit((parts.scheme, parts.netloc, "/" + AVATAR_CONTEXT_HARNESS, parts.query, ""))


def _avatar_context_passed(dom: str) -> bool:
    return re.search(r"<body(?:\s[^>]*)?>\s*AVATAR_CONTEXT_E2E: PASS(?:\s|<)", dom, flags=re.IGNORECASE) is not None


def browser_dom(
    address: str,
    *,
    require_browser: bool,
    timeout: float = MIN_BROWSER_WALLCLOCK_TIMEOUT,
    avatar_context: bool = False,
) -> str | None:
    browser = find_browser()
    if browser is None:
        if require_browser:
            raise RuntimeError("Kein Chrome/Chromium für den echten Browser-Acceptance-Test gefunden")
        return None

    harness_path: Path | None = None
    target_url = address
    if avatar_context:
        harness_path = ROOT / "web" / "a4" / AVATAR_CONTEXT_HARNESS
        if harness_path.exists():
            raise RuntimeError(f"Temporärer Browser-Harness-Pfad ist bereits belegt: {harness_path}")
        harness_path.write_text(_avatar_context_harness(), encoding="utf-8")
        target_url = _avatar_context_url(address)

    command = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--no-first-run",
        "--disable-background-networking",
        "--disable-extensions",
        "--disable-application-cache",
        "--disk-cache-size=1",
        "--incognito",
        "--window-size=900,760",
        f"--virtual-time-budget={BROWSER_VIRTUAL_TIME_BUDGET_MS}",
        "--dump-dom",
        target_url,
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=max(timeout, MIN_BROWSER_WALLCLOCK_TIMEOUT),
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Browser reagierte nicht rechtzeitig; möglicher JS-/MutationObserver-Freeze") from exc
    finally:
        if harness_path is not None:
            harness_path.unlink(missing_ok=True)

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().splitlines()[-5:]
        raise RuntimeError("Headless-Browser scheiterte: " + " | ".join(detail))
    dom = completed.stdout
    if avatar_context and not _avatar_context_passed(dom):
        detail = " | ".join(line.strip() for line in dom.splitlines() if "AVATAR_CONTEXT_E2E:" in line)
        raise RuntimeError("Avatar-Context-E2E lieferte keinen ausgeführten PASS-Nachweis" + (f": {detail}" if detail else ""))
    if "● BEREIT" not in dom:
        raise RuntimeError("UI wurde im echten Browser nicht reaktionsfähig: Verbindungsstatus erreichte BEREIT nicht")
    if "BUNKERFREQUENZ – Control Deck" not in dom:
        raise RuntimeError("Control-Deck-DOM fehlt im Browserergebnis")
    if "Timeline wird geladen" in dom:
        raise RuntimeError("UI erreichte zwar BEREIT, aber die Timeline blieb im Initialzustand; möglicher nachgelagerter JS-Freeze")
    return dom


def _wait_for_address(process: subprocess.Popen[str], timeout: float = 8.0) -> str:
    assert process.stdout is not None
    deadline = time.monotonic() + timeout
    lines: list[str] = []
    output: queue.Queue[str | None] = queue.Queue()

    def read_lines() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            output.put(line)
        output.put(None)

    threading.Thread(target=read_lines, daemon=True).start()
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            line = output.get(timeout=remaining)
        except queue.Empty:
            break
        if line is None:
            break
        lines.append(line.rstrip())
        if line.startswith("ADRESSE: "):
            return line.split("ADRESSE: ", 1)[1].strip()
    raise RuntimeError("Launcher lieferte keine Adresse: " + " | ".join(lines))


def _start_server(save_dir: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, "-u", str(LAUNCHER), "--port", "0", "--no-browser", "--save-dir", save_dir],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def run(address: str | None, *, browser_check: bool, require_browser: bool) -> None:
    if address:
        probe_http(address)
        print(f"SELBSTTEST: HTTP OK · {address}")
        if browser_check:
            dom = browser_dom(address, require_browser=require_browser, avatar_context=False)
            if dom is not None:
                print("SELBSTTEST: BROWSER OK · UI reaktionsfähig · read-only bestehende Session geprüft")
        return

    with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-acceptance-save-") as save_dir:
        if browser_check:
            owned_receipt = prepare_owned_map_fixture(save_dir, include_evidence=True)
            assert isinstance(owned_receipt, dict)
            _print_owned_evidence(owned_receipt)
        process = _start_server(save_dir)
        try:
            actual = _wait_for_address(process)
            probe_http(actual)
            print(f"ACCEPTANCE: HTTP OK · {actual}")
            if browser_check:
                dom = browser_dom(actual, require_browser=require_browser, avatar_context=True)
                if dom is not None:
                    print(
                        "ACCEPTANCE: BROWSER OK · UI reaktionsfähig · /api/state gerendert · "
                        "Timeline initialisiert · Profil→HUD→Map→Ranking mit Runtime-Eigentum bestätigt"
                    )
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            if process.stdout is not None:
                process.stdout.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Start-/Browser-Acceptance")
    parser.add_argument("--address", help="bereits laufende lokale Adresse read-only prüfen")
    parser.add_argument("--no-browser-check", action="store_true", help="nur /api/health und /api/state prüfen")
    parser.add_argument("--require-browser", action="store_true", help="ohne Chrome/Chromium fehlschlagen")
    parser.add_argument("--prepare-owned-map-fixture", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.prepare_owned_map_fixture is not None:
        try:
            receipt = prepare_owned_map_fixture(args.prepare_owned_map_fixture, include_evidence=True)
            assert isinstance(receipt, dict)
        except (RuntimeError, OSError, URLError, json.JSONDecodeError) as exc:
            print(f"START-SELBSTTEST FEHLGESCHLAGEN – {exc}", file=sys.stderr)
            return 1
        _print_owned_evidence(receipt)
        return 0
    try:
        run(args.address, browser_check=not args.no_browser_check, require_browser=args.require_browser)
    except (RuntimeError, OSError, URLError, json.JSONDecodeError) as exc:
        print(f"START-SELBSTTEST FEHLGESCHLAGEN – {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
