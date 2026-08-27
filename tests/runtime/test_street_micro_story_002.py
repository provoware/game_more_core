from __future__ import annotations

import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from bunkerfrequenz.application.street_encounter_service import StreetEncounterService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
TEXT = json.loads((ROOT / "content" / "de" / "ui" / "street_encounters.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-27T21:30:00+02:00",
        "street-story-002-session",
        "player-local",
        "character",
        "player-local",
        command_id,
        "street-story-002-test",
        "0.8.8",
        "player-local",
    )


def encounter(service: StreetEncounterService, encounter_id: str) -> dict:
    return next(item for item in service.encounters if item["encounter_id"] == encounter_id)


def test_lost_glove_followup_is_catalogued_externalized_and_balance_neutral() -> None:
    story = STREET["micro_story_002"]

    assert story["parent_encounter_id"] == "street.lost_glove"
    assert story["followup_id"] == "lost_glove_fence_echo"
    assert TEXT[story["title_key"]] == "Der Handschuh wartet noch"
    assert "Bauzaun" in TEXT[story["body_key"]]
    assert "keinen Gegenstand" in TEXT[story["body_key"]]
    assert STREET["policy"]["inventory_changes"] is False
    assert STREET["policy"]["economy_changes"] is False


def test_later_confirmed_walk_resolves_lost_glove_followup_atomically_and_exactly_once() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        kernel = PersistenceKernel(tmp, ALLOWED)
        character = CharacterState("player-local", "Street Story 002 Tester")
        kernel.initialize_state({"character": character.to_dict()})
        service = StreetEncounterService(kernel, STREET)

        with patch(
            "bunkerfrequenz.application.street_encounter_service._select",
            return_value=encounter(service, "street.lost_glove"),
        ):
            first = service.walk(
                character,
                walk_instance_id="glove-story-walk-001",
                world_seed="street-story-002-seed",
                journal_context=context("glove-story-walk-001"),
            )

        assert first.encounter_id == "street.lost_glove"
        assert not any(record["event_type"] == "street.followup_resolved" for record in kernel.read_records())

        with patch(
            "bunkerfrequenz.application.street_encounter_service._select",
            return_value=encounter(service, "street.none"),
        ):
            second = service.walk(
                first.character_after,
                walk_instance_id="glove-story-walk-002",
                world_seed="street-story-002-seed",
                journal_context=context("glove-story-walk-002"),
            )

        parent_event_id = "glove-story-walk-001:001"
        child_event_id = f"street-followup:{parent_event_id}:lost_glove_fence_echo"
        records = kernel.read_records()
        child = next(record for record in records if record["event_id"] == child_event_id)

        assert child_event_id in second.committed_event_ids
        assert child["event_type"] == "street.followup_resolved"
        assert child["causation_id"] == parent_event_id
        assert child["correlation_id"] == f"street-chain:{parent_event_id}"
        assert child["payload"]["parent_event_id"] == parent_event_id
        assert child["payload"]["character_id"] == "player-local"
        assert child["payload"]["followup_id"] == "lost_glove_fence_echo"
        assert "effects" not in child["payload"]
        assert "inventory" not in child["payload"]

        replay = service.walk(
            first.character_after,
            walk_instance_id="glove-story-walk-002",
            world_seed="street-story-002-seed",
            journal_context=context("glove-story-walk-002"),
        )
        assert replay.idempotent_replay is True
        assert kernel.read_records() == records
        assert sum(record["event_id"] == child_event_id for record in records) == 1
