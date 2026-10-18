#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import tempfile

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import start_a4_acceptance as acceptance

ROOT = Path(__file__).resolve().parents[1]
HARNESS = "__venue_profile_e2e__.html"
PASS = "VENUE_PROFILE_E2E: PASS"


def _harness() -> str:
    return """<!doctype html>
<meta charset=\"utf-8\">
<title>BUNKERFREQUENZ Venue Profile E2E</title>
<div id=\"status\">VENUE_PROFILE_E2E: RUNNING</div>
<iframe id=\"app\" style=\"width:760px;height:680px;border:0\"></iframe>
<script>
\"use strict\";
(() => {
  const status = document.getElementById(\"status\");
  const frame = document.getElementById(\"app\");
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const waitFor = async (probe, label, timeout = 10000) => {
    const end = performance.now() + timeout;
    while (performance.now() < end) {
      const value = probe();
      if (value) return value;
      await sleep(50);
    }
    throw new Error(\"Timeout: \" + label);
  };
  frame.addEventListener(\"load\", async () => {
    try {
      const w = frame.contentWindow;
      const d = frame.contentDocument;
      await waitFor(() => (d.getElementById(\"connection-status\")?.textContent || \"\").includes(\"BEREIT\"), \"BEREIT\");
      await waitFor(() => d.querySelectorAll(\"#property-list .equipment-row\").length > 1, \"Property-Liste\");
      w.BunkerUIPrefs.set(\"largeText\", true);
      w.BunkerUIPrefs.set(\"highContrast\", true);
      await waitFor(() => d.body.classList.contains(\"ui-large-text\") && d.body.classList.contains(\"ui-high-contrast\"), \"Anzeigeoptionen\");

      const rows = [...d.querySelectorAll(\"#property-list .equipment-row\")];
      const owned = rows.filter((row) => (row.querySelector(\"strong\")?.textContent || \"\").includes(\"EIGENTUM\"));
      if (owned.length !== 1) throw new Error(\"Erwartet genau einen bestätigten eigenen Ort, gefunden: \" + owned.length);
      const labels = [\"Prestige\", \"Publikumskraft\", \"Risiko\", \"Underground-Faktor\", \"Nutzen\"];
      const ownedDetail = owned[0].querySelector(\":scope > div > span\");
      if (!ownedDetail) throw new Error(\"Eigenes Betriebsprofil besitzt keine Detailzeile\");
      const ownedText = ownedDetail.textContent || \"\";
      for (const label of labels) {
        if (!ownedText.includes(label)) throw new Error(\"Eigenes Betriebsprofil verliert: \" + label);
        const valueToken = (ownedText.split(label)[1] || \"\").split(\"·\")[0].trim();
        const numericValue = Number(valueToken.replace(\",\", \".\"));
        if (!valueToken || !Number.isFinite(numericValue)) throw new Error(\"Eigenes Betriebsprofil hat keinen numerischen Wert für: \" + label);
      }
      const foreign = rows.filter((row) => row !== owned[0]);
      for (const row of foreign) {
        const text = row.querySelector(\":scope > div > span\")?.textContent || \"\";
        if (labels.some((label) => text.includes(label))) throw new Error(\"Fremder Ort zeigt ein Besitz-Betriebsprofil\");
      }
      const style = w.getComputedStyle(ownedDetail);
      const rect = ownedDetail.getBoundingClientRect();
      if (style.display === \"none\" || style.visibility === \"hidden\" || Number(style.opacity) === 0) {
        throw new Error(\"Eigenes Betriebsprofil ist per CSS unsichtbar\");
      }
      if (rect.width <= 0 || rect.height <= 0) throw new Error(\"Eigenes Betriebsprofil ist nicht sichtbar\");
      if (ownedDetail.scrollWidth > ownedDetail.clientWidth + 1) throw new Error(\"Betriebsprofil erzeugt horizontale Überbreite\");
      document.body.textContent = `VENUE_PROFILE_E2E: PASS\n● BEREIT\nBUNKERFREQUENZ – Control Deck\n760x680 · Große Schrift · Hoher Kontrast · genau ein sichtbares owned-only Fünf-Werte-Profil mit fünf numerischen Werten`;
    } catch (error) {
      document.body.textContent = `VENUE_PROFILE_E2E: FAIL · ${String(error?.message || error)}`;
    }
  }, { once: true });
  frame.src = \"/\";
})();
</script>
"""


def _passed(dom: str) -> bool:
    return re.search(r"<body(?:\s[^>]*)?>\s*VENUE_PROFILE_E2E: PASS(?:\s|<)", dom) is not None


def main() -> int:
    original = (acceptance.AVATAR_CONTEXT_HARNESS, acceptance._avatar_context_harness, acceptance._avatar_context_passed)
    acceptance.AVATAR_CONTEXT_HARNESS = HARNESS
    acceptance._avatar_context_harness = _harness
    acceptance._avatar_context_passed = _passed
    try:
        with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-venue-e2e-") as save_dir:
            acceptance.prepare_owned_map_fixture(save_dir)
            process = acceptance._start_server(save_dir)
            try:
                address = acceptance._wait_for_address(process)
                acceptance.probe_http(address)
                dom = acceptance.browser_dom(address, require_browser=True, timeout=35, avatar_context=True)
                if dom is None or not _passed(dom):
                    raise RuntimeError("Venue-Profile-E2E ohne ausgeführten PASS")
                print(PASS + " · owned-only · 5 Werte · 5 numerische Werte · 760x680 · Große Schrift · Hoher Kontrast")
                return 0
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
    finally:
        acceptance.AVATAR_CONTEXT_HARNESS, acceptance._avatar_context_harness, acceptance._avatar_context_passed = original


if __name__ == "__main__":
    raise SystemExit(main())
