from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import desktop_browser_e2e_pro as desktop  # noqa: E402
import start_a4_acceptance as acceptance  # noqa: E402


class RuntimeOwnedEvidenceReceiptTests(unittest.TestCase):
    def _runtime(self) -> Mock:
        runtime = Mock()
        runtime.city_map_manifest = {
            "locations": [
                {"location_id": "expensive", "purchasable": True, "purchase_price_cents": 9_000_000},
                {"location_id": "cheap", "purchasable": True, "purchase_price_cents": 3_100_000},
            ]
        }
        runtime.starter = {
            "event": {"event_id": "event-e2e", "budget_cents": 100_000},
            "character": {"character_id": "player-local"},
        }
        runtime.bootstrap.return_value = {"status": "confirmed"}
        runtime._context.return_value = object()
        runtime.session.dispatch.return_value = Mock(
            status="confirmed",
            error_code=None,
            committed_event_ids=(
                "acceptance-owned-map-purchase:economy",
                "acceptance-owned-map-purchase:property",
            ),
            metadata={
                "property": {
                    "location_id": "cheap",
                    "owner_character_id": "player-local",
                    "purchase_price_cents": 3_100_000,
                    "economy_transaction_id": "property:acceptance-owned-map-purchase",
                    "event_id": "event-e2e",
                }
            },
        )
        runtime.session.read_state.return_value = {
            "economy": {
                "ledger": [
                    {
                        "transaction_id": "property:acceptance-owned-map-purchase",
                        "kind": "property_purchase",
                        "item_id": "property:cheap",
                        "quantity": 1,
                        "unit_price_cents": 3_100_000,
                        "budget_delta_cents": -3_100_000,
                        "compensates": None,
                    }
                ]
            }
        }
        return runtime

    def test_receipt_uses_confirmed_property_result_and_ledger(self):
        runtime = self._runtime()
        with patch.object(acceptance.game_client, "A4ClientRuntime", return_value=runtime):
            receipt = acceptance.prepare_owned_map_fixture(Path("/isolated/save"), include_evidence=True)

        self.assertIsInstance(receipt, dict)
        assert isinstance(receipt, dict)
        self.assertEqual(receipt["status"], "confirmed")
        self.assertEqual(receipt["command_type"], "property.purchase")
        self.assertEqual(receipt["location_id"], "cheap")
        self.assertEqual(receipt["property_event_id"], "acceptance-owned-map-purchase:property")
        self.assertEqual(receipt["economy_event_id"], "acceptance-owned-map-purchase:economy")
        self.assertEqual(receipt["economy_transaction_id"], "property:acceptance-owned-map-purchase")
        self.assertEqual(receipt["ledger_kind"], "property_purchase")
        self.assertEqual(receipt["ledger_item_id"], "property:cheap")
        self.assertEqual(receipt["purchase_price_cents"], 3_100_000)
        self.assertEqual(receipt["owner_character_id"], "player-local")
        self.assertEqual(receipt["event_id"], "event-e2e")
        self.assertEqual(runtime.starter["event"]["budget_cents"], 3_100_000)

        command = runtime.session.dispatch.call_args.args[0]
        self.assertEqual(
            command,
            {
                "type": "property.purchase",
                "command_id": "acceptance-owned-map-purchase",
                "location_id": "cheap",
            },
        )
        self.assertNotIn("purchase_price_cents", command)
        self.assertNotIn("owner_character_id", command)

    def test_default_fixture_contract_remains_location_id_only(self):
        runtime = self._runtime()
        runtime.session.dispatch.return_value = Mock(status="confirmed", error_code=None)
        with patch.object(acceptance.game_client, "A4ClientRuntime", return_value=runtime):
            location_id = acceptance.prepare_owned_map_fixture(Path("/isolated/save"))
        self.assertEqual(location_id, "cheap")
        runtime.session.read_state.assert_not_called()

    def test_desktop_evidence_parser_requires_confirmed_event_and_ledger_references(self):
        payload = {
            "location_id": "cheap",
            "command_type": "property.purchase",
            "command_id": "acceptance-owned-map-purchase",
            "status": "confirmed",
            "property_event_id": "acceptance-owned-map-purchase:property",
            "economy_event_id": "acceptance-owned-map-purchase:economy",
            "committed_event_ids": [
                "acceptance-owned-map-purchase:economy",
                "acceptance-owned-map-purchase:property",
            ],
            "economy_transaction_id": "property:acceptance-owned-map-purchase",
            "ledger_kind": "property_purchase",
            "ledger_item_id": "property:cheap",
            "purchase_price_cents": 3_100_000,
            "owner_character_id": "player-local",
            "event_id": "event-e2e",
        }
        output = acceptance.OWNED_EVIDENCE_PREFIX + json.dumps(payload, sort_keys=True)
        parsed = desktop._extract_owned_evidence(output)
        self.assertEqual(parsed, payload)

        broken = dict(payload)
        broken["committed_event_ids"] = ["acceptance-owned-map-purchase:economy"]
        broken_output = acceptance.OWNED_EVIDENCE_PREFIX + json.dumps(broken, sort_keys=True)
        with self.assertRaisesRegex(RuntimeError, "Property-Ereignisreferenz"):
            desktop._extract_owned_evidence(broken_output)

    def test_existing_browser_evidence_keeps_receipt_in_scenario_detail(self):
        source = (ROOT / "tools" / "desktop_browser_e2e_pro.py").read_text(encoding="utf-8")
        self.assertIn('"runtime_owned_evidence_receipt": receipt', source)
        self.assertIn("runtime_owned_evidence_receipt_location_event_ledger", source)
        self.assertNotIn("RUNTIME_OWNED_EVIDENCE.json", source)


if __name__ == "__main__":
    unittest.main()
