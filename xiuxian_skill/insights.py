from __future__ import annotations

from .models import Analysis, Certificate, Message

USER_BEHAVIOR_TEXT = {
    "目标清晰度": {
        "strong": "开头就能把想做什么说清楚",
        "weak": "目标还不够收束，AI 需要边做边猜",
    },
    "上下文供给": {
        "strong": "路径、背景和边界给得够，AI 更容易直接落地",
        "weak": "背景和边界给得偏少，AI 容易在细节上反复确认",
    },
    "迭代修正力": {
        "strong": "发现方向偏了会立刻补充要求，把任务拉回正轨",
        "weak": "发现偏航后的修正还不够快，容易在错误方向上多走几步",
    },
    "验收意识": {
        "strong": "会主动要结果、证据和验证方式",
        "weak": "还不够主动要证据和验收，容易停在“看起来差不多”",
    },
    "协作节奏": {
        "strong": "一来一回接得顺，事情能持续往前推",
        "weak": "往返节奏还不够稳，容易在中途掉线",
    },
}

ASSISTANT_BEHAVIOR_TEXT = {
    "执行落地": {
        "strong": "能先动手，再汇报，推进感比较强",
        "weak": "还有停在解释里的时候，落地速度不够稳定",
    },
    "工具调度": {
        "strong": "会主动读文件、跑命令、查信息，能把工具真正用起来",
        "weak": "工具调用还不够积极，很多本可直接验证的事没有立刻去做",
    },
    "验证闭环": {
        "strong": "会说明改了什么、怎么验证、还有什么没验",
        "weak": "对“改了什么、怎么验证、还有什么没验”交代得还不够完整",
    },
    "上下文承接": {
        "strong": "能续住主线，不容易跑偏",
        "weak": "回合一长就容易丢主线，承接还不够稳",
    },
    "补救适配": {
        "strong": "遇到阻力会缩范围、换打法、继续推进",
        "weak": "遇到阻力后的调整还不够快",
    },
}

USER_CARD_BEHAVIOR_TEXT = {
    "目标清晰度": {"strong": "开头能说清要做什么", "weak": "目标还不够收束"},
    "上下文供给": {"strong": "背景和边界给得够", "weak": "背景和边界还给得不够"},
    "迭代修正力": {"strong": "发现偏了会及时补要求", "weak": "偏了以后补得还不够快"},
    "验收意识": {"strong": "会主动盯验证和证据", "weak": "还不够主动要证据和验收"},
    "协作节奏": {"strong": "一来一回接得顺", "weak": "往返节奏还不够稳"},
}

ASSISTANT_CARD_BEHAVIOR_TEXT = {
    "执行落地": {"strong": "会先动手再汇报", "weak": "落地速度还不够稳"},
    "工具调度": {"strong": "会主动用工具推进", "weak": "工具用得还不够积极"},
    "验证闭环": {"strong": "会把验证和回报交代清楚", "weak": "对“改了什么、怎么验证、还有什么没验”交代得还不够完整"},
    "上下文承接": {"strong": "能续住主线不乱跑", "weak": "回合一长容易丢主线"},
    "补救适配": {"strong": "遇阻也会换路继续推", "weak": "遇阻后的调整还不够快"},
}

USER_XIANXIA_STRONG = {
    "目标清晰度": "目标表达",
    "上下文供给": "上下文铺垫",
    "迭代修正力": "迭代修正",
    "验收意识": "结果验证",
    "协作节奏": "协作节奏",
}

USER_XIANXIA_WEAK = {
    "目标清晰度": "目标表达",
    "上下文供给": "上下文铺垫",
    "迭代修正力": "迭代修正",
    "验收意识": "结果验证",
    "协作节奏": "协作节奏",
}

ASSISTANT_XIANXIA = {
    "执行落地": "执行推进",
    "工具调度": "工具调用",
    "验证闭环": "回看确认",
    "上下文承接": "上下文承接",
    "补救适配": "补救适配",
}

USER_AI_TERMS = {
    "目标清晰度": "目标表达",
    "上下文供给": "上下文信息",
    "迭代修正力": "迭代修正",
    "验收意识": "结果验证",
    "协作节奏": "协作节奏",
}

ASSISTANT_AI_TERMS = {
    "执行落地": "执行推进",
    "工具调度": "工具调用",
    "验证闭环": "回看确认",
    "上下文承接": "上下文承接",
    "补救适配": "补救适配",
}

ABILITY_LIBRARY = {
    "L1": "还停留在单轮提问，能把问题问出去，但大多还要靠反复试。",
    "L2": "开始会调 prompt 了，知道换一种问法，回答就会跟着变。",
    "L3": "能独立跑完小任务，也会根据结果继续补充要求，把事做成。",
    "L4": "已经会把常见来回沉淀成工作流，熟悉的任务通常能沿着上下文稳定推进到多步完成。",
    "L5": "会把重复打法炼成可复用套路，同类问题不必每次都从零开始。",
    "L6": "会让 AI 先代做一段，再回来核对方向和结果，协作已经开始成形。",
    "L7": "能同时调动多 Agent 和工具，把一件完整差事拆开并行推进。",
    "L8": "开始设计能力和流程，不只是在完成任务，而是在搭一套可持续的方法。",
    "L9": "能把这套协作带进真实项目，边做边根据反馈修正方法。",
    "L10": "能把自己的方法传给团队，让别人也能复现同样的推进质量。",
}

CARD_ABILITY_LIBRARY = {
    "L1": "还停留在单轮提问，更多时候还要靠反复试。",
    "L2": "已经会调 prompt，知道换一种问法，回答就会变。",
    "L3": "能跑完小任务，也会根据结果继续补充要求。",
    "L4": "已经会把常见来回沉淀成工作流，熟悉任务通常能稳定推进到多步完成。",
    "L5": "会把重复打法炼成可复用套路，同类问题不必每次从零开始。",
    "L6": "会让 AI 先代做一段，再回来核对方向和结果。",
    "L7": "能同时调动多 Agent 和工具，把一件完整差事拆开并行推进。",
    "L8": "开始设计能力和流程，正在搭一套可持续的方法。",
    "L9": "能把这套协作带进真实项目，并根据反馈持续修正。",
    "L10": "能把自己的方法传给团队，让别人也能稳定复现。",
}

CARD_VERDICT_LIBRARY = {
    "L1": "这一层还在摸门，能问出问题，但稳定性还没真正出来。",
    "L2": "这一层开始知道问法会改结果，已经脱离纯撞运气。",
    "L3": "这一层已经能独立做成小事，也知道边做边补要求。",
    "L4": "这一层已经会把常见来回沉淀成工作流，熟悉任务通常能稳定推进到多步完成。",
    "L5": "这一层开始有自己的套路，同类任务不必每次都从零起手。",
    "L6": "这一层已经懂得让 AI 先做一段，再回来收方向和结果。",
    "L7": "这一层已经能同时调动多 Agent 和工具，把整件事拆开并行推进。",
    "L8": "这一层开始搭方法、搭流程，重心已经不只是一件件做任务。",
    "L9": "这一层能把协作带进真实项目，并根据反馈持续修正做法。",
    "L10": "这一层已经能把方法沉淀下来，再稳定复制给团队使用。",
}

IMAGE_CONCEPT_GROUPS = {
    "版式层级": ["标题", "副题", "小标题", "布局", "排版", "层级", "留白", "对齐", "间距", "框", "边框", "面板", "位置"],
    "文字可读": ["重叠", "可读", "看不清", "清晰", "字号", "字色", "颜色", "配色", "字距", "换行"],
    "修仙叙事": ["修仙", "境界", "灵根", "判词", "符箓", "修炼", "画像", "证书", "修仙小说"],
    "分享传播": ["png", "svg", "dpi", "readme", "预览", "分享", "社交", "海报", "爆款"],
    "生图约束": ["生图", "prompt", "生成", "图片", "框的位置", "最后一行", "风格", "样式"],
}

IMAGE_CONCEPT_NOTES = {
    "版式层级": "宣传图更看重一眼识别与稳定层级，标题、主字、正文和底部信息必须分明。",
    "文字可读": "用户持续强调清晰、留白和安全边距，卡片必须保证小字可读、正文不压框。",
    "修仙叙事": "世界观要贴近常见修仙小说语汇，重点是境界、功法、破境，不可乱造设定。",
    "分享传播": "这张卡既是评测结果，也是可晒图的社交物料，需优先照顾转发时的辨识度。",
    "生图约束": "如果交给模型生图，必须明确最后一行文字下方仍要保留完整安全边距。",
}

COACHING_PLAYBOOK = {
    "目标清晰度": {
        "focus": "起手先把目标写成一句清楚的话，别让 AI 自己猜主线。",
        "drill": "每次开局前先写三行：目标、边界、验收，再让 AI 开始做。",
        "prompt": "先别展开实现，先帮我把这次任务整理成：目标、边界、输出物、验收标准。",
    },
    "上下文供给": {
        "focus": "先把路径、环境、日志和约束给够，后面会顺很多。",
        "drill": "下一轮开局固定附上文件路径、运行环境、相关报错和已有尝试。",
        "prompt": "我先给你完整上下文，你先复述关键信息，再开始动手。",
    },
    "迭代修正力": {
        "focus": "别等偏太远才回头，看到苗头不对就立刻补要求。",
        "drill": "每轮看到结果不对时，只补一条最关键修正，别一次塞太多。",
        "prompt": "先基于刚才结果，指出偏差最大的地方，再按这个点重做一轮。",
    },
    "验收意识": {
        "focus": "把“看起来差不多”改成“拿出证据再算完成”。",
        "drill": "每轮结束都追问一次：证据在哪，怎么验的，还有什么没验。",
        "prompt": "这轮先别总结，先给我验证结果、验证方式，以及还没验证的部分。",
    },
    "协作节奏": {
        "focus": "保持短回合推进，一轮只解决一个最关键问题。",
        "drill": "把任务拆成 2 到 4 个连续小回合，每回合只追一个目标。",
        "prompt": "把这件事拆成三个连续回合，我们一次只推进一个最关键问题。",
    },
    "执行落地": {
        "focus": "优先让 AI 动手，而不是先写一大段解释。",
        "drill": "每轮开头都明确要求：先做、再验、最后回报。",
        "prompt": "直接开始做，先别讲大段方案。做完后告诉我改了什么、怎么验证的。",
    },
    "工具调度": {
        "focus": "能读文件、跑命令、看日志的事，就别靠猜。",
        "drill": "只要涉及代码或环境，第一轮先要求 AI 读取文件、运行命令、检查日志。",
        "prompt": "先读相关文件并跑一遍必要命令，再给我判断，不要只凭经验猜。",
    },
    "验证闭环": {
        "focus": "把收尾补全，别停在“改完了”，要停在“证实了”。",
        "drill": "每轮结尾固定追问三件事：改了什么、怎么验证、还有什么风险。",
        "prompt": "收尾时固定按这三项回报：改了什么、怎么验证、还有什么没验或有风险。",
    },
    "上下文承接": {
        "focus": "长回合里反复点名主线，防止 AI 漂走。",
        "drill": "每两轮重申一次当前目标和不该动的边界。",
        "prompt": "先用两句话复述当前主线和边界，确认没跑偏再继续。",
    },
    "补救适配": {
        "focus": "遇阻时快速缩范围、换打法，不要原地拧。",
        "drill": "出现阻塞时，先让 AI 提三个缩范围方案，再选最短路径继续。",
        "prompt": "现在卡住了，先给我三个最省时间的绕开方案，再选一个继续推进。",
    },
}


def build_analysis_insights(analysis: Analysis) -> dict[str, object]:
    return _build_insights(
        messages=analysis.transcript.messages,
        user_metrics=analysis.user_metrics,
        assistant_metrics=analysis.assistant_metrics,
        user_certificate=analysis.user_certificate,
        assistant_certificate=analysis.assistant_certificate,
        total_messages=len(analysis.transcript.messages),
        tool_calls=analysis.transcript.tool_calls,
        total_tokens=analysis.transcript.token_usage.total_tokens,
    )


def build_aggregate_insights(analyses: list[Analysis], aggregate: dict[str, object]) -> dict[str, object]:
    messages = [message for analysis in analyses for message in analysis.transcript.messages]
    return _build_insights(
        messages=messages,
        user_metrics=aggregate.get("user_metrics", []),
        assistant_metrics=aggregate.get("assistant_metrics", []),
        user_certificate=aggregate.get("user_certificate", {}),
        assistant_certificate=aggregate.get("assistant_certificate", {}),
        total_messages=int(aggregate.get("total_messages", 0) or 0),
        tool_calls=int(aggregate.get("total_tool_calls", 0) or 0),
        total_tokens=int(_as_dict(aggregate.get("token_usage")).get("total_tokens", 0) or 0),
    )


def _build_insights(
    *,
    messages: list[Message],
    user_metrics,
    assistant_metrics,
    user_certificate,
    assistant_certificate,
    total_messages: int,
    tool_calls: int,
    total_tokens: int,
) -> dict[str, object]:
    user_items = _metric_items(user_metrics)
    assistant_items = _metric_items(assistant_metrics)
    user_top, user_low = _top_and_low(user_items)
    assistant_top, assistant_low = _top_and_low(assistant_items)
    image_concepts = _image_concepts(messages)

    realm = _certificate_value(user_certificate, "level", "凡人")
    rank = _certificate_value(assistant_certificate, "level", "L1")
    level_ability_text = _ability_text(rank)
    card_level_ability_text = _card_ability_text(rank)
    user_top_name = USER_XIANXIA_STRONG.get(user_top["name"], user_top["name"])
    user_low_name = USER_XIANXIA_WEAK.get(user_low["name"], user_low["name"])
    assistant_top_name = ASSISTANT_XIANXIA.get(assistant_top["name"], assistant_top["name"])
    assistant_low_name = ASSISTANT_XIANXIA.get(assistant_low["name"], assistant_low["name"])

    ability_text = _compose_ability_summary(
        level_text=level_ability_text,
        user_top_name=user_top_name,
        assistant_top_name=assistant_top_name,
        user_low_name=user_low_name,
        assistant_low_name=assistant_low_name,
        user_top_text=_metric_behavior(user_top["name"], "strong", track="user"),
        assistant_top_text=_metric_behavior(assistant_top["name"], "strong", track="assistant"),
        user_low_text=_metric_behavior(user_low["name"], "weak", track="user"),
        assistant_low_text=_metric_behavior(assistant_low["name"], "weak", track="assistant"),
    )
    card_ability_text = _compose_card_ability_summary(
        level_text=card_level_ability_text,
        user_top_name=user_top_name,
        assistant_top_name=assistant_top_name,
        user_low_name=user_low_name,
        assistant_low_name=assistant_low_name,
        user_top_text=_metric_card_behavior(user_top["name"], "strong", track="user"),
        assistant_top_text=_metric_card_behavior(assistant_top["name"], "strong", track="assistant"),
        user_low_text=_metric_card_behavior(user_low["name"], "weak", track="user"),
        assistant_low_text=_metric_card_behavior(assistant_low["name"], "weak", track="assistant"),
    )
    verdict_lines = [
        f"这轮样本看下来，你现在落在{realm}，对应 {rank}。",
        _card_verdict(rank),
    ]
    card_verdict_lines = [
        f"当前落在{realm} / {rank}。",
        _card_verdict(rank),
    ]
    breakthrough_lines = _merge_growth_lines(user_certificate, assistant_certificate)
    card_breakthrough_lines = [
        "下一轮先把目标、边界和验收写在前面，再让 AI 动手；"
        "每轮结束都补一句：改了什么、怎么验证、还有什么没验。"
    ]
    coaching_focus_lines, coaching_drill_lines, coaching_prompt_lines, coaching_cycle_lines = _build_coaching_plan(
        user_low["name"],
        assistant_low["name"],
    )

    return {
        "realm": realm,
        "rank": rank,
        "ability_text": ability_text,
        "card_ability_text": card_ability_text,
        "usage_line": f"{_fmt_int(total_tokens)} tokens · {total_messages} 条消息 · {tool_calls} 次工具调用" if total_tokens else f"{total_messages} 条消息 · {tool_calls} 次工具调用",
        "verdict_lines": verdict_lines,
        "card_verdict_lines": card_verdict_lines,
        "breakthrough_lines": breakthrough_lines,
        "card_breakthrough_lines": card_breakthrough_lines,
        "coaching_focus_lines": coaching_focus_lines,
        "coaching_drill_lines": coaching_drill_lines,
        "coaching_prompt_lines": coaching_prompt_lines,
        "coaching_cycle_lines": coaching_cycle_lines,
        "user_summary_lines": [
            f"你这轮最稳的是“{user_top_name}”，{user_top['rationale']}",
            f"最拖后腿的是“{user_low_name}”，{user_low['rationale']}",
        ],
        "assistant_summary_lines": [
            f"AI 这轮最稳的是“{assistant_top_name}”，{assistant_top['rationale']}",
            f"AI 最该补的是“{assistant_low_name}”，{assistant_low['rationale']}",
            f"这轮蒸馏出来的 vibecoding 能力可以概括为：{level_ability_text}",
        ],
        "image_concepts": image_concepts,
        "report_basis_lines": [
            "单卡取材自：境界、等级、能力描述、短长板、真实会话规模与破境建议。",
            "传播层重点是：大境界字、等级色、可晒图能力判词，以及下一轮修炼方向。",
        ],
    }


def _merge_growth_lines(user_certificate, assistant_certificate) -> list[str]:
    merged: list[str] = []
    for item in _certificate_list(user_certificate, "growth_plan") + _certificate_list(assistant_certificate, "growth_plan"):
        cleaned = _xianxiaize_growth(item)
        if cleaned and cleaned not in merged:
            merged.append(cleaned)
    return merged[:2] or ["先守住一条主线，把最短的那块板补上，再看下一轮能不能破境。"]


def _xianxiaize_growth(text: str) -> str:
    cleaned = " ".join((text or "").split())
    replacements = {
        "要求 AI 说明“改了什么、怎么验、哪里还没验”": "每轮结束都把改了什么、怎么验证、哪里还没验交代清楚。",
        "鼓励 AI 先读仓库、跑命令、看真实日志，再给方案": "先读仓库、跑命令、看日志，再给方案，别一上来只讲思路。",
        "让 AI 在下一轮任务里强制执行“实现 -> 验证 -> 回报”节奏": "下一轮强制走“实现 -> 验证 -> 回报”三步，不要停在半路。",
        "每一轮收功时，都要附上看得见的凭据": "每轮结束都留下看得见的验证结果。",
        "下次闭关前，先把诉求写成“目标 + 约束 + 输出物 + 验收”四段式": "下次起手前，先把目标、边界、输出物和验收写清楚。",
        "待下一轮问答结束，再来看境界变化": "等下一轮做完，再回来看自己有没有破境。",
    }
    for src, dst in replacements.items():
        cleaned = cleaned.replace(src, dst)
    while cleaned.endswith("。。"):
        cleaned = cleaned[:-1]
    return cleaned


def _metric_items(metrics) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for item in metrics:
        if hasattr(item, "name") and hasattr(item, "score"):
            items.append({"name": str(item.name), "score": int(item.score), "rationale": str(getattr(item, "rationale", ""))})
        elif isinstance(item, dict) and "name" in item:
            items.append({"name": str(item.get("name", "")), "score": int(item.get("score", 0) or 0), "rationale": str(item.get("rationale", ""))})
    return items


def _top_and_low(items: list[dict[str, object]]) -> tuple[dict[str, object], dict[str, object]]:
    if not items:
        empty = {"name": "未定", "score": 0, "rationale": "当前样本仍需继续观察。"}
        return empty, empty
    ordered = sorted(items, key=lambda item: int(item.get("score", 0)), reverse=True)
    return ordered[0], ordered[-1]


def _metric_behavior(name: str, polarity: str, track: str) -> str:
    mapping = USER_BEHAVIOR_TEXT if track == "user" else ASSISTANT_BEHAVIOR_TEXT
    return mapping.get(name, {}).get(polarity, "当前样本仍需继续观察。")


def _metric_card_behavior(name: str, polarity: str, track: str) -> str:
    mapping = USER_CARD_BEHAVIOR_TEXT if track == "user" else ASSISTANT_CARD_BEHAVIOR_TEXT
    return mapping.get(name, {}).get(polarity, _metric_behavior(name, polarity, track))


def _build_coaching_plan(user_low_name: str, assistant_low_name: str) -> tuple[list[str], list[str], list[str], list[str]]:
    names = []
    for name in [user_low_name, assistant_low_name]:
        if name and name not in names:
            names.append(name)
    focus_lines: list[str] = []
    drill_lines: list[str] = []
    prompt_lines: list[str] = []
    for name in names:
        plan = COACHING_PLAYBOOK.get(name)
        if not plan:
            continue
        focus_lines.append(f"{name}：{plan['focus']}")
        drill_lines.append(plan["drill"])
        prompt_lines.append(plan["prompt"])
    if not focus_lines:
        focus_lines = ["先守住当前最稳的一条主线，再补最短的那块板。"]
    if not drill_lines:
        drill_lines = ["下一轮开局先写清目标、边界和验收，再让 AI 动手。"]
    if not prompt_lines:
        prompt_lines = ["先帮我把这次任务整理成目标、边界、验收，再开始执行。"]
    cycle_lines = [
        "第 1 步：先定目标、边界、验收。",
        "第 2 步：让 AI 直接执行，并强制读文件、跑命令或查日志。",
        "第 3 步：收尾只看三件事，改了什么、怎么验证、还有什么没验。",
    ]
    return focus_lines[:2], drill_lines[:3], prompt_lines[:3], cycle_lines


def _compose_ability_summary(
    *,
    level_text: str,
    user_top_name: str,
    assistant_top_name: str,
    user_low_name: str,
    assistant_low_name: str,
    user_top_text: str,
    assistant_top_text: str,
    user_low_text: str,
    assistant_low_text: str,
) -> str:
    return (
        f"{level_text}"
        f" 这轮最亮眼的是{user_top_name}和{assistant_top_name}：你这边{user_top_text}，AI 这边{assistant_top_text}。"
        f" 眼下最该补的是{user_low_name}和{assistant_low_name}：你这边{user_low_text}，AI 这边{assistant_low_text}。"
    )


def _compose_card_ability_summary(
    *,
    level_text: str,
    user_top_name: str,
    assistant_top_name: str,
    user_low_name: str,
    assistant_low_name: str,
    user_top_text: str,
    assistant_top_text: str,
    user_low_text: str,
    assistant_low_text: str,
) -> str:
    return (
        f"{level_text}"
        f" 这轮亮点在{user_top_name}和{assistant_top_name}：你这边{user_top_text}，AI 这边{assistant_top_text}。"
        f" 最该补的是{user_low_name}和{assistant_low_name}：你这边{user_low_text}，AI 这边{assistant_low_text}。"
    )


def _certificate_value(certificate, key: str, default: str) -> str:
    if isinstance(certificate, Certificate):
        return str(getattr(certificate, key, default))
    if isinstance(certificate, dict):
        return str(certificate.get(key, default))
    return default


def _certificate_list(certificate, key: str) -> list[str]:
    if isinstance(certificate, Certificate):
        value = getattr(certificate, key, [])
    elif isinstance(certificate, dict):
        value = certificate.get(key, [])
    else:
        value = []
    return [str(item) for item in value if str(item).strip()]


def _ability_text(rank: str) -> str:
    return ABILITY_LIBRARY.get(rank, "已经形成一套顺手可复用的协作做法。")


def _card_ability_text(rank: str) -> str:
    return CARD_ABILITY_LIBRARY.get(rank, "已经形成一套顺手可复用的协作做法。")


def _card_verdict(rank: str) -> str:
    return CARD_VERDICT_LIBRARY.get(rank, "这一层已经有稳定可复用的协作做法。")




def _image_concepts(messages: list[Message]) -> list[str]:
    text = "\n".join(message.text.lower() for message in messages if getattr(message, "role", "") == "user")
    hits: list[tuple[str, int, list[str]]] = []
    for name, keywords in IMAGE_CONCEPT_GROUPS.items():
        matched = [keyword for keyword in keywords if keyword.lower() in text]
        if matched:
            hits.append((name, len(matched), matched[:4]))
    hits.sort(key=lambda item: item[1], reverse=True)
    if not hits:
        return ["当前样本里没有额外宣发要求，这张卡主要依据真实修为、等级与破境方向生成。"]
    lines = []
    for name, _, keywords in hits[:4]:
        joined = "、".join(dict.fromkeys(keywords))
        lines.append(f"{name}：{IMAGE_CONCEPT_NOTES.get(name, '这一类要求在轨迹里被反复提及。')} 命中词包括 {joined}。")
    return lines


def _fmt_int(value: int) -> str:
    return f"{int(value):,}"


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}
