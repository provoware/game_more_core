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
            {"control_deck_focus.js", "map_usability.js", "receipt_clarity.js", "ui_prefs.js"},
            "Neuer MutationObserver benötigt einen expliziten Loop-Sicherheitsvertrag.",
        )

    def test_control_deck_focus_observed_writes_are_idempotent_and_self_quenching(self):
        source = self._observer_sources()["control_deck_focus.js"]
        self.assertIn("function setTextIfChanged(element, text)", source)
        self.assertIn("if (element.textContent !== text) element.textContent = text;", source)
        self.assertIn("setTextIfChanged(button, active ?", source)
        self.assertIn("setTextIfChanged(status, `NÄCHSTER SCHRITT:", source)
        self.assertIn("setTextIfChanged(status, \"NÄCHSTER SCHRITT: Runtime-Gate abwarten\")", source)
        self.assertIn("const currentSignal = document.querySelector(`.${SIGNAL_CLASS}`);", source)
        self.assertIn("if (currentSignal !== enabledEventAction)", source)
        self.assertIn("currentSignal?.classList.remove(SIGNAL_CLASS)", source)
        self.assertIn("new MutationObserver(scheduleReconcile)", source)
        self.assertIn("window.requestAnimationFrame(() =>", source)
        self.assertIn("observer?.disconnect();", source)
        self.assertIn("MAX_RECONCILE_FAILURES = 3", source)
        self.assertIn('attributeFilter: ["class", "disabled"]', source)
        self.assertNotIn(
            'for (const button of document.querySelectorAll(`.${SIGNAL_CLASS}`))',
            source,
        )

    def test_map_usability_observer_is_coalesced_and_self_quenching(self):
        source = self._observer_sources()["map_usability.js"]
        self.assertNotIn("attributes: true", source)
        self.assertIn("if (document.getElementById(STYLE_ID)) return;", source)
        self.assertIn("if (!canvas || document.getElementById(LEGEND_ID)) return;", source)
        self.assertIn("controls.querySelector", source)
        self.assertIn("new MutationObserver(scheduleEnhance)", source)
        self.assertIn("window.requestAnimationFrame(() =>", source)
        self.assertIn("observer?.disconnect();", source)
        self.assertIn("observer.observe(host, { childList: true, subtree: true });", source)

    def test_receipt_clarity_observer_only_restores_missing_ephemeral_notice(self):
        source = self._observer_sources()["receipt_clarity.js"]
        self.assertIn('if (lastReceipt && !document.getElementById("district-receipt-clarity"))', source)
        self.assertIn("queueMicrotask(() => renderReceipt());", source)
        self.assertIn(".observe(settlement, { childList: true });", source)
        self.assertNotIn("subtree: true", source)
        self.assertNotIn("attributes: true", source)

    def test_confirmed_avatar_hud_observers_write_outside_their_observed_trees(self):
        source = self._observer_sources()["ui_prefs.js"]
        self.assertIn('panelObserver.observe(profilePanel, { childList: true });', source)
        self.assertIn('editorObserver.observe(editor, { childList: true });', source)
        self.assertNotIn('panelObserver.observe(profilePanel, { childList: true, subtree: true })', source)
        self.assertNotIn('editorObserver.observe(editor, { childList: true, subtree: true })', source)
        self.assertIn('const host = document.querySelector(".hud-crew-identity")', source)
        self.assertIn('editorObserver?.disconnect();', source)


if __name__ == "__main__":
    unittest.main()
