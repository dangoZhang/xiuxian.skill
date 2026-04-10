from __future__ import annotations

from .analyzer import infer_talent, infer_talent_from_models
from .insights import build_analysis_insights
from .models import Analysis, MetricScore
from .xianxia import derive_xianxia_profile


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
        "# 修仙.skil 能力报告",
        "",
        "## 本轮概览",
        analysis.overview,
        f"- 命主：`{analysis.transcript.display_name or '道友'}`",
        f"- 来源：`{analysis.transcript.source}`",
    ]
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    sections.extend(_render_token_lines(analysis.transcript.token_usage, label="本轮 tokens"))
    if talent:
        sections.extend(
            [
                f"- 灵根：`{talent['root']}`",
                f"- 资质：`{talent['aptitude']}`",
                f"- 炉主：`{talent['primary_model']}`",
            ]
        )
    if memory_summary:
        sections.extend(["", _render_memory_summary(memory_summary)])
    sections.extend(["", _render_cultivation_judgement(insight_payload)])
    sections.extend(["", _render_xianxia_profile(_analysis_xianxia_payload(analysis))])
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
        "# 修仙.skil 聚合报告",
        "",
        "## 本轮概览",
        str(aggregate["overview"]),
        f"- 命主：`{aggregate.get('display_name', '道友')}`",
        f"- 纳入样本：`{aggregate['sessions_used']}` / `总样本 {aggregate['sessions_total']}`",
    ]
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    sections.extend(_render_token_lines(aggregate.get("token_usage", {}), label="本周期 tokens"))
    if talent:
        sections.extend(
            [
                f"- 灵根：`{talent['root']}`",
                f"- 资质：`{talent['aptitude']}`",
                f"- 炉主：`{talent['primary_model']}`",
            ]
        )
    if memory_summary:
        sections.extend(["", _render_memory_summary(memory_summary)])
    if insight_payload:
        sections.extend(["", _render_cultivation_judgement(insight_payload)])
    sections.extend(["", _render_xianxia_profile(aggregate)])
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
        "# 修仙.skil 破境报告",
        "",
        "## 对比概览",
        str(comparison["overview"]),
    ]
    if comparison.get("display_name"):
        sections.append(f"- 命主：`{comparison['display_name']}`")
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    sections.extend(["", _render_comparison_track("境界变化", comparison["user"])])
    sections.extend(["", _render_comparison_track("等级变化", comparison["assistant"])])
    return "\n".join(sections).strip() + "\n"


def _render_cultivation_judgement(insights: dict[str, object]) -> str:
    breakthrough_lines = _string_list(insights.get("breakthrough_lines"))
    lines = [
        "## 层级判断",
        f"- 境界：`{insights.get('realm', '凡人')}`",
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


def _render_insights_section(insights: dict[str, object]) -> str:
    groups = [
        ("### 你这边", insights.get("user_summary_lines")),
        ("### AI 这边", insights.get("assistant_summary_lines")),
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
) -> str:
    sections = [
        f"# {title}",
        "",
        "## 当前定位",
        f"- 命主：`{display_name or '道友'}`",
        f"- 来源：`{source}`",
        f"- 境界：`{insights.get('realm', '凡人')}`",
        f"- 等级：`{insights.get('rank', 'L1')}`",
    ]
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
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


def _render_xianxia_profile(payload: dict[str, object]) -> str:
    profile = derive_xianxia_profile(payload)
    if not profile:
        return ""
    lines = ["## 补充信息"]
    for item in profile[:8]:
        detail = f"，{item['detail']}" if item.get("detail") else ""
        lines.append(f"- {item['term']}：`{item['value']}`{detail}")
    return "\n".join(lines)


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
    lines.append(f"- 境界：{_render_memory_track(memory_summary['user'])}")
    lines.append(f"- 等级：{_render_memory_track(memory_summary['assistant'])}")
    return "\n".join(lines)


def _render_memory_track(track: dict[str, object]) -> str:
    delta = int(track["score_delta"])
    delta_text = f"{delta:+d}"
    return (
        f"`{track['before_level']} {track['before_score']}/100 -> "
        f"{track['after_level']} {track['after_score']}/100`，"
        f"{track['outcome']}（{delta_text}）"
    )


def _render_comparison_track(title: str, data: dict[str, object]) -> str:
    lines = [
        f"## {title}",
        f"- 结果：{data['outcome']}",
        f"- 前次：`{data['before_level']}`（`{data['before_score']}/100`）",
        f"- 本次：`{data['after_level']}`（`{data['after_score']}/100`）",
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


def _analysis_xianxia_payload(analysis: Analysis) -> dict[str, object]:
    return {
        "transcript": {
            "source": analysis.transcript.source,
            "message_count": len(analysis.transcript.messages),
            "tool_calls": analysis.transcript.tool_calls,
            "models": analysis.transcript.models,
            "providers": analysis.transcript.providers,
            "token_usage": {
                "total_tokens": analysis.transcript.token_usage.total_tokens,
            },
        },
        "user_metrics": [{"name": item.name, "score": item.score, "rationale": item.rationale} for item in analysis.user_metrics],
        "user_certificate": {
            "persona": {
                "subtitle": analysis.user_certificate.persona.subtitle,
            },
            "growth_plan": analysis.user_certificate.growth_plan,
        },
    }


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
