from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / "tools" / "start_a4_acceptance.py"


class AvatarContextTextClipE2ETests(unittest.TestCase):
    def test_avatar_harness_measures_real_compact_mark_clipping_fail_closed(self):
        source = ACCEPTANCE.read_text(encoding="utf-8")

        self.assertIn("node.scrollWidth > node.clientWidth + 1", source)
        self.assertIn("node.scrollHeight > node.clientHeight + 1", source)
        self.assertIn('style.overflowX', source)
        self.assertIn('style.overflowY', source)
        self.assertIn('throw new Error(\"Crew-Kurzmarke wird abgeschnitten:', source)
        self.assertIn('compactMarks = [', source)
        self.assertIn('[\"HUD\", hudMark]', source)
        self.assertIn('[\"Ranking\", hallMark]', source)
        self.assertIn('[\"Map\", mapMark]', source)
        self.assertIn('kein Text-Clipping', source)

    def test_clip_check_does_not_create_second_browser_or_avatar_path(self):
        source = ACCEPTANCE.read_text(encoding="utf-8")

        self.assertEqual(source.count('AVATAR_CONTEXT_HARNESS ='), 1)
        self.assertNotIn('text-overflow: ellipsis', source)
        self.assertNotIn('overflow = \"hidden\"', source)


if __name__ == "__main__":
    unittest.main()
