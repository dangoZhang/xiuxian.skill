from __future__ import annotations

import unittest
from pathlib import Path

from vibecoding_skill.distill import _compress_assistant_text, _distill_transcript, analyze_many_with_chunking
from vibecoding_skill.models import Message, TokenUsage, Transcript


class DistillPipelineTests(unittest.TestCase):
    def test_assistant_compression_uses_head_summary_without_synthetic_command_line(self) -> None:
        text = (
            "我先读文件确认范围。"
            "接下来会先跑测试，再整理结果。"
            "命令是 python3 -m pytest -q。"
            "验证完成后我会回报剩余风险。"
        )
        compressed = _compress_assistant_text(text)
        self.assertIn("我先读文件确认范围", compressed)
        self.assertIn("接下来会先跑测试", compressed)
        self.assertNotIn("命令重点", compressed)
        self.assertNotIn("验证完成后我会回报剩余风险", compressed)

    def test_distilled_messages_keep_original_signal_text(self) -> None:
        transcript = Transcript(
            source="codex",
            path=Path("demo.jsonl"),
            messages=[Message(role="assistant", text="先跑 pytest，再看日志。")],
            tool_calls=3,
            token_usage=TokenUsage(total_tokens=12),
        )
        distilled = _distill_transcript(transcript)
        self.assertEqual(distilled.messages[0].meta["signal_text"], "先跑 pytest，再看日志。")

    def test_chunked_analysis_preserves_total_tool_counts_without_inventing_chunk_counts(self) -> None:
        messages = []
        for index in range(220):
            messages.append(Message(role="user", text=f"第{index}轮：目标、边界、验收都在这里。"))
            messages.append(
                Message(
                    role="assistant",
                    text="我先读文件。接下来跑 pytest。最后给验证结果和风险。",
                )
            )
        transcript = Transcript(
            source="codex",
            path=Path("demo.jsonl"),
            messages=messages,
            tool_calls=11,
            token_usage=TokenUsage(input_tokens=100, output_tokens=30, total_tokens=130),
        )

        distilled = analyze_many_with_chunking([transcript], min_messages=1)
        self.assertEqual(distilled.kind, "aggregate")
        self.assertEqual(distilled.aggregate["total_tool_calls"], 11)
        self.assertEqual(distilled.aggregate["token_usage"]["total_tokens"], 130)
        self.assertEqual(distilled.aggregate["distillation"]["original_tool_calls"], 11)


if __name__ == "__main__":
    unittest.main()
