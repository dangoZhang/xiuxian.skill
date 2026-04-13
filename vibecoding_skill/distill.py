from __future__ import annotations

import re
from dataclasses import dataclass

from .analyzer import aggregate_analyses, analyze_transcript
from .models import Analysis, Message, TokenUsage, Transcript


DISTILL_MAX_UNITS = 12000
DISTILL_MAX_MESSAGES = 180
ASSISTANT_REPLY_MAX_CHARS = 180
ASSISTANT_PRIORITY_TOKENS = [
    "先",
    "接下来",
    "已",
    "完成",
    "验证",
    "测试",
    "read",
    "run",
    "build",
    "test",
    "verify",
    "changed",
    "updated",
    "next",
]


@dataclass(slots=True)
class DistilledRun:
    kind: str
    analysis: Analysis | None = None
    aggregate: dict[str, object] | None = None
    analyses: list[Analysis] | None = None


@dataclass(slots=True)
class DistilledTranscript:
    source: str
    path: object
    messages: list[Message]
    tool_calls: int
    raw_event_count: int
    models: list[str]
    providers: list[str]
    token_usage: TokenUsage
    display_name: str | None
    user_messages: int
    assistant_messages: int
    compressed_assistant_messages: int
    raw_units: int
    distilled_units: int


def analyze_with_chunking(transcript: Transcript) -> DistilledRun:
    distilled = _distill_transcript(transcript)
    if len(distilled.messages) <= DISTILL_MAX_MESSAGES and distilled.distilled_units <= DISTILL_MAX_UNITS:
        analysis = analyze_transcript(transcript)
        return DistilledRun(kind="single", analysis=analysis, analyses=[analysis])

    chunk_transcripts = _pack_distilled_transcripts([distilled])
    chunk_analyses = [analyze_transcript(chunk) for chunk in chunk_transcripts if chunk.messages]
    aggregate = aggregate_analyses(
        chunk_analyses,
        min_messages=1,
        total_tool_calls_override=transcript.tool_calls,
        token_usage_override=transcript.token_usage,
    )
    aggregate["distillation"] = _distillation_metadata([distilled], chunk_transcripts, min_messages=1)
    _rewrite_chunked_aggregate(aggregate)
    return DistilledRun(kind="aggregate", aggregate=aggregate, analyses=chunk_analyses)


def analyze_many_with_chunking(transcripts: list[Transcript], min_messages: int = 1) -> DistilledRun:
    distilled_transcripts = [_distill_transcript(transcript) for transcript in transcripts if transcript.messages]
    if not distilled_transcripts:
        raise ValueError("No transcripts to distill.")

    total_messages = sum(len(item.messages) for item in distilled_transcripts)
    total_units = sum(item.distilled_units for item in distilled_transcripts)
    if len(distilled_transcripts) == 1 and total_messages <= DISTILL_MAX_MESSAGES and total_units <= DISTILL_MAX_UNITS:
        analysis = analyze_transcript(transcripts[0])
        return DistilledRun(kind="single", analysis=analysis, analyses=[analysis])

    chunk_transcripts = _pack_distilled_transcripts(distilled_transcripts)
    chunk_analyses = [analyze_transcript(chunk) for chunk in chunk_transcripts if len(chunk.messages) >= min_messages]
    if not chunk_analyses:
        chunk_analyses = [analyze_transcript(chunk) for chunk in chunk_transcripts if chunk.messages]
    aggregate = aggregate_analyses(
        chunk_analyses,
        min_messages=1,
        total_tool_calls_override=sum(item.tool_calls for item in distilled_transcripts),
        token_usage_override=_sum_token_usage(item.token_usage for item in distilled_transcripts),
    )
    aggregate["distillation"] = _distillation_metadata(distilled_transcripts, chunk_transcripts, min_messages=min_messages)
    _rewrite_chunked_aggregate(aggregate)
    return DistilledRun(kind="aggregate", aggregate=aggregate, analyses=chunk_analyses)


def _distill_transcript(transcript: Transcript) -> DistilledTranscript:
    messages: list[Message] = []
    raw_units = 0
    distilled_units = 0
    user_messages = 0
    assistant_messages = 0
    compressed_assistant_messages = 0

    for message in transcript.messages:
        original_units = _text_units(message.text)
        raw_units += original_units
        if message.role == "assistant":
            assistant_messages += 1
            distilled_text = _compress_assistant_text(message.text)
            if distilled_text != message.text:
                compressed_assistant_messages += 1
        else:
            user_messages += 1
            distilled_text = message.text
        distilled_message = Message(
            role=message.role,
            text=distilled_text,
            timestamp=message.timestamp,
            meta={**dict(message.meta), "signal_text": message.text},
        )
        messages.append(distilled_message)
        distilled_units += _text_units(distilled_text)

    return DistilledTranscript(
        source=transcript.source,
        path=transcript.path,
        messages=messages,
        tool_calls=transcript.tool_calls,
        raw_event_count=transcript.raw_event_count,
        models=list(transcript.models),
        providers=list(transcript.providers),
        token_usage=transcript.token_usage,
        display_name=transcript.display_name,
        user_messages=user_messages,
        assistant_messages=assistant_messages,
        compressed_assistant_messages=compressed_assistant_messages,
        raw_units=raw_units,
        distilled_units=distilled_units,
    )


def _pack_distilled_transcripts(distilled_transcripts: list[DistilledTranscript]) -> list[Transcript]:
    prepared_chunks: list[list[tuple[Message, int]]] = []
    current: list[tuple[Message, int]] = []
    current_units = 0
    current_messages = 0

    for distilled in distilled_transcripts:
        for turn in _group_turn_messages(distilled.messages):
            turn_units = sum(units for _, units in turn)
            turn_messages = len(turn)
            if current and (
                current_units + turn_units > DISTILL_MAX_UNITS or current_messages + turn_messages > DISTILL_MAX_MESSAGES
            ):
                prepared_chunks.append(current)
                current = []
                current_units = 0
                current_messages = 0

            if turn_units > DISTILL_MAX_UNITS or turn_messages > DISTILL_MAX_MESSAGES:
                for message, units in turn:
                    if current and (
                        current_units + units > DISTILL_MAX_UNITS or current_messages + 1 > DISTILL_MAX_MESSAGES
                    ):
                        prepared_chunks.append(current)
                        current = []
                        current_units = 0
                        current_messages = 0
                    current.append((message, units))
                    current_units += units
                    current_messages += 1
                continue

            current.extend(turn)
            current_units += turn_units
            current_messages += turn_messages
    if current:
        prepared_chunks.append(current)

    models = _merge_unique(term for item in distilled_transcripts for term in item.models)
    providers = _merge_unique(term for item in distilled_transcripts for term in item.providers)
    display_name = next((item.display_name for item in distilled_transcripts if item.display_name), None)
    source = distilled_transcripts[0].source
    path = distilled_transcripts[0].path

    outputs: list[Transcript] = []
    for index, chunk in enumerate(prepared_chunks):
        outputs.append(
            Transcript(
                source=source,
                path=path,
                messages=[message for message, _ in chunk],
                tool_calls=0,
                raw_event_count=len(chunk),
                models=models,
                providers=providers,
                token_usage=TokenUsage(),
                display_name=display_name,
            )
        )
    return outputs


def _distillation_metadata(
    distilled_transcripts: list[DistilledTranscript],
    chunk_transcripts: list[Transcript],
    *,
    min_messages: int,
) -> dict[str, object]:
    raw_units = sum(item.raw_units for item in distilled_transcripts)
    distilled_units = sum(item.distilled_units for item in distilled_transcripts)
    sessions_used = sum(1 for item in distilled_transcripts if len(item.messages) >= min_messages)
    return {
        "chunked": True,
        "session_count": len(distilled_transcripts),
        "sessions_total": len(distilled_transcripts),
        "sessions_used": sessions_used or len(distilled_transcripts),
        "sessions_dropped": max(0, len(distilled_transcripts) - (sessions_used or len(distilled_transcripts))),
        "min_messages": min_messages,
        "chunk_count": len(chunk_transcripts),
        "message_count": sum(len(item.messages) for item in distilled_transcripts),
        "user_messages": sum(item.user_messages for item in distilled_transcripts),
        "assistant_messages": sum(item.assistant_messages for item in distilled_transcripts),
        "compressed_assistant_messages": sum(item.compressed_assistant_messages for item in distilled_transcripts),
        "raw_units": raw_units,
        "distilled_units": distilled_units,
        "compression_ratio": round(distilled_units / raw_units, 3) if raw_units else 1.0,
        "original_tool_calls": sum(item.tool_calls for item in distilled_transcripts),
        "original_total_tokens": sum(item.token_usage.total_tokens for item in distilled_transcripts),
        "strategy": "保留用户 prompt 原文，AI 回复只做取头压缩；chunk 级不再伪造 tool_call 和 token 证据，只在总报告层回收原始统计。",
    }


def _compress_assistant_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"```[\s\S]*?```", " [代码块略] ", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r" \1 ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    sentences = [item.strip() for item in re.split(r"(?<=[。！？.!?])", cleaned) if item.strip()]
    if len(cleaned) <= 72 and len(sentences) <= 2:
        return cleaned
    if sentences:
        compressed = " ".join(sentences[:2]).strip()
    else:
        compressed = cleaned[:ASSISTANT_REPLY_MAX_CHARS]
    compressed = re.sub(r"\s+", " ", compressed).strip()
    if len(sentences) <= 2 and len(cleaned) <= ASSISTANT_REPLY_MAX_CHARS:
        return cleaned
    if len(compressed) > ASSISTANT_REPLY_MAX_CHARS:
        compressed = compressed[: ASSISTANT_REPLY_MAX_CHARS - 1].rstrip() + "…"
    return compressed


def _text_units(text: str) -> int:
    return max(1, len(text))


def _allocate_integer_budget(total: int, weights: list[int]) -> list[int]:
    if not weights:
        return []
    if total <= 0:
        return [0 for _ in weights]
    weight_sum = sum(weights)
    if weight_sum <= 0:
        base = total // len(weights)
        result = [base for _ in weights]
        for index in range(total - base * len(weights)):
            result[index] += 1
        return result
    raw = [total * weight / weight_sum for weight in weights]
    base = [int(value) for value in raw]
    remain = total - sum(base)
    order = sorted(range(len(weights)), key=lambda index: raw[index] - base[index], reverse=True)
    for index in order[:remain]:
        base[index] += 1
    return base


def _allocate_token_usage(token_usage: TokenUsage, weights: list[int]) -> list[TokenUsage]:
    allocated_inputs = _allocate_integer_budget(token_usage.input_tokens, weights)
    allocated_cached = _allocate_integer_budget(token_usage.cached_input_tokens, weights)
    allocated_output = _allocate_integer_budget(token_usage.output_tokens, weights)
    allocated_reasoning = _allocate_integer_budget(token_usage.reasoning_output_tokens, weights)
    allocated_total = _allocate_integer_budget(token_usage.total_tokens, weights)
    outputs: list[TokenUsage] = []
    for index in range(len(weights)):
        total_tokens = allocated_total[index]
        if not total_tokens:
            total_tokens = (
                allocated_inputs[index]
                + allocated_cached[index]
                + allocated_output[index]
                + allocated_reasoning[index]
            )
        outputs.append(
            TokenUsage(
                input_tokens=allocated_inputs[index],
                cached_input_tokens=allocated_cached[index],
                output_tokens=allocated_output[index],
                reasoning_output_tokens=allocated_reasoning[index],
                total_tokens=total_tokens,
            )
        )
    return outputs


def _sum_token_usage(items) -> TokenUsage:
    total = TokenUsage()
    for item in items:
        total.input_tokens += item.input_tokens
        total.cached_input_tokens += item.cached_input_tokens
        total.output_tokens += item.output_tokens
        total.reasoning_output_tokens += item.reasoning_output_tokens
        total.total_tokens += item.total_tokens
    return total


def _merge_unique(items) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return seen


def _rewrite_chunked_aggregate(aggregate: dict[str, object]) -> None:
    distillation = aggregate.get("distillation")
    if not isinstance(distillation, dict):
        return
    sessions_total = int(distillation.get("sessions_total", aggregate.get("sessions_total", 0)) or 0)
    sessions_used = int(distillation.get("sessions_used", aggregate.get("sessions_used", 0)) or 0)
    sessions_dropped = int(distillation.get("sessions_dropped", aggregate.get("sessions_dropped", 0)) or 0)
    min_messages = int(distillation.get("min_messages", aggregate.get("min_messages", 1)) or 1)
    total_messages = int(aggregate.get("total_messages", 0) or 0)
    total_tool_calls = int(aggregate.get("total_tool_calls", 0) or 0)
    total_tokens = int(_as_int((aggregate.get("token_usage") or {}).get("total_tokens")) or 0)

    overview = f"共纳入 {sessions_used} 场会话，累计 {total_messages} 条有效消息，工具调用 {total_tool_calls} 次。"
    if total_tokens:
        overview += f"累计消耗 {total_tokens} token。"
    if sessions_dropped:
        overview += f" 另有 {sessions_dropped} 场低样本会话因消息数低于 {min_messages} 被排除。"

    aggregate["overview"] = overview
    aggregate["sessions_total"] = sessions_total
    aggregate["sessions_used"] = sessions_used
    aggregate["sessions_dropped"] = sessions_dropped
    aggregate["min_messages"] = min_messages
    _rewrite_metric_rationales(aggregate.get("user_metrics"), sessions_total, int(distillation.get("chunk_count", 0) or 0))
    _rewrite_metric_rationales(aggregate.get("assistant_metrics"), sessions_total, int(distillation.get("chunk_count", 0) or 0))


def _as_int(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def _rewrite_metric_rationales(metrics: object, session_total: int, chunk_count: int) -> None:
    if not isinstance(metrics, list):
        return
    for metric in metrics:
        rationale = getattr(metric, "rationale", "")
        if not isinstance(rationale, str) or "高位聚合" not in rationale:
            continue
        match = re.search(r"中位数\s*(\d+).+高位分\s*(\d+)", rationale)
        if match:
            median_score = match.group(1)
            high_score = match.group(2)
            metric.rationale = f"基于 {session_total} 场会话拆出的 {chunk_count} 段局部报告高位聚合，中位数 {median_score}，高位分 {high_score}。"
        else:
            metric.rationale = f"基于 {session_total} 场会话拆出的 {chunk_count} 段局部报告高位聚合。"


def _group_turn_messages(messages: list[Message]) -> list[list[tuple[Message, int]]]:
    turns: list[list[tuple[Message, int]]] = []
    current: list[tuple[Message, int]] = []
    seen_user = False
    for message in messages:
        pair = (message, _text_units(message.text))
        if message.role == "user":
            if current:
                turns.append(current)
            current = [pair]
            seen_user = True
            continue
        if not current:
            current = [pair]
            continue
        if not seen_user and current and current[0][0].role != "user":
            turns.append(current)
            current = [pair]
            continue
        current.append(pair)
    if current:
        turns.append(current)
    return turns
