from __future__ import annotations

from typing import Any

from .analyzer import infer_talent_from_models

XI_METRIC_TAGS = {
    "目标清晰度": "道心坚定",
    "上下文供给": "根基稳固",
    "迭代修正力": "悟性渐开",
    "验收意识": "收功谨慎",
    "协作节奏": "气机相合",
    "执行落地": "术法纯熟",
    "工具调度": "驭器纯熟",
    "验证闭环": "收功圆满",
    "上下文承接": "气脉贯通",
    "补救适配": "应变有方",
}


def derive_xianxia_profile(payload: dict[str, object]) -> list[dict[str, str]]:
    transcript = _as_dict(payload.get("transcript"))
    user_certificate = _as_dict(payload.get("user_certificate"))
    persona = _as_dict(user_certificate.get("persona"))
    metrics = _as_list(payload.get("user_metrics"))
    top_metric = _best_metric(metrics)
    total_tokens = _token_total(payload)
    source = str(transcript.get("source") or payload.get("source") or "记录")
    models = _models(payload)
    providers = _providers(payload)
    talent = infer_talent_from_models(models) or {}
    message_count = int(transcript.get("message_count") or payload.get("message_count") or payload.get("total_messages") or 0)
    tool_calls = int(transcript.get("tool_calls") or payload.get("tool_calls") or payload.get("total_tool_calls") or 0)
    sessions_used = payload.get("sessions_used")
    subtitle = str(persona.get("subtitle") or "")
    growth = _first(_as_list(user_certificate.get("growth_plan")))
    primary_model = str(talent.get("primary_model") or (models[0] if models else ""))
    top_metric_name = str(top_metric.get("name") or "")
    top_metric_score = int(top_metric.get("score") or 0)

    profile = [
        {
            "term": "灵根",
            "value": str(talent.get("root") or "未显灵根"),
            "detail": str(talent.get("aptitude") or "资质未明"),
        },
        {
            "term": "来路",
            "value": _compose_lingmai(source, primary_model, providers),
            "detail": "运行平台与主用模型",
        },
        {
            "term": "灵气",
            "value": f"{_fmt_int(total_tokens)} tokens" if total_tokens else "tokens 未显",
            "detail": _period_label(payload),
        },
        {
            "term": "心法",
            "value": f"{XI_METRIC_TAGS.get(top_metric_name, top_metric_name or '心法未明')} {top_metric_score}/100",
            "detail": "当前最稳的一项协作功底",
        },
        {
            "term": "功法",
            "value": _subtitle_to_gongfa(subtitle),
            "detail": "你如今真正会使的法门",
        },
        {
            "term": "分身",
            "value": _tool_call_phrase(tool_calls),
            "detail": "本轮工具调用情况",
        },
        {
            "term": "历练",
            "value": _review_phrase(message_count, sessions_used),
            "detail": "本轮纳入的真实样本",
        },
    ]
    if _has_method_sediment(subtitle):
        profile.append(
            {
                "term": "传承",
                "value": "法门已成",
                "detail": "开始把经验炼成可复用方法",
            }
        )
    if growth:
        profile.append(
            {
                "term": "机缘",
                "value": _truncate(growth, 18),
                "detail": "下一步该朝哪里冲关",
            }
        )
    return [item for item in profile if item["value"]]


def _compose_lingmai(source: str, primary_model: str, providers: list[str]) -> str:
    source_text = {
        "codex": "Codex",
        "claude": "Claude Code",
        "opencode": "OpenCode",
        "openclaw": "OpenClaw",
        "cursor": "Cursor",
        "vscode": "VS Code",
    }.get(source.lower(), source or "未知")
    if primary_model:
        return f"{source_text} · {primary_model}"
    return source_text


def _tool_call_phrase(tool_calls: int) -> str:
    if tool_calls <= 0:
        return "工具未调用"
    return f"工具调用 {tool_calls} 次"


def _review_phrase(message_count: int, sessions_used: Any) -> str:
    if isinstance(sessions_used, int) and sessions_used > 1:
        return f"纳入 {sessions_used} 场会话"
    if message_count > 0:
        return f"{message_count} 条对话"
    return "初经问答"


def _subtitle_to_gongfa(subtitle: str) -> str:
    cleaned = " ".join(subtitle.split())
    if not cleaned:
        return "功法未定"
    lowered = cleaned.lower()
    if any(token in lowered for token in ["skill", "workflow", "模板", "模块", "sop"]):
        return "章法初成"
    cleaned = cleaned.replace("开始把自己的做法封成", "").replace("已经有", "").strip(" ，。")
    return _truncate(cleaned or subtitle, 18)


def _has_method_sediment(subtitle: str) -> bool:
    lowered = subtitle.lower()
    return any(token in lowered for token in ["skill", "workflow", "模板", "模块", "sop"])


def _period_label(payload: dict[str, object]) -> str:
    window = _as_dict(payload.get("time_window"))
    since = window.get("since")
    until = window.get("until")
    if since or until:
        return f"{since or '最早'} 至 {until or '现在'}"
    sessions_used = payload.get("sessions_used")
    if isinstance(sessions_used, int) and sessions_used > 1:
        return f"{sessions_used} 场会话累计"
    return "此番问答"


def _best_metric(metrics: list[object]) -> dict[str, object]:
    items = [item for item in metrics if isinstance(item, dict) and "score" in item]
    if not items:
        return {}
    return sorted(items, key=lambda item: int(item.get("score", 0)), reverse=True)[0]


def _token_total(payload: dict[str, object]) -> int:
    transcript = _as_dict(payload.get("transcript"))
    token_usage = _as_dict(transcript.get("token_usage")) or _as_dict(payload.get("token_usage"))
    return int(token_usage.get("total_tokens") or 0)


def _models(payload: dict[str, object]) -> list[str]:
    transcript = _as_dict(payload.get("transcript"))
    return [str(item) for item in _as_list(transcript.get("models")) or _as_list(payload.get("models")) if item]


def _providers(payload: dict[str, object]) -> list[str]:
    transcript = _as_dict(payload.get("transcript"))
    return [str(item) for item in _as_list(transcript.get("providers")) or _as_list(payload.get("providers")) if item]


def _first(items: list[object]) -> str:
    return str(items[0]) if items else ""


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(1, limit - 1)] + "…"


def _fmt_int(value: int) -> str:
    return f"{int(value):,}"
