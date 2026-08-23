import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.presentation.scene_jobs_projection import build_scene_jobs_projection


ROOT = Path(__file__).parents[2]
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")
ASSISTANT_UI = (ROOT / "web" / "a4" / "assistant_jobs_ui.js").read_text(encoding="utf-8")
UI_PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
PAYOUT_PREVIEW = (ROOT / "web" / "a4" / "scene_job_payout_preview.js").read_text(encoding="utf-8")
LAUNCHER = (ROOT / "tools" / "start_a4_game_client.py").read_text(encoding="utf-8")


class A4AssistantJobsUiTests(unittest.TestCase):
    def test_projection_exposes_confirmed_control_state_and_catalog_label(self):
        state = {
            "character": CharacterState("char.local", "Local").to_dict(),
            "assistant": {"active_job_id": "scene.cable_repair", "revision": 4},
        }

        projection = build_scene_jobs_projection(state, JOBS["jobs"])

        self.assertTrue(projection["assistant"]["enabled"])
        self.assertEqual(projection["assistant"]["active_job_id"], "scene.cable_repair")
        self.assertEqual(projection["assistant"]["active_job_label"], "Kabel & Kleinkram reparieren")
        self.assertEqual(projection["assistant"]["revision"], 4)

    def test_projection_exposes_confirmed_wallet_and_bank_balances(self):
        finance = PlayerFinanceState(cash_cents=8_500, bank_cents=4_250, revision=3)
        state = {
            "character": CharacterState("char.local", "Local").to_dict(),
            "finance": finance.to_dict(),
        }

        projection = build_scene_jobs_projection(state, JOBS["jobs"])

        self.assertEqual(projection["cash_cents"], 8_500)
        self.assertEqual(projection["bank_cents"], 4_250)
        self.assertEqual(projection["finance_revision"], 3)

    def test_projection_exposes_canonical_effective_payout_from_confirmed_energy(self):
        character = CharacterState("char.local", "Local")
        character.energy = 4
        projection = build_scene_jobs_projection({"character": character.to_dict()}, JOBS["jobs"])
        cable = next(job for job in projection["jobs"] if job["job_id"] == "scene.cable_repair")

        self.assertEqual(cable["payout_cents"], 5_500)
        self.assertEqual(cable["effective_payout_cents"], 2_750)
        self.assertTrue(cable["payout_reduced_by_energy"])

        character.energy = 8
        full = build_scene_jobs_projection({"character": character.to_dict()}, JOBS["jobs"])
        cable_full = next(job for job in full["jobs"] if job["job_id"] == "scene.cable_repair")
        self.assertEqual(cable_full["effective_payout_cents"], 5_500)
        self.assertFalse(cable_full["payout_reduced_by_energy"])

        character.energy = 0
        empty = build_scene_jobs_projection({"character": character.to_dict()}, JOBS["jobs"])
        cable_empty = next(job for job in empty["jobs"] if job["job_id"] == "scene.cable_repair")
        self.assertEqual(cable_empty["effective_payout_cents"], 0)
        self.assertTrue(cable_empty["payout_reduced_by_energy"])

    def test_projection_fails_closed_if_saved_assistant_job_is_not_in_catalog(self):
        state = {
            "character": CharacterState("char.local", "Local").to_dict(),
            "assistant": {"active_job_id": "scene.removed", "revision": 1},
        }
        with self.assertRaisesRegex(ValueError, "unbekannten Scene Job"):
            build_scene_jobs_projection(state, JOBS["jobs"])

    def test_ui_reuses_jobs_panel_and_sends_only_control_job_id(self):
        self.assertIn('src="assistant_jobs_ui.js"', INDEX)
        self.assertLess(INDEX.index('src="app.js"'), INDEX.index('src="assistant_jobs_ui.js"'))
        self.assertIn('document.getElementById("jobs-list")', ASSISTANT_UI)
        self.assertIn('control.id = "jobs-assistant-control"', ASSISTANT_UI)
        self.assertNotIn('assistant-panel', ASSISTANT_UI)

        start = ASSISTANT_UI.index('type: "assistant.control"')
        fragment = ASSISTANT_UI[start:start + 180]
        self.assertIn("job_id: jobId", fragment)
        self.assertNotIn("payout_cents", fragment)
        self.assertNotIn("energy_delta", fragment)
        self.assertNotIn("stress_delta", fragment)
        self.assertNotIn("round", fragment.lower())

    def test_bank_ui_stays_in_jobs_panel_and_sends_only_direction_and_amount(self):
        self.assertIn('control.id = "jobs-bank-control"', ASSISTANT_UI)
        self.assertIn("WALLET ↔ BANK", ASSISTANT_UI)
        self.assertIn("EINZAHLEN", ASSISTANT_UI)
        self.assertIn("ABHEBEN", ASSISTANT_UI)
        self.assertIn("sceneJobs.bank_cents", ASSISTANT_UI)
        self.assertNotIn("bank-panel", ASSISTANT_UI)

        start = ASSISTANT_UI.index('type: "finance.transfer"')
        fragment = ASSISTANT_UI[start:start + 260]
        self.assertIn("direction,", fragment)
        self.assertIn("amount_cents: amountCents", fragment)
        self.assertNotIn("cash_after_cents", fragment)
        self.assertNotIn("bank_after_cents", fragment)
        self.assertNotIn("interest", fragment.lower())

    def test_payout_preview_only_renders_projection_values_without_gameplay_formula(self):
        self.assertIn('script.src = "scene_job_payout_preview.js"', UI_PREFS)
        self.assertIn("job.effective_payout_cents", PAYOUT_PREVIEW)
        self.assertIn("job.payout_reduced_by_energy", PAYOUT_PREVIEW)
        self.assertIn("Lohn bis zu", PAYOUT_PREVIEW)
        self.assertIn("AKTUELL", PAYOUT_PREVIEW)
        self.assertNotIn("sendCommand", PAYOUT_PREVIEW)
        self.assertNotIn("fetch(", PAYOUT_PREVIEW)
        self.assertNotIn("localStorage", PAYOUT_PREVIEW)
        self.assertNotIn("energy_delta]", PAYOUT_PREVIEW)
        self.assertNotIn("payout_cents *", PAYOUT_PREVIEW)

    def test_ui_explains_round_authority_and_launcher_routes_control_as_character_command(self):
        self.assertIn("intern bestätigten Spielrunde", ASSISTANT_UI)
        self.assertIn("Browser und Rechnerzeit starten keine Runde", ASSISTANT_UI)
        self.assertIn("FREUND STARTEN", ASSISTANT_UI)
        self.assertIn("FREUND WECHSELN", ASSISTANT_UI)
        self.assertIn("FREUND STOPPEN", ASSISTANT_UI)
        self.assertIn("AssistantGameClientSession", LAUNCHER)
        self.assertIn('"assistant.control"', LAUNCHER)
        self.assertIn('"web/a4/assistant_jobs_ui.js"', LAUNCHER)

    def test_afterglow_is_read_only_and_stays_inside_existing_jobs_control(self):
        self.assertIn('afterglow.id = "jobs-assistant-afterglow"', ASSISTANT_UI)
        self.assertIn('afterglowList.id = "jobs-assistant-afterglow-list"', ASSISTANT_UI)
        self.assertIn("NACHHALL // BESTÄTIGTE ARBEIT", ASSISTANT_UI)
        self.assertIn("bestätigte Assistentenrunde", ASSISTANT_UI)
        self.assertIn("entry.headline", ASSISTANT_UI)
        self.assertIn("entry.body", ASSISTANT_UI)
        self.assertNotIn("fetch(", ASSISTANT_UI)
        self.assertNotIn("localStorage", ASSISTANT_UI)
        self.assertNotIn("friendship_xp", ASSISTANT_UI)

    def test_launcher_builds_afterglow_only_from_journal_records_and_catalog(self):
        self.assertIn("build_assistant_afterglow_projection", LAUNCHER)
        self.assertIn('"content/de/ui/assistant_afterglow.json"', LAUNCHER)
        self.assertIn("records = self.kernel.read_records()", LAUNCHER)
        self.assertIn('projection["scene_jobs"]["assistant_afterglow"]', LAUNCHER)
        self.assertIn("self.assistant_afterglow_texts", LAUNCHER)


if __name__ == "__main__":
    unittest.main()
