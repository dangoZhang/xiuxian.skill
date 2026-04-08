from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import analyze_transcript, compare_analyses
from .parsers import latest_transcript, load_transcript, summarize_locations
from .renderer import render_comparison_markdown, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portrait-skill",
        description="Issue cultivation portraits and AI capability portraits from agent transcripts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Show default transcript locations and latest detected files.")
    scan.add_argument("--source", choices=["codex", "claude", "opencode", "all"], default="all")

    analyze = subparsers.add_parser("analyze", help="Analyze a transcript and print a markdown certificate.")
    analyze.add_argument("--path", help="Transcript path. If omitted, use the latest file for --source.")
    analyze.add_argument("--source", choices=["auto", "codex", "claude", "opencode"], default="auto")
    analyze.add_argument("--certificate", choices=["user", "assistant", "both"], default="both")
    analyze.add_argument("--output", help="Write markdown report to a file.")
    analyze.add_argument("--json-output", help="Write structured JSON summary to a file.")

    compare = subparsers.add_parser("compare", help="Compare two transcripts and judge whether the user or AI broke through.")
    compare.add_argument("--before", required=True, help="Previous-cycle transcript path.")
    compare.add_argument("--after", help="Current-cycle transcript path. If omitted, use latest file for --source.")
    compare.add_argument("--source", choices=["auto", "codex", "claude", "opencode"], default="auto")
    compare.add_argument("--certificate", choices=["user", "assistant", "both"], default="both")
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

    source = args.source
    if args.path:
        transcript = load_transcript(args.path, source=source)
    else:
        if source == "auto":
            source = "codex"
        transcript = load_transcript(latest_transcript(source), source=source)

    analysis = analyze_transcript(transcript)
    markdown = render_markdown(analysis, certificate_choice=args.certificate)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)

    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(_to_json(analysis), ensure_ascii=False, indent=2), encoding="utf-8")


def _handle_compare(args) -> None:
    source = args.source
    before = analyze_transcript(load_transcript(args.before, source=source))
    if args.after:
        after = analyze_transcript(load_transcript(args.after, source=source))
    else:
        if source == "auto":
            source = "codex"
        after = analyze_transcript(load_transcript(latest_transcript(source), source=source))

    comparison = compare_analyses(before, after)
    markdown = render_comparison_markdown(comparison, certificate_choice=args.certificate)
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
            latest = latest_transcript(name)
            print(f"- latest: {latest}")
        except FileNotFoundError as exc:
            print(f"- latest: not found ({exc})")


def _to_json(analysis):
    return {
        "overview": analysis.overview,
        "transcript": {
            "source": analysis.transcript.source,
            "path": str(analysis.transcript.path),
            "message_count": len(analysis.transcript.messages),
            "tool_calls": analysis.transcript.tool_calls,
        },
        "user_metrics": [{"name": item.name, "score": item.score, "rationale": item.rationale} for item in analysis.user_metrics],
        "assistant_metrics": [{"name": item.name, "score": item.score, "rationale": item.rationale} for item in analysis.assistant_metrics],
        "user_certificate": _certificate_to_json(analysis.user_certificate),
        "assistant_certificate": _certificate_to_json(analysis.assistant_certificate),
    }


def _certificate_to_json(certificate):
    return {
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


if __name__ == "__main__":
    main()
