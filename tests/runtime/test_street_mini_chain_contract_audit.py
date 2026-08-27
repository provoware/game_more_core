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
CONTRACT = STREET["follow_up_contract"]


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


def parent_is_contract_eligible(parent: dict[str, object]) -> bool:
    if parent.get("event_type") != CONTRACT["parent_event_type"]:
        return False
    if parent.get("entity_type") != CONTRACT["parent_entity_type"]:
        return False
    entity_id = parent.get("entity_id")
    if not isinstance(entity_id, str) or not entity_id:
        return False
    optional_character_id = parent.get("character_id")
    if CONTRACT["parent_optional_character_id_must_match_entity_id"]:
        return optional_character_id in (None, entity_id)
    return True


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
            self.assertTrue(parent_is_contract_eligible(parent))
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

    def test_contract_v1_catalogs_child_event_and_projection_remains_read_only(self):
        self.assertEqual(CONTRACT["journal_event_type"], "street.followup_resolved")
        self.assertEqual(CONTRACT["parent_event_type"], "street.encounter_resolved")
        self.assertIn("street.followup_resolved", ALLOWED)
        self.assertIn("street.encounter_resolved", SUPPORTED_EVENT_TYPES)
        self.assertIn("street.followup_resolved", SUPPORTED_EVENT_TYPES)
        self.assertTrue(CONTRACT["runtime_authority_only"])
        self.assertFalse(CONTRACT["client_can_write"])
        self.assertEqual(CONTRACT["trigger_policy"], "later_confirmed_street_walk_only")
        self.assertEqual(CONTRACT["maximum_followups_per_trigger_walk"], 1)

    def test_contract_v1_binds_character_to_parent_entity_id_and_fails_closed_on_mismatch(self):
        self.assertEqual(CONTRACT["parent_character_id_source"], "entity_id")
        self.assertTrue(CONTRACT["parent_optional_character_id_must_match_entity_id"])
        self.assertEqual(CONTRACT["child_character_id_source"], "parent.entity_id")
        self.assertEqual(CONTRACT["character_mismatch_policy"], "fail_closed")

        valid_parent = {
            "event_type": "street.encounter_resolved",
            "entity_type": "character",
            "entity_id": "player-local",
            "character_id": "player-local",
        }
        absent_optional_character_id = {
            "event_type": "street.encounter_resolved",
            "entity_type": "character",
            "entity_id": "player-local",
        }
        mismatch = dict(valid_parent, character_id="different-character")
        wrong_entity_type = dict(valid_parent, entity_type="district")

        self.assertTrue(parent_is_contract_eligible(valid_parent))
        self.assertTrue(parent_is_contract_eligible(absent_optional_character_id))
        self.assertFalse(parent_is_contract_eligible(mismatch))
        self.assertFalse(parent_is_contract_eligible(wrong_entity_type))

    def test_real_parent_mismatch_reproduced_by_audit_is_rejected_by_contract_v1(self):
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
            self.assertEqual(parent["entity_id"], "player-local")
            self.assertEqual(parent["character_id"], "different-character")
            self.assertFalse(parent_is_contract_eligible(parent))

    def test_contract_v1_defines_deterministic_causality_and_exactly_once_on_existing_kernel(self):
        parent_id = "street-parent:001"
        followup_id = "cable_tip_echo"
        event_id = CONTRACT["event_id_pattern"].format(
            parent_event_id=parent_id,
            followup_id=followup_id,
        )
        correlation_id = CONTRACT["correlation_id_pattern"].format(parent_event_id=parent_id)
        event = {
            "event_id": event_id,
            "event_type": CONTRACT["journal_event_type"],
            "payload": {
                "parent_event_id": parent_id,
                "character_id": "player-local",
                "followup_id": followup_id,
            },
            "causation_id": parent_id,
            "correlation_id": correlation_id,
        }

        self.assertEqual(event_id, "street-followup:street-parent:001:cable_tip_echo")
        self.assertEqual(correlation_id, "street-chain:street-parent:001")
        self.assertEqual(
            set(CONTRACT["required_payload_fields"]),
            {"parent_event_id", "character_id", "followup_id"},
        )

        with tempfile.TemporaryDirectory() as root:
            kernel = PersistenceKernel(root, ALLOWED)
            kernel.initialize_state({"character": {"character_id": "player-local"}})

            first = kernel.commit(
                transaction_id="tx:street-chain-contract-v1",
                events=[event],
                derived_state={"character": {"character_id": "player-local"}},
                context=context("street-chain-contract-v1"),
            )
            self.assertEqual(first.event_ids, (event_id,))
            record = kernel.read_records()[0]
            self.assertEqual(record["payload"]["parent_event_id"], parent_id)
            self.assertEqual(record["causation_id"], parent_id)
            self.assertEqual(record["correlation_id"], correlation_id)

            retry = kernel.commit(
                transaction_id="tx:street-chain-contract-v1-retry",
                events=[event],
                derived_state={"character": {"character_id": "player-local"}},
                context=context("street-chain-contract-v1-retry"),
            )
            self.assertEqual(retry.event_ids, ())
            self.assertEqual(len(kernel.read_records()), 1)

            conflicting = dict(event)
            conflicting["payload"] = dict(event["payload"], parent_event_id="different-parent:001")
            with self.assertRaisesRegex(PersistenceError, "Doppeltes Event mit anderem Inhalt"):
                kernel.commit(
                    transaction_id="tx:street-chain-contract-v1-conflict",
                    events=[conflicting],
                    derived_state={"character": {"character_id": "player-local"}},
                    context=context("street-chain-contract-v1-conflict"),
                )
            self.assertEqual(len(kernel.read_records()), 1)


if __name__ == "__main__":
    unittest.main()
