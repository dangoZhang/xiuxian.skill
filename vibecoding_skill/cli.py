from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

from .analyzer import aggregate_analyses, analyze_transcript, compare_analyses
from .cards import card_render_environment, write_cards
from .distill import analyze_many_with_chunking, analyze_with_chunking
from .exporter import export_bundle
from .insights import build_aggregate_insights, build_analysis_insights
from .memory import build_memory_summary, build_snapshot, load_previous_snapshot
from .terms import refresh_term_catalog
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
from .renderer import render_aggregate_markdown, render_coaching_markdown, render_comparison_markdown, render_markdown
from .secondary_skill import build_secondary_skill_distillation, render_secondary_skill_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vibecoding-skill",
        description="Read code-agent transcripts, distill vibecoding ability, and issue a concise ability report.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Show default transcript locations and latest detected files.")
    scan.add_argument("--source", choices=["codex", "claude", "cc", "opencode", "openclaw", "oc", "cursor", "vscode", "code", "all"], default="all")

    analyze = subparsers.add_parser("analyze", help="Analyze transcripts and print a vibecoding report.")
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
    analyze.add_argument("--memory", dest="memory_enabled", action="store_true", help="Read and write local evaluation memory. Off by default for one-off runs.")
    analyze.add_argument("--no-memory", dest="memory_enabled", action="store_false", help=argparse.SUPPRESS)
    analyze.set_defaults(memory_enabled=False)
    analyze.add_argument("--target-level", choices=[f"L{i}" for i in range(1, 11)], help="Optional target vibecoding level for upgrade coaching.")
    analyze.add_argument("--output", help="Write markdown report to a file.")
    analyze.add_argument("--json-output", help="Write structured JSON summary to a file.")
    analyze.add_argument("--card-dir", help="Write shareable SVG cards to this directory.")
    analyze.add_argument("--card-style", choices=["auto", "default", "xianxia"], default="auto", help="Card style. Auto switches to xianxia when the transcript clearly asks for 修仙 / 境界.")
    analyze.add_argument("--refresh-terms", action="store_true", help="Refresh the latest agent terminology input from official docs before analysis.")
    analyze.add_argument("--terms-dir", default="docs", help="Directory for refreshed terminology files.")

    export = subparsers.add_parser("export", help="Export a shareable vibecoding bundle, including a reusable skill package.")
    export.add_argument("--path", help="Transcript path. If omitted, use the latest file for --source.")
    export.add_argument("--source", choices=["auto", "codex", "claude", "cc", "opencode", "openclaw", "oc", "cursor", "vscode", "code"], default="auto")
    export.add_argument("--certificate", choices=["user", "assistant", "both"], default="both")
    export.add_argument("--username", help="Display name for the export bundle.")
    export.add_argument("--all", action="store_true", help="Aggregate all detected sessions for the source.")
    export.add_argument("--since", help="Only include sessions on/after this date or datetime. Example: 2026-04-01")
    export.add_argument("--until", help="Only include sessions on/before this date or datetime. Example: 2026-04-09")
    export.add_argument("--limit", type=int, help="Cap the number of sessions after filtering.")
    export.add_argument("--min-messages", type=int, default=8, help="Exclude tiny sessions below this message count in aggregate mode.")
    export.add_argument("--memory-key", help="Custom memory group key. Reuse it across cycles to compare with the previous evaluation.")
    export.add_argument("--memory", dest="memory_enabled", action="store_true", help="Read and write local evaluation memory. Off by default for one-off runs.")
    export.add_argument("--no-memory", dest="memory_enabled", action="store_false", help=argparse.SUPPRESS)
    export.set_defaults(memory_enabled=False)
    export.add_argument("--target-level", choices=[f"L{i}" for i in range(1, 11)], help="Optional target vibecoding level for upgrade coaching.")
    export.add_argument("--card-style", choices=["auto", "default", "xianxia"], default="auto", help="Card style. Auto switches to xianxia when the transcript clearly asks for 修仙 / 境界.")
    export.add_argument("--export-dir", required=True, help="Directory to write the shareable skill bundle into.")
    export.add_argument("--slug", help="Optional exported skill slug.")
    export.add_argument("--zip", action="store_true", help="Also create a zip archive next to the export directory.")
    export.add_argument("--refresh-terms", action="store_true", help="Refresh the latest agent terminology input from official docs before export.")
    export.add_argument("--terms-dir", default="docs", help="Directory for refreshed terminology files.")

    compare = subparsers.add_parser("compare", help="Compare two transcript windows and summarize the upgrade path.")
    compare.add_argument("--before", required=True, help="Previous-cycle transcript path.")
    compare.add_argument("--after", help="Current-cycle transcript path. If omitted, use latest file for --source.")
    compare.add_argument("--source", choices=["auto", "codex", "claude", "cc", "opencode", "openclaw", "oc", "cursor", "vscode", "code"], default="auto")
    compare.add_argument("--certificate", choices=["user", "assistant", "both"], default="both")
    compare.add_argument("--username", help="Display name for the comparison report.")
    compare.add_argument("--output", help="Write markdown comparison report to a file.")
    compare.add_argument("--json-output", help="Write structured comparison JSON to a file.")

    coach = subparsers.add_parser("coach", help="Generate a focused breakthrough coaching plan from transcripts.")
    coach.add_argument("--path", help="Transcript path. If omitted, use the latest file for --source.")
    coach.add_argument("--source", choices=["auto", "codex", "claude", "cc", "opencode", "openclaw", "oc", "cursor", "vscode", "code"], default="auto")
    coach.add_argument("--username", help="Display name for the coaching output.")
    coach.add_argument("--all", action="store_true", help="Aggregate all detected sessions for the source.")
    coach.add_argument("--since", help="Only include sessions on/after this date or datetime. Example: 2026-04-01")
    coach.add_argument("--until", help="Only include sessions on/before this date or datetime. Example: 2026-04-09")
    coach.add_argument("--limit", type=int, help="Cap the number of sessions after filtering.")
    coach.add_argument("--min-messages", type=int, default=8, help="Exclude tiny sessions below this message count in aggregate mode.")
    coach.add_argument("--target-level", choices=[f"L{i}" for i in range(1, 11)], help="Target vibecoding level to coach toward.")
    coach.add_argument("--output", help="Write markdown coaching plan to a file.")
    coach.add_argument("--json-output", help="Write structured coaching JSON to a file.")
    coach.add_argument("--refresh-terms", action="store_true", help="Refresh the latest agent terminology input from official docs before coaching.")
    coach.add_argument("--terms-dir", default="docs", help="Directory for refreshed terminology files.")

    distill_skill = subparsers.add_parser("distill-skill", help="Distill a secondary reusable skill profile from transcripts.")
    distill_skill.add_argument("--path", help="Transcript path. If omitted, use the latest file for --source.")
    distill_skill.add_argument("--source", choices=["auto", "codex", "claude", "cc", "opencode", "openclaw", "oc", "cursor", "vscode", "code"], default="auto")
    distill_skill.add_argument("--username", help="Display name for the distilled skill.")
    distill_skill.add_argument("--all", action="store_true", help="Aggregate all detected sessions for the source.")
    distill_skill.add_argument("--since", help="Only include sessions on/after this date or datetime.")
    distill_skill.add_argument("--until", help="Only include sessions on/before this date or datetime.")
    distill_skill.add_argument("--limit", type=int, help="Cap the number of sessions after filtering.")
    distill_skill.add_argument("--min-messages", type=int, default=8, help="Exclude tiny sessions below this message count in aggregate mode.")
    distill_skill.add_argument("--output", help="Write markdown distillation summary to a file.")
    distill_skill.add_argument("--json-output", help="Write structured distillation JSON to a file.")

    refresh_terms = subparsers.add_parser("refresh-terms", help="Refresh latest vibecoding / LLM agent terminology from official docs.")
    refresh_terms.add_argument("--output-dir", default="docs", help="Directory to write latest terminology markdown/json/prompt files.")
    refresh_terms.add_argument("--json-output", help="Write the refresh result metadata to a JSON file.")

    doctor = subparsers.add_parser("doctor", help="Show render and host support information for stable local reproduction.")
    doctor.add_argument("--json-output", help="Write doctor result to a JSON file.")

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

    if args.command == "coach":
        _handle_coach(args)
        return

    if args.command == "distill-skill":
        _handle_distill_skill(args)
        return

    if args.command == "refresh-terms":
        _handle_refresh_terms(args)
        return

    if args.command == "doctor":
        _handle_doctor(args)
        return

    payload, markdown = _build_analysis_result(args)
    resolved_card_style = _resolve_card_style(args.card_style, payload)
    payload["card_style"] = resolved_card_style

    if args.command == "export":
        exported = export_bundle(
            payload=payload,
            markdown=markdown,
            output_dir=args.export_dir,
            card_style=resolved_card_style,
            archive=args.zip,
            slug=args.slug,
        )
        print(json.dumps(exported, ensure_ascii=False, indent=2))
        return

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)

    if args.card_dir:
        payload["cards"] = write_cards(payload, args.card_dir, certificate_choice=args.certificate, style=resolved_card_style)

    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_analysis_result(args):
    generated_at = _generated_at()
    source = normalize_source(args.source)
    latest_terms = _refresh_terms_if_requested(args)
    certificate_choice = getattr(args, "certificate", "both")
    target_level = getattr(args, "target_level", None)
    memory_enabled = bool(getattr(args, "memory_enabled", False))
    analysis = None
    aggregate = None
    distill_messages = []
    distill_display_name = None
    distill_models: list[str] = []
    distill_source = source
    if args.path:
        transcript = load_transcript(args.path, source=source)
        _apply_display_name(transcript, args.username, track=certificate_choice)
        distill_messages = list(transcript.messages)
        distill_display_name = transcript.display_name
        distill_models = list(transcript.models)
        distill_source = transcript.source
        distilled = analyze_with_chunking(transcript)
        if distilled.kind == "single":
            analysis = distilled.analysis
            payload = _to_json(analysis)
        else:
            aggregate = distilled.aggregate
            aggregate["display_name"] = transcript.display_name
            payload = _aggregate_to_json(aggregate)
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
        transcripts = [load_transcript(ref, source=source) for ref in refs]
        for transcript in transcripts:
            _apply_display_name(transcript, args.username, track=certificate_choice)
        distill_messages = [message for transcript in transcripts for message in transcript.messages]
        distill_display_name = _resolve_display_name_from_transcripts(transcripts, override=args.username, track=certificate_choice)
        distill_models = sorted({model for transcript in transcripts for model in transcript.models})
        distill_source = source
        distilled = analyze_many_with_chunking(transcripts, min_messages=args.min_messages)
        aggregate = distilled.aggregate
        pooled_analyses = distilled.analyses or []
        aggregate["display_name"] = _resolve_display_name_from_transcripts(transcripts, override=args.username, track=certificate_choice)
        aggregate["time_window"] = {
            "since": args.since,
            "until": args.until,
            "latest_session": _display_ref(refs[0]),
            "oldest_session": _display_ref(refs[-1]),
        }
        payload = _aggregate_to_json(aggregate)
        scope_kind = "window" if args.since or args.until else "aggregate"
        scope_label = _scope_label(source, scope_kind, args)
    else:
        if source == "auto":
            source = "codex"
        transcript = load_transcript(_latest_ref(source), source=source)
        _apply_display_name(transcript, args.username, track=certificate_choice)
        distill_messages = list(transcript.messages)
        distill_display_name = transcript.display_name
        distill_models = list(transcript.models)
        distill_source = transcript.source
        distilled = analyze_with_chunking(transcript)
        if distilled.kind == "single":
            analysis = distilled.analysis
            payload = _to_json(analysis)
        else:
            aggregate = distilled.aggregate
            aggregate["display_name"] = transcript.display_name
            payload = _aggregate_to_json(aggregate)
        scope_kind = "latest"
        scope_label = f"{source}:最近一次"

    payload["generated_at"] = generated_at
    payload["style_signals"] = {
        "xianxia_requested": any(any(keyword in message.text for keyword in ("修仙", "境界")) for message in distill_messages),
    }
    payload["xianxia_profile"] = derive_xianxia_profile(payload)
    insight_payload = payload.get("insights") if isinstance(payload.get("insights"), dict) else {}
    secondary_display_name = distill_display_name or str(payload.get("display_name") or "码奸")
    payload["secondary_skill"] = build_secondary_skill_distillation(
        messages=distill_messages,
        display_name=secondary_display_name,
        source=distill_source,
        rank=str(insight_payload.get("rank") or ""),
        generated_at=generated_at,
        models=distill_models,
        tool_calls=int(_distill_tool_calls(payload) or 0),
    )
    secondary_skill = payload["secondary_skill"] if isinstance(payload.get("secondary_skill"), dict) else {}
    if analysis is not None:
        payload["insights"] = build_analysis_insights(
            analysis,
            target_level=target_level,
            secondary_skill=secondary_skill,
        )
    else:
        aggregate["insights"] = build_aggregate_insights(
            distilled.analyses or [],
            aggregate,
            target_level=target_level,
            secondary_skill=secondary_skill,
        )
        payload["insights"] = aggregate["insights"]
    if latest_terms:
        payload["latest_terms"] = latest_terms
    snapshot_source = _payload_source(payload, fallback=source)
    scope_label = scope_label.replace(f"{source}:", f"{snapshot_source}:")

    memory_summary = None
    if memory_enabled:
        memory_key = args.memory_key or _default_memory_key(args, payload, snapshot_source, scope_kind)
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

    if analysis is not None:
        markdown = render_markdown(
            analysis,
            certificate_choice=certificate_choice,
            memory_summary=memory_summary,
            generated_at=generated_at,
            insights=payload.get("insights"),
        )
    else:
        markdown = render_aggregate_markdown(
            aggregate,
            certificate_choice=certificate_choice,
            memory_summary=memory_summary,
            generated_at=generated_at,
            insights=aggregate.get("insights"),
        )
    return payload, markdown


def _handle_distill_skill(args) -> None:
    payload, _ = _build_analysis_result(args)
    secondary = payload.get("secondary_skill", {})
    markdown = render_secondary_skill_markdown(secondary if isinstance(secondary, dict) else {})
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(secondary, ensure_ascii=False, indent=2), encoding="utf-8")


def _handle_doctor(args) -> None:
    info = {
        "hosts": {
            "codex": "native",
            "claude-code": "native",
            "opencode": "native",
            "openclaw": "native",
            "cursor": "native-project-rule",
        },
        "card_render": card_render_environment(),
        "environment_config": {
            "python_requirement": ">=3.10",
            "install_command": "python3 -m pip install -e .",
            "python_dependencies": ["cairosvg", "Pillow"],
            "analysis_and_export_json_markdown": ["macOS", "Linux", "Windows"],
            "svg_card": ["macOS", "Linux", "Windows"],
            "png_card": ["macOS", "Linux", "Windows"] if card_render_environment()["png_supported"] else [],
            "cursor_rule": True,
        },
    }
    text = json.dumps(info, ensure_ascii=False, indent=2)
    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    else:
        print(text)


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
        after_source = _resolve_compare_source(source, before_transcript.source)
        after_transcript = load_transcript(_latest_ref(after_source), source=after_source)
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


def _resolve_card_style(requested_style: str, payload: dict[str, object]) -> str:
    if requested_style in {"default", "xianxia"}:
        return requested_style
    return "xianxia" if _payload_requests_xianxia(payload) else "default"


def _payload_requests_xianxia(payload: dict[str, object]) -> bool:
    style_signals = payload.get("style_signals")
    if isinstance(style_signals, dict) and bool(style_signals.get("xianxia_requested")):
        return True
    keywords = ("修仙", "境界")
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        messages = transcript.get("messages")
        if isinstance(messages, list):
            for item in messages:
                if isinstance(item, dict):
                    text = str(item.get("text") or "")
                    if any(keyword in text for keyword in keywords):
                        return True
    insights = payload.get("insights")
    if isinstance(insights, dict):
        for value in insights.values():
            if isinstance(value, str) and any(keyword in value for keyword in keywords):
                return True
            if isinstance(value, list) and any(any(keyword in str(part) for keyword in keywords) for part in value):
                return True
    return False


def _handle_coach(args) -> None:
    generated_at = _generated_at()
    source = normalize_source(args.source)
    latest_terms = _refresh_terms_if_requested(args)
    if args.path:
        transcript = load_transcript(args.path, source=source)
        _apply_display_name(transcript, args.username, track="user")
        distilled = analyze_with_chunking(transcript)
        if distilled.kind == "single":
            analysis = distilled.analysis
            insights = build_analysis_insights(analysis, target_level=args.target_level)
        else:
            insights = build_aggregate_insights(distilled.analyses or [], distilled.aggregate or {}, target_level=args.target_level)
        payload = {
            "display_name": transcript.display_name,
            "source": transcript.source,
            "insights": insights,
            "generated_at": generated_at,
            "target_level": args.target_level,
        }
    elif args.all or args.since or args.until or args.limit:
        if source == "auto":
            source = "codex"
        since = parse_date_bound(args.since)
        until = parse_date_bound(args.until, is_end=True)
        refs = _list_transcript_refs(source, since=since, until=until, limit=args.limit)
        if not refs:
            raise SystemExit("No sessions matched the requested source/time window.")
        transcripts = [load_transcript(ref, source=source) for ref in refs]
        for transcript in transcripts:
            _apply_display_name(transcript, args.username, track="user")
        distilled = analyze_many_with_chunking(transcripts, min_messages=args.min_messages)
        aggregate = distilled.aggregate
        pooled_analyses = distilled.analyses or []
        payload = {
            "display_name": _resolve_display_name_from_transcripts(transcripts, override=args.username, track="user"),
            "source": source,
            "insights": build_aggregate_insights(pooled_analyses, aggregate, target_level=args.target_level),
            "generated_at": generated_at,
            "target_level": args.target_level,
        }
    else:
        if source == "auto":
            source = "codex"
        transcript = load_transcript(_latest_ref(source), source=source)
        _apply_display_name(transcript, args.username, track="user")
        distilled = analyze_with_chunking(transcript)
        if distilled.kind == "single":
            analysis = distilled.analysis
            insights = build_analysis_insights(analysis, target_level=args.target_level)
        else:
            insights = build_aggregate_insights(distilled.analyses or [], distilled.aggregate or {}, target_level=args.target_level)
        payload = {
            "display_name": transcript.display_name,
            "source": transcript.source,
            "insights": insights,
            "generated_at": generated_at,
            "target_level": args.target_level,
        }
    if latest_terms:
        payload["latest_terms"] = latest_terms

    markdown = render_coaching_markdown(
        "vibecoding.skill 突破教练",
        display_name=str(payload.get("display_name") or "码奸"),
        source=str(payload.get("source") or source),
        generated_at=generated_at,
        insights=payload["insights"],
        target_level=args.target_level,
    )
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)

    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _handle_refresh_terms(args) -> None:
    try:
        result = refresh_term_catalog(args.output_dir)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


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
        "insights": build_analysis_insights(analysis),
    }


def _certificate_to_json(certificate):
    if isinstance(certificate, dict):
        return certificate
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


def _aggregate_to_json(aggregate: dict[str, object]) -> dict[str, object]:
    payload = dict(aggregate)
    payload["user_metrics"] = [_metric_to_json(item) for item in list(aggregate.get("user_metrics", []))]
    payload["assistant_metrics"] = [_metric_to_json(item) for item in list(aggregate.get("assistant_metrics", []))]
    payload["user_certificate"] = _certificate_to_json(aggregate.get("user_certificate"))
    payload["assistant_certificate"] = _certificate_to_json(aggregate.get("assistant_certificate"))
    return payload


def _distill_tool_calls(payload: dict[str, object]) -> int:
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        return int(transcript.get("tool_calls", 0) or 0)
    return int(payload.get("total_tool_calls", 0) or 0)


def _metric_to_json(metric) -> dict[str, object]:
    if isinstance(metric, dict):
        return metric
    return {
        "name": metric.name,
        "score": metric.score,
        "rationale": metric.rationale,
    }


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


def _default_memory_key(args, payload: dict[str, object], source: str, scope_kind: str) -> str:
    if scope_kind == "path":
        transcript = payload.get("transcript")
        if isinstance(transcript, dict):
            path = transcript.get("path")
            if isinstance(path, str) and path:
                return f"{source}:{scope_kind}:{_fingerprint_value(path)}"
    if scope_kind == "window":
        since = getattr(args, "since", None) or "earliest"
        until = getattr(args, "until", None) or "latest"
        limit = getattr(args, "limit", None) or "all"
        return f"{source}:{scope_kind}:{since}:{until}:{limit}"
    return f"{source}:{scope_kind}"


def _fingerprint_value(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def _aggregate_scope(analyses, refs, min_messages: int):
    paired = [(analysis, ref) for analysis, ref in zip(analyses, refs) if len(analysis.transcript.messages) >= min_messages]
    if not paired:
        return analyses, refs
    pooled_analyses = [analysis for analysis, _ in paired]
    pooled_refs = [ref for _, ref in paired]
    return pooled_analyses, pooled_refs


def _payload_source(payload: dict[str, object], fallback: str) -> str:
    transcript = payload.get("transcript", {})
    if isinstance(transcript, dict):
        source = transcript.get("source")
        if isinstance(source, str) and source:
            return source
    return fallback


def _resolve_compare_source(requested_source: str, before_source: str) -> str:
    return before_source if requested_source == "auto" else requested_source


def _apply_display_name(transcript, override: str | None, track: str) -> None:
    transcript.display_name = override or infer_display_name(transcript) or default_display_name("user" if track != "assistant" else "assistant")


def _resolve_display_name_from_analyses(analyses, override: str | None, track: str) -> str:
    if override:
        return override
    for analysis in analyses:
        if analysis.transcript.display_name:
            return str(analysis.transcript.display_name)
    return default_display_name("user" if track != "assistant" else "assistant")


def _resolve_display_name_from_transcripts(transcripts, override: str | None, track: str) -> str:
    if override:
        return override
    for transcript in transcripts:
        if transcript.display_name:
            return str(transcript.display_name)
    return default_display_name("user" if track != "assistant" else "assistant")


def _generated_at() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")


def _refresh_terms_if_requested(args) -> dict[str, str] | None:
    if not getattr(args, "refresh_terms", False):
        return None
    output_dir = getattr(args, "terms_dir", None) or "docs"
    try:
        return refresh_term_catalog(output_dir)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
