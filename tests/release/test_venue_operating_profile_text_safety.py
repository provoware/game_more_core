from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).parents[2]


class VenueOperatingProfileTextSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = (ROOT / "web/a4/app.js").read_text(encoding="utf-8")

    def test_profile_values_stay_text_only_and_projection_owned(self) -> None:
        render = re.search(
            r"function renderProperties\(properties, propertyUpgrades\) \{(?P<body>.*?)\n\}",
            self.app,
            re.DOTALL,
        )
        self.assertIsNotNone(render, "renderProperties fehlt")
        body = render.group("body")

        self.assertIn("upgradeEntry?.effective_values", body)
        self.assertIn("detail.textContent =", body)
        self.assertNotIn("detail.innerHTML =", body)
        self.assertNotIn("insertAdjacentHTML", body)

    def test_profile_exposes_exactly_the_five_confirmed_labels(self) -> None:
        render = re.search(
            r"function renderProperties\(properties, propertyUpgrades\) \{(?P<body>.*?)\n\}",
            self.app,
            re.DOTALL,
        )
        self.assertIsNotNone(render, "renderProperties fehlt")
        body = render.group("body")

        for label in (
            "Prestige",
            "Publikumskraft",
            "Risiko",
            "Underground-Faktor",
            "Nutzen",
        ):
            self.assertIn(label, body)

        self.assertNotIn("Gewinn", body)
        self.assertNotIn("Ertrag", body)
        self.assertNotIn("Kapazität", body)
        self.assertNotIn("Event-Bonus", body)


if __name__ == "__main__":
    unittest.main()
