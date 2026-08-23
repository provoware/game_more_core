from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")
TIMELINE_JS = (ROOT / "web" / "a4" / "event_timeline.js").read_text(encoding="utf-8")
LAUNCHER = (ROOT / "tools" / "start_a4_game_client.py").read_text(encoding="utf-8")


class A4EventTimelineControlDeckTests(unittest.TestCase):
    def test_runtime_exposes_existing_c4a_projection(self):
        self.assertIn("build_event_timeline_projection", LAUNCHER)
        self.assertIn('projection["event_timeline"]', LAUNCHER)
        self.assertIn("self.kernel.read_records()", LAUNCHER)
        self.assertIn('"content/de/ui/district_events.json"', LAUNCHER)
        self.assertIn('"content/de/ui/incidents.json"', LAUNCHER)

    def test_control_deck_has_accessible_read_only_timeline(self):
        self.assertIn('id="event-timeline-panel"', INDEX)
        self.assertIn('id="event-timeline-list"', INDEX)
        self.assertIn('id="event-timeline-status"', INDEX)
        self.assertIn('aria-live="polite"', INDEX)
        self.assertIn('src="event_timeline.js"', INDEX)
        self.assertIn('href="#event-timeline-panel"', INDEX)

    def test_local_filters_cover_all_street_crisis_and_district_without_persistence(self):
        for filter_id, label in (
            ('all', 'ALLE'),
            ('street', 'STRASSE'),
            ('crisis', 'KRISE'),
            ('district', 'BEZIRK'),
        ):
            self.assertIn(f'{filter_id}: Object.freeze({{ label: "{label}"', TIMELINE_JS)
        self.assertIn('controls.setAttribute("role", "group")', TIMELINE_JS)
        self.assertIn('controls.setAttribute("aria-label", "Timeline filtern")', TIMELINE_JS)
        self.assertIn('button.setAttribute("aria-pressed"', TIMELINE_JS)
        self.assertIn('button.addEventListener("click", () => setFilter(filterId))', TIMELINE_JS)
        self.assertNotIn("localStorage", TIMELINE_JS)
        self.assertNotIn("sessionStorage", TIMELINE_JS)

    def test_browser_does_not_rebuild_write_or_reorder_timeline(self):
        self.assertIn('fetch("/api/state"', TIMELINE_JS)
        self.assertNotIn('method: "POST"', TIMELINE_JS)
        self.assertNotIn("sendCommand", TIMELINE_JS)
        self.assertNotIn(".sort(", TIMELINE_JS)
        self.assertNotIn(".reverse(", TIMELINE_JS)
        self.assertNotIn("Date.now", TIMELINE_JS)
        self.assertNotIn("Math.random", TIMELINE_JS)

    def test_filter_only_selects_existing_entries_and_renderer_preserves_source_order(self):
        self.assertIn('confirmedEntries.filter((entry) => entry?.kind === selected.kind)', TIMELINE_JS)
        self.assertIn("for (const entry of visible)", TIMELINE_JS)
        self.assertIn("title.textContent", TIMELINE_JS)
        self.assertIn("body.textContent", TIMELINE_JS)
        self.assertNotIn("innerHTML", TIMELINE_JS)
        self.assertIn("Reihenfolge aus dem Journal.", TIMELINE_JS)


if __name__ == "__main__":
    unittest.main()
