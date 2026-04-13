from __future__ import annotations

from .analyzer import infer_talent, infer_talent_from_models
from .insights import build_analysis_insights
from .models import Analysis, MetricScore

STAGE_LABELS = {
    "L1": "试手期",
    "L2": "入门期",
    "L3": "成形期",
    "L4": "稳定期",
    "L5": "复用期",
    "L6": "委托期",
    "L7": "并行期",
    "L8": "系统期",
    "L9": "落地期",
    "L10": "传承期",
}


def render_markdown(
    analysis: Analysis,
    certificate_choice: str = "both",
    memory_summary: dict[str, object] | None = None,
    generated_at: str | None = None,
    insights: dict[str, object] | None = None,
) -> str:
    del certificate_choice
    insight_payload = insights or build_analysis_insights(analysis)
    talent = infer_talent(analysis.transcript)
    sections = [
        "# vibecoding.skill 能力报告",
        "",
        "## 本轮概览",
        analysis.overview,
        f"- 用户：`{analysis.transcript.display_name or '用户'}`",
        f"- 来源：`{analysis.transcript.source}`",
    ]
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    sections.extend(_render_token_lines(analysis.transcript.token_usage, label="本轮 tokens"))
    if talent:
        sections.extend(
            [
                f"- 资质判断：`{talent['root']}`",
                f"- 稳定性：`{talent['aptitude']}`",
                f"- 主用模型：`{talent['primary_model']}`",
            ]
        )
    if memory_summary:
        sections.extend(["", _render_memory_summary(memory_summary)])
    sections.extend(["", _render_cultivation_judgement(insight_payload)])
    sections.extend(["", _render_habit_section(insight_payload)])
    sections.extend(["", _render_insights_section(insight_payload)])
    sections.extend(["", _render_coaching_section(insight_payload)])
    sections.extend(
        [
            "",
            "## 细项评分",
            _render_metrics("你这边", analysis.user_metrics),
            "",
            _render_metrics("AI 这边", analysis.assistant_metrics),
        ]
    )
    return "\n".join(sections).strip() + "\n"


def render_aggregate_markdown(
    aggregate: dict[str, object],
    certificate_choice: str = "both",
    memory_summary: dict[str, object] | None = None,
    generated_at: str | None = None,
    insights: dict[str, object] | None = None,
) -> str:
    del certificate_choice
    insight_payload = insights or {}
    talent = infer_talent_from_models(aggregate.get("models", []))
    sections = [
        "# vibecoding.skill 聚合报告",
        "",
        "## 本轮概览",
        str(aggregate["overview"]),
        f"- 用户：`{aggregate.get('display_name', '用户')}`",
        f"- 纳入样本：`{aggregate['sessions_used']}` / `总样本 {aggregate['sessions_total']}`",
    ]
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    sections.extend(_render_token_lines(aggregate.get("token_usage", {}), label="本周期 tokens"))
    sections.extend(_render_distillation_lines(aggregate.get("distillation")))
    if talent:
        sections.extend(
            [
                f"- 资质判断：`{talent['root']}`",
                f"- 稳定性：`{talent['aptitude']}`",
                f"- 主用模型：`{talent['primary_model']}`",
            ]
        )
    if memory_summary:
        sections.extend(["", _render_memory_summary(memory_summary)])
    if insight_payload:
        sections.extend(["", _render_cultivation_judgement(insight_payload)])
    if insight_payload:
        sections.extend(["", _render_habit_section(insight_payload)])
    if insight_payload:
        sections.extend(["", _render_insights_section(insight_payload)])
        sections.extend(["", _render_coaching_section(insight_payload)])
    sections.extend(
        [
            "",
            "## 细项评分",
            _render_metrics("你这边", aggregate["user_metrics"]),
            "",
            _render_metrics("AI 这边", aggregate["assistant_metrics"]),
        ]
    )
    return "\n".join(sections).strip() + "\n"


def render_comparison_markdown(
    comparison: dict[str, object],
    certificate_choice: str = "both",
    generated_at: str | None = None,
) -> str:
    del certificate_choice
    sections = [
        "# vibecoding.skill 对比报告",
        "",
        "## 对比概览",
        str(comparison["overview"]),
    ]
    if comparison.get("display_name"):
        sections.append(f"- 用户：`{comparison['display_name']}`")
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    sections.extend(["", _render_comparison_track("阶段变化", comparison["user"])])
    sections.extend(["", _render_comparison_track("等级变化", comparison["assistant"])])
    return "\n".join(sections).strip() + "\n"


def _render_cultivation_judgement(insights: dict[str, object]) -> str:
    breakthrough_lines = _string_list(insights.get("breakthrough_lines"))
    lines = [
        "## 层级判断",
        f"- 阶段：`{_stage_label(str(insights.get('rank', 'L1')))}`",
        f"- 等级：`{insights.get('rank', 'L1')}`",
        f"- vibecoding 判断：{insights.get('ability_text', '仍在引气试手。')}",
    ]
    if insights.get("usage_line"):
        lines.append(f"- 本轮规模：`{insights['usage_line']}`")
    verdict_lines = _string_list(insights.get("verdict_lines"))
    if verdict_lines:
        lines.extend(["", "### 判词"])
        for item in verdict_lines:
            lines.append(f"- {item}")
    if breakthrough_lines:
        lines.extend(["", "### 下一步"])
        for item in breakthrough_lines:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _render_habit_section(insights: dict[str, object]) -> str:
    lines = ["## 习惯画像"]
    habit_profile_lines = _string_list(insights.get("habit_profile_lines"))
    mimic_lines = _string_list(insights.get("mimic_lines"))
    target_summary_lines = _string_list(insights.get("target_summary_lines"))
    target_gap_lines = _string_list(insights.get("target_gap_lines"))
    target_drill_lines = _string_list(insights.get("target_drill_lines"))
    has_content = False
    if habit_profile_lines:
        has_content = True
        lines.extend(["", "### 这套 vibecoding 习惯是什么"])
        for item in habit_profile_lines:
            lines.append(f"- {item}")
    if mimic_lines:
        has_content = True
        lines.extend(["", "### 如果要模仿这套习惯"])
        for item in mimic_lines:
            lines.append(f"- {item}")
    if target_summary_lines or target_gap_lines or target_drill_lines:
        has_content = True
        lines.extend(["", "### 如果目标是某个等级"])
        for item in target_summary_lines + target_gap_lines + target_drill_lines:
            lines.append(f"- {item}")
    return "\n".join(lines) if has_content else ""


def _render_insights_section(insights: dict[str, object]) -> str:
    groups = [
        ("### 16 维主判", insights.get("dimension_summary_lines")),
        ("### 你这边", insights.get("user_summary_lines")),
        ("### AI 这边", insights.get("assistant_summary_lines")),
        ("### 现代协作信号", insights.get("modern_signal_lines")),
        ("### 分享卡取材", insights.get("image_concepts")),
        ("### 判断依据", insights.get("report_basis_lines")),
    ]
    lines = ["## 拆解依据"]
    has_content = False
    for title, items in groups:
        values = _string_list(items)
        if not values:
            continue
        has_content = True
        lines.extend(["", title])
        for item in values:
            lines.append(f"- {item}")
    return "\n".join(lines) if has_content else ""


def render_coaching_markdown(
    title: str,
    *,
    display_name: str,
    source: str,
    generated_at: str | None,
    insights: dict[str, object],
    target_level: str | None = None,
) -> str:
    sections = [
        f"# {title}",
        "",
        "## 当前定位",
        f"- 用户：`{display_name or '用户'}`",
        f"- 来源：`{source}`",
        f"- 阶段：`{_stage_label(str(insights.get('rank', 'L1')))}`",
        f"- 等级：`{insights.get('rank', 'L1')}`",
    ]
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    if target_level:
        sections.append(f"- 目标等级：`{target_level}`")
    sections.extend(["", _render_habit_section(insights)])
    sections.extend(["", _render_coaching_section(insights)])
    return "\n".join(sections).strip() + "\n"


def _render_coaching_section(insights: dict[str, object]) -> str:
    groups = [
        ("### 下一轮先补什么", insights.get("coaching_focus_lines")),
        ("### 具体怎么练", insights.get("coaching_drill_lines")),
        ("### 可直接对 AI 说", insights.get("coaching_prompt_lines")),
        ("### 建议节奏", insights.get("coaching_cycle_lines")),
    ]
    lines = ["## 突破建议"]
    has_content = False
    for title, items in groups:
        values = _string_list(items)
        if not values:
            continue
        has_content = True
        lines.extend(["", title])
        for item in values:
            lines.append(f"- {item}")
    return "\n".join(lines) if has_content else ""
def _render_metrics(title: str, metrics: list[MetricScore]) -> str:
    lines = [f"### {title}"]
    for item in metrics:
        lines.append(f"- {item.name}：`{item.score}/100`，{item.rationale}")
    return "\n".join(lines)


def _render_memory_summary(memory_summary: dict[str, object]) -> str:
    lines = ["## 上次评测记忆"]
    if not memory_summary.get("has_previous"):
        lines.append(f"- {memory_summary['message']}")
        return "\n".join(lines)
    if memory_summary.get("previous_at"):
        lines.append(f"- 上次评测：`{_format_memory_time(str(memory_summary['previous_at']))}`")
    if memory_summary.get("scope_label"):
        lines.append(f"- 记忆分组：`{memory_summary['scope_label']}`")
    lines.append(f"- 阶段：{_render_memory_track(memory_summary['user'])}")
    lines.append(f"- 等级：{_render_memory_track(memory_summary['assistant'])}")
    return "\n".join(lines)


def _render_memory_track(track: dict[str, object]) -> str:
    delta = int(track["score_delta"])
    delta_text = f"{delta:+d}"
    before_level = str(track.get("display_before_level") or track["before_level"])
    after_level = str(track.get("display_after_level") or track["after_level"])
    return (
        f"`{before_level} {track['before_score']}/100 -> "
        f"{after_level} {track['after_score']}/100`，"
        f"{track['outcome']}（{delta_text}）"
    )


def _render_comparison_track(title: str, data: dict[str, object]) -> str:
    before_level = str(data.get("display_before_level") or data["before_level"])
    after_level = str(data.get("display_after_level") or data["after_level"])
    lines = [
        f"## {title}",
        f"- 结果：{data['outcome']}",
        f"- 前次：`{before_level}`（`{data['before_score']}/100`）",
        f"- 本次：`{after_level}`（`{data['after_score']}/100`）",
        f"- 分数变化：`{data['score_delta']:+d}`",
        "",
        "### 关键变化",
    ]
    improvements = data.get("top_improvements") or []
    regressions = data.get("top_regressions") or []
    if improvements:
        for item in improvements:
            lines.append(f"- 上涨：{item['name']} `+{item['delta']}`，从 {item['before']} 到 {item['after']}")
    else:
        lines.append("- 本轮没有上涨项。")
    if regressions:
        for item in regressions:
            lines.append(f"- 回落：{item['name']} `{item['delta']}`，从 {item['before']} 到 {item['after']}")
    next_focus = _string_list(data.get("next_focus"))
    if next_focus:
        lines.extend(["", "### 下一轮聚焦"])
        for item in next_focus:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _render_token_lines(token_usage, label: str) -> list[str]:
    total = _token_value(token_usage, "total_tokens")
    if not total:
        return []
    input_tokens = _token_value(token_usage, "input_tokens")
    cached_input_tokens = _token_value(token_usage, "cached_input_tokens")
    output_tokens = _token_value(token_usage, "output_tokens")
    reasoning_output_tokens = _token_value(token_usage, "reasoning_output_tokens")
    return [
        f"- {label}：`{_fmt_int(total)} token`",
        f"- token 明细：`输入 {_fmt_int(input_tokens)} / 缓存 {_fmt_int(cached_input_tokens)} / 输出 {_fmt_int(output_tokens)} / 推理 {_fmt_int(reasoning_output_tokens)}`",
    ]


def _render_distillation_lines(distillation) -> list[str]:
    if not isinstance(distillation, dict) or not distillation.get("chunked"):
        return []
    chunk_count = int(distillation.get("chunk_count", 0) or 0)
    session_count = int(distillation.get("sessions_total", distillation.get("session_count", 0)) or 0)
    user_messages = int(distillation.get("user_messages", 0) or 0)
    assistant_messages = int(distillation.get("assistant_messages", 0) or 0)
    compressed_assistant = int(distillation.get("compressed_assistant_messages", 0) or 0)
    ratio = float(distillation.get("compression_ratio", 1.0) or 1.0)
    strategy = str(distillation.get("strategy") or "保留用户 prompt 原文，强压缩 AI 回复，按用户回合拼块后再汇总")
    return [
        f"- 超长记录处理：`{session_count} 场会话分块为 {chunk_count} 段`",
        f"- 分块策略：`{strategy}`",
        f"- 消息统计：`用户 {user_messages} / AI {assistant_messages} / 压缩 AI {compressed_assistant}`",
        f"- 压缩比例：`{ratio:.3f}`",
    ]


def _token_value(token_usage, key: str) -> int:
    if isinstance(token_usage, dict):
        value = token_usage.get(key, 0)
        return int(value) if isinstance(value, int) else 0
    value = getattr(token_usage, key, 0)
    return int(value) if isinstance(value, int) else 0


def _format_memory_time(value: str) -> str:
    return value.replace("T", " ")


def _fmt_int(value: int) -> str:
    return f"{value:,}"


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _stage_label(rank: str) -> str:
    return STAGE_LABELS.get(rank, "试手期")
