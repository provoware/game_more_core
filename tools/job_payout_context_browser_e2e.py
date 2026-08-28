#!/usr/bin/env python3
"""Real Chromium proof for runtime-owned Scene-Job payout context."""

from __future__ import annotations

import re
from pathlib import Path
import sys
import tempfile

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import start_a4_acceptance as acceptance  # noqa: E402
import start_a4_game_client as game_client  # noqa: E402


HARNESS_NAME = "__job_payout_context_e2e__.html"
PASS_MARKER = "JOB_PAYOUT_CONTEXT_E2E: PASS"
CONTEXT = "Aktueller Lohn reduziert – deine Energie reicht nicht für die volle Auszahlung."
FIXTURE_ENERGY = 8


def _prepare_fixture(save_dir: str | Path) -> None:
    runtime = game_client.A4ClientRuntime(Path(save_dir))
    starter_character = runtime.starter.get("character")
    if not isinstance(starter_character, dict):
        raise RuntimeError("Job-Payout-E2E-Starter besitzt keinen gültigen Character-State")
    starter_character["energy"] = FIXTURE_ENERGY
    bootstrap = runtime.bootstrap({"command_id": "acceptance-job-payout-context-bootstrap"})
    if bootstrap.get("status") != "confirmed":
        raise RuntimeError(f"Job-Payout-E2E konnte den isolierten Starter nicht bestätigen: {bootstrap}")


def _harness() -> str:
    return f"""<!doctype html>
<meta charset=\"utf-8\">
<title>BUNKERFREQUENZ Job Payout Context E2E</title>
<style>
  html, body {{ margin: 0; background: #05070a; color: #fff; font-family: sans-serif; }}
  #status {{ padding: 8px; font: 700 14px/1.3 monospace; }}
  #app {{ display: block; width: 760px; height: 680px; border: 0; }}
</style>
<div id=\"status\">JOB_PAYOUT_CONTEXT_E2E: RUNNING</div>
<iframe id=\"app\"></iframe>
<script>
\"use strict\";
(() => {{
  const frame = document.getElementById(\"app\");
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const waitFor = async (probe, label, timeout = 9000) => {{
    const deadline = performance.now() + timeout;
    while (performance.now() < deadline) {{
      const value = probe();
      if (value) return value;
      await sleep(50);
    }}
    throw new Error(\"Timeout: \" + label);
  }};
  const text = (node) => (node?.textContent || \"\").trim();

  frame.addEventListener(\"load\", async () => {{
    try {{
      const w = frame.contentWindow;
      const d = frame.contentDocument;
      await waitFor(() => text(d.getElementById(\"connection-status\")).includes(\"BEREIT\"), \"BEREIT\");
      await waitFor(() => !text(d.getElementById(\"event-timeline-status\")).includes(\"Timeline wird \" + \"geladen\"), \"Timeline\");
      const rows = await waitFor(() => {{
        const found = Array.from(d.querySelectorAll(\"#jobs-list .equipment-row\"));
        return found.length >= 5 ? found : null;
      }}, \"Jobkarten\");

      if (!w.BunkerUIPrefs || typeof w.BunkerUIPrefs.set !== \"function\") {{
        throw new Error(\"BunkerUIPrefs fehlt\");
      }}
      w.BunkerUIPrefs.set(\"highContrast\", true);
      await waitFor(() => d.body.classList.contains(\"ui-high-contrast\"), \"Hoher Kontrast\");

      const reducedRows = rows.filter((row) => row.dataset.payoutReducedByEnergy === \"true\");
      const fullRows = rows.filter((row) => row.dataset.payoutReducedByEnergy === \"false\");
      if (!reducedRows.length || !fullRows.length) {{
        throw new Error(`Fixture braucht volle und reduzierte Jobkarten: reduziert=${{reducedRows.length}}, voll=${{fullRows.length}}`);
      }}

      for (const row of reducedRows) {{
        const detail = row.querySelector(\":scope > div:first-child span:last-child\");
        const run = row.querySelector(\":scope > .inline-actions > button.primary\");
        if (!text(detail).includes({CONTEXT!r})) {{
          throw new Error(\"Reduzierte Jobkarte erklärt die Lohnursache nicht\");
        }}
        if (!(run?.getAttribute(\"aria-label\") || \"\").includes({CONTEXT!r})) {{
          throw new Error(\"Reduzierte Jobkarte verliert den Hinweis im aria-label\");
        }}
        if (!text(run).includes(\"AKTUELL\")) {{
          throw new Error(\"Reduzierter Jobbutton zeigt den aktuellen Lohn nicht klar\");
        }}
      }}

      for (const row of fullRows) {{
        if (text(row).includes({CONTEXT!r})) {{
          throw new Error(\"Volllohn-Jobkarte zeigt fälschlich den Reduktionshinweis\");
        }}
      }}

      const viewportWidth = d.documentElement.clientWidth;
      for (const row of rows) {{
        const rect = row.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0 || rect.left < -1 || rect.right > viewportWidth + 1) {{
          throw new Error(`Jobkarte passt nicht ins kleine Fenster: left=${{rect.left.toFixed(1)}}, right=${{rect.right.toFixed(1)}}, viewport=${{viewportWidth}}`);
        }}
      }}

      document.body.textContent = `JOB_PAYOUT_CONTEXT_E2E: PASS
● BEREIT
BUNKERFREQUENZ – Control Deck
reduziert=${{reducedRows.length}} · voll=${{fullRows.length}} · Energie={FIXTURE_ENERGY} · Hoher Kontrast · kleines Fenster`;
    }} catch (error) {{
      document.body.textContent = `JOB_PAYOUT_CONTEXT_E2E: FAIL · ${{String(error?.message || error)}}`;
    }}
  }}, {{ once: true }});
  frame.src = \"/\";
}})();
</script>
"""


def _passed(dom: str) -> bool:
    return re.search(r"<body(?:\s[^>]*)?>\s*JOB_PAYOUT_CONTEXT_E2E: PASS(?:\s|<)", dom, flags=re.IGNORECASE) is not None


def run() -> None:
    original_name = acceptance.AVATAR_CONTEXT_HARNESS
    original_harness = acceptance._avatar_context_harness
    original_passed = acceptance._avatar_context_passed
    acceptance.AVATAR_CONTEXT_HARNESS = HARNESS_NAME
    acceptance._avatar_context_harness = _harness
    acceptance._avatar_context_passed = _passed
    try:
        with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-job-payout-e2e-") as save_dir:
            _prepare_fixture(save_dir)
            process = acceptance._start_server(save_dir)
            try:
                address = acceptance._wait_for_address(process)
                _, state = acceptance.probe_http(address)
                scene_jobs = state.get("state", {}).get("scene_jobs")
                jobs = scene_jobs.get("jobs") if isinstance(scene_jobs, dict) else None
                if not isinstance(jobs, list):
                    raise RuntimeError("/api/state besitzt keine Scene-Jobs-Projektion")
                reduced = [job for job in jobs if isinstance(job, dict) and job.get("payout_reduced_by_energy") is True]
                full = [job for job in jobs if isinstance(job, dict) and job.get("payout_reduced_by_energy") is False]
                if not reduced or not full:
                    raise RuntimeError(
                        f"Projection-Fixture braucht volle und reduzierte Jobs: reduziert={len(reduced)}, voll={len(full)}"
                    )
                dom = acceptance.browser_dom(address, require_browser=True, avatar_context=True)
                if dom is None or PASS_MARKER not in dom:
                    raise RuntimeError("Chromium lieferte keinen Job-Payout-Context-PASS")
                print(
                    "JOB-PAYOUT-CONTEXT-E2E: PASS · "
                    f"Projection reduziert={len(reduced)} · voll={len(full)} · Energie={FIXTURE_ENERGY} · "
                    "Chromium · Hoher Kontrast · kleines Fenster"
                )
            finally:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except Exception:
                    process.kill()
                    process.wait(timeout=3)
                if process.stdout is not None:
                    process.stdout.close()
    finally:
        acceptance.AVATAR_CONTEXT_HARNESS = original_name
        acceptance._avatar_context_harness = original_harness
        acceptance._avatar_context_passed = original_passed


if __name__ == "__main__":
    run()
