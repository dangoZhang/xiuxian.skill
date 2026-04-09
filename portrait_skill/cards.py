from __future__ import annotations

from html import escape
from pathlib import Path

from .parsers import default_display_name
from .themes import get_ai_level_theme
from .xianxia import derive_xianxia_profile

XI_METRIC_NAMES = {
    "目标清晰度": "心法清明",
    "上下文供给": "根基稳固",
    "迭代修正力": "吐纳绵长",
    "验收意识": "收功自验",
    "协作节奏": "同修合拍",
    "执行落地": "法诀沉稳",
    "工具调度": "御器有度",
    "验证闭环": "收束成环",
    "上下文承接": "承气不断",
    "补救适配": "转圜有余",
}

XI_WEAK_METRIC_NAMES = {
    "目标清晰度": "心法未定",
    "上下文供给": "根基浮动",
    "迭代修正力": "吐纳不匀",
    "验收意识": "收功松散",
    "协作节奏": "同修失序",
    "执行落地": "法诀虚浮",
    "工具调度": "御器未熟",
    "验证闭环": "收束松散",
    "上下文承接": "承气断续",
    "补救适配": "转圜迟缓",
}

AI_LEVEL_ABILITIES = {
    "L1": "完成单轮问答",
    "L2": "感知提问方式对结果的影响",
    "L3": "稳定完成简单任务",
    "L4": "重复跑通常见 workflow",
    "L5": "把经验封成模板或 skill",
    "L6": "先替你推进一段具体工作",
    "L7": "协同多个 agent 与工具完成任务",
    "L8": "承担能力层与系统层工作",
    "L9": "进入真实业务回路并持续回流",
    "L10": "把方法复制到团队与客户场景",
}


def write_cards(payload: dict[str, object], output_dir: str | Path, certificate_choice: str = "both") -> dict[str, str]:
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    if certificate_choice in {"user", "both"} and payload.get("user_certificate"):
        path = target_dir / "portrait-user.svg"
        path.write_text(render_user_portrait_card(payload), encoding="utf-8")
        written["user"] = str(path)
    if certificate_choice in {"assistant", "both"} and payload.get("assistant_certificate"):
        path = target_dir / "portrait-assistant.svg"
        path.write_text(render_assistant_certificate_card(payload), encoding="utf-8")
        written["assistant"] = str(path)
    return written


def render_user_portrait_card(payload: dict[str, object]) -> str:
    certificate = _as_dict(payload.get("user_certificate"))
    persona = _as_dict(certificate.get("persona"))
    display_name = _get_display_name(payload, track="user")
    generated_at = _format_generated_at(payload.get("generated_at"))
    level = str(certificate.get("level", "凡人"))
    summary = str(persona.get("summary") or "")
    subtitle = str(persona.get("subtitle") or "")
    growth_value = _first_line(_as_list(certificate.get("growth_plan")), fallback="再炼一轮，稳住当前气脉，再冲下一境。")
    card_terms = derive_xianxia_profile(payload)[:6]
    while len(card_terms) < 6:
        card_terms.append({"term": "未显", "value": "气机待定", "detail": ""})

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

  <text x="600" y="232" fill="url(#ink)" font-size="34" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif" letter-spacing="4">画像.skill</text>
  <text x="600" y="308" fill="url(#ink)" font-size="102" text-anchor="middle" font-family="STKaiti, KaiTi, serif">修仙画像</text>
  <text x="600" y="356" fill="#7A461F" font-size="23" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">{_escape(subtitle or "观卷知命，照见此身灵根、气海与关隘")}</text>
  {_meta_chip(266, 386, 278, "道号", _truncate_text(display_name, 14), dark=True)}
  {_meta_chip(656, 386, 278, "生成时间", generated_at)}

  <g>
    <circle cx="600" cy="552" r="134" fill="#6A2E13" fill-opacity="0.06" stroke="#7F3415" stroke-width="3"/>
    <circle cx="600" cy="552" r="106" stroke="#8B3C19" stroke-opacity="0.28" stroke-width="2" stroke-dasharray="8 10"/>
    <text x="600" y="540" fill="#532410" font-size="98" text-anchor="middle" font-family="STKaiti, KaiTi, serif">{_escape(level)}</text>
    <text x="600" y="590" fill="#7B471F" font-size="22" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif" letter-spacing="5">当前境界</text>
  </g>

  <g>
    <rect x="262" y="712" width="676" height="158" rx="24" fill="#FFF6E6" fill-opacity="0.42" stroke="#A56A2A" stroke-opacity="0.18" stroke-width="2"/>
    <text x="600" y="756" fill="#8A562D" font-size="20" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif" letter-spacing="3">观气判词</text>
    {_text_lines(_wrap_text(summary, 24, limit=3), x=600, y=806, font_size=26, line_height=34, fill="#5B2A12", anchor="middle", family="STKaiti, KaiTi, serif", weight="700")}
  </g>

  {_panel(262, 918, 304, 134, str(card_terms[0]["term"]), str(card_terms[0]["value"]), caption=str(card_terms[0].get("detail") or ""))}
  {_panel(634, 918, 304, 134, str(card_terms[1]["term"]), str(card_terms[1]["value"]), caption=str(card_terms[1].get("detail") or ""))}
  {_panel(262, 1080, 304, 134, str(card_terms[2]["term"]), str(card_terms[2]["value"]), caption=str(card_terms[2].get("detail") or ""))}
  {_panel(634, 1080, 304, 134, str(card_terms[3]["term"]), str(card_terms[3]["value"]), caption=str(card_terms[3].get("detail") or ""))}
  {_panel(262, 1242, 304, 134, str(card_terms[4]["term"]), str(card_terms[4]["value"]), caption=str(card_terms[4].get("detail") or ""))}
  {_panel(634, 1242, 304, 134, str(card_terms[5]["term"]), str(card_terms[5]["value"]), caption=str(card_terms[5].get("detail") or ""))}

  <g>
    <rect x="262" y="1406" width="676" height="50" rx="16" fill="#6E3114" fill-opacity="0.08"/>
    <text x="294" y="1438" fill="#6B3417" font-size="18" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">破境机缘：{_escape(_truncate_text(growth_value, 30))}</text>
  </g>

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
    token_value = f"{_certificate_period_label(payload)} 消耗 {_fmt_int(_extract_token_total(payload))} token"

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

  <text x="600" y="234" fill="{_escape(str(theme.get('muted', '#7F96B9')))}" font-size="32" text-anchor="middle" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif" letter-spacing="3">画像.skill</text>
  <text x="600" y="314" fill="#10263A" font-size="74" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" font-weight="700">AI 协作能力证书</text>
  <text x="600" y="362" fill="#5E7287" font-size="23" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">真实会话稳定定级</text>
  {_cert_meta_chip(258, 388, 312, "持有人", _truncate_text(display_name, 16), "#EAF1FF", "#315FBC", "#18314E")}
  {_cert_meta_chip(630, 388, 312, "生成时间", generated_at, "#EAF1FF", "#315FBC", "#425B73")}

  <g>
    <rect x="258" y="462" width="684" height="664" rx="42" fill="{_escape(str(theme.get('panel_bg', '#162B49')))}"/>
    <rect x="286" y="490" width="628" height="608" rx="32" stroke="{_escape(str(theme.get('accent', '#7EAEFF')))}" stroke-opacity="0.32" stroke-width="2"/>
    <text x="600" y="680" fill="{_escape(str(theme.get('accent', '#7EAEFF')))}" font-size="236" text-anchor="middle" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif" font-weight="800">{_escape(level)}</text>
    <text x="600" y="748" fill="#ECF2F8" font-size="26" text-anchor="middle" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif" letter-spacing="6">CURRENT LEVEL</text>
    <line x1="360" y1="822" x2="840" y2="822" stroke="{_escape(str(theme.get('accent', '#7EAEFF')))}" stroke-opacity="0.16" stroke-width="2"/>
    <text x="600" y="884" fill="#A6B7C8" font-size="22" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">能够</text>
    {_text_lines(_wrap_text(ability, 16, limit=2), x=600, y=944, font_size=38, line_height=46, fill="#F5F8FB", anchor="middle", family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif", weight="700")}
    <rect x="332" y="1010" width="536" height="76" rx="20" fill="#FFFFFF" fill-opacity="0.06"/>
    <text x="600" y="1058" fill="#C3D0DB" font-size="24" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">{_escape(token_value)}</text>
  </g>

  <line x1="318" y1="1248" x2="882" y2="1248" stroke="#D4DDE6" stroke-width="2"/>
  <text x="600" y="1306" fill="#72889C" font-size="20" text-anchor="middle" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif">画像.skill · Certified Collaboration Level</text>
</svg>
"""


def _panel(x: int, y: int, width: int, height: int, title: str, value: str, caption: str | None = None) -> str:
    value_lines = _wrap_text(value, 11, limit=2)
    title_y = y + 34
    value_y = y + 72
    caption_y = y + height - 22
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="22" fill="#FFF9ED" fill-opacity="0.24" stroke="#A46A2B" stroke-opacity="0.18" stroke-width="2"/>
    <text x="{x + 22}" y="{title_y}" fill="#8C5B31" font-size="19" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">{_escape(title)}</text>
    {_text_lines(value_lines, x=x + 22, y=value_y, font_size=28, line_height=32, fill="#4F2812", anchor="start", family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif", weight="700")}
    {_caption_line(caption, x + 26, caption_y)}
  </g>"""


def _caption_line(text: str | None, x: int, y: int) -> str:
    if not text:
        return ""
    return _text_lines(
        _wrap_text(text, 16, limit=2),
        x=x,
        y=y,
        font_size=16,
        line_height=18,
        fill="#8C5A31",
        anchor="start",
        family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif",
    )


def _meta_chip(x: int, y: int, width: int, title: str, value: str, dark: bool = False) -> str:
    fill = "#6D3318" if dark else "#FFF7EA"
    fill_opacity = "0.10" if dark else "0.42"
    title_fill = "#9B6A3E" if dark else "#8B5A31"
    value_fill = "#5A2812" if dark else "#6B3518"
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="44" rx="14" fill="{fill}" fill-opacity="{fill_opacity}" stroke="#A56A2A" stroke-opacity="0.16" stroke-width="1.5"/>
    <text x="{x + 18}" y="{y + 28}" fill="{title_fill}" font-size="16" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">{_escape(title)}</text>
    <text x="{x + width - 18}" y="{y + 28}" fill="{value_fill}" font-size="18" text-anchor="end" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, serif">{_escape(_truncate_text(value, 18))}</text>
  </g>"""


def _cert_meta_chip(x: int, y: int, width: int, title: str, value: str, bg: str, border: str, text: str) -> str:
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="46" rx="14" fill="{bg}" fill-opacity="0.88" stroke="{border}" stroke-opacity="0.18" stroke-width="1.5"/>
    <text x="{x + 18}" y="{y + 29}" fill="#72889C" font-size="16" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif">{_escape(title)}</text>
    <text x="{x + width - 18}" y="{y + 29}" fill="{text}" font-size="18" text-anchor="end" font-family="Inter, PingFang SC, Microsoft YaHei, sans-serif">{_escape(_truncate_text(value, 18))}</text>
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
    return "本次卷宗"


def _certificate_period_label(payload: dict[str, object]) -> str:
    window = _as_dict(payload.get("time_window"))
    since = window.get("since")
    until = window.get("until")
    if since or until:
        return f"{since or '最早'} 至 {until or '现在'}"
    sessions_used = payload.get("sessions_used")
    if isinstance(sessions_used, int) and sessions_used > 1:
        return f"{sessions_used} 场会话累计"
    return "本次卷宗"


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
    return cleaned


def _escape(value: str) -> str:
    return escape(value, quote=True)
