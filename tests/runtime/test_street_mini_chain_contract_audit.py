from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.street_encounter_service import StreetEncounterService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel
from bunkerfrequenz.presentation.event_timeline import SUPPORTED_EVENT_TYPES


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str, *, character_id: str | None = "player-local") -> JournalContext:
    return JournalContext(
        "2026-08-27T05:30:00+02:00",
        "street-chain-audit",
        "player-local",
        "character",
        "player-local",
        command_id,
        "street-mini-chain-contract-audit",
        "0.8.8",
        character_id,
    )


class StreetMiniChainContractAuditTests(unittest.TestCase):
    def test_confirmed_street_encounter_is_stable_replayable_entity_bound_parent_evidence(self):
        with tempfile.TemporaryDirectory() as root:
            kernel = PersistenceKernel(root, ALLOWED)
            character = CharacterState("player-local", "Street Chain Audit")
            kernel.initialize_state({"character": character.to_dict()})
            service = StreetEncounterService(kernel, STREET)

            first = service.walk(
                character,
                walk_instance_id="street-chain-parent",
                world_seed="street-chain-audit-seed",
                journal_context=context("street-chain-parent"),
                approach_id="network",
            )
            records_after_first = kernel.read_records()
            parent = records_after_first[0]

            self.assertFalse(first.idempotent_replay)
            self.assertEqual(parent["event_id"], "street-chain-parent:001")
            self.assertEqual(parent["event_type"], "street.encounter_resolved")
            self.assertEqual(parent["entity_type"], "character")
            self.assertEqual(parent["entity_id"], "player-local")
            self.assertEqual(parent["character_id"], "player-local")
            self.assertEqual(parent["payload"]["walk_instance_id"], "street-chain-parent")
            self.assertEqual(parent["payload"]["approach_id"], "network")
            self.assertIn("encounter_id", parent["payload"])
            self.assertIn("contract_version", parent["payload"])

            replay = service.walk(
                character,
                walk_instance_id="street-chain-parent",
                world_seed="a-different-seed-must-not-reroll",
                journal_context=context("street-chain-parent"),
                approach_id="network",
            )
            self.assertTrue(replay.idempotent_replay)
            self.assertEqual(replay.encounter_id, first.encounter_id)
            self.assertEqual(kernel.read_records(), records_after_first)

    def test_optional_journal_character_id_is_not_yet_a_safe_chain_authority(self):
        """Audit finding: current Street validation trusts entity_id, not context.character_id."""
        with tempfile.TemporaryDirectory() as root:
            kernel = PersistenceKernel(root, ALLOWED)
            character = CharacterState("player-local", "Street Chain Audit")
            kernel.initialize_state({"character": character.to_dict()})
            service = StreetEncounterService(kernel, STREET)

            result = service.walk(
                character,
                walk_instance_id="street-chain-character-id-gap",
                world_seed="street-chain-audit-seed",
                journal_context=context(
                    "street-chain-character-id-gap",
                    character_id="different-character",
                ),
                approach_id="balanced",
            )
            self.assertFalse(result.idempotent_replay)
            parent = kernel.read_records()[0]
            self.assertEqual(parent["entity_type"], "character")
            self.assertEqual(parent["entity_id"], "player-local")
            self.assertEqual(parent["character_id"], "different-character")

            # Contract V1 must therefore use entity_id as the current canonical
            # parent identity and fail closed on absent/mismatched character_id
            # before any Street child can be approved.
            self.assertNotEqual(parent["character_id"], parent["entity_id"])

    def test_production_contract_has_no_street_child_event_or_projection_yet(self):
        self.assertIn("street.encounter_resolved", ALLOWED)
        self.assertNotIn("street.followup_resolved", ALLOWED)
        self.assertIn("street.encounter_resolved", SUPPORTED_EVENT_TYPES)
        self.assertNotIn("street.followup_resolved", SUPPORTED_EVENT_TYPES)

        with tempfile.TemporaryDirectory() as root:
            kernel = PersistenceKernel(root, ALLOWED)
            kernel.initialize_state({})
            with self.assertRaisesRegex(PersistenceError, "Nicht katalogisierter Journal-Eventtyp"):
                kernel.commit(
                    transaction_id="tx:street-followup-not-yet-contract",
                    events=[{
                        "event_id": "street-followup:missing-contract",
                        "event_type": "street.followup_resolved",
                        "payload": {
                            "parent_event_id": "street-chain-parent:001",
                            "followup_id": "audit-only",
                            "character_id": "player-local",
                        },
                        "causation_id": "street-chain-parent:001",
                        "correlation_id": "street-chain:street-chain-parent:001",
                    }],
                    derived_state={},
                    context=context("street-followup-not-yet-contract"),
                )
            self.assertEqual(kernel.read_records(), ())

    def test_existing_persistence_kernel_supports_generic_causality_and_exactly_once_without_district_logic(self):
        allowed = {"audit.street_followup_probe"}
        with tempfile.TemporaryDirectory() as root:
            kernel = PersistenceKernel(root, allowed)
            kernel.initialize_state({"character": {"character_id": "player-local"}})
            parent_id = "street-parent:001"
            event = {
                "event_id": "street-followup:street-parent:001:cable-tip-echo",
                "event_type": "audit.street_followup_probe",
                "payload": {
                    "parent_event_id": parent_id,
                    "character_id": "player-local",
                    "followup_id": "cable_tip_echo",
                },
                "causation_id": parent_id,
                "correlation_id": f"street-chain:{parent_id}",
            }

            first = kernel.commit(
                transaction_id="tx:street-chain-probe",
                events=[event],
                derived_state={"character": {"character_id": "player-local"}},
                context=context("street-chain-probe"),
            )
            self.assertEqual(first.event_ids, (event["event_id"],))
            record = kernel.read_records()[0]
            self.assertEqual(record["payload"]["parent_event_id"], parent_id)
            self.assertEqual(record["causation_id"], parent_id)
            self.assertEqual(record["correlation_id"], f"street-chain:{parent_id}")

            retry = kernel.commit(
                transaction_id="tx:street-chain-probe-retry",
                events=[event],
                derived_state={"character": {"character_id": "player-local"}},
                context=context("street-chain-probe-retry"),
            )
            self.assertEqual(retry.event_ids, ())
            self.assertEqual(len(kernel.read_records()), 1)

            conflicting = dict(event)
            conflicting["payload"] = dict(event["payload"], parent_event_id="different-parent:001")
            with self.assertRaisesRegex(PersistenceError, "Doppeltes Event mit anderem Inhalt"):
                kernel.commit(
                    transaction_id="tx:street-chain-probe-conflict",
                    events=[conflicting],
                    derived_state={"character": {"character_id": "player-local"}},
                    context=context("street-chain-probe-conflict"),
                )
            self.assertEqual(len(kernel.read_records()), 1)


if __name__ == "__main__":
    unittest.main()
