from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "demo_codex_session.jsonl"


class CliE2ETests(unittest.TestCase):
    def _run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            [sys.executable, "-m", "vibecoding_skill.cli", *args],
            cwd=ROOT,
            env=merged_env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_analyze_auto_switches_to_xianxia_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._run_cli("analyze", "--path", str(DEMO), "--source", "codex", "--card-dir", tmpdir)
            self.assertTrue((Path(tmpdir) / "vibecoding-card-xianxia.svg").exists())
            self.assertTrue((Path(tmpdir) / "vibecoding-card-xianxia.png").exists())

    def test_export_emits_end_to_end_bundle_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._run_cli("export", "--path", str(DEMO), "--source", "codex", "--export-dir", tmpdir)
            root = Path(tmpdir)
            self.assertTrue((root / "README.md").exists())
            self.assertTrue((root / ".cursor" / "rules").exists())
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("assets/vibecoding-card-xianxia.png", readme)
            self.assertIn(".cursor/rules/", readme)

    def test_export_captures_model_and_renders_platform_model_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._run_cli("export", "--path", str(DEMO), "--source", "codex", "--export-dir", tmpdir)
            root = Path(tmpdir)
            snapshot = json.loads((root / "snapshot.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["transcript"]["models"], ["openai/gpt-5.4"])
            self.assertEqual(snapshot["transcript"]["providers"], ["openai"])
            svg = (root / "assets" / "vibecoding-card-xianxia.svg").read_text(encoding="utf-8")
            self.assertIn("Codex · gpt-5.4", svg)

    def test_analyze_does_not_persist_memory_without_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            result = self._run_cli(
                "analyze",
                "--path",
                str(DEMO),
                "--source",
                "codex",
                env={"VIBECODING_SKILL_HOME": home},
            )
            self.assertNotIn("## 上次评测记忆", result.stdout)
            self.assertFalse((Path(home) / "history.json").exists())

    def test_memory_opt_in_uses_distinct_bucket_per_path(self) -> None:
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as sessions:
            first = Path(sessions) / "first.jsonl"
            second = Path(sessions) / "second.jsonl"
            first.write_text(DEMO.read_text(encoding="utf-8"), encoding="utf-8")
            second.write_text(DEMO.read_text(encoding="utf-8"), encoding="utf-8")

            self._run_cli(
                "analyze",
                "--path",
                str(first),
                "--source",
                "codex",
                "--memory",
                env={"VIBECODING_SKILL_HOME": home},
            )
            result = self._run_cli(
                "analyze",
                "--path",
                str(second),
                "--source",
                "codex",
                "--memory",
                env={"VIBECODING_SKILL_HOME": home},
            )

            self.assertIn("已记住本次评测", result.stdout)
            self.assertNotIn("与上次持平", result.stdout)


if __name__ == "__main__":
    unittest.main()
