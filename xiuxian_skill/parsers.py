from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from .models import Message, TokenUsage, Transcript


DEFAULT_LOCATIONS = {
    "codex": [
        Path("~/.codex/archived_sessions").expanduser(),
        Path("~/.codex/sessions").expanduser(),
    ],
    "claude": [
        Path("~/.claude/projects").expanduser(),
    ],
    "opencode": [
        Path("~/.local/share/opencode").expanduser(),
        Path("~/Library/Application Support/opencode").expanduser(),
        Path("~/.config/opencode").expanduser(),
    ],
    "openclaw": [
        Path("~/.openclaw/agents/main/sessions").expanduser(),
        Path("~/.openclaw/agents").expanduser(),
    ],
    "cursor": [
        Path("~/Library/Application Support/Cursor/User/workspaceStorage").expanduser(),
        Path("~/Library/Application Support/Cursor/User/globalStorage").expanduser(),
        Path("~/.config/Cursor/User/workspaceStorage").expanduser(),
        Path("~/.config/Cursor/User/globalStorage").expanduser(),
    ],
    "vscode": [
        Path("~/Library/Application Support/Code/User/workspaceStorage").expanduser(),
        Path("~/Library/Application Support/Code - Insiders/User/workspaceStorage").expanduser(),
        Path("~/Library/Application Support/Code/User/globalStorage").expanduser(),
        Path("~/Library/Application Support/Code - Insiders/User/globalStorage").expanduser(),
        Path("~/.config/Code/User/workspaceStorage").expanduser(),
        Path("~/.config/Code - Insiders/User/workspaceStorage").expanduser(),
        Path("~/.config/VSCodium/User/workspaceStorage").expanduser(),
        Path("~/.config/Code/User/globalStorage").expanduser(),
        Path("~/.config/Code - Insiders/User/globalStorage").expanduser(),
        Path("~/.config/VSCodium/User/globalStorage").expanduser(),
    ],
}

SOURCE_ALIASES = {
    "cc": "claude",
    "code": "vscode",
    "oc": "openclaw",
}

SOURCE_EXTENSIONS = {
    "codex": {".jsonl"},
    "claude": {".json", ".jsonl", ".log"},
    "opencode": {".json", ".jsonl", ".log"},
    "openclaw": {".jsonl"},
    "cursor": {".json", ".jsonl"},
    "vscode": {".json", ".jsonl"},
}

OPENCODE_SESSION_PREFIX = "opencode://"

DISPLAY_NAME_PATTERNS = [
    re.compile(r"(?:我是|我叫|叫我|称呼我为)([A-Za-z0-9_\-\u4e00-\u9fff]{2,24})"),
    re.compile(r"(?:my name is|i am|i'm|call me)\s+([A-Za-z0-9_\-]{2,24})", re.IGNORECASE),
]


def discover_candidate_files(source: str) -> list[Path]:
    source = normalize_source(source)
    candidates: list[Path] = []
    if source == "opencode":
        return _discover_opencode_exports()
    for root in DEFAULT_LOCATIONS.get(source, []):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in SOURCE_EXTENSIONS.get(source, {".json", ".jsonl", ".log"}):
                continue
            if not _path_matches_source(path, source):
                continue
            candidates.append(path)
    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)


def load_transcript(path: str | Path, source: str = "auto") -> Transcript:
    source = normalize_source(source)
    if isinstance(path, str) and path.startswith(OPENCODE_SESSION_PREFIX):
        return parse_opencode_session(path[len(OPENCODE_SESSION_PREFIX) :])
    file_path = Path(path).expanduser().resolve()
    detected_source = detect_source(file_path, source)
    if detected_source == "codex":
        return parse_codex(file_path)
    if detected_source == "opencode" and file_path.name == "opencode.db":
        return parse_opencode_session(_latest_opencode_session_id(file_path), db_path=file_path)
    if detected_source == "opencode" and _looks_like_opencode_export(file_path):
        return parse_opencode_export(file_path)
    if detected_source in {"claude", "opencode", "openclaw", "cursor", "vscode"}:
        return parse_generic(file_path, detected_source)
    return parse_generic(file_path, "generic")


def infer_display_name(transcript: Transcript) -> str | None:
    if transcript.display_name:
        return transcript.display_name
    for message in transcript.messages[:12]:
        if message.role != "user":
            continue
        for pattern in DISPLAY_NAME_PATTERNS:
            match = pattern.search(message.text)
            if match:
                candidate = _clean_display_name(match.group(1))
                if candidate:
                    return candidate
    return None


def default_display_name(certificate_track: str = "user") -> str:
    return "道友" if certificate_track == "user" else "用户"


def detect_source(path: Path, source: str) -> str:
    source = normalize_source(source)
    if source != "auto":
        return source
    normalized = str(path).lower()
    if ".codex" in normalized:
        return "codex"
    if ".claude" in normalized:
        return "claude"
    if "opencode" in normalized:
        return "opencode"
    if ".openclaw" in normalized or "openclaw" in normalized:
        return "openclaw"
    if "cursor" in normalized and "workspacestorage" in normalized:
        return "cursor"
    if any(token in normalized for token in ["workspacestorage", "chatsessions"]) and any(
        token in normalized for token in ["application support/code", ".config/code", "vscodium", "code - insiders"]
    ):
        return "vscode"
    if path.suffix.lower() == ".jsonl":
        try:
            first = next(iter_jsonl(path))
        except StopIteration:
            return "generic"
        if first.get("type") == "session_meta" and isinstance(first.get("payload"), dict):
            return "codex"
    return "generic"


def parse_codex(path: Path) -> Transcript:
    messages: list[Message] = []
    tool_calls = 0
    raw_event_count = 0
    models: list[str] = []
    providers: list[str] = []
    token_usage = TokenUsage()
    for item in iter_jsonl(path):
        raw_event_count += 1
        event_type = item.get("type")
        payload = item.get("payload") or {}
        if event_type == "session_meta" and isinstance(payload, dict):
            if isinstance(payload.get("model_provider"), str):
                providers.append(payload["model_provider"])
            if isinstance(payload.get("model"), str):
                models.append(payload["model"])
        elif event_type == "turn_context" and isinstance(payload, dict):
            if isinstance(payload.get("model"), str):
                models.append(payload["model"])
        if event_type == "event_msg" and payload.get("type") == "user_message":
            text = payload.get("message") or _flatten_text(payload.get("text_elements"))
            if text:
                messages.append(
                    Message(
                        role="user",
                        text=text,
                        timestamp=item.get("timestamp"),
                        meta={"source_type": "user_message"},
                    )
                )
        elif event_type == "response_item" and payload.get("type") == "message":
            role = payload.get("role") or "assistant"
            text = _flatten_text(payload.get("content"))
            if text:
                messages.append(
                    Message(
                        role=role,
                        text=text,
                        timestamp=item.get("timestamp"),
                        meta={"source_type": "message"},
                    )
                )
        elif event_type == "response_item" and payload.get("type") in {"function_call", "custom_tool_call"}:
            tool_calls += 1
        elif event_type == "response_item" and payload.get("type") == "reasoning":
            continue
        elif event_type == "event_msg" and payload.get("type") == "token_count":
            token_usage = _merge_token_usage(token_usage, _token_usage_from_payload(payload))
    return Transcript(
        source="codex",
        path=path,
        messages=messages,
        tool_calls=tool_calls,
        raw_event_count=raw_event_count,
        models=sorted(set(models)),
        providers=sorted(set(providers)),
        token_usage=token_usage,
        display_name=_infer_display_name_from_messages(messages),
    )


def parse_generic(path: Path, source: str) -> Transcript:
    messages: list[Message] = []
    tool_calls = 0
    raw_event_count = 0
    models: list[str] = []
    providers: list[str] = []
    token_usage = TokenUsage()
    items = _load_data(path)

    if source in {"cursor", "vscode"}:
        turn_messages, turn_tools, turn_events = _extract_pair_turns(items)
        model_hits, provider_hits = _collect_models(items)
        if turn_messages:
            return Transcript(
                source=source,
                path=path,
                messages=turn_messages,
                tool_calls=turn_tools,
                raw_event_count=turn_events,
                models=sorted(set(model_hits)),
                providers=sorted(set(provider_hits)),
                token_usage=_collect_token_usage(items),
                display_name=_infer_display_name_from_messages(turn_messages),
            )

    for obj in _walk_objects(items):
        if not isinstance(obj, dict):
            continue
        raw_event_count += 1
        role = _extract_role(obj)
        text = _extract_text(obj)
        if role in {"user", "assistant"} and text:
            messages.append(
                Message(
                    role=role,
                    text=text,
                    timestamp=_extract_timestamp(obj),
                    meta={"keys": sorted(obj.keys())[:12]},
                )
            )
        if _looks_like_tool_call(obj):
            tool_calls += 1
        model_hits, provider_hits = _extract_model_info(obj)
        models.extend(model_hits)
        providers.extend(provider_hits)
        token_usage = _merge_token_usage(token_usage, _token_usage_from_any(obj))
    return Transcript(
        source=source,
        path=path,
        messages=messages,
        tool_calls=tool_calls,
        raw_event_count=raw_event_count,
        models=sorted(set(models)),
        providers=sorted(set(providers)),
        token_usage=token_usage,
        display_name=_infer_display_name_from_messages(messages),
    )


def parse_opencode_session(session_id: str, db_path: Path | None = None) -> Transcript:
    db_file = db_path or _resolve_opencode_db()
    with sqlite3.connect(f"file:{db_file}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        session_row = cursor.execute(
            "select id, directory, time_created from session where id = ?",
            (session_id,),
        ).fetchone()
        if not session_row:
            raise FileNotFoundError(f"OpenCode session not found: {session_id}")

        messages: list[Message] = []
        tool_calls = 0
        raw_event_count = 0
        models: list[str] = []
        providers: list[str] = []
        token_usage = TokenUsage()

        message_rows = cursor.execute(
            "select id, data, time_created from message where session_id = ? order by time_created asc, id asc",
            (session_id,),
        ).fetchall()

        for message_row in message_rows:
            raw_event_count += 1
            message_data = _safe_json_loads(message_row["data"])
            if not isinstance(message_data, dict):
                continue
            role = _extract_role(message_data)
            model_hits, provider_hits = _extract_model_info(message_data)
            models.extend(model_hits)
            providers.extend(provider_hits)
            token_usage = _merge_token_usage(token_usage, _token_usage_from_any(message_data))
            if _looks_like_tool_call(message_data):
                tool_calls += 1

            part_rows = cursor.execute(
                "select data, time_created, id from part where message_id = ? order by time_created asc, id asc",
                (message_row["id"],),
            ).fetchall()
            raw_event_count += len(part_rows)
            part_texts: list[str] = []
            for part_row in part_rows:
                part_data = _safe_json_loads(part_row["data"])
                if not isinstance(part_data, dict):
                    continue
                if part_data.get("type") == "text":
                    text = _flatten_text(part_data.get("text"))
                    if text:
                        part_texts.append(text)
                model_hits, provider_hits = _extract_model_info(part_data)
                models.extend(model_hits)
                providers.extend(provider_hits)
                token_usage = _merge_token_usage(token_usage, _token_usage_from_any(part_data))
                if _looks_like_tool_call(part_data):
                    tool_calls += 1

            text = "\n".join(part_texts).strip()
            if role in {"user", "assistant"} and text:
                messages.append(
                    Message(
                        role=role,
                        text=text,
                        timestamp=_ms_to_iso(message_data.get("time", {}).get("created") if isinstance(message_data.get("time"), dict) else message_row["time_created"]),
                        meta={"session_id": session_id, "source_type": "opencode_db"},
                    )
                )

    return Transcript(
        source="opencode",
        path=db_file,
        messages=messages,
        tool_calls=tool_calls,
        raw_event_count=raw_event_count,
        models=sorted(set(models)),
        providers=sorted(set(providers)),
        token_usage=token_usage,
        display_name=_infer_display_name_from_messages(messages),
    )


def parse_opencode_export(path: Path) -> Transcript:
    data = _load_data(path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid OpenCode export JSON: {path}")
    info = data.get("info")
    items = data.get("messages")
    if not isinstance(info, dict) or not isinstance(items, list):
        raise ValueError(f"Invalid OpenCode export structure: {path}")

    messages: list[Message] = []
    tool_calls = 0
    raw_event_count = 0
    models: list[str] = []
    providers: list[str] = []
    token_usage = TokenUsage()

    for item in items:
        if not isinstance(item, dict):
            continue
        raw_event_count += 1
        message_info = item.get("info")
        parts = item.get("parts")
        if not isinstance(message_info, dict) or not isinstance(parts, list):
            continue
        role = _extract_role(message_info)
        model_hits, provider_hits = _extract_model_info(message_info)
        models.extend(model_hits)
        providers.extend(provider_hits)
        token_usage = _merge_token_usage(token_usage, _token_usage_from_any(message_info))
        if _looks_like_tool_call(message_info):
            tool_calls += 1

        text_parts: list[str] = []
        for part in parts:
            if not isinstance(part, dict):
                continue
            raw_event_count += 1
            if part.get("type") == "text":
                text = _flatten_text(part.get("text"))
                if text:
                    text_parts.append(text)
            model_hits, provider_hits = _extract_model_info(part)
            models.extend(model_hits)
            providers.extend(provider_hits)
            token_usage = _merge_token_usage(token_usage, _token_usage_from_any(part))
            if _looks_like_tool_call(part):
                tool_calls += 1

        text = "\n".join(text_parts).strip()
        if role in {"user", "assistant"} and text:
            messages.append(
                Message(
                    role=role,
                    text=text,
                    timestamp=_ms_to_iso(message_info.get("time", {}).get("created") if isinstance(message_info.get("time"), dict) else None),
                    meta={"source_type": "opencode_export"},
                )
            )

    return Transcript(
        source="opencode",
        path=path,
        messages=messages,
        tool_calls=tool_calls,
        raw_event_count=raw_event_count,
        models=sorted(set(models)),
        providers=sorted(set(providers)),
        token_usage=token_usage,
    )


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _load_data(path: Path):
    if path.suffix.lower() == ".jsonl":
        return list(iter_jsonl(path))
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start >= 0:
            return json.loads(text[start:])
        raise


def _walk_objects(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_objects(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_objects(item)


def _extract_pair_turns(node) -> tuple[list[Message], int, int]:
    messages: list[Message] = []
    tool_calls = 0
    raw_event_count = 0
    for obj in _walk_objects(node):
        if not isinstance(obj, dict):
            continue
        requests = _extract_requests(obj)
        if not requests:
            continue
        for request in requests:
            raw_event_count += 1
            user_text = _extract_text(request if isinstance(request, dict) else {})
            if user_text:
                messages.append(Message(role="user", text=user_text, timestamp=_extract_timestamp(request or {})))

            response = request.get("response") if isinstance(request, dict) else None
            response_text = _flatten_text(response)
            if not response_text and isinstance(response, list):
                response_text = "\n".join(
                    part for part in (_flatten_text(item) for item in response) if part
                )
            if response_text:
                messages.append(Message(role="assistant", text=response_text, timestamp=_extract_timestamp(request or {})))

            if _looks_like_tool_call(request if isinstance(request, dict) else {}):
                tool_calls += 1
            if isinstance(response, list):
                tool_calls += sum(1 for item in response if isinstance(item, dict) and _looks_like_tool_call(item))
            elif isinstance(response, dict) and _looks_like_tool_call(response):
                tool_calls += 1
    return messages, tool_calls, raw_event_count


def _extract_requests(obj: dict[str, object]) -> list[dict[str, object]]:
    direct = obj.get("requests")
    if isinstance(direct, list):
        return [item for item in direct if isinstance(item, dict)]
    value = obj.get("v")
    if isinstance(value, dict):
        nested = value.get("requests")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
    return []


def _collect_models(node) -> tuple[list[str], list[str]]:
    models: list[str] = []
    providers: list[str] = []
    for obj in _walk_objects(node):
        if not isinstance(obj, dict):
            continue
        model_hits, provider_hits = _extract_model_info(obj)
        models.extend(model_hits)
        providers.extend(provider_hits)
    return models, providers


def _extract_model_info(obj: dict[str, object]) -> tuple[list[str], list[str]]:
    models: list[str] = []
    providers: list[str] = []
    for key in ("model", "modelName", "model_name", "modelId", "model_id", "modelID", "modelSlug"):
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            models.append(value.strip())
    for key in ("provider", "modelProvider", "providerName", "providerID"):
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            providers.append(value.strip())
    return models, providers


def _collect_token_usage(node) -> TokenUsage:
    usage = TokenUsage()
    for obj in _walk_objects(node):
        if not isinstance(obj, dict):
            continue
        usage = _merge_token_usage(usage, _token_usage_from_any(obj))
    return usage


def _token_usage_from_payload(payload: dict[str, object]) -> TokenUsage:
    info = payload.get("info")
    if not isinstance(info, dict):
        return TokenUsage()
    total = info.get("total_token_usage")
    if isinstance(total, dict):
        return _token_usage_from_mapping(total)
    last = info.get("last_token_usage")
    if isinstance(last, dict):
        return _token_usage_from_mapping(last)
    return TokenUsage()


def _token_usage_from_any(obj: dict[str, object]) -> TokenUsage:
    for key in ("total_token_usage", "last_token_usage", "usage", "token_usage", "tokens"):
        value = obj.get(key)
        if isinstance(value, dict):
            usage = _token_usage_from_mapping(value)
            if usage.total_tokens:
                return usage
    nested = obj.get("info")
    if isinstance(nested, dict):
        return _token_usage_from_payload({"info": nested})
    return TokenUsage()


def _token_usage_from_mapping(obj: dict[str, object]) -> TokenUsage:
    cache = obj.get("cache")
    cache_read = cache.get("read") if isinstance(cache, dict) else None
    if cache_read is None and isinstance(cache, dict):
        cache_read = cache.get("cacheRead")
    return TokenUsage(
        input_tokens=_to_int(obj.get("input_tokens") if obj.get("input_tokens") is not None else obj.get("input")),
        cached_input_tokens=_to_int(
            obj.get("cached_input_tokens")
            if obj.get("cached_input_tokens") is not None
            else (obj.get("cacheRead") if obj.get("cacheRead") is not None else cache_read)
        ),
        output_tokens=_to_int(obj.get("output_tokens") if obj.get("output_tokens") is not None else obj.get("output")),
        reasoning_output_tokens=_to_int(obj.get("reasoning_output_tokens") if obj.get("reasoning_output_tokens") is not None else obj.get("reasoning")),
        total_tokens=_to_int(
            obj.get("total_tokens")
            if obj.get("total_tokens") is not None
            else (obj.get("totalTokens") if obj.get("totalTokens") is not None else obj.get("total"))
        ),
    )


def _merge_token_usage(current: TokenUsage, candidate: TokenUsage) -> TokenUsage:
    return TokenUsage(
        input_tokens=max(current.input_tokens, candidate.input_tokens),
        cached_input_tokens=max(current.cached_input_tokens, candidate.cached_input_tokens),
        output_tokens=max(current.output_tokens, candidate.output_tokens),
        reasoning_output_tokens=max(current.reasoning_output_tokens, candidate.reasoning_output_tokens),
        total_tokens=max(current.total_tokens, candidate.total_tokens),
    )


def _to_int(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _extract_role(obj: dict[str, object]) -> str | None:
    for key in ("role", "speaker", "sender", "author"):
        value = obj.get(key)
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in {"user", "human"}:
                return "user"
            if lowered in {"assistant", "ai", "model"}:
                return "assistant"
    if obj.get("type") == "user_message":
        return "user"
    message = obj.get("message")
    if isinstance(message, dict):
        return _extract_role(message)
    return None


def _extract_timestamp(obj: dict[str, object]) -> str | None:
    for key in ("timestamp", "created_at", "time", "ts"):
        value = obj.get(key)
        if isinstance(value, str):
            return value
    return None


def _extract_text(obj: dict[str, object]) -> str:
    for key in ("text", "message", "content", "prompt", "response", "summary"):
        if key not in obj:
            continue
        text = _flatten_text(obj[key])
        if text:
            return text
    return ""


def _flatten_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, list):
        parts = [_flatten_text(item) for item in value]
        parts = [item for item in parts if item]
        return "\n".join(parts)
    if isinstance(value, dict):
        for key in ("text", "value", "messageText", "query", "inputText"):
            if isinstance(value.get(key), str):
                return _flatten_text(value[key])
        if isinstance(value.get("text"), str):
            return _flatten_text(value["text"])
        if isinstance(value.get("message"), str):
            return _flatten_text(value["message"])
        if "content" in value:
            return _flatten_text(value["content"])
        if "message" in value and isinstance(value.get("message"), dict):
            return _flatten_text(value["message"])
        if "response" in value:
            return _flatten_text(value["response"])
        if isinstance(value.get("summary"), list):
            return _flatten_text(value["summary"])
        if isinstance(value.get("parts"), list):
            return _flatten_text(value["parts"])
        if isinstance(value.get("value"), list):
            return _flatten_text(value["value"])
        if isinstance(value.get("markdown"), str):
            return _flatten_text(value["markdown"])
        if isinstance(value.get("body"), list):
            return _flatten_text(value["body"])
    return ""


def _looks_like_tool_call(obj: dict[str, object]) -> bool:
    call_type = str(obj.get("type", "")).lower()
    if "tool" in call_type or "function_call" in call_type:
        return True
    if isinstance(obj.get("name"), str) and isinstance(obj.get("arguments"), (str, dict)):
        return True
    return False


def latest_transcript(source: str) -> Path:
    source = normalize_source(source)
    if source == "opencode":
        return _resolve_opencode_db()
    candidates = discover_candidate_files(source)
    if not candidates:
        locations = ", ".join(str(item) for item in DEFAULT_LOCATIONS.get(source, []))
        raise FileNotFoundError(f"No {source} transcript found. Checked: {locations}")
    return candidates[0]


def summarize_locations() -> list[tuple[str, list[str]]]:
    return [(name, [os.fspath(path) for path in paths]) for name, paths in DEFAULT_LOCATIONS.items()]


def session_datetime(path: Path, source: str = "auto") -> datetime:
    source = normalize_source(source if source != "auto" else detect_source(path, source))
    if source == "codex":
        match = re.search(r"rollout-(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-(\d{2})", path.name)
        if match:
            date_part, hour, minute, second = match.groups()
            return datetime.fromisoformat(f"{date_part}T{hour}:{minute}:{second}")
        parts = path.parts
        try:
            idx = parts.index("sessions")
            year, month, day = parts[idx + 1 : idx + 4]
            return datetime(int(year), int(month), int(day))
        except (ValueError, IndexError):
            pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def filter_candidate_files(
    source: str,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int | None = None,
) -> list[Path]:
    source = normalize_source(source)
    if source == "opencode":
        return _discover_opencode_exports(since=since, until=until, limit=limit)
    files = discover_candidate_files(source)
    selected: list[Path] = []
    for path in files:
        stamp = session_datetime(path, source)
        if since and stamp < since:
            continue
        if until and stamp > until:
            continue
        selected.append(path)
        if limit and len(selected) >= limit:
            break
    return selected


def parse_date_bound(value: str | None, is_end: bool = False) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    if len(value) == 10 and is_end:
        dt = dt + timedelta(days=1) - timedelta(microseconds=1)
    return dt


def normalize_source(source: str) -> str:
    return SOURCE_ALIASES.get(source, source)


def redact_path(path: Path) -> str:
    try:
        home = Path.home().resolve()
        resolved = path.resolve()
        resolved_str = resolved.as_posix()
        home_str = home.as_posix()
        if resolved_str.startswith(home_str):
            return resolved_str.replace(home_str, "~", 1)
        return f".../{resolved.name}"
    except OSError:
        return path.name if path.name else str(path)


def _path_matches_source(path: Path, source: str) -> bool:
    normalized = str(path).lower()
    if source in {"cursor", "vscode"}:
        return "chatsessions" in normalized
    if source == "openclaw":
        return normalized.endswith(".jsonl") and "/sessions/" in normalized
    return True


def _looks_like_opencode_export(path: Path) -> bool:
    if path.suffix.lower() != ".json":
        return False
    try:
        data = _load_data(path)
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(data, dict) and isinstance(data.get("info"), dict) and isinstance(data.get("messages"), list)


def list_opencode_session_refs(
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int | None = None,
) -> list[str]:
    db_file = _resolve_opencode_db()
    clauses = []
    params: list[object] = []
    if since:
        clauses.append("time_created >= ?")
        params.append(int(since.timestamp() * 1000))
    if until:
        clauses.append("time_created <= ?")
        params.append(int(until.timestamp() * 1000))
    where = f"where {' and '.join(clauses)}" if clauses else ""
    sql = f"select id from session {where} order by time_created desc"
    if limit:
        sql += " limit ?"
        params.append(limit)
    with sqlite3.connect(f"file:{db_file}?mode=ro", uri=True) as connection:
        rows = connection.execute(sql, params).fetchall()
    return [f"{OPENCODE_SESSION_PREFIX}{row[0]}" for row in rows]


def latest_opencode_session_ref() -> str:
    return f"{OPENCODE_SESSION_PREFIX}{_latest_opencode_session_id(_resolve_opencode_db())}"


def _discover_opencode_exports(
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int | None = None,
) -> list[Path]:
    candidates: list[Path] = []
    for root in DEFAULT_LOCATIONS.get("opencode", []):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in SOURCE_EXTENSIONS["opencode"]:
                continue
            candidates.append(path)
    candidates = sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)
    selected: list[Path] = []
    for path in candidates:
        stamp = session_datetime(path, "opencode")
        if since and stamp < since:
            continue
        if until and stamp > until:
            continue
        selected.append(path)
        if limit and len(selected) >= limit:
            break
    return selected


def _resolve_opencode_db() -> Path:
    for root in DEFAULT_LOCATIONS.get("opencode", []):
        candidate = root / "opencode.db"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No OpenCode database found. Checked ~/.local/share/opencode, ~/Library/Application Support/opencode, ~/.config/opencode")


def _latest_opencode_session_id(db_path: Path) -> str:
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as connection:
        row = connection.execute("select id from session order by time_created desc limit 1").fetchone()
    if not row:
        raise FileNotFoundError(f"No OpenCode session found in {db_path}")
    return str(row[0])


def _safe_json_loads(value: object) -> dict[str, object] | None:
    if not isinstance(value, str):
        return None
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _ms_to_iso(value: object) -> str | None:
    milliseconds = _to_int(value)
    if not milliseconds:
        return None
    return datetime.fromtimestamp(milliseconds / 1000).isoformat()


def _infer_display_name_from_messages(messages: list[Message]) -> str | None:
    transcript = Transcript(source="inference", path=Path("."), messages=messages)
    return infer_display_name(transcript)


def _clean_display_name(value: str) -> str | None:
    candidate = value.strip(" \t\r\n，。,:：\"'`()[]{}<>")
    if len(candidate) < 2 or len(candidate) > 24:
        return None
    blacklist = {"ai", "agent", "codex", "claude", "opencode", "openclaw", "cursor", "vscode"}
    if candidate.lower() in blacklist:
        return None
    return candidate
