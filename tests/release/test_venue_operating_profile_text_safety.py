from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).parents[2]
EXPECTED_PROFILE_TEMPLATE = (
    " · Prestige ${values.prestige} · Publikumskraft ${values.audience_pull} · "
    "Risiko ${values.risk} · Underground-Faktor ${values.underground_factor} · "
    "Nutzen ${values.utility}"
)


class VenueOperatingProfileTextSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = (ROOT / "web/a4/app.js").read_text(encoding="utf-8")

    def _render_properties_body(self) -> str:
        render = re.search(
            r"function renderProperties\(properties, propertyUpgrades\) \{(?P<body>.*?)\n\}",
            self.app,
            re.DOTALL,
        )
        self.assertIsNotNone(render, "renderProperties fehlt")
        return render.group("body")

    def test_profile_values_stay_text_only_and_projection_owned(self) -> None:
        body = self._render_properties_body()

        self.assertIn("upgradeEntry?.effective_values", body)
        self.assertRegex(body, r"detail\.textContent\s*=")
        self.assertNotRegex(body, r"detail\.innerHTML\s*=")
        self.assertNotIn("insertAdjacentHTML", body)

    def test_profile_template_is_exactly_the_five_confirmed_fields(self) -> None:
        body = self._render_properties_body()
        template = re.search(
            r"const valueText = values\s*\n\s*\? `(?P<template>[^`]+)`\s*\n\s*: \"\";",
            body,
        )
        self.assertIsNotNone(template, "Venue-Betriebsprofil-Template fehlt")
        self.assertEqual(template.group("template"), EXPECTED_PROFILE_TEMPLATE)

        fields = re.findall(r"\$\{values\.([a-z_]+)\}", template.group("template"))
        self.assertEqual(
            fields,
            ["prestige", "audience_pull", "risk", "underground_factor", "utility"],
        )


if __name__ == "__main__":
    unittest.main()
