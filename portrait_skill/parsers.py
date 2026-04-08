from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Message, Transcript


DEFAULT_LOCATIONS = {
    "codex": [
        Path("~/.codex/archived_sessions").expanduser(),
        Path("~/.codex/sessions").expanduser(),
    ],
    "claude": [
        Path("~/.claude/projects").expanduser(),
    ],
    "opencode": [
        Path("~/.local/share/opencode/project").expanduser(),
        Path("~/Library/Application Support/opencode/project").expanduser(),
        Path("~/.config/opencode").expanduser(),
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
}

SOURCE_EXTENSIONS = {
    "codex": {".jsonl"},
    "claude": {".json", ".jsonl", ".log"},
    "opencode": {".json", ".jsonl", ".log"},
    "cursor": {".json", ".jsonl"},
    "vscode": {".json", ".jsonl"},
}


def discover_candidate_files(source: str) -> list[Path]:
    source = normalize_source(source)
    candidates: list[Path] = []
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
    file_path = Path(path).expanduser().resolve()
    detected_source = detect_source(file_path, source)
    if detected_source == "codex":
        return parse_codex(file_path)
    if detected_source in {"claude", "opencode", "cursor", "vscode"}:
        return parse_generic(file_path, detected_source)
    return parse_generic(file_path, "generic")


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
    return Transcript(
        source="codex",
        path=path,
        messages=messages,
        tool_calls=tool_calls,
        raw_event_count=raw_event_count,
        models=sorted(set(models)),
        providers=sorted(set(providers)),
    )


def parse_generic(path: Path, source: str) -> Transcript:
    messages: list[Message] = []
    tool_calls = 0
    raw_event_count = 0
    models: list[str] = []
    providers: list[str] = []
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
    return Transcript(
        source=source,
        path=path,
        messages=messages,
        tool_calls=tool_calls,
        raw_event_count=raw_event_count,
        models=sorted(set(models)),
        providers=sorted(set(providers)),
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
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
    for key in ("model", "modelName", "model_name", "modelId", "model_id", "modelSlug"):
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            models.append(value.strip())
    for key in ("provider", "modelProvider", "providerName"):
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            providers.append(value.strip())
    return models, providers


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
    candidates = discover_candidate_files(source)
    if not candidates:
        locations = ", ".join(str(item) for item in DEFAULT_LOCATIONS.get(source, []))
        raise FileNotFoundError(f"No {source} transcript found. Checked: {locations}")
    return candidates[0]


def summarize_locations() -> list[tuple[str, list[str]]]:
    return [(name, [os.fspath(path) for path in paths]) for name, paths in DEFAULT_LOCATIONS.items()]


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
    return True
