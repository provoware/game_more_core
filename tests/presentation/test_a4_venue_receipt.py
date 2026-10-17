from pathlib import Path
import os
import subprocess
import tempfile
import unittest

from bunkerfrequenz.application.property_upgrade_service import PropertyUpgradeService
from bunkerfrequenz.application.settlement_service import SettlementService
from bunkerfrequenz.infrastructure.persistence import PersistenceKernel
from tests.runtime.test_game_client_property_upgrade_integration import ALLOWED, PROPERTY
from tests.runtime.test_venue_settlement_receipt import initial_state, context, CITY_MAP, UPGRADES
from tools import start_a4_acceptance as acceptance


ROOT = Path(__file__).parents[2]


class A4VenueReceiptTests(unittest.TestCase):
    def test_renderer_distinguishes_owned_null_and_legacy_without_mutation_or_html(self):
        source = (ROOT / "web/a4/app.js").read_text()
        renderer = source.split("function renderSettlement(p)", 1)[1].split("async function sendCommand", 1)[0]
        script = r'''
const assert = require("node:assert/strict");
class Element {
  constructor() { this.children = []; this.text = ""; }
  append(...children) { this.children.push(...children); }
  replaceChildren() { this.children = []; }
  set textContent(value) { this.text = String(value); this.children = []; }
  get textContent() { return this.text + this.children.map(c => c.textContent).join(" "); }
  set innerHTML(value) { throw Error("Unsafe HTML write"); }
}
const host = new Element();
const $ = () => host;
const document = { createElement: () => new Element() };
''' + "\nfunction renderSettlement(p)" + renderer + r'''
for (const [receipt, expected] of [
  [{venue_evidence: {location_id: "signalwerk", audience_pull: 94}}, "94/100"],
  [{venue_evidence: null}, "kein eigener Veranstaltungsort"],
  [{}, "Ältere Abrechnung"],
]) {
  const p = {settlement: receipt, event: {location: {location_id: "signalwerk", display_name: "<img onerror=alert(1)>"}},
             property_upgrades: {effective_values_by_location: {signalwerk: {audience_pull: 12}}}};
  const before = JSON.stringify(p);
  renderSettlement(p);
  assert.ok(host.textContent.includes(expected), host.textContent);
  assert.ok(host.textContent.includes("keinen zusätzlichen Geldbonus"));
  assert.equal(JSON.stringify(p), before);
  if (receipt.venue_evidence) {
    assert.ok(host.textContent.includes("<img onerror=alert(1)>"));
    assert.ok(!host.textContent.includes("12/100"));
  }
}
console.log("VENUE_RECEIPT_RENDERER: PASS");
'''
        result = subprocess.run(["node", "-e", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VENUE_RECEIPT_RENDERER: PASS", result.stdout)

    @unittest.skipUnless(acceptance.find_browser() and os.environ.get("BUNKER_PLAYWRIGHT_MODULE"),
                         "Realer Browsertest benötigt BUNKER_PLAYWRIGHT_MODULE und Chromium")
    def test_real_browser_keeps_receipt_value_after_confirmed_upgrade_and_reload(self):
        harness_path = ROOT / "web/a4/__venue_receipt_test__.html"
        self.assertFalse(harness_path.exists())
        harness = r'''<!doctype html><meta charset="utf-8"><div id="status">RUNNING</div>
<iframe id="app" style="width:760px;height:680px;border:0"></iframe><script>
const frame = document.getElementById("app");
frame.addEventListener("load", async () => {
  try {
    const w = frame.contentWindow, d = frame.contentDocument;
    const until = async (probe) => {
      for (let i=0;i<160;i++) { if(probe()) return; await new Promise(r=>setTimeout(r,50)); }
      throw Error("readiness timeout");
    };
    await until(()=>d.getElementById("settlement-venue-receipt"));
    w.BunkerUIPrefs.set("largeText",true); w.BunkerUIPrefs.set("highContrast",true);
    await until(()=>d.body.classList.contains("ui-large-text") && d.body.classList.contains("ui-high-contrast"));
    const card = d.getElementById("settlement-venue-receipt");
    if(!card.textContent.includes("94/100") || card.textContent.includes("99/100")) throw Error("historical value lost");
    if(!card.textContent.includes("Eigenes Eigentum") || !card.textContent.includes("keinen zusätzlichen Geldbonus")) throw Error("explanation missing");
    if(card.getBoundingClientRect().height <= 0 || card.closest(".hidden")) throw Error("card hidden");
    if(card.scrollWidth > card.clientWidth+1) throw Error("card overflows");
    const response = await fetch("/api/state"), payload = await response.json();
    const p = payload.state || payload;
    if(p.settlement.venue_evidence.audience_pull !== 94) throw Error("wrong receipt in API");
    if(p.property_upgrades.effective_values_by_location.signalwerk.audience_pull !== 99) throw Error("upgrade fixture not confirmed");
    document.body.textContent = "VENUE_RECEIPT_BROWSER: PASS · saved94/current99 · reload · large text · high contrast · 760x680";
  } catch(error) { document.body.textContent="VENUE_RECEIPT_BROWSER: FAIL · "+error; }
},{once:true}); frame.src="/";
</script>'''
        with tempfile.TemporaryDirectory(prefix="venue-receipt-browser-") as tmp:
            state = initial_state()
            state["event"]["budget_cents"] = 20_000_000
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state(state)
            SettlementService(kernel, city_map_manifest=CITY_MAP, upgrade_manifest=UPGRADES).complete(
                context=context("browser-complete")
            )
            PropertyUpgradeService(kernel, UPGRADES, PROPERTY, CITY_MAP).upgrade(
                "signalwerk", "stage", context=context("browser-upgrade")
            )
            process = acceptance._start_server(tmp)
            try:
                address = acceptance._wait_for_address(process)
                acceptance.probe_http(address)
                harness_path.write_text(harness)
                script = r'''const {chromium} = require(process.argv[1]);
(async () => {
  const browser = await chromium.launch({executablePath:process.argv[2], headless:true, args:["--no-sandbox"], timeout:10000});
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    await page.waitForFunction(() => /VENUE_RECEIPT_BROWSER: (PASS|FAIL)/.test(document.body.textContent), {timeout:15000});
    const result = await page.locator("body").innerText();
    if (!result.includes("VENUE_RECEIPT_BROWSER: PASS")) throw Error(result);
    console.log(result);
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode=1;});'''
                result = subprocess.run([
                    "node", "-e", script, os.environ["BUNKER_PLAYWRIGHT_MODULE"], acceptance.find_browser(),
                    address.rstrip("/") + "/" + harness_path.name,
                ], capture_output=True, text=True, timeout=35)
                self.assertEqual(result.returncode, 0, result.stderr[-2500:])
                self.assertIn("VENUE_RECEIPT_BROWSER: PASS", result.stdout)
            finally:
                harness_path.unlink(missing_ok=True)
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
                if process.stdout:
                    process.stdout.close()


if __name__ == "__main__":
    unittest.main()
