#!/usr/bin/env python3
"""Prüft den Action-Vertrag gegen seine kanonischen Manifeste."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prüft Actions, Gewichte und Manifest-Referenzen.",
        epilog=(
            "Ampel: 🟢 bestanden, 🟡 nicht ausgeführt, 🔴 fehlgeschlagen. "
            "Der Befehl liest nur Manifeste und verändert keine Dateien."
        ),
    )
    return parser.parse_args()


def load_manifest(name: str) -> dict:
    path = ROOT / "manifests" / name
    return json.loads(path.read_text(encoding="utf-8"))


def validate_unique_ids(actions: list[dict]) -> None:
    ids = [action["action_id"] for action in actions]
    assert len(ids) == len(set(ids)), "doppelte Action-ID"
    assert len(actions) == 20, f"erwartet: 20 Actions, gefunden: {len(actions)}"


def validate_weights(actions: list[dict]) -> None:
    for action in actions:
        action_id = action["action_id"]
        assert abs(sum(action["skill_weights"].values()) - 1.0) < 1e-9, (
            f"Skill-Gewichte != 1: {action_id}"
        )
        assert abs(sum(action["trait_evidence_weights"].values()) - 1.0) < 1e-9, (
            f"Trait-Gewichte != 1: {action_id}"
        )


def validate_references(actions: list[dict], skills: set[str], traits: set[str], events: set[str]) -> None:
    for action in actions:
        action_id = action["action_id"]
        for key in action["skill_weights"]:
            assert key in skills or key == "selected_skill", f"unbekannter Skill {key}: {action_id}"
        for key in action["trait_evidence_weights"]:
            assert key in traits or key == "selected_trait_family", (
                f"unbekannte Trait-Familie {key}: {action_id}"
            )
        for event in action["journal_events"]:
            assert event in events, f"unbekannter Journaltyp {event}: {action_id}"


def validate_biography_range(actions: list[dict]) -> None:
    for action in actions:
        value = action["biography_importance_base"]
        assert 0 <= value <= 100, f"Biografie-Wichtigkeit außerhalb 0–100: {action['action_id']}"


def run_checkpoint(label: str, validation, *args) -> None:
    validation(*args)
    print(f"🟢 {label}")


def main() -> int:
    parse_args()
    manifest = load_manifest("ACTION_MANIFEST.json")
    skill_manifest = load_manifest("SKILL_MANIFEST.json")
    trait_manifest = load_manifest("TRAIT_ENGINE_MANIFEST.json")
    journal = load_manifest("JOURNAL_MANIFEST.json")
    actions = manifest["actions"]
    skills = {item["skill_id"].split(".", 1)[1] for item in skill_manifest["skills"]}
    traits = {item["effect_template_id"].split(".", 1)[1] for item in trait_manifest["effect_templates"]}
    events = set(journal["event_types"])

    try:
        run_checkpoint("Checkpoint 1/4: Action-Anzahl und IDs", validate_unique_ids, actions)
        run_checkpoint("Checkpoint 2/4: Gewichte", validate_weights, actions)
        run_checkpoint("Checkpoint 3/4: Manifest-Referenzen", validate_references, actions, skills, traits, events)
        run_checkpoint("Checkpoint 4/4: Biografie-Grenzen", validate_biography_range, actions)
    except (AssertionError, KeyError, TypeError) as error:
        print(f"🔴 ACTION_CONTRACT FAIL: {error}")
        return 1

    print("🟢 ACTION_CONTRACT PASS: 20 Actions, Gewichte/Referenzen/Journaltypen gültig")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
