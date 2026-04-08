from __future__ import annotations

from .analyzer import infer_talent, infer_talent_from_models
from .parsers import redact_path
from .models import Analysis, Certificate, MetricScore


def render_markdown(analysis: Analysis, certificate_choice: str = "both") -> str:
    talent = infer_talent(analysis.transcript)
    sections = [
        "# portrait.skill 画像报告",
        "",
        "## 会话概览",
        analysis.overview,
        f"- 来源：`{analysis.transcript.source}`",
        f"- 文件：`{redact_path(analysis.transcript.path)}`",
    ]
    if talent:
        sections.extend(
            [
                f"- 灵根：`{talent['root']}`",
                f"- 资质：`{talent['aptitude']}`",
                f"- 炉主模型：`{talent['primary_model']}`",
            ]
        )
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
        sections.extend(["", _render_certificate(analysis.assistant_certificate)])
    return "\n".join(sections).strip() + "\n"


def render_comparison_markdown(comparison: dict[str, object], certificate_choice: str = "both") -> str:
    sections = [
        "# portrait.skill 破境报告",
        "",
        "## 对比概览",
        str(comparison["overview"]),
    ]
    if certificate_choice in {"user", "both"}:
        sections.extend(["", _render_comparison_track("修仙画像", comparison["user"])])
    if certificate_choice in {"assistant", "both"}:
        sections.extend(["", _render_comparison_track("AI 协作能力证书", comparison["assistant"])])
    return "\n".join(sections).strip() + "\n"


def render_aggregate_markdown(aggregate: dict[str, object], certificate_choice: str = "both") -> str:
    talent = infer_talent_from_models(aggregate.get("models", []))
    sections = [
        "# portrait.skill 炼化总报告",
        "",
        "## 聚合概览",
        str(aggregate["overview"]),
        f"- 纳入会话：`{aggregate['sessions_used']}` / `总会话 {aggregate['sessions_total']}`",
    ]
    if talent:
        sections.extend(
            [
                f"- 灵根：`{talent['root']}`",
                f"- 资质：`{talent['aptitude']}`",
                f"- 主炉模型：`{talent['primary_model']}`",
            ]
        )
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
        sections.extend(["", _render_certificate_dict(aggregate["assistant_certificate"])])
    return "\n".join(sections).strip() + "\n"


def _render_metrics(title: str, metrics: list[MetricScore]) -> str:
    lines = [f"### {title}"]
    for item in metrics:
        lines.append(f"- {item.name}：`{item.score}/100`，{item.rationale}")
    return "\n".join(lines)


def _render_certificate(certificate: Certificate) -> str:
    if certificate.track == "assistant":
        return _render_assistant_certificate(certificate)
    lines = [
        f"## {certificate.title}",
        f"**等级**：{certificate.level}",
        f"**总分**：`{certificate.score}/100`",
        f"**画像**：{certificate.persona.title}",
        f"**副标题**：{certificate.persona.subtitle}",
        f"**标签**：{' / '.join(certificate.persona.tags)}",
        f"**总结**：{certificate.persona.summary}",
        "",
        "### 判定依据",
    ]
    for item in certificate.evidence:
        lines.append(f"- {item}")
    lines.extend(["", "### 下一次突破任务"])
    for item in certificate.growth_plan:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_certificate_dict(certificate: dict[str, object]) -> str:
    if certificate["track"] == "assistant":
        return _render_assistant_certificate_dict(certificate)
    persona = certificate["persona"]
    lines = [
        f"## {certificate['title']}",
        f"**等级**：{certificate['level']}",
        f"**总分**：`{certificate['score']}/100`",
        f"**画像**：{persona['title']}",
        f"**副标题**：{persona['subtitle']}",
        f"**标签**：{' / '.join(persona['tags'])}",
        f"**总结**：{persona['summary']}",
        "",
        "### 判定依据",
    ]
    for item in certificate["evidence"]:
        lines.append(f"- {item}")
    lines.extend(["", "### 下一次突破任务"])
    for item in certificate["growth_plan"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_assistant_certificate(certificate: Certificate) -> str:
    lines = [
        f"## {certificate.title}",
        f"**等级**：{certificate.level}",
        f"**总分**：`{certificate.score}/100`",
        f"**能力类型**：{certificate.persona.title}",
        f"**能力说明**：{certificate.persona.subtitle}",
        f"**能力标签**：{' / '.join(certificate.persona.tags)}",
        f"**结论**：{certificate.persona.summary}",
        "",
        "### 判定依据",
    ]
    for item in certificate.evidence:
        lines.append(f"- {item}")
    lines.extend(["", "### 下一次提升建议"])
    for item in certificate.growth_plan:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _render_assistant_certificate_dict(certificate: dict[str, object]) -> str:
    persona = certificate["persona"]
    lines = [
        f"## {certificate['title']}",
        f"**等级**：{certificate['level']}",
        f"**总分**：`{certificate['score']}/100`",
        f"**能力类型**：{persona['title']}",
        f"**能力说明**：{persona['subtitle']}",
        f"**能力标签**：{' / '.join(persona['tags'])}",
        f"**结论**：{persona['summary']}",
        "",
        "### 判定依据",
    ]
    for item in certificate["evidence"]:
        lines.append(f"- {item}")
    lines.extend(["", "### 下一次提升建议"])
    for item in certificate["growth_plan"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


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
