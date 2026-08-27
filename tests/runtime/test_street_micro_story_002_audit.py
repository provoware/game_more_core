from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json"
AUDIT = ROOT / "docs" / "STREET_MICRO_STORY_002_AUDIT.md"


def _manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_second_story_audit_uses_existing_rare_parent_without_implementing_story() -> None:
    manifest = _manifest()
    encounters = {item["encounter_id"]: item for item in manifest["encounters"]}

    assert manifest["micro_story_001"]["parent_encounter_id"] == "street.cable_tip"
    assert "micro_story_002" not in manifest
    assert encounters["street.lost_glove"]["polarity"] == "negative"
    assert encounters["street.lost_glove"]["weight"] == 2


def test_second_story_audit_keeps_existing_followup_contract_as_only_future_path() -> None:
    manifest = _manifest()
    contract = manifest["follow_up_contract"]
    audit = AUDIT.read_text(encoding="utf-8")

    assert contract["journal_event_type"] == "street.followup_resolved"
    assert contract["parent_event_type"] == "street.encounter_resolved"
    assert contract["maximum_followups_per_trigger_walk"] == 1
    assert "street.lost_glove -> lost_glove_fence_echo" in audit
    assert "keine Map-, Location- oder NPC-Persistenz" in audit
    assert "keine Balancewirkung" in audit
