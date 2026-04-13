#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
from argparse import Namespace


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vibecoding_skill.cli import _build_analysis_result, _resolve_card_style
from vibecoding_skill.exporter import export_bundle
from vibecoding_skill.readme_sync import (
    README_EXAMPLE_MARKER_END,
    README_EXAMPLE_MARKER_START,
    README_PROFILE_MARKER_END,
    README_PROFILE_MARKER_START,
    render_profile_block,
    render_profile_example_quote,
    update_marked_file,
)
from vibecoding_skill.secondary_skill import build_readme_profile_panel

DEMO = ROOT / "examples" / "demo_codex_session.jsonl"
README = ROOT / "README.md"
DEMO_BUNDLE = ROOT / "examples" / "generated" / "demo_codex_session-share-bundle"


def build_demo_payload() -> tuple[dict[str, object], str]:
    args = Namespace(
        command="analyze",
        path=str(DEMO),
        source="codex",
        certificate="both",
        username="码奸",
        all=False,
        since=None,
        until=None,
        limit=None,
        min_messages=8,
        memory_enabled=False,
        memory_key=None,
        target_level=None,
        output=None,
        json_output=None,
        card_dir=None,
        card_style="auto",
        refresh_terms=False,
        terms_dir="docs",
    )
    payload, markdown = _build_analysis_result(args)
    payload["card_style"] = _resolve_card_style(args.card_style, payload)
    return payload, markdown


def main() -> None:
    payload, markdown = build_demo_payload()
    secondary = payload.get("secondary_skill")
    if not isinstance(secondary, dict):
        raise SystemExit("Missing secondary_skill in demo payload.")
    panel = build_readme_profile_panel(payload)

    update_marked_file(
        README,
        README_PROFILE_MARKER_START,
        README_PROFILE_MARKER_END,
        render_profile_block(panel),
    )
    update_marked_file(
        README,
        README_EXAMPLE_MARKER_START,
        README_EXAMPLE_MARKER_END,
        render_profile_example_quote(panel),
    )

    export_bundle(
        payload=payload,
        markdown=markdown,
        output_dir=DEMO_BUNDLE,
        card_style=str(payload.get("card_style") or "default"),
    )


if __name__ == "__main__":
    main()
