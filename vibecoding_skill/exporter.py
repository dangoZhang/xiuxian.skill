from __future__ import annotations

import json
import zipfile
from pathlib import Path

from .cards import write_cards
from .secondary_skill import (
    build_readme_profile_panel,
    render_secondary_skill_markdown,
    result_skill_slug,
    result_skill_title_from_display,
)


def export_bundle(
    *,
    payload: dict[str, object],
    markdown: str,
    output_dir: str | Path,
    card_style: str = "default",
    archive: bool = False,
    slug: str | None = None,
) -> dict[str, str]:
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    display_name = _display_name(payload)
    result_skill_name = result_skill_slug(slug or display_name)
    result_skill_title = result_skill_title_from_display(display_name)
    assets_dir = root / "assets"
    cards = write_cards(payload, assets_dir, style=card_style)
    card_png_name = Path(cards["card_png"]).name

    report_path = root / "REPORT.md"
    profile_path = root / "PROFILE.md"
    skill_path = root / "SKILL.md"
    readme_path = root / "README.md"
    json_path = root / "snapshot.json"
    secondary_path = root / "DISTILLED_SKILL.json"
    cursor_rules_dir = root / ".cursor" / "rules"
    cursor_rules_dir.mkdir(parents=True, exist_ok=True)
    cursor_rule_path = cursor_rules_dir / f"{result_skill_name}.mdc"

    report_path.write_text(markdown, encoding="utf-8")
    profile_path.write_text(_render_profile(payload), encoding="utf-8")
    skill_path.write_text(_render_skill(payload, result_skill_name), encoding="utf-8")
    readme_path.write_text(_render_readme(payload, result_skill_name, result_skill_title, card_png_name), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    secondary_path.write_text(json.dumps(_secondary_skill(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    cursor_rule_path.write_text(_render_cursor_rule(payload, result_skill_name), encoding="utf-8")

    result = {
        "export_dir": str(root),
        "share_skill_dir": str(root),
        "result_skill_name": result_skill_name,
        "result_skill_title": result_skill_title,
        "share_readme": str(readme_path),
        "share_profile": str(profile_path),
        "share_report": str(report_path),
        "share_json": str(json_path),
        "distilled_skill_json": str(secondary_path),
        "cursor_rule": str(cursor_rule_path),
        "card_svg": cards["card_svg"],
        "card_png": cards["card_png"],
    }
    if archive:
        zip_path = root.parent / f"{root.name}.zip"
        _zip_dir(root, zip_path)
        result["share_zip"] = str(zip_path)
    return result


def _render_readme(payload: dict[str, object], result_skill_name: str, result_skill_title: str, card_png_name: str) -> str:
    name = _display_name(payload)
    rank = _insight(payload, "rank", "L1")
    ability = _insight(payload, "ability_text", "这套协作还在试手期。")
    generated_at = str(payload.get("generated_at") or "")
    usage_line = _insight(payload, "usage_line", "")
    habit_lines = _list_insight(payload, "habit_profile_lines")
    breakthrough_lines = _list_insight(payload, "breakthrough_lines")
    panel = build_readme_profile_panel(payload)
    lines = [
        f"# {name} 的 vibecoding 导出包",
        "",
        f"这是从真实协作记录里导出的共享包，当前判断为 `{rank}`。",
        "",
        f"这份导出包会保留 {name} 和 AI 协作时最稳定的节奏，方便交给另一个也在用 vibecoding.skill 的人继续复用。",
        "",
        "<table>",
        "<tr>",
        '<td width="54%" valign="top">',
        "",
        f"### {panel.get('title', '这套 vibecoding 像什么')}",
        "",
    ]
    for tag in panel.get("tags", []):
        lines.append(f"`{tag}` ")
    if panel.get("tags"):
        lines.append("")
    for paragraph in panel.get("paragraphs", []):
        lines.extend([paragraph, ""])
    for bullet in panel.get("bullets", []):
        lines.append(f"- {bullet}")
    lines.extend(
        [
            "",
            "</td>",
            '<td width="46%" valign="top">',
            "",
            f'<img src="./assets/{card_png_name}" alt="vibecoding 分享卡" width="100%" />',
            "",
            "</td>",
            "</tr>",
            "</table>",
            "",
            "## 分享哪个文件",
            "",
            "- 想让另一个也在用 vibecoding.skill 的人直接复用：分享整个目录，或压缩后的 zip。",
            "- 想让别人快速看懂这套做法：分享 `PROFILE.md`。",
            "- 想让别人看完整判断依据：分享 `REPORT.md`。",
            f"- 想发群或发社交平台：分享 `assets/{card_png_name}`。",
            "",
            "## 这包里有什么",
            "",
            f"- `SKILL.md`：蒸馏结果 skill，本包核心入口。调用名是 `{result_skill_name}`，显示标题是 `{result_skill_title}`。",
            f"- `.cursor/rules/{result_skill_name}.mdc`：给 Cursor 原生读取。",
            "- `PROFILE.md`：压缩后的习惯画像，适合转发和快速阅读。",
            "- `REPORT.md`：完整报告，包含判断依据和突破建议。",
            "- `snapshot.json`：结构化结果，方便二次开发。",
            "- `DISTILLED_SKILL.json`：16 维蒸馏主判结果，内含语义分桶证据和供 LLM 做二次综合的 prompt。",
            "- `assets/`：分享卡图片。",
            "",
            "## 这套习惯的摘要",
            "",
            "- 画像来源：先做 16 维蒸馏，报告、README、共享页和导出包都只从这份主判结果派生。",
            f"- 等级：`{rank}`",
            f"- 判断：{ability}",
        ]
    )
    if usage_line:
        lines.append(f"- 取样规模：`{usage_line}`")
    if generated_at:
        lines.append(f"- 导出时间：`{generated_at}`")
    if habit_lines:
        lines.extend(["", "## 这套 vibecoding 习惯", ""])
        for item in habit_lines:
            lines.append(f"- {item}")
    if breakthrough_lines:
        lines.extend(["", "## 下一步怎么把 AI 接得更深", ""])
        for item in breakthrough_lines[:3]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## 接收方怎么用",
            "",
            "更顺手的场景是双方都已经在自己的宿主里装了 `vibecoding.skill`。",
            f"`vibecoding.skill` 是入口 skill，这次蒸馏出的结果 skill 调用名是 `{result_skill_name}`。",
            "",
            "1. 把整个目录或 zip 发给接收方。",
            "2. 接收方在自己的对话里把这份导出包交给 `vibecoding.skill`。",
            f"3. 让 `vibecoding.skill` 先读取并调用 `{result_skill_name}`。",
            "4. 再按这套方式继续协作。",
            "",
            "## 接收方可以直接说",
            "",
            f"- 这是同事的导出包。先读他的画像，再调用 `{result_skill_name}` 和我一起做当前任务。",
            f"- 先按这份导出包总结协作习惯，再切到 `{result_skill_name}` 开始当前任务。",
            "- 按这份画像指出我最该补的动作。",
            "- 结合这份画像，继续帮我把 AI 融入现在的工作流程。",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _render_skill(payload: dict[str, object], result_skill_name: str) -> str:
    secondary = _secondary_skill(payload)
    lines = [
        "---",
        f"name: {result_skill_name}",
        f"description: 这是从{_display_name(payload)}的真实记录蒸馏出的结果 skill，供 vibecoding.skill 读取或直接调用，用来复用这套协作方式。",
        "---",
        "",
        render_secondary_skill_markdown(secondary).strip(),
        "",
        "## Called By vibecoding.skill",
        "",
        f"- 当 `vibecoding.skill` 收到这份导出包时，应先读取 `PROFILE.md`、`REPORT.md`、`DISTILLED_SKILL.json`，再调用 `{result_skill_name}`。",
        "- 如果当前仓库指令和这份结果 skill 冲突，以更高优先级指令为准。",
    ]
    return "\n".join(lines).strip() + "\n"


def _render_cursor_rule(payload: dict[str, object], result_skill_name: str) -> str:
    secondary = _secondary_skill(payload)
    contract = secondary.get("secondary_skill_contract") if isinstance(secondary, dict) else {}
    if not isinstance(contract, dict):
        contract = {}
    lines = [
        "---",
        f"description: Use {result_skill_name} as a native Cursor project rule for this distilled vibecoding style.",
        "alwaysApply: false",
        "---",
        "",
        f"# {result_skill_name}",
        "",
        "按这份导出包里的 vibecoding 习惯推进任务，不做人设扮演。",
        "",
        "## Default Behavior",
        "",
    ]
    for item in contract.get("default_behavior", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Guardrails", ""])
    for item in contract.get("guardrails", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Prompt Examples", ""])
    for item in contract.get("prompt_examples", []):
        lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def _render_profile(payload: dict[str, object]) -> str:
    name = _display_name(payload)
    rank = _insight(payload, "rank", "L1")
    stage = _insight(payload, "stage", "试手期")
    ability = _insight(payload, "ability_text", "还在试手。")
    usage_line = _insight(payload, "usage_line", "")
    generated_at = str(payload.get("generated_at") or "")
    habit_lines = _list_insight(payload, "habit_profile_lines")
    mimic_lines = _list_insight(payload, "mimic_lines")
    verdict_lines = _list_insight(payload, "verdict_lines")
    breakthrough_lines = _list_insight(payload, "breakthrough_lines")
    modern_lines = _list_insight(payload, "modern_signal_lines")
    user_summary = _list_insight(payload, "user_summary_lines")
    assistant_summary = _list_insight(payload, "assistant_summary_lines")
    model_name = _primary_model(payload)

    lines = [
        f"# {name} 的 vibecoding 画像",
        "",
        f"- 等级：`{rank}`",
        f"- 阶段：`{stage}`",
        f"- 主用模型：`{model_name}`",
        f"- 能力摘要：{ability}",
    ]
    if usage_line:
        lines.append(f"- 取样规模：`{usage_line}`")
    if generated_at:
        lines.append(f"- 生成时间：`{generated_at}`")
    if habit_lines:
        lines.extend(["", "## 这套习惯是什么"])
        for item in habit_lines:
            lines.append(f"- {item}")
    if user_summary or assistant_summary:
        lines.extend(["", "## 关键观察"])
        for item in user_summary + assistant_summary:
            lines.append(f"- {item}")
    if verdict_lines:
        lines.extend(["", "## 判词"])
        for item in verdict_lines:
            lines.append(f"- {item}")
    if mimic_lines:
        lines.extend(["", "## 如果想模仿这套做法"])
        for item in mimic_lines:
            lines.append(f"- {item}")
    if breakthrough_lines:
        lines.extend(["", "## 如果想继续升级"])
        for item in breakthrough_lines:
            lines.append(f"- {item}")
    if modern_lines:
        lines.extend(["", "## 现代协作信号"])
        for item in modern_lines:
            lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def _insight(payload: dict[str, object], key: str, default: str) -> str:
    insights = payload.get("insights")
    if isinstance(insights, dict):
        value = insights.get(key)
        if isinstance(value, str) and value:
            return value
    return default


def _list_insight(payload: dict[str, object], key: str) -> list[str]:
    insights = payload.get("insights")
    if not isinstance(insights, dict):
        return []
    value = insights.get(key)
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _display_name(payload: dict[str, object]) -> str:
    for key in ("display_name",):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        value = transcript.get("display_name")
        if isinstance(value, str) and value:
            return value
    return "码奸"


def _secondary_skill(payload: dict[str, object]) -> dict[str, object]:
    value = payload.get("secondary_skill")
    return value if isinstance(value, dict) else {}


def _primary_model(payload: dict[str, object]) -> str:
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        models = transcript.get("models")
        if isinstance(models, list) and models:
            return str(models[0])
    models = payload.get("models")
    if isinstance(models, list) and models:
        top = models[0]
        if isinstance(top, dict):
            return str(top.get("name") or top.get("model") or "未知模型")
        if isinstance(top, str):
            return top
    return "未知模型"
def _zip_dir(root: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            archive.write(path, arcname=path.relative_to(root.parent))
