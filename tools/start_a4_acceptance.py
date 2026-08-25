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

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "tools" / "start_a4_game_client.py"
BROWSER_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
MIN_BROWSER_WALLCLOCK_TIMEOUT = 30.0
BROWSER_VIRTUAL_TIME_BUDGET_MS = 18000
AVATAR_CONTEXT_HARNESS = "__avatar_context_e2e__.html"
AVATAR_CONTEXT_PASS = "AVATAR_CONTEXT_E2E: PASS"


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
        d.getElementById("character-name").value = "E2E Crew";
        d.getElementById("event-name").value = "E2E Event";
        d.getElementById("new-game").click();
      }
      await waitFor(() => visible(d.getElementById("profile-panel")), "Profil sichtbar");
      const markInput = await waitFor(() => d.getElementById("crew-identity-mark-input"), "Crew-Editor");
      markInput.value = "E2E";
      markInput.dispatchEvent(new Event("input", { bubbles: true }));
      markInput.dispatchEvent(new Event("change", { bubbles: true }));
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
      let syntheticOwned = null;
      if (!canvas.querySelector(".map-marker.owned")) {
        syntheticOwned = d.createElement("button");
        syntheticOwned.type = "button";
        syntheticOwned.className = "map-marker owned";
        syntheticOwned.setAttribute("aria-label", "E2E read-only owned marker fixture");
        canvas.append(syntheticOwned);
      }
      const mapMark = await waitFor(() => {
        const mark = d.querySelector("#berlin-map-canvas .map-marker.owned .map-crew-badge .hud-crew-mark");
        return markText(mark) === "E2E" ? mark : null;
      }, "Map-Crew-Klon");

      if (!w.BunkerUIPrefs || typeof w.BunkerUIPrefs.set !== "function") {
        throw new Error("BunkerUIPrefs fehlt");
      }
      w.BunkerUIPrefs.set("highContrast", true);
      await waitFor(() => d.body.classList.contains("ui-high-contrast"), "Hoher Kontrast");

      const profileMark = d.getElementById("crew-identity-mark");
      const nodes = [profileMark, hudMark, hallMark, mapMark];
      if (nodes.some((node) => !node || node.getBoundingClientRect().width <= 0 || node.getBoundingClientRect().height <= 0)) {
        throw new Error("Crew-Marke in mindestens einem Kontext ohne sichtbare Geometrie");
      }
      if (nodes.some((node) => node.getBoundingClientRect().left < -1)) {
        throw new Error("Crew-Marke ragt im kleinen Fenster links aus dem sichtbaren Bereich");
      }
      if (markText(profileMark) !== "E2E") {
        throw new Error("Profilvorschau verlor die bestätigte Kurzmarke");
      }

      syntheticOwned?.remove();
      document.body.textContent =
        "AVATAR_CONTEXT_E2E: PASS\n● BEREIT\nBUNKERFREQUENZ – Control Deck\n" +
        "Profil→HUD→Map→Ranking · Hoher Kontrast · kleines Fenster";
    } catch (error) {
      document.body.textContent = "AVATAR_CONTEXT_E2E: FAIL\n" + String(error?.message || error);
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
        raise RuntimeError(
            "Browser reagierte nicht rechtzeitig; möglicher JS-/MutationObserver-Freeze"
        ) from exc
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
        raise RuntimeError(
            "UI wurde im echten Browser nicht reaktionsfähig: Verbindungsstatus erreichte BEREIT nicht"
        )
    if "BUNKERFREQUENZ – Control Deck" not in dom:
        raise RuntimeError("Control-Deck-DOM fehlt im Browserergebnis")
    if "Timeline wird geladen" in dom:
        raise RuntimeError(
            "UI erreichte zwar BEREIT, aber die Timeline blieb im Initialzustand; möglicher nachgelagerter JS-Freeze"
        )
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
                        "Timeline initialisiert · Profil→HUD→Map→Ranking bestätigt"
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
    args = parser.parse_args(argv)
    try:
        run(args.address, browser_check=not args.no_browser_check, require_browser=args.require_browser)
    except (RuntimeError, OSError, URLError, json.JSONDecodeError) as exc:
        print(f"START-SELBSTTEST FEHLGESCHLAGEN – {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
