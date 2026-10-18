import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from tools import start_a4_acceptance as acceptance


class BrowserAcceptanceBackendTests(unittest.TestCase):
    def test_driver_failure_is_not_hidden_and_temporary_harness_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'web/a4').mkdir(parents=True)
            with (
                patch.object(acceptance, 'ROOT', root),
                patch.object(acceptance, 'find_browser', return_value='/usr/bin/chromium'),
                patch.object(importlib.util, 'find_spec', return_value=object()),
                patch.object(acceptance, '_playwright_dom', side_effect=RuntimeError('UI-Freeze')),
                patch.object(acceptance.subprocess, 'run') as fallback,
            ):
                with self.assertRaisesRegex(RuntimeError, 'UI-Freeze'):
                    acceptance.browser_dom('http://127.0.0.1:8000/', require_browser=True, avatar_context=True)
                fallback.assert_not_called()
            self.assertFalse((root / 'web/a4' / acceptance.AVATAR_CONTEXT_HARNESS).exists())

    def test_optional_driver_absence_keeps_existing_browser_path_functional(self):
        completed = Mock(returncode=0, stdout='● BEREIT\nBUNKERFREQUENZ – Control Deck', stderr='')
        with (
            patch.object(acceptance, 'find_browser', return_value='/usr/bin/chromium'),
            patch.object(importlib.util, 'find_spec', return_value=None),
            patch.object(acceptance.subprocess, 'run', return_value=completed),
            patch.object(acceptance, '_playwright_dom') as driver,
        ):
            self.assertIn('BEREIT', acceptance.browser_dom('http://127.0.0.1:8000/', require_browser=True))
            driver.assert_not_called()

    def test_source_code_containing_pass_marker_cannot_fake_executed_harness(self):
        fake = '<body><script>"AVATAR_CONTEXT_E2E: PASS";</script>● BEREIT\nBUNKERFREQUENZ – Control Deck</body>'
        with (
            patch.object(acceptance, 'find_browser', return_value='/usr/bin/chromium'),
            patch.object(acceptance, '_playwright_dom', return_value=fake),
        ):
            with self.assertRaisesRegex(RuntimeError, 'keinen ausgeführten PASS-Nachweis'):
                acceptance.browser_dom('http://127.0.0.1:8000/', require_browser=True,
                                       avatar_context=True, backend='playwright')


if __name__ == '__main__':
    unittest.main()
