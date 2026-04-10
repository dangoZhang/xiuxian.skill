from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from .analyzer import level_rank


def load_previous_snapshot(snapshot: dict[str, object], max_entries: int = 200) -> dict[str, object] | None:
    store = _read_store()
    history = store.get("evaluations", [])
    previous = _find_previous(history, snapshot)
    history.append(snapshot)
    if len(history) > max_entries:
        history = history[-max_entries:]
    store["evaluations"] = history
    _write_store(store)
    return previous


def build_memory_summary(previous: dict[str, object] | None, current: dict[str, object]) -> dict[str, object]:
    if not previous:
        return {
            "has_previous": False,
            "memory_key": current["memory_key"],
            "message": "已记住本次评测。下次再测时，会自动显示变化与突破。",
        }
    return {
        "has_previous": True,
        "memory_key": current["memory_key"],
        "previous_at": previous.get("created_at"),
        "scope_label": current.get("scope_label"),
        "user": _build_track_summary("user", previous["user_certificate"], current["user_certificate"]),
        "assistant": _build_track_summary("assistant", previous["assistant_certificate"], current["assistant_certificate"]),
    }


def build_snapshot(
    payload: dict[str, object],
    *,
    source: str,
    scope_kind: str,
    scope_label: str,
    memory_key: str,
) -> dict[str, object]:
    transcript = payload.get("transcript", {})
    time_window = payload.get("time_window", {})
    return {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": source,
        "scope_kind": scope_kind,
        "scope_label": scope_label,
        "memory_key": memory_key,
        "overview": payload.get("overview", ""),
        "transcript": {
            "path": transcript.get("path") or time_window.get("latest_session") or "",
            "message_count": transcript.get("message_count", payload.get("sessions_used", 0)),
            "tool_calls": transcript.get("tool_calls", 0),
            "total_tokens": _token_total(payload),
        },
        "user_certificate": payload["user_certificate"],
        "assistant_certificate": payload["assistant_certificate"],
    }


def memory_store_path() -> Path:
    override = os.getenv("XIUXIAN_SKILL_HOME")
    if override:
        return Path(override).expanduser().resolve() / "history.json"
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "xiuxian-skill"
    elif os.name == "nt":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / "xiuxian-skill"
    else:
        xdg = os.getenv("XDG_DATA_HOME")
        base = Path(xdg).expanduser() / "xiuxian-skill" if xdg else Path.home() / ".local" / "share" / "xiuxian-skill"
    return base / "history.json"


def _build_track_summary(track: str, previous: dict[str, object], current: dict[str, object]) -> dict[str, object]:
    before_level = str(previous["level"])
    after_level = str(current["level"])
    before_score = int(previous["score"])
    after_score = int(current["score"])
    before_rank = level_rank(track, before_level)
    after_rank = level_rank(track, after_level)
    score_delta = after_score - before_score
    if after_rank > before_rank:
        outcome = "破境成功" if track == "user" else "等级提升"
    elif after_rank == before_rank and score_delta > 0:
        outcome = "境界未变，功力上涨" if track == "user" else "等级未变，能力上涨"
    elif score_delta == 0:
        outcome = "与上次持平"
    else:
        outcome = "本轮未突破" if track == "user" else "本轮未升级"
    return {
        "before_level": before_level,
        "after_level": after_level,
        "before_score": before_score,
        "after_score": after_score,
        "score_delta": score_delta,
        "outcome": outcome,
    }


def _find_previous(history: list[dict[str, object]], snapshot: dict[str, object]) -> dict[str, object] | None:
    current_key = snapshot["memory_key"]
    for item in reversed(history):
        if item.get("memory_key") == current_key:
            return item
    return None


def _read_store() -> dict[str, object]:
    path = memory_store_path()
    if not path.exists():
        return {"evaluations": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"evaluations": []}


def _write_store(store: dict[str, object]) -> None:
    path = memory_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def _token_total(payload: dict[str, object]) -> int:
    token_usage = payload.get("token_usage")
    if isinstance(token_usage, dict):
        return int(token_usage.get("total_tokens", 0))
    transcript = payload.get("transcript", {})
    if isinstance(transcript, dict):
        usage = transcript.get("token_usage", {})
        if isinstance(usage, dict):
            return int(usage.get("total_tokens", 0))
    return 0
