from __future__ import annotations

import gc
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import start_a4_acceptance as acceptance  # noqa: E402
import start_a4_game_client as game_client  # noqa: E402
from bunkerfrequenz.application import street_encounter_service as street_module  # noqa: E402


class StreetChainRuntimeBrowserE2ETests(unittest.TestCase):
    def _force_encounter(self, runtime, encounter_id: str):
        service = runtime.session.street
        self.assertIsNotNone(service)
        selected = next(item for item in service.encounters if item["encounter_id"] == encounter_id)
        return patch.object(street_module, "_select", return_value=selected)

    def test_confirmed_street_chain_survives_retry_reopen_api_and_real_browser(self):
        with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-street-chain-browser-") as root:
            save_dir = Path(root) / "save"
            runtime = game_client.A4ClientRuntime(save_dir)
            bootstrap = runtime.bootstrap({"command_id": "acceptance-street-chain-bootstrap"})
            self.assertEqual(bootstrap.get("status"), "confirmed")

            with self._force_encounter(runtime, "street.cable_tip"):
                first = runtime.command({
                    "type": "street.walk",
                    "command_id": "street-chain-e2e-parent",
                    "approach_id": "balanced",
                })
            self.assertEqual(first.get("status"), "confirmed")
            self.assertEqual(first["metadata"]["street_encounter"]["encounter_id"], "street.cable_tip")

            parent_event_id = "street-chain-e2e-parent:001"
            child_event_id = f"street-followup:{parent_event_id}:cable_tip_echo"
            self.assertFalse(runtime.kernel.has_event(child_event_id))

            with self._force_encounter(runtime, "street.cable_tip"):
                second = runtime.command({
                    "type": "street.walk",
                    "command_id": "street-chain-e2e-child",
                    "approach_id": "balanced",
                })
            self.assertEqual(second.get("status"), "confirmed")
            self.assertIn(child_event_id, second.get("committed_event_ids", []))

            child = next(record for record in runtime.kernel.read_records() if record["event_id"] == child_event_id)
            self.assertEqual(child["event_type"], "street.followup_resolved")
            self.assertEqual(child["causation_id"], parent_event_id)
            self.assertEqual(child["correlation_id"], f"street-chain:{parent_event_id}")
            self.assertEqual(child["payload"]["parent_event_id"], parent_event_id)
            self.assertEqual(child["payload"]["character_id"], runtime.starter["character"]["character_id"])
            self.assertEqual(child["payload"]["followup_id"], "cable_tip_echo")

            records_before_retry = runtime.kernel.read_records()
            retry = runtime.command({
                "type": "street.walk",
                "command_id": "street-chain-e2e-child",
                "approach_id": "balanced",
            })
            self.assertEqual(retry.get("status"), "confirmed")
            self.assertTrue(retry.get("idempotent_replay"))
            self.assertEqual(runtime.kernel.read_records(), records_before_retry)
            self.assertEqual(sum(record["event_id"] == child_event_id for record in records_before_retry), 1)

            projected = runtime.projection()["event_timeline"]
            child_projection = next(
                entry
                for entry in projected
                if entry.get("metadata", {}).get("followup_id") == "cable_tip_echo"
            )
            self.assertEqual(child_projection["title"], "Der Tipp macht die Runde")
            self.assertEqual(child_projection["caused_by"]["event_id"], parent_event_id)
            self.assertEqual(child_projection["caused_by"]["title"], "Kabeltipp am Bauzaun")

            # Re-open the exact persisted save through the normal local server and real Chromium DOM.
            del runtime
            gc.collect()
            process = acceptance._start_server(str(save_dir))
            try:
                address = acceptance._wait_for_address(process)
                _, state_payload = acceptance.probe_http(address)
                api_timeline = state_payload["state"]["event_timeline"]
                api_child = next(
                    entry
                    for entry in api_timeline
                    if entry.get("metadata", {}).get("followup_id") == "cable_tip_echo"
                )
                self.assertEqual(api_child["title"], "Der Tipp macht die Runde")
                self.assertEqual(api_child["caused_by"]["title"], "Kabeltipp am Bauzaun")

                dom = acceptance.browser_dom(address, require_browser=True, avatar_context=False)
                self.assertIsNotNone(dom)
                assert dom is not None
                self.assertIn("Der Tipp macht die Runde", dom)
                self.assertIn("Folge von: Kabeltipp am Bauzaun", dom)
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


if __name__ == "__main__":
    unittest.main()
