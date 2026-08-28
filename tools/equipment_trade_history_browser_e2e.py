#!/usr/bin/env python3
"""Real Chromium proof for the read-only Equipment trade history."""

from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import start_a4_acceptance as acceptance  # noqa: E402
import start_a4_game_client as game_client  # noqa: E402


HARNESS_NAME = "__equipment_trade_history_e2e__.html"
PASS_MARKER = "EQUIPMENT_TRADE_HISTORY_E2E: PASS"
ITEM_ID = "equipment.pa"
UNIT_PRICE_CENTS = 10_000
COMPENSATED_BUY_ID = "acceptance-trade-history-compensated-buy"
COMPENSATION_ID = "acceptance-trade-history-compensation"
DENSITY_LIMIT = 8
LONG_DISPLAY_LABEL = (
    "Mobiles Vierkanal-Hochleistungs-Soundsystem mit wetterfester "
    "Verstärker- und Kabelverteilung"
)
MODE = "empty"


def _prepare_fixture(save_dir: str | Path) -> None:
    runtime = game_client.A4ClientRuntime(Path(save_dir))
    economy = runtime.starter.get("economy")
    if not isinstance(economy, dict):
        raise RuntimeError("Trade-History-E2E-Starter besitzt keinen Economy-State")
    economy["ledger"] = [
        {
            "transaction_id": COMPENSATED_BUY_ID,
            "kind": "buy",
            "item_id": ITEM_ID,
            "quantity": 1,
            "unit_price_cents": UNIT_PRICE_CENTS,
            "budget_delta_cents": -UNIT_PRICE_CENTS,
            "compensates": None,
        },
        {
            "transaction_id": COMPENSATION_ID,
            "kind": "sell",
            "item_id": ITEM_ID,
            "quantity": 1,
            "unit_price_cents": UNIT_PRICE_CENTS,
            "budget_delta_cents": UNIT_PRICE_CENTS,
            "compensates": COMPENSATED_BUY_ID,
        },
    ]
    economy["revision"] = 2
    bootstrap = runtime.bootstrap({"command_id": "acceptance-trade-history-bootstrap"})
    if bootstrap.get("status") != "confirmed":
        raise RuntimeError(f"Trade-History-E2E konnte den Starter nicht bestätigen: {bootstrap}")
    history = runtime.projection().get("economy", {}).get("trade_history")
    if history != []:
        raise RuntimeError("Kompensiertes Fixture muss als leere wirksame Handelshistorie projiziert werden")


def _add_effective_buy_and_sell(save_dir: str | Path) -> list[dict]:
    runtime = game_client.A4ClientRuntime(Path(save_dir))
    for kind in ("buy", "sell"):
        result = runtime.command({
            "type": "economy.transact",
            "command_id": f"acceptance-trade-history-{kind}",
            "kind": kind,
            "item_id": ITEM_ID,
            "quantity": 1,
        })
        if result.get("status") != "confirmed":
            raise RuntimeError(f"Trade-History-E2E konnte {kind} nicht bestätigen: {result}")
    history = runtime.projection().get("economy", {}).get("trade_history")
    if not isinstance(history, list) or len(history) != 2:
        raise RuntimeError(f"Projection braucht exakt zwei wirksame Trades, erhalten: {history}")
    if [entry.get("kind") for entry in history] != ["sell", "buy"]:
        raise RuntimeError(f"Trade-History-Reihenfolge ist unerwartet: {history}")
    if any(entry.get("unit_price_cents") != UNIT_PRICE_CENTS for entry in history):
        raise RuntimeError("Trade-History verwendet nicht den bestätigten Ausführungspreis")
    ids = {entry.get("transaction_id") for entry in history}
    if COMPENSATED_BUY_ID in ids or COMPENSATION_ID in ids:
        raise RuntimeError("Kompensiertes Paar ist fälschlich in der wirksamen Projection sichtbar")
    return history


def _extend_to_density_limit(save_dir: str | Path) -> list[dict]:
    runtime = game_client.A4ClientRuntime(Path(save_dir))
    for pair_index in range(3):
        for kind in ("buy", "sell"):
            result = runtime.command({
                "type": "economy.transact",
                "command_id": f"acceptance-trade-history-density-{pair_index}-{kind}",
                "kind": kind,
                "item_id": ITEM_ID,
                "quantity": 1,
            })
            if result.get("status") != "confirmed":
                raise RuntimeError(
                    f"Trade-History-Dichte-Audit konnte {kind} in Paar {pair_index} nicht bestätigen: {result}"
                )
    history = runtime.projection().get("economy", {}).get("trade_history")
    if not isinstance(history, list) or len(history) != DENSITY_LIMIT:
        raise RuntimeError(
            f"Dichte-Audit braucht exakt {DENSITY_LIMIT} wirksame Trades, erhalten: {history}"
        )
    ids = {entry.get("transaction_id") for entry in history}
    if COMPENSATED_BUY_ID in ids or COMPENSATION_ID in ids:
        raise RuntimeError("Kompensiertes Paar ist im Dichte-Maximalfall fälschlich sichtbar")
    return history


def _harness() -> str:
    expected_mode = MODE
    return f"""<!doctype html>
<meta charset=\"utf-8\">
<title>BUNKERFREQUENZ Equipment Trade History E2E</title>
<style>
  html, body {{ margin: 0; background: #05070a; color: #fff; font-family: sans-serif; }}
  #status {{ padding: 8px; font: 700 14px/1.3 monospace; }}
  #app {{ display: block; width: 760px; height: 680px; border: 0; }}
</style>
<div id=\"status\">EQUIPMENT_TRADE_HISTORY_E2E: RUNNING</div>
<iframe id=\"app\"></iframe>
<script>
\"use strict\";
(() => {{
  const frame = document.getElementById(\"app\");
  const expectedMode = {expected_mode!r};
  const densityLimit = {DENSITY_LIMIT};
  const longDisplayLabel = {LONG_DISPLAY_LABEL!r};
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
      const section = await waitFor(() => d.getElementById(\"equipment-trade-history\"), \"Handelsverlauf\");
      await waitFor(() => text(d.getElementById(\"equipment-trade-history-title\")) === \"Letzte Käufe & Verkäufe\", \"Titel\");

      if (!w.BunkerUIPrefs || typeof w.BunkerUIPrefs.set !== \"function\") {{
        throw new Error(\"BunkerUIPrefs fehlt\");
      }}
      w.BunkerUIPrefs.set(\"highContrast\", true);
      await waitFor(() => d.body.classList.contains(\"ui-high-contrast\"), \"Hoher Kontrast\");
      if (expectedMode === \"density\") {{
        w.BunkerUIPrefs.set(\"largeText\", true);
        await waitFor(() => d.body.classList.contains(\"ui-large-text\"), \"Große Schrift\");
      }}

      const rows = Array.from(section.querySelectorAll(\".equipment-row\"));
      if (expectedMode === \"empty\") {{
        if (rows.length !== 0 || !text(section).includes(\"Noch kein wirksamer bestätigter Kauf oder Verkauf.\")) {{
          throw new Error(\"Leere Handelshistorie wird nicht eindeutig dargestellt\");
        }}
      }} else {{
        const expectedRows = expectedMode === \"density\" ? densityLimit : 2;
        await waitFor(
          () => section.querySelectorAll(\".equipment-row\").length === expectedRows,
          expectedMode === \"density\" ? \"acht wirksame Trades\" : \"zwei wirksame Trades\"
        );
        const effectiveRows = Array.from(section.querySelectorAll(\".equipment-row\"));
        const rowText = effectiveRows.map(text);
        if (expectedMode === \"filled\") {{
          if (rowText.filter((value) => value.includes(\"GEKAUFT · PA\")).length !== 1) {{
            throw new Error(\"Bestätigter Kauf fehlt oder ist doppelt\");
          }}
          if (rowText.filter((value) => value.includes(\"VERKAUFT · PA\")).length !== 1) {{
            throw new Error(\"Bestätigter Verkauf fehlt oder ist doppelt\");
          }}
          if (!rowText.every((value) => value.includes(\"Stückpreis 100,00 €\") || value.includes(\"Stückpreis 100,00 €\"))) {{
            throw new Error(\"Historie zeigt nicht den bestätigten Ausführungspreis\");
          }}
        }}
        if (rowText.some((value) => value.includes(\"Gewinn\") || value.includes(\"Verlust\"))) {{
          throw new Error(\"Handelszeile erfindet Gewinn- oder Verlustlogik\");
        }}
        if (section.querySelector(\"button\")) {{
          throw new Error(\"Read-only Handelsverlauf enthält unerwartete Aktion\");
        }}

        if (expectedMode === \"density\") {{
          const stressHeading = effectiveRows[0]?.querySelector(\"strong\");
          if (!stressHeading) throw new Error(\"Dichte-Audit findet keine erste Handelsüberschrift\");
          const action = text(stressHeading).startsWith(\"VERKAUFT\") ? \"VERKAUFT\" : \"GEKAUFT\";
          stressHeading.textContent = `${{action}} · ${{longDisplayLabel}}`;
          if (!text(stressHeading).includes(longDisplayLabel)) {{
            throw new Error(\"Langer Test-Anzeigename wurde nicht sicher gesetzt\");
          }}
        }}
      }}

      const viewportWidth = d.documentElement.clientWidth;
      const effectiveRows = Array.from(section.querySelectorAll(\".equipment-row\"));
      const measured = [section, ...effectiveRows];
      for (const node of measured) {{
        const rect = node.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0 || rect.left < -1 || rect.right > viewportWidth + 1) {{
          throw new Error(`Handelsverlauf passt nicht ins kleine Fenster: left=${{rect.left.toFixed(1)}}, right=${{rect.right.toFixed(1)}}, viewport=${{viewportWidth}}`);
        }}
        if (node.scrollWidth > node.clientWidth + 1) {{
          throw new Error(`Handelsverlauf besitzt horizontale Überbreite: ${{node.scrollWidth}}>${{node.clientWidth}}`);
        }}
      }}
      if (expectedMode === \"density\") {{
        for (const row of effectiveRows) {{
          const info = row.firstElementChild;
          const heading = info?.querySelector(\"strong\");
          const detail = info?.querySelector(\"span\");
          if (!info || !heading || !detail || !text(heading) || !text(detail)) {{
            throw new Error(\"Dichte-Audit verliert Aktions-/Mengen-/Preisstruktur\");
          }}
          const rowRect = row.getBoundingClientRect();
          for (const node of [info, heading, detail]) {{
            const rect = node.getBoundingClientRect();
            if (rect.left < rowRect.left - 1 || rect.right > rowRect.right + 1) {{
              throw new Error(\"Textinhalt ragt aus der Handelszeile heraus\");
            }}
          }}
        }}
      }}

      document.body.textContent = `EQUIPMENT_TRADE_HISTORY_E2E: PASS
● BEREIT
BUNKERFREQUENZ – Control Deck
Modus=${{expectedMode}} · Hoher Kontrast · ${{expectedMode === \"density\" ? \"Große Schrift · 8 Trades · langer Anzeigename · \" : \"\"}}kleines Fenster · read-only`;
    }} catch (error) {{
      document.body.textContent = `EQUIPMENT_TRADE_HISTORY_E2E: FAIL · ${{String(error?.message || error)}}
AVATAR_CONTEXT_E2E: FAIL · ${{String(error?.message || error)}}`;
    }}
  }}, {{ once: true }});
  frame.src = \"/\";
}})();
</script>
"""


def _passed(dom: str) -> bool:
    return re.search(r"<body(?:\s[^>]*)?>\s*EQUIPMENT_TRADE_HISTORY_E2E: PASS(?:\s|<)", dom, flags=re.IGNORECASE) is not None


def _stop(process) -> None:
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=5)
    except Exception:
        process.kill()
        process.wait(timeout=3)
    if process.stdout is not None:
        process.stdout.close()


def _browser_phase(save_dir: str, mode: str) -> None:
    global MODE
    MODE = mode
    process = acceptance._start_server(save_dir)
    try:
        address = acceptance._wait_for_address(process)
        acceptance.probe_http(address)
        dom = acceptance.browser_dom(address, require_browser=True, avatar_context=True)
        if dom is None or PASS_MARKER not in dom:
            raise RuntimeError(f"Chromium lieferte keinen Trade-History-PASS für Modus {mode}")
    finally:
        _stop(process)


def run() -> None:
    original_name = acceptance.AVATAR_CONTEXT_HARNESS
    original_harness = acceptance._avatar_context_harness
    original_passed = acceptance._avatar_context_passed
    acceptance.AVATAR_CONTEXT_HARNESS = HARNESS_NAME
    acceptance._avatar_context_harness = _harness
    acceptance._avatar_context_passed = _passed
    try:
        with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-trade-history-e2e-") as save_dir:
            _prepare_fixture(save_dir)
            _browser_phase(save_dir, "empty")
            history = _add_effective_buy_and_sell(save_dir)
            _browser_phase(save_dir, "filled")
            density_history = _extend_to_density_limit(save_dir)
            _browser_phase(save_dir, "density")
            print(
                "EQUIPMENT-TRADE-HISTORY-E2E: PASS · "
                f"wirksame Trades={len(history)} · Dichte-Maximum={len(density_history)} · "
                f"Ausführungspreis={UNIT_PRICE_CENTS} Cent · Compensation ausgeblendet · "
                "Chromium · Hoher Kontrast · große Schrift · kleines Fenster"
            )
    finally:
        acceptance.AVATAR_CONTEXT_HARNESS = original_name
        acceptance._avatar_context_harness = original_harness
        acceptance._avatar_context_passed = original_passed


if __name__ == "__main__":
    run()
