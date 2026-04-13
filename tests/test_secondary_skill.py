from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from vibecoding_skill.insights import build_analysis_insights
from vibecoding_skill.models import Analysis, Certificate, Message, MetricScore, Persona, Transcript
from vibecoding_skill.cards import build_card_data, render_vibecoding_card
from vibecoding_skill.exporter import export_bundle
from vibecoding_skill.readme_sync import replace_marked_section
from vibecoding_skill.secondary_skill import (
    build_readme_profile_panel,
    build_secondary_skill_distillation,
    result_skill_slug,
    result_skill_title_from_display,
)


class SecondarySkillDistillationTests(unittest.TestCase):
    def test_distillation_expands_to_sixteen_dimensions(self) -> None:
        messages = [
            Message(
                role="user",
                text=(
                    "目标是做一个新的 skill。边界：纯本地。验收：生成 README、JSON、导出包和结果 skill。"
                    "先读 /tmp/demo.py 和 logs/demo.log，再开始做。不要空讲，结论优先。"
                ),
            ),
            Message(
                role="assistant",
                text=(
                    "我先读文件并运行 python3 -m py_compile，然后把任务拆成三步。"
                    "会先产出 README、脚本和 JSON，并补验证结果和未验证项。"
                ),
            ),
            Message(
                role="user",
                text=(
                    "如果偏了先缩范围再继续。继续沿用上次 snapshot，最后要给同事导出包和结果 skill 接管。"
                    "把这套做法沉成可复用 workflow。"
                ),
            ),
            Message(
                role="assistant",
                text=(
                    "我会并行检查 README 和导出脚本；如果测试失败就 fallback 到最小可运行版本。"
                    "完成后给你验证日志、未验证项和下一步建议。"
                ),
            ),
        ]

        distillation = build_secondary_skill_distillation(
            messages=messages,
            display_name="码奸",
            source="codex",
            rank="L4",
            generated_at="2026-04-14 12:00",
        )

        axes = distillation["axes"]
        self.assertEqual(len(axes), 16)
        axis_map = {axis["id"]: axis for axis in axes}

        self.assertGreaterEqual(axis_map["goal_framing"]["score"], 2)
        self.assertGreaterEqual(axis_map["tool_orchestration"]["score"], 2)
        self.assertGreaterEqual(axis_map["verification_loop"]["score"], 2)
        self.assertGreaterEqual(axis_map["handoff_memory"]["score"], 1)
        self.assertGreaterEqual(axis_map["abstraction_reuse"]["score"], 1)
        self.assertGreaterEqual(axis_map["workflow_orchestration"]["score"], 1)

        panel = build_readme_profile_panel(distillation)
        self.assertTrue(panel["paragraphs"])
        self.assertTrue(panel["bullets"])
        self.assertLessEqual(len(panel["tags"]), 4)
        self.assertEqual(panel["title"], "你怎么和 AI 协作")
        self.assertIn("码奸，你的水平已经达到了L4级", panel["paragraphs"][0])
        self.assertIn("常见任务可以多步推进", panel["paragraphs"][0])
        self.assertIn("第一段必须先给等级结论", panel["llm_prompt"])
        self.assertIn("结构化画像", panel["llm_prompt"])
        self.assertIn("prompt", "".join(panel["paragraphs"]))

    def test_large_corpus_uses_coverage_ratio_instead_of_raw_count(self) -> None:
        messages = []
        for _ in range(14):
            messages.append(
                Message(
                    role="user",
                    text="目标、边界、验收都写清楚。先读 /tmp/demo.py，再直接开始做并补验证结果。",
                )
            )
            messages.append(
                Message(
                    role="assistant",
                    text="我先读文件并执行，完成后给测试日志、证据和未验证项。",
                )
            )

        messages.extend(
            [
                Message(role="user", text="沿用上次 snapshot，最后补一个导出包。"),
                Message(role="assistant", text="我会基于 snapshot 收尾，并补导出包接管说明。"),
                Message(role="user", text="这轮先专注主线，不需要额外交接设计。"),
                Message(role="assistant", text="继续推进主线，优先验证和交付。"),
            ]
        )

        distillation = build_secondary_skill_distillation(
            messages=messages,
            display_name="码奸",
            source="codex",
            rank="L7",
            generated_at="2026-04-14 13:00",
        )

        axis_map = {axis["id"]: axis for axis in distillation["axes"]}
        self.assertEqual(len(messages), 32)
        self.assertEqual(axis_map["goal_framing"]["score"], 4)
        self.assertLess(axis_map["handoff_memory"]["score"], 4)
        self.assertLess(axis_map["handoff_memory"]["score"], axis_map["goal_framing"]["score"])
        self.assertLess(axis_map["handoff_memory"]["coverage_ratio"], 0.15)

    def test_result_skill_name_is_portable_ascii_slug(self) -> None:
        self.assertEqual(result_skill_title_from_display("码奸"), "码奸.skill")
        slug = result_skill_slug("码奸")
        self.assertTrue(slug.startswith("vibecoding-profile-"))
        self.assertRegex(slug, r"^[a-z0-9-]+$")
        self.assertEqual(result_skill_slug("vibecoding-skill"), "vibecoding-skill")

    def test_communication_axis_prefers_observed_brevity_over_declared_preference(self) -> None:
        verbose_messages = [
            Message(role="user", text="请你简洁一点，但下面我会用很长很长的一段话解释背景。" + "背景" * 120),
            Message(role="assistant", text="收到。"),
        ]
        concise_messages = [
            Message(role="user", text="修这个 bug。边界别动接口。验收跑测试。"),
            Message(role="assistant", text="收到。"),
        ]

        verbose = build_secondary_skill_distillation(
            messages=verbose_messages,
            display_name="码奸",
            source="codex",
            rank="L4",
            generated_at="2026-04-14 12:00",
        )
        concise = build_secondary_skill_distillation(
            messages=concise_messages,
            display_name="码奸",
            source="codex",
            rank="L4",
            generated_at="2026-04-14 12:00",
        )

        verbose_axis = {axis["id"]: axis for axis in verbose["axes"]}["communication_compression"]
        concise_axis = {axis["id"]: axis for axis in concise["axes"]}["communication_compression"]
        self.assertLess(verbose_axis["score"], concise_axis["score"])

    def test_panel_ignores_stale_insights_and_uses_secondary_summary(self) -> None:
        payload = {
            "display_name": "码奸",
            "insights": {
                "rank": "L9",
                "ability_text": "这是一段故意过时的兼容字段，不应再进入 README 画像。",
                "habit_profile_lines": [
                    "起手习惯：这段旧文案不应再被读取。",
                    "推进习惯：这段旧文案也不应再被读取。",
                    "容易掉点的地方：这段旧文案也不应再被读取。",
                ],
                "breakthrough_lines": ["这条旧建议不应进入画像。"],
            },
            "secondary_skill": {
                "display_name": "码奸",
                "rank": "L4",
                "axes": [
                    {"id": "goal_framing", "label": "目标 framing", "score": 4, "summary": "起手偏好先说清目标、边界和验收，再让 agent 接手执行。"},
                    {"id": "context_supply", "label": "上下文供给", "score": 4, "summary": "偏好把路径、文件、背景和历史直接交给 agent，减少来回确认。"},
                    {"id": "execution_preference", "label": "执行默认", "score": 4, "summary": "更偏好直接动手、直接出结果，解释不要挡在执行前面。"},
                    {"id": "tool_orchestration", "label": "工具编排", "score": 4, "summary": "倾向让 agent 读文件、跑命令、查日志、落脚本，而不是停在口头判断。"},
                    {"id": "verification_loop", "label": "验证闭环", "score": 4, "summary": "默认要可验证结果，最好顺带交代验证方式和未验证项。"},
                    {"id": "abstraction_reuse", "label": "抽象复用", "score": 0, "summary": "当前记录里，抽象复用信号还不够明确。"},
                    {"id": "constraint_governance", "label": "约束治理", "score": 0, "summary": "当前记录里，约束治理信号还不够明确。"},
                ],
            },
        }

        panel = build_readme_profile_panel(payload)
        self.assertIn("码奸，你的水平已经达到了L4级", panel["paragraphs"][0])
        self.assertIn("目标 framing", panel["paragraphs"][0])
        self.assertIn("执行默认", panel["paragraphs"][1])
        self.assertIn("抽象复用", panel["paragraphs"][2])
        self.assertNotIn("过时的兼容字段", "\n".join(panel["paragraphs"]))
        self.assertNotIn("旧建议", "\n".join(panel["paragraphs"]))

    def test_panel_uses_secondary_summary_tags_and_bullets(self) -> None:
        payload = {
            "display_name": "码奸",
            "insights": {
                "rank": "L4",
                "ability_text": "你已经能把常见任务沿着上下文稳定推到多步完成。",
                "habit_profile_lines": [
                    "起手习惯：当前最稳的是“目标 framing”，起手偏好先说清目标、边界和验收，再让 agent 接手执行。",
                    "推进习惯：当前最稳的是“工具编排”，倾向让 agent 读文件、跑命令、查日志、落脚本，而不是停在口头判断。",
                    "容易掉点的地方：当前最该补的是“交接与记忆”，当前记录里，交接与记忆信号还不够稳定。",
                ],
                "breakthrough_lines": ["下一轮先补交接与记忆。"],
            },
            "secondary_skill": {
                "display_name": "码奸",
                "rank": "L4",
                "axes": [
                    {"id": "goal_framing", "score": 4},
                    {"id": "context_supply", "score": 4},
                    {"id": "verification_loop", "score": 4},
                    {"id": "tool_orchestration", "score": 4},
                ],
            },
        }

        panel = build_readme_profile_panel(payload)
        self.assertIn("目标先收束", panel["tags"])
        self.assertIn("上下文给够", panel["tags"])
        self.assertTrue(any("最稳" in item for item in panel["bullets"]))

    def test_insights_can_be_derived_from_secondary_skill_summary(self) -> None:
        transcript = Transcript(
            source="codex",
            path=Path("demo.jsonl"),
            display_name="码奸",
            messages=[Message(role="user", text="目标、边界、验收写清楚。"), Message(role="assistant", text="我先读文件再验证。")],
        )
        analysis = Analysis(
            transcript=transcript,
            user_metrics=[MetricScore("目标清晰度", 4, "目标很清楚。"), MetricScore("上下文供给", 3, "上下文较完整。"), MetricScore("迭代修正力", 2, "修正一般。"), MetricScore("验收意识", 3, "会要验证。"), MetricScore("协作节奏", 3, "节奏稳定。")],
            assistant_metrics=[MetricScore("执行落地", 4, "执行很强。"), MetricScore("工具调度", 3, "会读文件。"), MetricScore("验证闭环", 3, "会验证。"), MetricScore("上下文承接", 2, "承接一般。"), MetricScore("补救适配", 2, "补救一般。")],
            user_certificate=Certificate("user", "用户", "筑基", 42, Persona("t", "s", [], "sum"), [], []),
            assistant_certificate=Certificate("assistant", "AI", "L4", 42, Persona("t", "s", [], "sum"), [], []),
            overview="demo",
        )
        secondary = build_secondary_skill_distillation(
            messages=transcript.messages,
            display_name="码奸",
            source="codex",
            rank="L4",
            generated_at="2026-04-14 12:00",
        )

        insights = build_analysis_insights(analysis, secondary_skill=secondary)
        self.assertTrue(insights["dimension_summary_lines"])
        self.assertTrue(insights["report_basis_lines"])
        self.assertIn("16 维蒸馏", " ".join(insights["report_basis_lines"]))

    def test_xianxia_card_uses_realm_and_sect_labels(self) -> None:
        payload = {
            "generated_at": "2026-04-14 13:00",
            "insights": {"rank": "L4"},
            "transcript": {
                "display_name": "码奸",
                "source": "codex",
                "models": ["gpt-5.4"],
            },
            "secondary_skill": {
                "axes": [{"score": 4}] * 16,
            },
        }
        card = build_card_data(payload, style="xianxia")
        self.assertEqual(card.level_label, "境界")
        self.assertEqual(card.level, "金丹")
        self.assertEqual(card.platform_model_label, "宗门和法宝")
        self.assertEqual(card.user_label, "道号")
        self.assertIn("多个傀儡", card.summary)
        self.assertEqual(len(card.axis_scores), 16)

    def test_card_renders_constellation_panel(self) -> None:
        payload = {
            "generated_at": "2026-04-14 13:00",
            "insights": {"rank": "L4"},
            "transcript": {
                "display_name": "码奸",
                "source": "codex",
                "models": ["gpt-5.4"],
            },
            "secondary_skill": {
                "axes": [{"score": value} for value in [4, 4, 1, 0, 1, 0, 2, 0, 1, 0, 4, 2, 0, 1, 0, 0]],
            },
        }
        svg = render_vibecoding_card(payload, style="default")
        self.assertIn("十六维星图 · 奎宿", svg)
        self.assertIn("用户名", svg)
        self.assertIn("stroke-dasharray", svg)

    def test_card_can_render_english_labels(self) -> None:
        payload = {
            "generated_at": "2026-04-14 13:00",
            "insights": {"rank": "L4"},
            "transcript": {
                "display_name": "Jian",
                "source": "codex",
                "models": ["gpt-5.4"],
            },
            "secondary_skill": {
                "axes": [{"score": 4}] * 16,
            },
        }
        svg = render_vibecoding_card(payload, style="default", locale="en")
        self.assertIn("Platforms and Models", svg)
        self.assertIn("16-Star Axis Map · Kui", svg)
        self.assertIn("Username", svg)

    def test_export_bundle_emits_cursor_rule(self) -> None:
        payload = {
            "generated_at": "2026-04-14 13:00",
            "display_name": "码奸",
            "insights": {"rank": "L4", "ability_text": "你已经能稳定推进常见任务。"},
            "transcript": {
                "display_name": "码奸",
                "source": "codex",
                "models": ["gpt-5.4"],
            },
            "secondary_skill": {
                "secondary_skill_contract": {
                    "default_behavior": ["先收束目标、边界、验收，再直接开始做。"],
                    "guardrails": ["如果事实不够，先补文件、日志或命令结果，不要硬猜。"],
                    "prompt_examples": ["按这套 vibecoding 习惯和我一起推进这个任务。"],
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            exported = export_bundle(
                payload=payload,
                markdown="# report\n",
                output_dir=tmpdir,
            )
            cursor_rule_path = Path(exported["cursor_rule"])
            self.assertTrue(cursor_rule_path.exists())
            self.assertIn("alwaysApply: false", cursor_rule_path.read_text(encoding="utf-8"))

    def test_replace_marked_section_updates_only_target_range(self) -> None:
        source = "before\n<!-- A -->\nold\n<!-- B -->\nafter\n"
        updated = replace_marked_section(source, "<!-- A -->", "<!-- B -->", "<!-- A -->\nnew\n<!-- B -->")
        self.assertEqual(updated, "before\n<!-- A -->\nnew\n<!-- B -->\nafter\n")


if __name__ == "__main__":
    unittest.main()
