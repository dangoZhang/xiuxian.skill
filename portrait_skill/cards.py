from __future__ import annotations

from html import escape
from pathlib import Path
import subprocess

from .parsers import default_display_name
from .themes import get_ai_level_theme

XI_METRIC_NAMES = {
    "目标清晰度": "道心坚定",
    "上下文供给": "根基稳固",
    "迭代修正力": "悟性渐开",
    "验收意识": "收功谨慎",
    "协作节奏": "气机相合",
    "执行落地": "术法纯熟",
    "工具调度": "驭器纯熟",
    "验证闭环": "收功圆满",
    "上下文承接": "气脉贯通",
    "补救适配": "应变有方",
}

XI_WEAK_METRIC_NAMES = {
    "目标清晰度": "道心未定",
    "上下文供给": "根基浮动",
    "迭代修正力": "悟性未开",
    "验收意识": "收功不稳",
    "协作节奏": "气机不顺",
    "执行落地": "术法生疏",
    "工具调度": "驭器未熟",
    "验证闭环": "收功有缺",
    "上下文承接": "气脉不畅",
    "补救适配": "应变不足",
}

AI_LEVEL_ABILITIES = {
    "L1": "完成单轮问答",
    "L2": "感知提问方式对结果的影响",
    "L3": "稳定完成简单任务",
    "L4": "重复跑通常见流程",
    "L5": "把经验封成模板技法",
    "L6": "先替你推进一段具体工作",
    "L7": "协同多具分身与工具完成任务",
    "L8": "承担能力层与系统层工作",
    "L9": "进入真实业务回路并持续回流",
    "L10": "把方法复制到团队与客户场景",
}

ASSISTANT_METRIC_LABELS = {
    "执行落地": "执行推进",
    "工具调度": "工具调度",
    "验证闭环": "验证闭环",
    "上下文承接": "上下文承接",
    "补救适配": "补救适配",
}

ASSISTANT_BEHAVIOR_TEXT = {
    "执行落地": {
        "strong": "能把任务往实现上推，不只停在总结",
        "weak": "落到实现的速度还不够快",
    },
    "工具调度": {
        "strong": "会主动调度工具推进任务",
        "weak": "工具使用还不够主动",
    },
    "验证闭环": {
        "strong": "会把验证和结果确认一起推进",
        "weak": "验证动作偏少，结果确认还不够主动",
    },
    "上下文承接": {
        "strong": "能承接关键上下文，较少跑偏",
        "weak": "承接上下文还不够稳",
    },
    "补救适配": {
        "strong": "遇到阻力还能转向补救，继续推进",
        "weak": "遇到阻力时补救还不够快",
    },
}

USER_BEHAVIOR_TEXT = {
    "目标清晰度": {
        "strong": "所求明确，轻重先后都说得清楚",
        "weak": "所求仍散，轻重先后还未理顺",
    },
    "上下文供给": {
        "strong": "前因后果交代得更全，来龙去脉都备得齐",
        "weak": "前因后果交代仍少，来龙去脉还不够全",
    },
    "迭代修正力": {
        "strong": "见势不对便肯回身修正，不急着一条路走到底",
        "weak": "修正还不够勤，常常停在第一轮",
    },
    "验收意识": {
        "strong": "每到收功时都肯细看结果，不轻易草草翻过",
        "weak": "收功时看得还不够细，结果尚未盯紧",
    },
    "协作节奏": {
        "strong": "往返有序，彼此呼应，推进时不乱",
        "weak": "步调仍乱，前后呼应还不够稳",
    },
}


def write_cards(payload: dict[str, object], output_dir: str | Path, certificate_choice: str = "both") -> dict[str, str]:
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    if certificate_choice in {"user", "both"} and payload.get("user_certificate"):
        svg_path = target_dir / "portrait-user.svg"
        png_path = target_dir / "portrait-user.png"
        svg_path.write_text(render_user_portrait_card(payload), encoding="utf-8")
        _render_png(svg_path, png_path)
        written["user_svg"] = str(svg_path)
        written["user_png"] = str(png_path)
    if certificate_choice in {"assistant", "both"} and payload.get("assistant_certificate"):
        svg_path = target_dir / "portrait-assistant.svg"
        png_path = target_dir / "portrait-assistant.png"
        svg_path.write_text(render_assistant_certificate_card(payload), encoding="utf-8")
        _render_png(svg_path, png_path)
        written["assistant_svg"] = str(svg_path)
        written["assistant_png"] = str(png_path)
    return written


def render_user_portrait_card(payload: dict[str, object]) -> str:
    certificate = _as_dict(payload.get("user_certificate"))
    persona = _as_dict(certificate.get("persona"))
    display_name = _get_display_name(payload, track="user")
    generated_at = _format_generated_at(payload.get("generated_at"))
    level = str(certificate.get("level", "凡人"))
    summary_lines = _user_portrait_verdict_lines(payload, level, fallback=str(persona.get("summary") or ""))
    subtitle = str(persona.get("subtitle") or "")
    growth_value = _xianxia_guidance_text(
        _first_line(_as_list(certificate.get("growth_plan")), fallback="再炼一轮，稳住当前气脉，再冲下一境。")
    )

    return f"""<svg width="1200" height="1600" viewBox="0 0 1200 1600" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="86" y1="48" x2="1124" y2="1556" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0E0A07"/>
      <stop offset="0.46" stop-color="#1D140D"/>
      <stop offset="1" stop-color="#090705"/>
    </linearGradient>
    <linearGradient id="paper" x1="194" y1="124" x2="1018" y2="1486" gradientUnits="userSpaceOnUse">
      <stop stop-color="#F8EFD8"/>
      <stop offset="0.45" stop-color="#E9D2A1"/>
      <stop offset="1" stop-color="#D3A45A"/>
    </linearGradient>
    <linearGradient id="ink" x1="292" y1="210" x2="812" y2="1428" gradientUnits="userSpaceOnUse">
      <stop stop-color="#6F3218"/>
      <stop offset="1" stop-color="#3E1D0E"/>
    </linearGradient>
    <radialGradient id="mist" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(920 222) rotate(145) scale(314 224)">
      <stop stop-color="#E9C777" stop-opacity="0.2"/>
      <stop offset="1" stop-color="#E9C777" stop-opacity="0"/>
    </radialGradient>
    <filter id="shadow" x="118" y="92" width="964" height="1436" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feFlood flood-opacity="0" result="BackgroundImageFix"/>
      <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
      <feOffset dy="26"/>
      <feGaussianBlur stdDeviation="24"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.03 0 0 0 0 0.015 0 0 0 0 0.006 0 0 0 0.48 0"/>
      <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_0_1"/>
      <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_0_1" result="shape"/>
    </filter>
  </defs>

  <rect width="1200" height="1600" rx="48" fill="url(#bg)"/>
  <ellipse cx="920" cy="222" rx="252" ry="178" fill="url(#mist)"/>

  <g filter="url(#shadow)">
    <path d="M252 130H948C980 130 1006 156 1006 188V1412C1006 1446 980 1472 948 1472H252C220 1472 194 1446 194 1412V188C194 156 220 130 252 130Z" fill="url(#paper)"/>
    <path d="M252 150H948C968 150 988 168 988 188V1410C988 1430 968 1450 948 1450H252C230 1450 212 1430 212 1410V188C212 168 230 150 252 150Z" stroke="#FBF3E2" stroke-width="8"/>
    <rect x="236" y="174" width="728" height="1232" rx="28" stroke="#A56A2A" stroke-opacity="0.34" stroke-width="2" stroke-dasharray="10 10"/>
  </g>

  <text x="600" y="250" fill="url(#ink)" font-size="34" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif" letter-spacing="4">画像</text>
  <text x="600" y="324" fill="url(#ink)" font-size="100" text-anchor="middle" font-family="STKaiti, KaiTi, serif">修仙画像</text>
  {_text_lines(_wrap_text(_card_subtitle(subtitle or "照见此身根骨、修为与机缘"), 22, limit=2), x=600, y=366, font_size=21, line_height=28, fill="#7B421B", anchor="middle", family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif")}
  <g>
    <circle cx="600" cy="540" r="126" fill="#6A2E13" fill-opacity="0.05" stroke="#7F3415" stroke-width="3"/>
    <circle cx="600" cy="540" r="98" stroke="#8B3C19" stroke-opacity="0.28" stroke-width="2" stroke-dasharray="8 10"/>
    <text x="600" y="528" fill="#532410" font-size="92" text-anchor="middle" font-family="STKaiti, KaiTi, serif">{_escape(level)}</text>
    <text x="600" y="576" fill="#6A3618" font-size="22" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif" letter-spacing="5">当前境界</text>
  </g>

  <g>
    <rect x="214" y="676" width="772" height="292" rx="30" fill="#FFF7EA" fill-opacity="0.78" stroke="#A56A2A" stroke-opacity="0.24" stroke-width="2"/>
    <text x="600" y="744" fill="#6B3817" font-size="20" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif" letter-spacing="4">仙途评语</text>
    {_text_lines(summary_lines, x=600, y=810, font_size=28, line_height=38, fill="#4C2412", anchor="middle", family="STKaiti, KaiTi, serif", weight="700")}
  </g>

  <g>
    <rect x="214" y="1012" width="772" height="228" rx="30" fill="#FFF6E4" fill-opacity="0.82" stroke="#A56A2A" stroke-opacity="0.22" stroke-width="2"/>
    <text x="600" y="1066" fill="#6B3817" font-size="20" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif" letter-spacing="4">破境之法</text>
    {_text_lines(_wrap_text(growth_value, 21, limit=3), x=600, y=1134, font_size=28, line_height=38, fill="#4F2812", anchor="middle", family="STKaiti, KaiTi, serif", weight="700")}
    <text x="600" y="1196" fill="#81502A" font-size="18" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">守住一条主线，再寻下一次破境</text>
  </g>

  <line x1="320" y1="1382" x2="880" y2="1382" stroke="#A56A2A" stroke-opacity="0.18" stroke-width="2"/>
  <text x="600" y="1430" fill="#7A4B28" font-size="17" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">{_escape(f'持有人 · {display_name}　　生成时间 · {generated_at}')}</text>

</svg>
"""


def render_assistant_certificate_card(payload: dict[str, object]) -> str:
    certificate = _as_dict(payload.get("assistant_certificate"))
    persona = _as_dict(certificate.get("persona"))
    display_name = _get_display_name(payload, track="assistant")
    generated_at = _format_generated_at(payload.get("generated_at"))
    level = str(certificate.get("level", "L1"))
    theme = _as_dict(certificate.get("theme")) or get_ai_level_theme(level)
    ability = _ability_text(level, str(persona.get("subtitle") or ""))
    verdict_lines = _assistant_verdict_lines(payload, ability)
    token_period = _certificate_period_label(payload)
    token_value = f"消耗 {_fmt_int(_extract_token_total(payload))} 枚令牌"

    return f"""<svg width="1200" height="1600" viewBox="0 0 1200 1600" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="96" y1="54" x2="1106" y2="1546" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(str(theme.get("bg_from", "#07111E")))}"/>
      <stop offset="0.52" stop-color="{_escape(str(theme.get("bg_to", "#123052")))}"/>
      <stop offset="1" stop-color="#091523"/>
    </linearGradient>
    <radialGradient id="halo" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(924 232) rotate(142) scale(292 208)">
      <stop stop-color="{_escape(str(theme.get("halo", "#5F98FF")))}" stop-opacity="0.28"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("halo", "#5F98FF")))}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="card" x1="176" y1="124" x2="1022" y2="1486" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(str(theme.get("card_bg", "#F7FAFF")))}"/>
      <stop offset="1" stop-color="#FFFFFF"/>
    </linearGradient>
    <linearGradient id="rim" x1="238" y1="184" x2="952" y2="1416" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(str(theme.get("accent", "#7EAEFF")))}"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("accent_dark", "#315FBC")))}"/>
    </linearGradient>
    <filter id="shadow" x="118" y="92" width="964" height="1436" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feFlood flood-opacity="0" result="BackgroundImageFix"/>
      <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
      <feOffset dy="24"/>
      <feGaussianBlur stdDeviation="24"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.02 0 0 0 0 0.05 0 0 0 0 0.08 0 0 0 0.28 0"/>
      <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_0_1"/>
      <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_0_1" result="shape"/>
    </filter>
  </defs>

  <rect width="1200" height="1600" rx="48" fill="url(#bg)"/>
  <ellipse cx="924" cy="232" rx="246" ry="182" fill="url(#halo)"/>

  <g filter="url(#shadow)">
    <rect x="176" y="126" width="848" height="1360" rx="34" fill="url(#card)"/>
    <rect x="196" y="146" width="808" height="1320" rx="26" stroke="url(#rim)" stroke-width="6"/>
    <rect x="228" y="178" width="744" height="1256" rx="18" stroke="{_escape(str(theme.get("accent", "#7EAEFF")))}" stroke-opacity="0.24" stroke-width="2" stroke-dasharray="8 10"/>
  </g>

  <text x="600" y="234" fill="{_escape(str(theme.get('muted', '#7F96B9')))}" font-size="32" text-anchor="middle" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif" letter-spacing="3">画像</text>
  <text x="600" y="308" fill="#10263A" font-size="70" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" font-weight="700">AI 协作能力证书</text>
  <text x="600" y="356" fill="#566A7E" font-size="22" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">基于真实会话稳定定级</text>
  <g>
    <rect x="238" y="392" width="724" height="886" rx="42" fill="{_escape(str(theme.get('panel_bg', '#162B49')))}"/>
    <rect x="268" y="422" width="664" height="826" rx="32" stroke="{_escape(str(theme.get('accent', '#7EAEFF')))}" stroke-opacity="0.36" stroke-width="2"/>
    <rect x="454" y="468" width="292" height="56" rx="28" fill="#FFFFFF" fill-opacity="0.08"/>
    <text x="600" y="504" fill="#E3EBF3" font-size="20" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" letter-spacing="4">协作能力等级</text>
    <text x="600" y="690" fill="{_escape(str(theme.get('accent', '#7EAEFF')))}" font-size="248" text-anchor="middle" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif" font-weight="800">{_escape(level)}</text>
    <text x="600" y="754" fill="#F4F8FC" font-size="24" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" letter-spacing="6">当前等级</text>
    <line x1="344" y1="812" x2="856" y2="812" stroke="{_escape(str(theme.get('accent', '#7EAEFF')))}" stroke-opacity="0.22" stroke-width="2"/>
    <text x="600" y="876" fill="#DDE6EE" font-size="21" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">能够</text>
    {_text_lines(_wrap_text(ability, 13, limit=2), x=600, y=928, font_size=40, line_height=48, fill="#FFFFFF", anchor="middle", family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif", weight="700")}
    <line x1="324" y1="1024" x2="876" y2="1024" stroke="#FFFFFF" stroke-opacity="0.14" stroke-width="2"/>
    <text x="600" y="1084" fill="#DDE6EE" font-size="20" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" letter-spacing="4">判词</text>
    {_text_lines(verdict_lines, x=322, y=1146, font_size=26, line_height=36, fill="#F6FAFD", anchor="start", family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif", weight="500")}
  </g>

  <g>
    <rect x="286" y="1316" width="628" height="116" rx="30" fill="#FFFFFF" fill-opacity="0.96"/>
    <text x="600" y="1360" fill="#5A6D81" font-size="18" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">{_escape(_truncate_text(token_period, 30))}</text>
    <text x="600" y="1412" fill="#18314E" font-size="32" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" font-weight="700">{_escape(_truncate_text(token_value, 22))}</text>
  </g>

  <line x1="318" y1="1476" x2="882" y2="1476" stroke="#D4DDE6" stroke-width="2"/>
  <text x="600" y="1524" fill="#72889C" font-size="17" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">{_escape(f'持有人 · {display_name}　　生成时间 · {generated_at}')}</text>
</svg>
"""


def _panel(x: int, y: int, width: int, height: int, title: str, value: str, caption: str | None = None) -> str:
    value_lines = _wrap_text(value, 12, limit=2)
    title_y = y + 30
    value_y = y + 68
    caption_y = y + height - 28
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="22" fill="#FFF9ED" fill-opacity="0.42" stroke="#A46A2B" stroke-opacity="0.22" stroke-width="2"/>
    <text x="{x + 24}" y="{title_y}" fill="#7A471F" font-size="18" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">{_escape(title)}</text>
    {_text_lines(value_lines, x=x + 24, y=value_y, font_size=26, line_height=30, fill="#3F1F10", anchor="start", family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif", weight="700")}
    {_caption_line(caption, x + 24, caption_y, width_units=18)}
  </g>"""


def _caption_line(text: str | None, x: int, y: int, width_units: int = 16) -> str:
    if not text:
        return ""
    return _text_lines(
        _wrap_text(_truncate_text(text, width_units * 2), width_units, limit=2),
        x=x,
        y=y,
        font_size=14,
        line_height=16,
        fill="#7D5435",
        anchor="start",
        family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif",
    )


def _meta_chip(x: int, y: int, width: int, title: str, value: str, dark: bool = False) -> str:
    fill = "#DDBB7A" if dark else "#FFF7EA"
    fill_opacity = "0.28" if dark else "0.82"
    title_fill = "#6F4826"
    value_fill = "#3E2211"
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="52" rx="16" fill="{fill}" fill-opacity="{fill_opacity}" stroke="#A56A2A" stroke-opacity="0.24" stroke-width="1.5"/>
    <text x="{x + 18}" y="{y + 32}" fill="{title_fill}" font-size="16" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">{_escape(title)}</text>
    <text x="{x + width - 18}" y="{y + 32}" fill="{value_fill}" font-size="18" text-anchor="end" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">{_escape(_truncate_text(value, 20))}</text>
  </g>"""


def _cert_meta_chip(x: int, y: int, width: int, title: str, value: str, bg: str, border: str, text: str) -> str:
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="52" rx="16" fill="{bg}" fill-opacity="0.99" stroke="{border}" stroke-opacity="0.24" stroke-width="1.5"/>
    <text x="{x + 18}" y="{y + 32}" fill="#50657B" font-size="16" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif">{_escape(title)}</text>
    <text x="{x + width - 18}" y="{y + 32}" fill="{text}" font-size="18" text-anchor="end" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif">{_escape(_truncate_text(value, 20))}</text>
  </g>"""


def _text_lines(
    lines: list[str],
    *,
    x: int,
    y: int,
    font_size: int,
    line_height: int,
    fill: str,
    anchor: str,
    family: str,
    weight: str = "400",
) -> str:
    if not lines:
        return ""
    parts = [f'<text x="{x}" y="{y}" fill="{fill}" font-size="{font_size}" text-anchor="{anchor}" font-family="{family}" font-weight="{weight}">']
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        parts.append(f'<tspan x="{x}" dy="{dy}">{_escape(line)}</tspan>')
    parts.append("</text>")
    return "".join(parts)


def _wrap_text(text: str, max_units: float, limit: int | None = None) -> list[str]:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return []
    lines: list[str] = []
    current = ""
    current_units = 0.0
    for char in cleaned:
        char_units = _char_units(char)
        if current and current_units + char_units > max_units:
            lines.append(current)
            current = char
            current_units = char_units
            if limit and len(lines) >= limit:
                break
            continue
        current += char
        current_units += char_units
    if current and (not limit or len(lines) < limit):
        lines.append(current)
    if limit and len(lines) > limit:
        lines = lines[:limit]
    if limit and lines and len(lines) == limit and sum(_char_units(ch) for ch in cleaned) > sum(_char_units(ch) for line in lines for ch in line):
        lines[-1] = _truncate_text(lines[-1], max(2, int(max_units) - 2))
    return lines


def _truncate_text(text: str, limit_units: int) -> str:
    total = 0.0
    result = []
    for char in text:
        units = _char_units(char)
        if total + units > limit_units:
            result.append("…")
            break
        result.append(char)
        total += units
    return "".join(result)


def _char_units(char: str) -> float:
    if char.isspace():
        return 0.35
    if ord(char) < 128:
        return 0.58
    return 1.0


def _metric_extremes(metrics: object) -> dict[str, dict[str, object]]:
    items = [item for item in _as_list(metrics) if isinstance(item, dict) and "score" in item]
    if not items:
        return {
            "top": {"name": "未定", "score": 0},
            "low": {"name": "未定", "score": 0},
        }
    ordered = sorted(items, key=lambda item: int(item.get("score", 0)), reverse=True)
    return {"top": ordered[0], "low": ordered[-1]}


def _extract_models(payload: dict[str, object]) -> list[str]:
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        models = transcript.get("models")
        if isinstance(models, list):
            return [str(item) for item in models if item]
    models = payload.get("models")
    if isinstance(models, list):
        return [str(item) for item in models if item]
    return []


def _extract_token_total(payload: dict[str, object]) -> int:
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        token_usage = transcript.get("token_usage")
        if isinstance(token_usage, dict):
            return int(token_usage.get("total_tokens", 0) or 0)
    token_usage = payload.get("token_usage")
    if isinstance(token_usage, dict):
        return int(token_usage.get("total_tokens", 0) or 0)
    return 0


def _get_display_name(payload: dict[str, object], track: str) -> str:
    transcript = payload.get("transcript")
    if isinstance(transcript, dict) and transcript.get("display_name"):
        return str(transcript["display_name"])
    if payload.get("display_name"):
        return str(payload["display_name"])
    return default_display_name(track)


def _format_generated_at(value: object) -> str:
    text = str(value or "").strip()
    return text.replace("T", " ").replace("+08:00", "").replace("+00:00", " UTC")


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _as_list(value: object) -> list:
    return value if isinstance(value, list) else []


def _first_line(items: list[object], fallback: str) -> str:
    if not items:
        return fallback
    return str(items[0])


def _fmt_int(value: int) -> str:
    return f"{int(value):,}"


def _short_model_name(value: str) -> str:
    if not value:
        return "未识炉主"
    cleaned = value.replace("openai/", "").replace("anthropic/", "")
    return _truncate_text(cleaned, 16)


def _xianxia_period_label(payload: dict[str, object]) -> str:
    window = _as_dict(payload.get("time_window"))
    since = window.get("since")
    until = window.get("until")
    if since or until:
        return f"{since or '最早'} 至 {until or '现在'}"
    sessions_used = payload.get("sessions_used")
    if isinstance(sessions_used, int) and sessions_used > 1:
        return f"{sessions_used} 场会话"
    return "此番问答"


def _certificate_period_label(payload: dict[str, object]) -> str:
    window = _as_dict(payload.get("time_window"))
    since = window.get("since")
    until = window.get("until")
    if since or until:
        return f"{since or '最早'} 至 {until or '现在'}"
    sessions_used = payload.get("sessions_used")
    if isinstance(sessions_used, int) and sessions_used > 1:
        return f"{sessions_used} 场会话累计"
    return "本次记录"


def _ability_text(level: str, value: str) -> str:
    mapped = AI_LEVEL_ABILITIES.get(level)
    if mapped:
        return mapped
    cleaned = " ".join(value.split())
    if not cleaned:
        return "完成当前等级对应的协作任务"
    if cleaned.startswith("已经能"):
        return cleaned[3:]
    if cleaned.startswith("能"):
        return cleaned[1:]
    if cleaned.startswith("开始把"):
        return "把" + cleaned[3:]
    if cleaned.startswith("开始拥有"):
        return "拥有" + cleaned[4:]
    if cleaned.startswith("开始"):
        return cleaned[2:]
    cleaned = cleaned.replace("workflow", "流程").replace("skill", "技法").replace("agent", "分身").replace("SOP", "章法")
    return cleaned


def _assistant_verdict_lines(payload: dict[str, object], ability: str) -> list[str]:
    metrics = [item for item in _as_list(payload.get("assistant_metrics")) if isinstance(item, dict)]
    message_count = _extract_message_count(payload)
    tool_calls = _extract_tool_calls(payload)
    token_total = _fmt_int(_extract_token_total(payload))
    if not metrics:
        return [
            f"已能{ability}。",
            "当前协作强度已可稳定承接。",
            f"本轮 {message_count} 条消息，{tool_calls} 次工具，{token_total} 枚令牌。",
        ]
    ordered = sorted(metrics, key=lambda item: int(item.get("score", 0)), reverse=True)
    top = ordered[0]
    low = ordered[-1]
    top_name_raw = str(top.get("name") or "")
    low_name_raw = str(low.get("name") or "")
    top_name = ASSISTANT_METRIC_LABELS.get(top_name_raw, top_name_raw or "强项")
    low_name = ASSISTANT_METRIC_LABELS.get(low_name_raw, low_name_raw or "短板")
    return [
        f"已能{ability}。",
        f"{top_name}更稳，{_metric_behavior(top_name_raw, 'strong', track='assistant')}。",
        f"{low_name}偏弱，{_metric_behavior(low_name_raw, 'weak', track='assistant')}。",
        f"本轮 {message_count} 条消息，{tool_calls} 次工具，{token_total} 枚令牌。",
    ]


def _user_portrait_verdict_lines(payload: dict[str, object], level: str, fallback: str) -> list[str]:
    metrics = [item for item in _as_list(payload.get("user_metrics")) if isinstance(item, dict)]
    if not metrics:
        return _wrap_text(fallback, 20, limit=4)
    ordered = sorted(metrics, key=lambda item: int(item.get("score", 0)), reverse=True)
    top = ordered[0]
    low = ordered[-1]
    message_count = _extract_message_count(payload)
    tool_calls = _extract_tool_calls(payload)
    token_total = _fmt_int(_extract_token_total(payload))
    top_name_raw = str(top.get("name") or "")
    low_name_raw = str(low.get("name") or "")
    top_name = XI_METRIC_NAMES.get(top_name_raw, top_name_raw or "长处")
    low_name = XI_WEAK_METRIC_NAMES.get(low_name_raw, low_name_raw or "关隘")
    return [
        f"照此行迹，已至{level}之境。",
        f"{top_name}已成气候，{_metric_behavior(top_name_raw, 'strong', track='user')}。",
        f"{low_name}未稳，{_metric_behavior(low_name_raw, 'weak', track='user')}。",
        f"此番 {message_count} 条对话，{tool_calls} 次分身，耗去 {token_total} 枚灵气。",
    ]


def _extract_message_count(payload: dict[str, object]) -> int:
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        return int(transcript.get("message_count", 0) or 0)
    return int(payload.get("total_messages", 0) or 0)


def _extract_tool_calls(payload: dict[str, object]) -> int:
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        return int(transcript.get("tool_calls", 0) or 0)
    return int(payload.get("total_tool_calls", 0) or 0)


def _metric_behavior(name: str, polarity: str, track: str) -> str:
    mapping = USER_BEHAVIOR_TEXT if track == "user" else ASSISTANT_BEHAVIOR_TEXT
    item = mapping.get(name, {})
    text = item.get(polarity)
    if text:
        return text
    return "当前样本仍需继续观察"


def _escape(value: str) -> str:
    return escape(value, quote=True)


def _card_subtitle(value: str) -> str:
    cleaned = " ".join(value.split())
    cleaned = cleaned.replace("skill", "技法").replace("workflow", "流程").replace("prompt", "提示法").replace("agent", "分身")
    cleaned = cleaned.replace("模板", "章法").replace("模块", "法门").replace("SOP", "章法")
    cleaned = cleaned.replace(" / ", "、")
    return cleaned


def _xianxia_guidance_text(text: str) -> str:
    cleaned = " ".join((text or "").split())
    replacements = {
        "验证命令或可观察结果": "看见实证",
        "验证命令": "看见实证",
        "可观察结果": "看见实证",
        "目标 + 约束 + 输出物 + 验收": "先定目标、边界与成法",
        "关键文件、路径、模型、运行方式": "把来路与条件先备齐",
        "连续会话里重复目标名词": "反复守住题眼",
        "缩小范围，改成最小可用版本再突破": "先收束，再图突破",
        "让 AI 先报第一步，再做实现，避免空泛总结": "先落第一子，再徐徐推进",
        "鼓励 AI 先读仓库、跑命令、看真实日志，再给方案": "先探来路，再定章法",
        "要求 AI 说明“改了什么、怎么验、哪里还没验”": "每次收功，都把变化与结果说清",
    }
    for src, dst in replacements.items():
        cleaned = cleaned.replace(src, dst)
    return cleaned


def _render_png(svg_path: Path, png_path: Path) -> None:
    subprocess.run(
        [
            "rsvg-convert",
            "--dpi-x",
            "300",
            "--dpi-y",
            "300",
            str(svg_path),
            "-o",
            str(png_path),
        ],
        check=True,
    )
    subprocess.run(
        [
            "sips",
            "-s",
            "dpiWidth",
            "300",
            "-s",
            "dpiHeight",
            "300",
            str(png_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
