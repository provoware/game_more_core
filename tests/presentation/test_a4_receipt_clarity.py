from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")
RECEIPT_JS = (ROOT / "web" / "a4" / "receipt_clarity.js").read_text(encoding="utf-8")
SESSION = (ROOT / "src" / "bunkerfrequenz" / "application" / "game_client_session.py").read_text(encoding="utf-8")


class A4ReceiptClarityTests(unittest.TestCase):
    def test_control_deck_loads_receipt_clarity_after_existing_app(self):
        self.assertIn('src="receipt_clarity.js?v=', INDEX)
        self.assertLess(INDEX.index('src="app.js?v='), INDEX.index('src="receipt_clarity.js?v='))

    def test_three_plain_language_states_are_derived_from_existing_runtime_signals(self):
        for label in ("NEU BESTÄTIGT", "BEREITS BESTÄTIGT", "NICHT AUSGELÖST"):
            self.assertIn(label, RECEIPT_JS)
        self.assertIn('payload?.metadata?.district_world_event', RECEIPT_JS)
        self.assertIn('payload?.idempotent_replay === true', RECEIPT_JS)
        self.assertIn('!event.event_id && !event.event_instance_id', RECEIPT_JS)
        self.assertIn('"district_world_event"', SESSION)
        self.assertIn('"event_instance_id": event_result.event_instance_id', SESSION)

    def test_receipt_clarity_is_ephemeral_read_only_presentation(self):
        self.assertIn('id = "district-receipt-clarity"', RECEIPT_JS)
        self.assertIn('setAttribute("role", "status")', RECEIPT_JS)
        self.assertIn('setAttribute("aria-live", "polite")', RECEIPT_JS)
        self.assertNotIn("localStorage", RECEIPT_JS)
        self.assertNotIn("sessionStorage", RECEIPT_JS)
        self.assertNotIn('method: "POST"', RECEIPT_JS)
        self.assertNotIn("sendCommand", RECEIPT_JS)
        self.assertNotIn("/api/checkpoint", RECEIPT_JS)

    def test_no_event_copy_does_not_claim_or_invent_a_journal_event(self):
        self.assertIn("kein Bezirksereignis ausgelöst", RECEIPT_JS)
        self.assertIn("nichts erfunden oder nachgetragen", RECEIPT_JS)
        self.assertNotIn("Date.now", RECEIPT_JS)
        self.assertNotIn("Math.random", RECEIPT_JS)


if __name__ == "__main__":
    unittest.main()
