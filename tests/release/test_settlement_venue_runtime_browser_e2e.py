from copy import deepcopy
from html import unescape
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[2]
if str(ROOT / 'tools') not in sys.path:
    sys.path.insert(0, str(ROOT / 'tools'))

import start_a4_acceptance as acceptance
import start_a4_game_client as game_client
from bunkerfrequenz.application.settlement_service import SettlementService
from bunkerfrequenz.domain.settlement import LEGACY_SETTLEMENT_CONTRACT_VERSION


class SettlementVenueRuntimeBrowserTests(unittest.TestCase):
    def test_owned_unowned_and_legacy_receipts_survive_reopen_api_and_real_dom(self):
        for mode in ('owned', 'unowned', 'legacy'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix='venue-receipt-browser-') as tmp:
                runtime = game_client.A4ClientRuntime(Path(tmp))
                # Isolated GENESIS fixture; all purchase, upgrade and settlement writes use real commands.
                state = deepcopy(runtime.starter)
                state.pop('schema_version')
                state['event']['phase'] = 'settlement'
                state['event']['revision'] = 8
                state['event']['budget_cents'] = 10_000_000
                state['event']['location']['location_id'] = 'signalwerk'
                state['event']['location']['display_name'] = 'Signalwerk <img src=x onerror=alert(1)>'
                runtime.kernel.initialize_state(state)
                if mode == 'owned':
                    commands = [
                        {'type': 'property.purchase', 'command_id': 'venue-buy', 'location_id': 'signalwerk'},
                        {'type': 'property.upgrade', 'command_id': 'venue-stage-1', 'location_id': 'signalwerk', 'upgrade_id': 'stage'},
                        {'type': 'property.upgrade', 'command_id': 'venue-stage-2', 'location_id': 'signalwerk', 'upgrade_id': 'stage'},
                    ]
                    for command in commands:
                        result = runtime.command(command)
                        self.assertEqual(result['status'], 'confirmed', result)
                if mode == 'legacy':
                    runtime.session.settlement = SettlementService(
                        runtime.kernel, contract_version=LEGACY_SETTLEMENT_CONTRACT_VERSION)
                command = {'type': 'settlement.complete', 'command_id': 'venue-complete'}
                result = runtime.command(command)
                self.assertEqual(result['status'], 'confirmed', result)
                receipt = runtime.kernel.load_state()['settlement']
                if mode == 'owned':
                    self.assertEqual(receipt['venue_evidence']['audience_pull'], 94)
                    upgraded = runtime.command({
                        'type': 'property.upgrade', 'command_id': 'venue-stage-after-settlement',
                        'location_id': 'signalwerk', 'upgrade_id': 'stage',
                    })
                    self.assertEqual(upgraded['status'], 'confirmed', upgraded)
                    self.assertEqual(runtime.kernel.load_state()['settlement'], receipt)
                elif mode == 'unowned':
                    self.assertIsNone(receipt['venue_evidence'])
                else:
                    self.assertNotIn('venue_evidence', receipt)
                records = runtime.kernel.read_records()
                reopened = game_client.A4ClientRuntime(Path(tmp))
                retry = reopened.command(command)
                self.assertEqual(retry['status'], 'confirmed', retry)
                self.assertTrue(retry['idempotent_replay'])
                self.assertEqual(reopened.kernel.read_records(), records)
                self.assertEqual(reopened.projection()['settlement'], receipt)
                process = acceptance._start_server(tmp)
                try:
                    address = acceptance._wait_for_address(process)
                    _, api = acceptance.probe_http(address)
                    self.assertEqual(api['state']['settlement'], receipt)
                    dom = acceptance.browser_dom(address, require_browser=True, avatar_context=False)
                    match = re.search(r'<p id="settlement-venue-evidence">(.*?)</p>', dom, re.S)
                    self.assertIsNotNone(match, 'Ortsnachweis fehlt im echten Chromium-DOM')
                    markup = match.group(1)
                    text = unescape(markup)
                    if mode == 'owned':
                        self.assertEqual(api['state']['settlement_venue_comparison'], {
                            'location_id': 'signalwerk', 'at_settlement': 94, 'current': 99,
                        })
                        self.assertIn('Eigener Veranstaltungsort bestätigt: Signalwerk', text)
                        self.assertIn('94/100', text)
                        self.assertIn('keinen zusätzlichen Gewinn oder Bonus', text)
                        self.assertIn('&lt;img', markup)
                        self.assertNotIn('<img', markup)
                        self.assertIn('Heutige Publikumskraft: 99/100', dom)
                    elif mode == 'unowned':
                        self.assertIn('Kein eigener Veranstaltungsort', text)
                        self.assertNotIn('/100', text)
                    else:
                        self.assertIn('Ältere Abrechnung', text)
                        self.assertNotIn('/100', text)
                    self.assertEqual(game_client.A4ClientRuntime(Path(tmp)).kernel.read_records(), records)
                finally:
                    if process.poll() is None:
                        process.terminate()
                    process.wait(timeout=5)
                    if process.stdout:
                        process.stdout.close()


if __name__ == '__main__':
    unittest.main()
