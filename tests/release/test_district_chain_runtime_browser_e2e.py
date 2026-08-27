from __future__ import annotations

import gc
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import start_a4_acceptance as acceptance  # noqa: E402
import start_a4_game_client as game_client  # noqa: E402


class DistrictChainRuntimeBrowserE2ETests(unittest.TestCase):
    def _force_event(self, service, event_id: str) -> None:
        selected = next(item for item in service.events if item["event_id"] == event_id)
        service._select = lambda _eligible, **_kwargs: selected

    def _trigger(self, runtime, *, district_id: str, trigger_id: str, event_id: str):
        service = runtime.session.district_events
        self.assertIsNotNone(service)
        self._force_event(service, event_id)
        character_id = runtime.starter["character"]["character_id"]
        return service.trigger(
            world_seed="district-chain-browser-e2e",
            district_id=district_id,
            trigger_id=trigger_id,
            context=runtime._context(
                f"acceptance-{trigger_id}",
                "district",
                district_id,
                character_id,
            ),
        )

    def test_both_confirmed_chains_survive_replay_district_boundary_projection_and_real_browser(self):
        with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-district-chain-browser-") as root:
            save_dir = Path(root) / "save"
            runtime = game_client.A4ClientRuntime(save_dir)
            bootstrap = runtime.bootstrap({"command_id": "acceptance-district-chain-bootstrap"})
            self.assertEqual(bootstrap.get("status"), "confirmed")

            service = runtime.session.district_events
            self.assertIsNotNone(service)
            service._cadence_block_reason = lambda _trigger_id: None

            # Story 001: Parent in Friedrichshain. A later cycle in Mitte must not consume it.
            first_parent = self._trigger(
                runtime,
                district_id="friedrichshain",
                trigger_id="chain-001-parent",
                event_id="district.power_flicker",
            )
            self.assertEqual(first_parent.event_id, "district.power_flicker")
            self._trigger(
                runtime,
                district_id="mitte",
                trigger_id="chain-001-wrong-district",
                event_id="district.word_of_mouth_wave",
            )
            self.assertEqual(
                [r for r in runtime.kernel.read_records() if r.get("event_type") == "world.district_followup_resolved"],
                [],
            )

            first_child_cycle = self._trigger(
                runtime,
                district_id="friedrichshain",
                trigger_id="chain-001-child",
                event_id="district.word_of_mouth_wave",
            )
            self.assertEqual(first_child_cycle.district_result.metadata["followup"]["followup_id"], "power_flicker_afterglow")
            before_retry = runtime.kernel.read_records()
            first_retry = self._trigger(
                runtime,
                district_id="friedrichshain",
                trigger_id="chain-001-child",
                event_id="district.patrol_sweep",
            )
            self.assertTrue(first_retry.district_result.idempotent_replay)
            self.assertEqual(runtime.kernel.read_records(), before_retry)

            # Story 002: same contract, different parent and narrative. Again fail closed across districts.
            second_parent = self._trigger(
                runtime,
                district_id="friedrichshain",
                trigger_id="chain-002-parent",
                event_id="district.temporary_space_opens",
            )
            self.assertEqual(second_parent.event_id, "district.temporary_space_opens")
            self._trigger(
                runtime,
                district_id="mitte",
                trigger_id="chain-002-wrong-district",
                event_id="district.patrol_sweep",
            )
            children_before_second = [
                r for r in runtime.kernel.read_records() if r.get("event_type") == "world.district_followup_resolved"
            ]
            self.assertEqual(len(children_before_second), 1)

            second_child_cycle = self._trigger(
                runtime,
                district_id="friedrichshain",
                trigger_id="chain-002-child",
                event_id="district.patrol_sweep",
            )
            self.assertEqual(
                second_child_cycle.district_result.metadata["followup"]["followup_id"],
                "temporary_space_afterimage",
            )
            before_second_retry = runtime.kernel.read_records()
            second_retry = self._trigger(
                runtime,
                district_id="friedrichshain",
                trigger_id="chain-002-child",
                event_id="district.power_flicker",
            )
            self.assertTrue(second_retry.district_result.idempotent_replay)
            self.assertEqual(runtime.kernel.read_records(), before_second_retry)

            children = [
                record
                for record in runtime.kernel.read_records()
                if record.get("event_type") == "world.district_followup_resolved"
            ]
            self.assertEqual(len(children), 2)
            by_followup = {record["payload"]["followup_id"]: record for record in children}
            self.assertEqual(set(by_followup), {"power_flicker_afterglow", "temporary_space_afterimage"})
            for record in by_followup.values():
                self.assertEqual(record["payload"]["district_id"], "friedrichshain")
                self.assertEqual(record["causation_id"], record["payload"]["parent_event_id"])
                self.assertEqual(record["correlation_id"], f"district-chain:{record['payload']['parent_event_id']}")

            projected = runtime.projection()["event_timeline"]
            projected_children = {
                entry["metadata"]["followup_id"]: entry
                for entry in projected
                if entry.get("metadata", {}).get("followup_id") in by_followup
            }
            self.assertEqual(
                projected_children["power_flicker_afterglow"]["caused_by"]["title"],
                "Das Netz flackert",
            )
            self.assertEqual(
                projected_children["temporary_space_afterimage"]["caused_by"]["title"],
                "Eine Tür steht plötzlich offen",
            )

            # Re-open the same persisted save through the real local server and real Chromium DOM.
            del runtime
            gc.collect()
            process = acceptance._start_server(str(save_dir))
            try:
                address = acceptance._wait_for_address(process)
                _, state_payload = acceptance.probe_http(address)
                api_timeline = state_payload["state"]["event_timeline"]
                api_causes = {
                    entry.get("caused_by", {}).get("title")
                    for entry in api_timeline
                    if isinstance(entry.get("caused_by"), dict)
                }
                self.assertIn("Das Netz flackert", api_causes)
                self.assertIn("Eine Tür steht plötzlich offen", api_causes)

                dom = acceptance.browser_dom(address, require_browser=True, avatar_context=False)
                self.assertIsNotNone(dom)
                assert dom is not None
                self.assertIn("Das Licht ist zurück – die Erinnerung bleibt", dom)
                self.assertIn("Die Tür ist zu – die Adresse lebt weiter.", dom)
                self.assertIn("Folge von: Das Netz flackert", dom)
                self.assertIn("Folge von: Eine Tür steht plötzlich offen", dom)
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
