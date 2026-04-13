from __future__ import annotations

from pathlib import Path


README_PROFILE_MARKER_START = "<!-- AUTO_PROFILE_START -->"
README_PROFILE_MARKER_END = "<!-- AUTO_PROFILE_END -->"
README_EXAMPLE_MARKER_START = "<!-- AUTO_EXAMPLE1_START -->"
README_EXAMPLE_MARKER_END = "<!-- AUTO_EXAMPLE1_END -->"


def render_profile_block(panel: dict[str, object]) -> str:
    tags = panel.get("tags")
    if not isinstance(tags, list):
        tags = []
    paragraphs = panel.get("paragraphs")
    if not isinstance(paragraphs, list):
        paragraphs = []
    lines: list[str] = [README_PROFILE_MARKER_START]
    if tags:
        lines.append(" ".join(f"`{tag}`" for tag in tags))
        lines.append("")
    for paragraph in paragraphs:
        lines.append(str(paragraph))
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines.append(README_PROFILE_MARKER_END)
    return "\n".join(lines)


def render_profile_example_quote(panel: dict[str, object]) -> str:
    tags = panel.get("tags")
    if not isinstance(tags, list):
        tags = []
    paragraphs = panel.get("paragraphs")
    if not isinstance(paragraphs, list):
        paragraphs = []
    bullets = panel.get("bullets")
    if not isinstance(bullets, list):
        bullets = []

    lines = [README_EXAMPLE_MARKER_START]
    if paragraphs:
        lines.append(f"> {paragraphs[0]}")
    if len(paragraphs) > 1:
        lines.append(">")
        lines.append("> 协作画像大致是：")
        for paragraph in paragraphs[1:]:
            lines.append(f"> - {paragraph}")
    if bullets:
        lines.append(">")
        lines.append("> 落成可复用习惯时，最稳定的动作包括：")
        for bullet in bullets:
            lines.append(f"> - {bullet}")
    if tags:
        lines.append(">")
        lines.append(f"> 标签：{' / '.join(str(tag) for tag in tags)}")
    lines.append(README_EXAMPLE_MARKER_END)
    return "\n".join(lines)


def replace_marked_section(text: str, start_marker: str, end_marker: str, new_block: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start < 0 or end < 0 or end < start:
        raise ValueError(f"Missing markers: {start_marker} ... {end_marker}")
    end += len(end_marker)
    return text[:start] + new_block + text[end:]


def update_marked_file(path: str | Path, start_marker: str, end_marker: str, new_block: str) -> None:
    target = Path(path).expanduser().resolve()
    text = target.read_text(encoding="utf-8")
    updated = replace_marked_section(text, start_marker, end_marker, new_block)
    target.write_text(updated, encoding="utf-8")
