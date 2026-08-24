from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
A4 = ROOT / "web" / "a4"


class A4MutationObserverGuardTests(unittest.TestCase):
    def _observer_sources(self) -> dict[str, str]:
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(A4.glob("*.js"))
            if "MutationObserver" in path.read_text(encoding="utf-8")
        }

    def test_every_mutation_observer_is_explicitly_inventory_tracked(self):
        sources = self._observer_sources()
        self.assertEqual(
            set(sources),
            {"control_deck_focus.js", "map_usability.js"},
            "Neuer MutationObserver benötigt einen expliziten Loop-Sicherheitsvertrag.",
        )

    def test_control_deck_focus_only_mutates_signal_when_target_changes(self):
        source = self._observer_sources()["control_deck_focus.js"]
        self.assertIn("const currentSignal = document.querySelector(`.${SIGNAL_CLASS}`);", source)
        self.assertIn("if (currentSignal !== enabledEventAction)", source)
        self.assertIn("currentSignal?.classList.remove(SIGNAL_CLASS)", source)
        self.assertNotIn(
            'for (const button of document.querySelectorAll(`.${SIGNAL_CLASS}`))',
            source,
        )
        self.assertIn('attributeFilter: ["class", "disabled"]', source)

    def test_map_usability_observer_watches_structure_only_and_helpers_are_idempotent(self):
        source = self._observer_sources()["map_usability.js"]
        self.assertIn("observer.observe(host, { childList: true, subtree: true });", source)
        self.assertNotIn("attributes: true", source)
        self.assertIn("if (document.getElementById(STYLE_ID)) return;", source)
        self.assertIn("if (!canvas || document.getElementById(LEGEND_ID)) return;", source)
        self.assertIn("controls.querySelector", source)


if __name__ == "__main__":
    unittest.main()
