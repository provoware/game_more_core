#!/usr/bin/env python3
"""Real start acceptance for the local A4 client."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "tools" / "start_a4_game_client.py"
BROWSER_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
MIN_BROWSER_WALLCLOCK_TIMEOUT = 30.0


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


def browser_dom(address: str, *, require_browser: bool, timeout: float = MIN_BROWSER_WALLCLOCK_TIMEOUT) -> str | None:
    browser = find_browser()
    if browser is None:
        if require_browser:
            raise RuntimeError("Kein Chrome/Chromium für den echten Browser-Acceptance-Test gefunden")
        return None

    command = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--no-first-run",
        "--disable-background-networking",
        "--disable-extensions",
        "--incognito",
        "--virtual-time-budget=4000",
        "--dump-dom",
        address,
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
        raise RuntimeError(
            "Browser reagierte nicht rechtzeitig; möglicher JS-/MutationObserver-Freeze"
        ) from exc

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().splitlines()[-5:]
        raise RuntimeError("Headless-Browser scheiterte: " + " | ".join(detail))
    dom = completed.stdout
    if "● BEREIT" not in dom:
        raise RuntimeError(
            "UI wurde im echten Browser nicht reaktionsfähig: Verbindungsstatus erreichte BEREIT nicht"
        )
    if "BUNKERFREQUENZ – Control Deck" not in dom:
        raise RuntimeError("Control-Deck-DOM fehlt im Browserergebnis")
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
            dom = browser_dom(address, require_browser=require_browser)
            if dom is not None:
                print("SELBSTTEST: BROWSER OK · UI ist reaktionsfähig")
        return

    with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-acceptance-save-") as save_dir:
        process = _start_server(save_dir)
        try:
            actual = _wait_for_address(process)
            probe_http(actual)
            print(f"ACCEPTANCE: HTTP OK · {actual}")
            if browser_check:
                dom = browser_dom(actual, require_browser=require_browser)
                if dom is not None:
                    print("ACCEPTANCE: BROWSER OK · /api/state gerendert · UI reaktionsfähig")
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
    parser.add_argument("--address", help="bereits laufende lokale Adresse prüfen")
    parser.add_argument("--no-browser-check", action="store_true", help="nur /api/health und /api/state prüfen")
    parser.add_argument("--require-browser", action="store_true", help="ohne Chrome/Chromium fehlschlagen")
    args = parser.parse_args(argv)
    try:
        run(args.address, browser_check=not args.no_browser_check, require_browser=args.require_browser)
    except (RuntimeError, OSError, URLError, json.JSONDecodeError) as exc:
        print(f"START-SELBSTTEST FEHLGESCHLAGEN – {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
