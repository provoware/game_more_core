from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")


class A4ToolHelpClarityTests(unittest.TestCase):
    def test_help_legend_explains_three_player_relevant_states(self):
        self.assertIn('id="help-legend"', INDEX)
        self.assertIn("Bestätigt", INDEX)
        self.assertIn("Nur Anzeige", INDEX)
        self.assertIn("Sofort gespeichert", INDEX)

    def test_core_panels_use_action_oriented_plain_language(self):
        for text in (
            "Wähle, wie du durch die Stadt ziehst.",
            "Hier siehst du, was in deinen Bezirken gerade los ist.",
            "Hier siehst du deine bestätigten Erlebnisse in zeitlicher Reihenfolge.",
            "Die Karte zeigt deine Bezirke, Orte und Ausbauten auf einen Blick.",
            "Hier kaufst du Orte und baust sie bis Stufe 3 aus.",
            "Hier siehst du deine bestätigte Platzierung.",
            "Hier steuerst du dein vorbereitetes Event Schritt für Schritt.",
            "Hier kaufst und verwaltest du deine Ausrüstung.",
            "Vor deiner Entscheidung siehst du die bekannten Folgen jeder Antwort.",
            "Deine bestätigten Aktionen werden sofort gespeichert.",
        ):
            with self.subTest(text=text):
                self.assertIn(text, INDEX)

    def test_visible_help_avoids_internal_architecture_terms(self):
        for technical_text in (
            "Application-Services",
            "katalogisierten Slots",
            "District-, Property- und Ausbau-Projections",
            "Browser sendet nur Location- und Ausbau-ID",
            "Jeder bestätigte Command wird sofort journalisiert",
        ):
            with self.subTest(technical_text=technical_text):
                self.assertNotIn(technical_text, INDEX)

    def test_diagnostic_character_id_is_explained_not_removed(self):
        self.assertIn("Technische ID", INDEX)
        self.assertIn("Hilft bei Fehlerberichten; für das Spielen musst du sie nicht kennen.", INDEX)


if __name__ == "__main__":
    unittest.main()
