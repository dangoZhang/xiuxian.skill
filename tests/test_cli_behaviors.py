from __future__ import annotations

import tempfile
import unittest
from unittest.mock import patch

from vibecoding_skill.cli import _resolve_compare_source
from vibecoding_skill.terms import refresh_term_catalog


class CliBehaviorTests(unittest.TestCase):
    def test_compare_reuses_detected_before_source_when_auto(self) -> None:
        self.assertEqual(_resolve_compare_source("auto", "openclaw"), "openclaw")
        self.assertEqual(_resolve_compare_source("codex", "openclaw"), "codex")

    def test_refresh_terms_fails_loudly_on_missing_official_sources(self) -> None:
        failures = [{"name": "Cursor Rules", "url": "https://example.com", "error": "timeout"}]
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("vibecoding_skill.terms._fetch_source_texts", return_value=({}, failures)):
                with self.assertRaisesRegex(RuntimeError, "Cursor Rules"):
                    refresh_term_catalog(tmpdir)


if __name__ == "__main__":
    unittest.main()
