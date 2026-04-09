from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from .analyzer import aggregate_analyses, analyze_transcript, compare_analyses
from .cards import write_cards
from .memory import build_memory_summary, build_snapshot, load_previous_snapshot
from .themes import get_ai_level_theme
from .xianxia import derive_xianxia_profile
from .parsers import (
    default_display_name,
    filter_candidate_files,
    infer_display_name,
    latest_transcript,
    latest_opencode_session_ref,
    list_opencode_session_refs,
    load_transcript,
    normalize_source,
    parse_date_bound,
    redact_path,
    summarize_locations,
)
from .renderer import render_aggregate_markdown, render_comparison_markdown, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portrait-skill",
        description="Issue cultivation portraits and AI capability portraits from agent transcripts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Show default transcript locations and latest detected files.")
    scan.add_argument("--source", choices=["codex", "claude", "cc", "opencode", "openclaw", "oc", "cursor", "vscode", "code", "all"], default="all")

    analyze = subparsers.add_parser("analyze", help="Analyze a transcript and print a markdown certificate.")
    analyze.add_argument("--path", help="Transcript path. If omitted, use the latest file for --source.")
    analyze.add_argument("--source", choices=["auto", "codex", "claude", "cc", "opencode", "openclaw", "oc", "cursor", "vscode", "code"], default="auto")
    analyze.add_argument("--certificate", choices=["user", "assistant", "both"], default="both")
    analyze.add_argument("--username", help="Display name for the report and cards. If omitted, try to infer from transcript content.")
    analyze.add_argument("--all", action="store_true", help="Aggregate all detected sessions for the source.")
    analyze.add_argument("--since", help="Only include sessions on/after this date or datetime. Example: 2026-04-01")
    analyze.add_argument("--until", help="Only include sessions on/before this date or datetime. Example: 2026-04-09")
    analyze.add_argument("--limit", type=int, help="Cap the number of sessions after filtering.")
    analyze.add_argument("--min-messages", type=int, default=8, help="Exclude tiny sessions below this message count in aggregate mode.")
    analyze.add_argument("--memory-key", help="Custom memory group key. Reuse it across cycles to compare with the previous evaluation.")
    analyze.add_argument("--no-memory", action="store_true", help="Do not read or write local evaluation memory.")
    analyze.add_argument("--output", help="Write markdown report to a file.")
    analyze.add_argument("--json-output", help="Write structured JSON summary to a file.")
    analyze.add_argument("--card-dir", help="Write shareable SVG cards to this directory.")

    compare = subparsers.add_parser("compare", help="Compare two transcripts and judge whether the user or AI broke through.")
    compare.add_argument("--before", required=True, help="Previous-cycle transcript path.")
    compare.add_argument("--after", help="Current-cycle transcript path. If omitted, use latest file for --source.")
    compare.add_argument("--source", choices=["auto", "codex", "claude", "cc", "opencode", "openclaw", "oc", "cursor", "vscode", "code"], default="auto")
    compare.add_argument("--certificate", choices=["user", "assistant", "both"], default="both")
    compare.add_argument("--username", help="Display name for the comparison report.")
    compare.add_argument("--output", help="Write markdown comparison report to a file.")
    compare.add_argument("--json-output", help="Write structured comparison JSON to a file.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        _handle_scan(args.source)
        return

    if args.command == "compare":
        _handle_compare(args)
        return

    generated_at = _generated_at()
    source = normalize_source(args.source)
    if args.path:
        transcript = load_transcript(args.path, source=source)
        _apply_display_name(transcript, args.username, track=args.certificate)
        analysis = analyze_transcript(transcript)
        payload = _to_json(analysis)
        scope_kind = "path"
        scope_label = f"{source}:单次记录"
    elif args.all or args.since or args.until or args.limit:
        if source == "auto":
            source = "codex"
        since = parse_date_bound(args.since)
        until = parse_date_bound(args.until, is_end=True)
        refs = _list_transcript_refs(source, since=since, until=until, limit=args.limit)
        if not refs:
            raise SystemExit("No sessions matched the requested source/time window.")
        analyses = [analyze_transcript(load_transcript(ref, source=source)) for ref in refs]
        for analysis in analyses:
            _apply_display_name(analysis.transcript, args.username, track=args.certificate)
        aggregate = aggregate_analyses(analyses, min_messages=args.min_messages)
        aggregate["display_name"] = _resolve_display_name_from_analyses(analyses, override=args.username, track=args.certificate)
        aggregate["time_window"] = {
            "since": args.since,
            "until": args.until,
            "latest_session": _display_ref(refs[0]),
            "oldest_session": _display_ref(refs[-1]),
        }
        payload = aggregate
        scope_kind = "window" if args.since or args.until else "aggregate"
        scope_label = _scope_label(source, scope_kind, args)
    else:
        if source == "auto":
            source = "codex"
        transcript = load_transcript(_latest_ref(source), source=source)
        _apply_display_name(transcript, args.username, track=args.certificate)
        analysis = analyze_transcript(transcript)
        payload = _to_json(analysis)
        scope_kind = "latest"
        scope_label = f"{source}:最近一次"

    payload["generated_at"] = generated_at
    payload["xianxia_profile"] = derive_xianxia_profile(payload)
    snapshot_source = _payload_source(payload, fallback=source)
    scope_label = scope_label.replace(f"{source}:", f"{snapshot_source}:")

    memory_summary = None
    if not args.no_memory:
        memory_key = args.memory_key or f"{snapshot_source}:{scope_kind}"
        snapshot = build_snapshot(
            payload,
            source=snapshot_source,
            scope_kind=scope_kind,
            scope_label=scope_label,
            memory_key=memory_key,
        )
        previous = load_previous_snapshot(snapshot)
        memory_summary = build_memory_summary(previous, snapshot)
        payload["memory"] = memory_summary

    if args.path or (not args.all and not args.since and not args.until and not args.limit):
        markdown = render_markdown(
            analysis,
            certificate_choice=args.certificate,
            memory_summary=memory_summary,
            generated_at=generated_at,
        )
    else:
        markdown = render_aggregate_markdown(
            aggregate,
            certificate_choice=args.certificate,
            memory_summary=memory_summary,
            generated_at=generated_at,
        )

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)

    if args.card_dir:
        payload["cards"] = write_cards(payload, args.card_dir, certificate_choice=args.certificate)

    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _handle_compare(args) -> None:
    generated_at = _generated_at()
    source = normalize_source(args.source)
    before_transcript = load_transcript(args.before, source=source)
    _apply_display_name(before_transcript, args.username, track=args.certificate)
    before = analyze_transcript(before_transcript)
    if args.after:
        after_transcript = load_transcript(args.after, source=source)
        _apply_display_name(after_transcript, args.username, track=args.certificate)
        after = analyze_transcript(after_transcript)
    else:
        if source == "auto":
            source = "codex"
        after_transcript = load_transcript(_latest_ref(source), source=source)
        _apply_display_name(after_transcript, args.username, track=args.certificate)
        after = analyze_transcript(after_transcript)

    comparison = compare_analyses(before, after)
    comparison["display_name"] = after.transcript.display_name or before.transcript.display_name
    comparison["generated_at"] = generated_at
    markdown = render_comparison_markdown(comparison, certificate_choice=args.certificate, generated_at=generated_at)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)

    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")


def _handle_scan(source: str) -> None:
    for name, locations in summarize_locations():
        if source != "all" and source != name:
            continue
        print(f"[{name}]")
        for location in locations:
            print(f"- default: {location}")
        try:
            latest = _latest_ref(name)
            print(f"- latest: {latest}")
        except FileNotFoundError as exc:
            print(f"- latest: not found ({exc})")


def _to_json(analysis):
    return {
        "overview": analysis.overview,
        "transcript": {
            "source": analysis.transcript.source,
            "path": redact_path(analysis.transcript.path),
            "message_count": len(analysis.transcript.messages),
            "tool_calls": analysis.transcript.tool_calls,
            "models": analysis.transcript.models,
            "providers": analysis.transcript.providers,
            "display_name": analysis.transcript.display_name,
            "token_usage": {
                "input_tokens": analysis.transcript.token_usage.input_tokens,
                "cached_input_tokens": analysis.transcript.token_usage.cached_input_tokens,
                "output_tokens": analysis.transcript.token_usage.output_tokens,
                "reasoning_output_tokens": analysis.transcript.token_usage.reasoning_output_tokens,
                "total_tokens": analysis.transcript.token_usage.total_tokens,
            },
        },
        "user_metrics": [{"name": item.name, "score": item.score, "rationale": item.rationale} for item in analysis.user_metrics],
        "assistant_metrics": [{"name": item.name, "score": item.score, "rationale": item.rationale} for item in analysis.assistant_metrics],
        "user_certificate": _certificate_to_json(analysis.user_certificate),
        "assistant_certificate": _certificate_to_json(analysis.assistant_certificate),
    }


def _certificate_to_json(certificate):
    payload = {
        "track": certificate.track,
        "title": certificate.title,
        "level": certificate.level,
        "score": certificate.score,
        "persona": {
            "title": certificate.persona.title,
            "subtitle": certificate.persona.subtitle,
            "tags": certificate.persona.tags,
            "summary": certificate.persona.summary,
        },
        "evidence": certificate.evidence,
        "growth_plan": certificate.growth_plan,
    }
    if certificate.track == "assistant":
        payload["theme"] = get_ai_level_theme(certificate.level)
    return payload


def _latest_ref(source: str):
    source = normalize_source(source)
    if source == "opencode":
        return latest_opencode_session_ref()
    return latest_transcript(source)


def _list_transcript_refs(
    source: str,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int | None = None,
):
    source = normalize_source(source)
    if source == "opencode":
        return list_opencode_session_refs(since=since, until=until, limit=limit)
    return filter_candidate_files(source, since=since, until=until, limit=limit)


def _display_ref(ref) -> str:
    if isinstance(ref, Path):
        return redact_path(ref)
    return str(ref)


def _scope_label(source: str, scope_kind: str, args) -> str:
    if scope_kind == "window":
        since = args.since or "最早"
        until = args.until or "现在"
        return f"{source}:{since}~{until}"
    if scope_kind == "aggregate":
        return f"{source}:全量会话"
    if scope_kind == "latest":
        return f"{source}:最近一次"
    return f"{source}:单次记录"


def _payload_source(payload: dict[str, object], fallback: str) -> str:
    transcript = payload.get("transcript", {})
    if isinstance(transcript, dict):
        source = transcript.get("source")
        if isinstance(source, str) and source:
            return source
    return fallback


def _apply_display_name(transcript, override: str | None, track: str) -> None:
    transcript.display_name = override or infer_display_name(transcript) or default_display_name("user" if track != "assistant" else "assistant")


def _resolve_display_name_from_analyses(analyses, override: str | None, track: str) -> str:
    if override:
        return override
    for analysis in analyses:
        if analysis.transcript.display_name:
            return str(analysis.transcript.display_name)
    return default_display_name("user" if track != "assistant" else "assistant")


def _generated_at() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")


if __name__ == "__main__":
    main()
