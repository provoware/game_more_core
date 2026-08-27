from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json"
AUDIT = ROOT / "docs" / "STREET_TONE_DIVERSITY_AUDIT.md"


def _manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_tone_audit_keeps_two_existing_stories_and_does_not_preimplement_story_003() -> None:
    manifest = _manifest()

    assert manifest["micro_story_001"]["parent_encounter_id"] == "street.cable_tip"
    assert manifest["micro_story_001"]["followup_id"] == "cable_tip_echo"
    assert manifest["micro_story_002"]["parent_encounter_id"] == "street.lost_glove"
    assert manifest["micro_story_002"]["followup_id"] == "lost_glove_fence_echo"
    assert "micro_story_003" not in manifest


def test_tone_audit_candidates_are_real_catalog_entries_and_reserve_is_not_promoted() -> None:
    manifest = _manifest()
    encounters = {item["encounter_id"]: item for item in manifest["encounters"]}
    audit = AUDIT.read_text(encoding="utf-8")

    for candidate in (
        "street.poster_wall",
        "street.open_door",
        "street.construction_detour",
        "street.sudden_rain",
    ):
        assert candidate in encounters
        assert candidate in audit

    assert encounters["street.construction_detour"]["weight"] == 4
    assert "Story 003 wird in diesem Audit bewusst noch nicht freigegeben" in audit
    assert "stärkste Reservekandidat bleibt `street.construction_detour`" in audit


def test_tone_audit_preserves_single_followup_contract_and_balance_boundary() -> None:
    manifest = _manifest()
    contract = manifest["follow_up_contract"]
    audit = AUDIT.read_text(encoding="utf-8")

    assert contract["journal_event_type"] == "street.followup_resolved"
    assert contract["parent_event_type"] == "street.encounter_resolved"
    assert contract["maximum_followups_per_trigger_walk"] == 1
    assert contract["runtime_authority_only"] is True
    assert contract["client_can_write"] is False
    assert "keine Balancewirkung" in audit
    assert "keine NPC-, Location-, Objekt- oder Map-Persistenz" in audit
