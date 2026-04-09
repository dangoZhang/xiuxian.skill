from __future__ import annotations

from .analyzer import infer_talent, infer_talent_from_models
from .parsers import redact_path
from .models import Analysis, Certificate, MetricScore
from .xianxia import derive_xianxia_profile

AI_LEVEL_ABILITIES = {
    "L1": "完成单轮问答",
    "L2": "感知提问方式对结果的影响",
    "L3": "稳定完成简单任务",
    "L4": "重复跑通常见流程",
    "L5": "把经验封成模板技法",
    "L6": "先替你推进一段具体工作",
    "L7": "协同多个分身与工具完成任务",
    "L8": "承担能力层与系统层工作",
    "L9": "进入真实业务回路并持续回流",
    "L10": "把方法复制到团队与客户场景",
}


def render_markdown(
    analysis: Analysis,
    certificate_choice: str = "both",
    memory_summary: dict[str, object] | None = None,
    generated_at: str | None = None,
) -> str:
    talent = infer_talent(analysis.transcript)
    token_label = "消耗 token" if certificate_choice == "assistant" else "灵气流转"
    token_lines = _render_token_lines(analysis.transcript.token_usage, cultivation_label="修炼时长", token_label=token_label)
    certificate_token_note = _render_period_token_note(analysis.transcript.token_usage, label="本次卷宗消耗")
    sections = [
        "# 画像.skill 画像报告",
        "",
        "## 会话概览",
        analysis.overview,
        f"- 用户名：`{analysis.transcript.display_name or '道友'}`",
        f"- 来源：`{analysis.transcript.source}`",
        f"- 文件：`{redact_path(analysis.transcript.path)}`",
    ]
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    sections.extend(token_lines)
    if talent:
        sections.extend(
            [
                f"- 灵根：`{talent['root']}`",
                f"- 资质：`{talent['aptitude']}`",
                f"- 炉主模型：`{talent['primary_model']}`",
            ]
        )
    if memory_summary:
        sections.extend(["", _render_memory_summary(memory_summary, certificate_choice)])
    if certificate_choice in {"user", "both"}:
        sections.extend(["", _render_xianxia_profile(_analysis_xianxia_payload(analysis))])
    sections.extend(
        [
            "",
            "## 维度评分",
            _render_metrics("用户协作维度", analysis.user_metrics),
            "",
            _render_metrics("AI 协作维度", analysis.assistant_metrics),
        ]
    )
    if certificate_choice in {"user", "both"}:
        sections.extend(["", _render_certificate(analysis.user_certificate)])
    if certificate_choice in {"assistant", "both"}:
        sections.extend(["", _render_certificate(analysis.assistant_certificate, token_note=certificate_token_note)])
    return "\n".join(sections).strip() + "\n"


def render_comparison_markdown(
    comparison: dict[str, object],
    certificate_choice: str = "both",
    generated_at: str | None = None,
) -> str:
    sections = [
        "# 画像.skill 破境报告",
        "",
        "## 对比概览",
        str(comparison["overview"]),
    ]
    if comparison.get("display_name"):
        sections.append(f"- 用户名：`{comparison['display_name']}`")
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    if certificate_choice in {"user", "both"}:
        sections.extend(["", _render_comparison_track("修仙画像", comparison["user"])])
    if certificate_choice in {"assistant", "both"}:
        sections.extend(["", _render_comparison_track("AI 协作能力证书", comparison["assistant"])])
    return "\n".join(sections).strip() + "\n"


def render_aggregate_markdown(
    aggregate: dict[str, object],
    certificate_choice: str = "both",
    memory_summary: dict[str, object] | None = None,
    generated_at: str | None = None,
) -> str:
    talent = infer_talent_from_models(aggregate.get("models", []))
    token_label = "累计消耗 token" if certificate_choice == "assistant" else "累计灵气流转"
    token_lines = _render_token_lines(aggregate.get("token_usage", {}), cultivation_label="累计修炼时长", token_label=token_label)
    certificate_token_note = _render_period_token_note(aggregate.get("token_usage", {}), label="本周期累计消耗")
    sections = [
        "# 画像.skill 炼化总报告",
        "",
        "## 聚合概览",
        str(aggregate["overview"]),
        f"- 用户名：`{aggregate.get('display_name', '道友')}`",
        f"- 纳入会话：`{aggregate['sessions_used']}` / `总会话 {aggregate['sessions_total']}`",
    ]
    if generated_at:
        sections.append(f"- 生成时间：`{generated_at}`")
    sections.extend(token_lines)
    if talent:
        sections.extend(
            [
                f"- 灵根：`{talent['root']}`",
                f"- 资质：`{talent['aptitude']}`",
                f"- 主炉模型：`{talent['primary_model']}`",
            ]
        )
    if memory_summary:
        sections.extend(["", _render_memory_summary(memory_summary, certificate_choice)])
    if certificate_choice in {"user", "both"}:
        sections.extend(["", _render_xianxia_profile(aggregate)])
    sections.extend(
        [
            "",
            "## 维度评分",
            _render_metrics("用户协作维度", aggregate["user_metrics"]),
            "",
            _render_metrics("AI 协作维度", aggregate["assistant_metrics"]),
        ]
    )
    if certificate_choice in {"user", "both"}:
        sections.extend(["", _render_certificate_dict(aggregate["user_certificate"])])
    if certificate_choice in {"assistant", "both"}:
        sections.extend(["", _render_certificate_dict(aggregate["assistant_certificate"], token_note=certificate_token_note)])
    return "\n".join(sections).strip() + "\n"


def _render_metrics(title: str, metrics: list[MetricScore]) -> str:
    lines = [f"### {title}"]
    for item in metrics:
        lines.append(f"- {item.name}：`{item.score}/100`，{item.rationale}")
    return "\n".join(lines)


def _render_xianxia_profile(payload: dict[str, object]) -> str:
    profile = derive_xianxia_profile(payload)
    if not profile:
        return ""
    lines = ["## 修仙映照"]
    for item in profile[:8]:
        detail = f"，{item['detail']}" if item.get("detail") else ""
        lines.append(f"- {item['term']}：`{item['value']}`{detail}")
    return "\n".join(lines)


def _render_memory_summary(memory_summary: dict[str, object], certificate_choice: str) -> str:
    lines = ["## 上次评测记忆"]
    if not memory_summary.get("has_previous"):
        lines.append(f"- {memory_summary['message']}")
        return "\n".join(lines)
    if memory_summary.get("previous_at"):
        lines.append(f"- 上次评测：`{_format_memory_time(str(memory_summary['previous_at']))}`")
    if memory_summary.get("scope_label"):
        lines.append(f"- 记忆分组：`{memory_summary['scope_label']}`")
    if certificate_choice in {"user", "both"}:
        lines.append(f"- 修仙画像：{_render_memory_track(memory_summary['user'])}")
    if certificate_choice in {"assistant", "both"}:
        lines.append(f"- AI 协作能力证书：{_render_memory_track(memory_summary['assistant'])}")
    return "\n".join(lines)


def _render_memory_track(track: dict[str, object]) -> str:
    delta = int(track["score_delta"])
    delta_text = f"{delta:+d}"
    return (
        f"`{track['before_level']} {track['before_score']}/100 -> "
        f"{track['after_level']} {track['after_score']}/100`，"
        f"{track['outcome']}（{delta_text}）"
    )


def _format_memory_time(value: str) -> str:
    return value.replace("T", " ")


def _render_certificate(certificate: Certificate, token_note: str | None = None) -> str:
    if certificate.track == "assistant":
        return _render_assistant_certificate(certificate, token_note=token_note)
    lines = [
        f"## {certificate.title}",
        f"**境界**：{certificate.level}",
        f"**命格**：{certificate.persona.title}",
        f"**道解**：{certificate.persona.subtitle}",
        f"**气象**：{' / '.join(certificate.persona.tags)}",
        f"**总评**：{certificate.persona.summary}",
        "",
        "### 观气所得",
    ]
    for item in certificate.evidence:
        lines.append(f"- {item}")
    lines.extend(["", "### 破境机缘"])
    for item in certificate.growth_plan:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_certificate_dict(certificate: dict[str, object], token_note: str | None = None) -> str:
    if certificate["track"] == "assistant":
        return _render_assistant_certificate_dict(certificate, token_note=token_note)
    persona = certificate["persona"]
    lines = [
        f"## {certificate['title']}",
        f"**境界**：{certificate['level']}",
        f"**命格**：{persona['title']}",
        f"**道解**：{persona['subtitle']}",
        f"**气象**：{' / '.join(persona['tags'])}",
        f"**总评**：{persona['summary']}",
        "",
        "### 观气所得",
    ]
    for item in certificate["evidence"]:
        lines.append(f"- {item}")
    lines.extend(["", "### 破境机缘"])
    for item in certificate["growth_plan"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_assistant_certificate(certificate: Certificate, token_note: str | None = None) -> str:
    lines = [
        f"## {certificate.title}",
        f"**等级**：{certificate.level}",
        f"**能力**：能够{_assistant_ability(certificate.level, certificate.persona.subtitle)}",
        f"**判词**：{_assistant_certificate_verdict(certificate.evidence, certificate.level, certificate.persona.subtitle)}",
        token_note or _render_certificate_token_line(certificate),
        "",
        "### 判定依据",
    ]
    for item in certificate.evidence:
        lines.append(f"- {item}")
    lines.extend(["", "### 下一次提升建议"])
    for item in certificate.growth_plan:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_assistant_certificate_dict(certificate: dict[str, object], token_note: str | None = None) -> str:
    persona = certificate["persona"]
    lines = [
        f"## {certificate['title']}",
        f"**等级**：{certificate['level']}",
        f"**能力**：能够{_assistant_ability(str(certificate['level']), persona['subtitle'])}",
        f"**判词**：{_assistant_certificate_verdict(certificate["evidence"], str(certificate['level']), persona['subtitle'])}",
        token_note or _render_certificate_token_line(certificate),
        "",
        "### 判定依据",
    ]
    for item in certificate["evidence"]:
        lines.append(f"- {item}")
    lines.extend(["", "### 下一次提升建议"])
    for item in certificate["growth_plan"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_certificate_token_line(certificate) -> str:
    score = certificate["score"] if isinstance(certificate, dict) else certificate.score
    return f"**当前评分**：`{score}/100`"


def _render_period_token_note(token_usage, label: str) -> str | None:
    total = _token_value(token_usage, "total_tokens")
    if not total:
        return None
    return f"**{label}**：`{_fmt_int(total)} token`"


def _render_comparison_track(title: str, data: dict[str, object]) -> str:
    lines = [
        f"## {title}",
        f"**结果**：{data['outcome']}",
        f"**前次等级**：{data['before_level']}（`{data['before_score']}/100`）",
        f"**本次等级**：{data['after_level']}（`{data['after_score']}/100`）",
        f"**分数变化**：`{data['score_delta']:+d}`",
        "",
        "### 关键变化",
    ]
    improvements = data.get("top_improvements") or []
    regressions = data.get("top_regressions") or []
    if improvements:
        for item in improvements:
            lines.append(f"- 上涨：{item['name']} `+{item['delta']}`，从 {item['before']} 到 {item['after']}")
    else:
        lines.append("- 本轮没有出现上涨项。")
    if regressions:
        for item in regressions:
            lines.append(f"- 回落：{item['name']} `{item['delta']}`，从 {item['before']} 到 {item['after']}")
    lines.extend(["", "### 下一轮聚焦"])
    for item in data.get("next_focus") or []:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_token_lines(token_usage, cultivation_label: str, token_label: str) -> list[str]:
    total = _token_value(token_usage, "total_tokens")
    if not total:
        return []
    input_tokens = _token_value(token_usage, "input_tokens")
    cached_input_tokens = _token_value(token_usage, "cached_input_tokens")
    output_tokens = _token_value(token_usage, "output_tokens")
    reasoning_output_tokens = _token_value(token_usage, "reasoning_output_tokens")
    return [
        f"- {cultivation_label}：`{_fmt_int(total)} token`",
        f"- {token_label}：`输入 {_fmt_int(input_tokens)} / 缓存 {_fmt_int(cached_input_tokens)} / 输出 {_fmt_int(output_tokens)} / 推理 {_fmt_int(reasoning_output_tokens)}`",
    ]


def _token_value(token_usage, key: str) -> int:
    if isinstance(token_usage, dict):
        value = token_usage.get(key, 0)
        return int(value) if isinstance(value, int) else 0
    value = getattr(token_usage, key, 0)
    return int(value) if isinstance(value, int) else 0


def _fmt_int(value: int) -> str:
    return f"{value:,}"


def _assistant_ability(level: str, value: str) -> str:
    mapped = AI_LEVEL_ABILITIES.get(level)
    if mapped:
        return mapped
    cleaned = " ".join(value.split())
    if not cleaned:
        return "完成当前等级对应的协作任务"
    if cleaned.startswith("已经能"):
        return cleaned[3:]
    if cleaned.startswith("能"):
        return cleaned[1:]
    if cleaned.startswith("开始把"):
        return "把" + cleaned[3:]
    if cleaned.startswith("开始拥有"):
        return "拥有" + cleaned[4:]
    if cleaned.startswith("开始"):
        return cleaned[2:]
    return cleaned


def _assistant_certificate_verdict(evidence: list[str], level: str, subtitle: str) -> str:
    top_name = "执行推进"
    low_name = "补短板"
    if evidence:
        first = str(evidence[0]).split("：", 1)
        if len(first) == 2:
            top_name = first[1].split(" ", 1)[0]
        if len(evidence) > 1:
            second = str(evidence[1]).split("：", 1)
            if len(second) == 2:
                low_name = second[1].split(" ", 1)[0]
    ability = _assistant_ability(level, subtitle)
    return f"当前已能{ability}，{top_name}更稳，{low_name}仍可继续补强。"


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
