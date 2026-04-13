from __future__ import annotations

import re

from .models import Analysis, Certificate, Message
from .secondary_skill import build_secondary_skill_distillation, summarize_secondary_skill

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
    "L1": "你和 AI 还停在问一句答一句的阶段，能把问题抛出去，但推进更多靠反复试。",
    "L2": "你已经开始懂得调 prompt，同一个问题会换问法，开始能有意识地把回答往对的方向拽。",
    "L3": "你能独立做成小任务，也会顺着结果继续补要求，协作开始有连续性了。",
    "L4": "你已经能把常见任务沿着上下文稳定推到多步完成，熟悉的问题不太会半路掉线。",
    "L5": "你开始把顺手打法沉成可复用套路，同类问题不用每次都重新摸索一遍。",
    "L6": "你已经会把一段工作先委给 AI 做，再回来看方向、结果和风险，协作开始真正成形。",
    "L7": "你已经能把任务拆开，调动多 Agent 和工具并行推进，推进方式开始带一点调度味道。",
    "L8": "你开始搭方法和流程，重点已经从单次做完任务转向经营一套可持续的协作系统。",
    "L9": "你能把这套协作带进真实项目，在约束、反馈和返工里继续修正做法。",
    "L10": "你已经能把自己的协作方法讲清、沉淀下，再稳定复制给别人和团队。",
}

CARD_ABILITY_LIBRARY = {
    "L1": "AI 还更像临时帮手。你能把问题抛出去，但推进还主要靠反复试错。",
    "L2": "你已经开始主动调 prompt。结果不再只靠运气，而是能被问法明显拉动。",
    "L3": "你已经能把小任务做完。协作开始连续，不再总是问完一轮就断。",
    "L4": "你已经不只是在提需求，而是在稳定推进一段真实工作。熟悉任务能沿着上下文连续落地。",
    "L5": "你开始把顺手打法沉成套路。做得更快只是表面，真正出现的是可复用的方法感。",
    "L6": "AI 已经不只是回答器，而是先执行一段工作的搭档。你开始收方向、结果和风险。",
    "L7": "你开始像调度者一样工作。多 Agent、多工具不再是点缀，而是真正进入推进主链路。",
    "L8": "你在经营的已经不是单次任务，而是一套能持续放大的方法、流程和能力层。",
    "L9": "这套协作已经进入真实项目。它要面对约束、返工和反馈，也还能继续往前推。",
    "L10": "你的方法已经能被复制。它不只服务你自己，也开始服务团队和更长的工作流。",
}

CARD_ABILITY_LIBRARY_EN = {
    "L1": "You are still mostly in single-turn probing mode. You can ask the question, but progress still depends on repeated retries.",
    "L2": "You already know the wording changes the result, and you actively rewrite prompts to pull the answer closer to something usable.",
    "L3": "You can already land small tasks on your own and keep refining from the result instead of stopping after one reply.",
    "L4": "You can already push familiar tasks through multi-step collaboration without losing the thread too easily.",
    "L5": "You are starting to turn repeatable wins into reusable patterns, so similar tasks feel more and more like your own playbook.",
    "L6": "You can already hand a concrete block of work to AI first, then come back to direction, results, and risk.",
    "L7": "You can already split a full task and run multiple agents and tools in parallel with real coordination.",
    "L8": "You are starting to operate your own methods and workflows, and the focus is no longer just whether one task got done.",
    "L9": "You can already bring this collaboration style into real projects and keep adapting inside feedback, rework, and constraints.",
    "L10": "You can already distill your collaboration method into something other people can reproduce with consistency.",
}

CARD_VERDICT_LIBRARY = {
    "L1": "这一层，AI 还是问答工具，还没真正进入执行位。",
    "L2": "这一层，已经知道 prompt 有杠杆，但协作还没形成稳定手感。",
    "L3": "这一层，小任务已经能落地，协作开始有连续回合。",
    "L4": "这一层，常见任务已经能稳定推进，AI 开始像真正的执行位。",
    "L5": "这一层，打法开始复用，效率背后出现的是方法论雏形。",
    "L6": "这一层，AI 能先跑一段，你回来收方向、结果和风险。",
    "L7": "这一层，多 Agent 和工具已经进主流程，不只是演示效果。",
    "L8": "这一层，重点开始从做任务转向搭方法、搭流程、搭能力层。",
    "L9": "这一层，这套协作能顶住真实项目里的反馈、返工和约束。",
    "L10": "这一层，方法可以稳定复制，协作能力开始具备团队尺度。",
}

CARD_VERDICT_LIBRARY_EN = {
    "L1": "People at this level are still using AI like a temporary helper in one-turn exchanges.",
    "L2": "People at this level already know prompting changes the result, but the rhythm is not stable yet.",
    "L3": "People at this level can land small tasks and keep adjusting as they go.",
    "L4": "People at this level can reliably push common tasks through multi-step collaboration.",
    "L5": "People at this level start turning repeated wins into reusable patterns.",
    "L6": "People at this level let AI move first, then come back to direction and results.",
    "L7": "People at this level can coordinate multiple agents and tools in parallel.",
    "L8": "People at this level start building methods and workflows, not just finishing isolated tasks.",
    "L9": "People at this level can carry this collaboration style into real projects and keep adapting it.",
    "L10": "People at this level can distill the method and copy it reliably across a team.",
}

NEXT_LEVEL_FOCUS_LIBRARY = {
    "L1": "下一步先把目标讲清，别让 AI 靠猜补主线。",
    "L2": "下一步要证明的，是你能把任务做成，不只是把答案问出来。",
    "L3": "下一步要看的，是能不能把熟悉任务稳定推进成多步协作。",
    "L4": "下一步要冲的，是把顺手打法沉成可复用套路。",
    "L5": "下一步要突破的，是把一段具体工作放心交给 AI 先推进。",
    "L6": "下一步要拉开的，是多 Agent、多工具的真实并行调度。",
    "L7": "下一步要升级的，是从做任务走向搭方法、搭流程。",
    "L8": "下一步要验证的，是这套打法能不能放进真实项目继续成立。",
    "L9": "下一步要完成的，是把方法讲清、沉淀下、再复制给别人。",
    "L10": "下一步更重要的是守住稳定度，把方法沉成长期资产。",
}

NEXT_LEVEL_FOCUS_LIBRARY_EN = {
    "L1": "The next layer depends on whether you can state the problem clearly instead of making AI guess the main thread.",
    "L2": "The next layer depends on whether you can actually land a small task, not just ask for an answer.",
    "L3": "The next layer depends on whether you can reliably turn familiar work into multi-step collaboration.",
    "L4": "The next layer depends on whether you can turn a smooth tactic into a reusable pattern.",
    "L5": "The next layer depends on whether you can confidently hand a concrete block of work to AI first.",
    "L6": "The next layer depends on whether you can truly organize multiple agents and tools in parallel.",
    "L7": "The next layer depends on whether you can move from finishing tasks to building methods and workflows.",
    "L8": "The next layer depends on whether you can carry the method into real projects and keep adapting through feedback.",
    "L9": "The next layer depends on whether you can explain the method clearly, distill it, and transfer it to others.",
    "L10": "At this layer the key is to keep the method stable and keep turning it into a durable asset.",
}

USER_CARD_BEHAVIOR_TEXT_EN = {
    "目标清晰度": {"strong": "state the goal clearly up front", "weak": "still leave the goal a bit too open"},
    "上下文供给": {"strong": "provide enough background and boundaries", "weak": "still leave out some key context"},
    "迭代修正力": {"strong": "correct the course quickly when things drift", "weak": "still recover too slowly after drift"},
    "验收意识": {"strong": "actively ask for validation and evidence", "weak": "still ask for validation too late"},
    "协作节奏": {"strong": "keep the back-and-forth moving smoothly", "weak": "still lose rhythm across rounds"},
}

ASSISTANT_CARD_BEHAVIOR_TEXT_EN = {
    "执行落地": {"strong": "move first and report after", "weak": "still explain too much before acting"},
    "工具调度": {"strong": "pull tools in to push the task forward", "weak": "still underuse tools that could verify faster"},
    "验证闭环": {"strong": "close the loop with validation and a clear recap", "weak": "still leave the closing recap incomplete"},
    "上下文承接": {"strong": "hold the thread across rounds", "weak": "still lose the thread in longer runs"},
    "补救适配": {"strong": "switch paths and keep pushing when blocked", "weak": "still adapt too slowly after friction"},
}

USER_LABELS_EN = {
    "目标清晰度": "goal framing",
    "上下文供给": "context setup",
    "迭代修正力": "iteration control",
    "验收意识": "validation instinct",
    "协作节奏": "collaboration rhythm",
}

ASSISTANT_LABELS_EN = {
    "执行落地": "execution drive",
    "工具调度": "tool orchestration",
    "验证闭环": "validation loop",
    "上下文承接": "context carry",
    "补救适配": "recovery handling",
}

STAGE_LABELS = {
    "L1": "试手期",
    "L2": "入门期",
    "L3": "成形期",
    "L4": "稳定期",
    "L5": "复用期",
    "L6": "委托期",
    "L7": "并行期",
    "L8": "系统期",
    "L9": "落地期",
    "L10": "传承期",
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

MODERN_AGENT_SIGNALS = {
    "cross_agent_memory": {
        "keywords": ["memory", "记忆", "上次评测", "previous snapshot", "snapshot", "长期", "跨周期", "history"],
        "line": "出现了跨轮次记忆信号，说明这套协作已经不再只看单次对话，而开始积累长期上下文。",
    },
    "context_compaction": {
        "keywords": ["压缩上下文", "总结当前进展", "继续上次", "context compaction", "handoff", "交接", "阶段总结"],
        "line": "出现了上下文压缩 / 交接信号，说明你已经在处理更长链路任务，而不只是短回合问答。",
    },
    "interactive_steering": {
        "keywords": ["边做边改", "继续做", "我先看一下", "先做到这里", "while it’s working", "steer", "interact in real time"],
        "line": "出现了过程内调向信号，说明你会在 AI 执行过程中持续修正方向，不会一直等到最后答案才回头。",
    },
    "agentic_workflow": {
        "keywords": [".github/workflows", "workflow", "工作流", "自动化", "triage", "CI", "markdown", "schedule"],
        "line": "出现了工作流化信号，说明协作开始从单任务推进走向可复用的自动化流程。",
    },
    "repo_legibility": {
        "keywords": ["AGENTS.md", "README", "docs", "设计文档", "文档索引", "schema", "可见", "repo 内"],
        "line": "出现了仓库可读性信号，说明你开始把知识写回仓库，让 Agent 能在运行时直接看见规则和上下文。",
    },
    "async_teammate": {
        "keywords": ["后台", "异步", "delegate", "assign", "交给 agent", "先让 ai 做", "teammate"],
        "line": "出现了异步委托信号，说明你已经开始把 AI 当成能独立推进一段工作的协作对象。",
    },
    "mcp_tooling": {
        "keywords": ["mcp", "tool", "工具调用", "connector", "server", "读文件", "跑命令", "web search"],
        "line": "出现了工具编排信号，说明这轮协作已经明显依赖外部工具和连接器，而不只是纯文本问答。",
    },
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
        "focus": "优先让 AI 动手，先别写一大段解释。",
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


def build_analysis_insights(
    analysis: Analysis,
    target_level: str | None = None,
    secondary_skill: dict[str, object] | None = None,
) -> dict[str, object]:
    secondary_skill = secondary_skill or build_secondary_skill_distillation(
        messages=analysis.transcript.messages,
        display_name=analysis.transcript.display_name or "你",
        source=analysis.transcript.source,
        rank=None,
        generated_at="",
        models=analysis.transcript.models,
        tool_calls=analysis.transcript.tool_calls,
    )
    return _build_insights(
        messages=analysis.transcript.messages,
        user_metrics=analysis.user_metrics,
        assistant_metrics=analysis.assistant_metrics,
        user_certificate=analysis.user_certificate,
        assistant_certificate=analysis.assistant_certificate,
        total_messages=len(analysis.transcript.messages),
        tool_calls=analysis.transcript.tool_calls,
        total_tokens=analysis.transcript.token_usage.total_tokens,
        target_level=target_level,
        secondary_skill=secondary_skill,
    )


def build_aggregate_insights(
    analyses: list[Analysis],
    aggregate: dict[str, object],
    target_level: str | None = None,
    secondary_skill: dict[str, object] | None = None,
) -> dict[str, object]:
    messages = [message for analysis in analyses for message in analysis.transcript.messages]
    secondary_skill = secondary_skill or build_secondary_skill_distillation(
        messages=messages,
        display_name=str(aggregate.get("display_name") or "你"),
        source=str(aggregate.get("source") or (analyses[0].transcript.source if analyses else "codex")),
        rank=None,
        generated_at="",
        models=[],
        tool_calls=int(aggregate.get("total_tool_calls", 0) or 0),
    )
    return _build_insights(
        messages=messages,
        user_metrics=aggregate.get("user_metrics", []),
        assistant_metrics=aggregate.get("assistant_metrics", []),
        user_certificate=aggregate.get("user_certificate", {}),
        assistant_certificate=aggregate.get("assistant_certificate", {}),
        total_messages=int(aggregate.get("total_messages", 0) or 0),
        tool_calls=int(aggregate.get("total_tool_calls", 0) or 0),
        total_tokens=int(_as_dict(aggregate.get("token_usage")).get("total_tokens", 0) or 0),
        target_level=target_level,
        secondary_skill=secondary_skill,
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
    target_level: str | None,
    secondary_skill: dict[str, object] | None,
) -> dict[str, object]:
    secondary_summary = summarize_secondary_skill(secondary_skill or {})
    image_concepts = _image_concepts(messages)
    card_language = _card_language(messages)
    rank = str(secondary_summary.get("rank") or _certificate_value(assistant_certificate, "level", "L1"))
    realm = _certificate_value(user_certificate, "level", "凡人")
    stage = STAGE_LABELS.get(rank, "试手期")
    level_ability_text = _ability_text(rank)
    card_level_ability_text = _card_ability_text(rank)
    top_axes = [item for item in secondary_summary.get("top_axes", []) if isinstance(item, dict)]
    weak_axes = [item for item in secondary_summary.get("weak_axes", []) if isinstance(item, dict)]
    user_axis = next((item for item in top_axes if str(item.get("semantic_mode") or "") == "user_behavior"), top_axes[0] if top_axes else {})
    assistant_axis = next((item for item in top_axes if str(item.get("semantic_mode") or "") != "user_behavior"), top_axes[0] if top_axes else {})
    user_weak_axis = next((item for item in weak_axes if str(item.get("semantic_mode") or "") == "user_behavior"), weak_axes[0] if weak_axes else {})
    assistant_weak_axis = next((item for item in weak_axes if str(item.get("semantic_mode") or "") != "user_behavior"), weak_axes[0] if weak_axes else {})
    user_top_name = str(user_axis.get("label") or "目标 framing")
    user_low_name = str(user_weak_axis.get("label") or "短板维度")
    assistant_top_name = str(assistant_axis.get("label") or "执行默认")
    assistant_low_name = str(assistant_weak_axis.get("label") or "短板维度")

    ability_text = _compose_axis_ability_summary(level_ability_text, secondary_summary)
    card_ability_text = _compose_axis_card_summary(card_level_ability_text, secondary_summary)
    card_ability_text_en = _compose_axis_card_summary_en(_card_ability_text_en(rank), secondary_summary)
    verdict_lines = [
        f"这轮样本看下来，你现在处在{stage}，对应 {rank}。",
        _card_verdict(rank),
    ]
    standard_card_verdict_lines = [_card_verdict(rank)]
    card_verdict_lines = [_card_verdict(rank)]
    standard_card_verdict_lines_en = [_card_verdict_en(rank)]
    card_verdict_lines_en = [_card_verdict_en(rank)]
    breakthrough_lines = _list_or_default(
        secondary_summary.get("breakthrough_lines"),
        _merge_growth_lines(user_certificate, assistant_certificate),
    )
    card_breakthrough_lines = [
        _card_breakthrough_text(
            rank=rank,
            user_low_name=user_low_name,
            assistant_low_name=assistant_low_name,
        )
    ]
    card_breakthrough_lines_en = [
        _card_breakthrough_text_en(
            rank=rank,
            user_low_name=user_low_name,
            assistant_low_name=assistant_low_name,
        )
    ]
    coaching_focus_lines, coaching_drill_lines, coaching_prompt_lines, coaching_cycle_lines = _build_coaching_plan(
        user_low_name,
        assistant_low_name,
    )
    habit_profile_lines = _list_or_default(secondary_summary.get("habit_profile_lines"), [])
    mimic_lines = _list_or_default(secondary_summary.get("mimic_lines"), [])
    target_summary_lines, target_gap_lines, target_drill_lines = _build_target_level_plan(
        current_rank=rank,
        target_level=target_level,
        user_low_name=user_low_name,
        assistant_low_name=assistant_low_name,
    )
    modern_signal_lines = _modern_agent_signal_lines(
        messages=messages,
        total_messages=total_messages,
        tool_calls=tool_calls,
    )

    return {
        "realm": realm,
        "rank": rank,
        "stage": stage,
        "target_level": target_level,
        "card_language": card_language,
        "ability_text": ability_text,
        "card_ability_text": card_ability_text,
        "card_ability_text_en": card_ability_text_en,
        "usage_line": f"{_fmt_int(total_tokens)} tokens · {total_messages} 条消息 · {tool_calls} 次工具调用" if total_tokens else f"{total_messages} 条消息 · {tool_calls} 次工具调用",
        "verdict_lines": verdict_lines,
        "standard_card_verdict_lines": standard_card_verdict_lines,
        "standard_card_verdict_lines_en": standard_card_verdict_lines_en,
        "card_verdict_lines": card_verdict_lines,
        "card_verdict_lines_en": card_verdict_lines_en,
        "breakthrough_lines": breakthrough_lines,
        "card_breakthrough_lines": card_breakthrough_lines,
        "card_breakthrough_lines_en": card_breakthrough_lines_en,
        "coaching_focus_lines": coaching_focus_lines,
        "coaching_drill_lines": coaching_drill_lines,
        "coaching_prompt_lines": coaching_prompt_lines,
        "coaching_cycle_lines": coaching_cycle_lines,
        "habit_profile_lines": habit_profile_lines,
        "mimic_lines": mimic_lines,
        "target_summary_lines": target_summary_lines,
        "target_gap_lines": target_gap_lines,
        "target_drill_lines": target_drill_lines,
        "modern_signal_lines": modern_signal_lines,
        "profile_tags": secondary_summary.get("tags", []),
        "profile_bullets": secondary_summary.get("bullets", []),
        "dimension_summary_lines": secondary_summary.get("dimension_summary_lines", []),
        "user_summary_lines": secondary_summary.get("user_summary_lines", []),
        "assistant_summary_lines": secondary_summary.get("assistant_summary_lines", []),
        "image_concepts": image_concepts,
        "report_basis_lines": secondary_summary.get("report_basis_lines", []) + [
            "单卡取材自：等级、能力摘要、短长板和真实会话规模。",
            "传播层重点是：大字等级、一眼能看懂的判断，以及下一轮最该补的动作。",
        ],
    }


def _build_habit_profile_lines(
    *,
    user_top_name: str,
    assistant_top_name: str,
    user_low_name: str,
    assistant_low_name: str,
    user_top_text: str,
    assistant_top_text: str,
    user_low_text: str,
    assistant_low_text: str,
) -> list[str]:
    return [
        f"起手习惯：你通常会先抓住“{user_top_name}”，{user_top_text}。",
        f"推进习惯：AI 侧最像你的地方是“{assistant_top_name}”，{assistant_top_text}。",
        f"容易掉点的地方：你这边的“{user_low_name}”和 AI 侧的“{assistant_low_name}”还不够稳，分别表现为{user_low_text}、{assistant_low_text}。",
    ]


def _build_mimic_lines(
    *,
    user_top_name: str,
    assistant_top_name: str,
    user_low_name: str,
) -> list[str]:
    return [
        f"如果要复刻这套习惯，开局先按“目标先说清 + 上下文先给够”的方式推进，再把“{assistant_top_name}”保持住。",
        f"协作时优先模仿你的强项：先把主线收束，再让 Agent 直接动手，不要把解释放在执行前面。",
        f"如果要模仿得更像，最要避免的是“{user_low_name}”掉线；每轮结束都补一次验证和回看。",
    ]


def _build_target_level_plan(
    *,
    current_rank: str,
    target_level: str | None,
    user_low_name: str,
    assistant_low_name: str,
) -> tuple[list[str], list[str], list[str]]:
    if not target_level:
        return [], [], []
    current_value = _rank_number(current_rank)
    target_value = _rank_number(target_level)
    if target_value <= 0:
        return [], [], []
    if target_value <= current_value:
        return [
            f"当前已经在 {current_rank}，目标 {target_level} 已经覆盖到了。"
        ], [
            "现在更值得做的是把这层能力稳定下来，再扩大样本看看是否真稳。"
        ], [
            "连续几轮都保留同样的起手、执行、验证节奏，避免只在单次样本里偶然发挥。"
        ]

    missing_habits = _target_habit_focus(target_level)
    target_habit_drills = _target_habit_drills(*missing_habits)
    return [
        f"当前是 {current_rank}，目标是 {target_level}，中间还差 {target_value - current_value} 个等级。"
    ], [
        f"冲到 {target_level}，关键不只是在单轮里更顺，还要把“{missing_habits[0]}”“{missing_habits[1]}”练成稳定习惯。",
        f"眼下最先补的是“{user_low_name}”和“{assistant_low_name}”，这两项会直接限制你往更高等级走。",
    ], [
        target_habit_drills[0],
        target_habit_drills[1],
        f"每做完一轮，都对照 {target_level} 回看一次：这轮有没有真正出现更高等级应有的习惯。",
    ]


def _target_habit_focus(target_level: str) -> tuple[str, str]:
    mapping = {
        "L1": ("目标表达", "协作节奏"),
        "L2": ("目标表达", "迭代修正"),
        "L3": ("上下文信息", "结果验证"),
        "L4": ("协作节奏", "回看确认"),
        "L5": ("复用套路", "结果验证"),
        "L6": ("委托执行", "回看确认"),
        "L7": ("并行推进", "工具调用"),
        "L8": ("系统打法", "上下文布置"),
        "L9": ("真实项目回流", "补救适配"),
        "L10": ("方法沉淀", "团队复制"),
    }
    return mapping.get(target_level, ("协作节奏", "结果验证"))


def _target_habit_drills(first_habit: str, second_habit: str) -> tuple[str, str]:
    drill_map = {
        "目标表达": "下一轮开局先把目标、边界、输出物和验收写成四行，再让 Agent 开始做。",
        "协作节奏": "把任务拆成更短的连续回合，每回合只推进一个最关键问题。",
        "迭代修正": "看到结果偏了就立刻补一条关键修正，不要等整轮做完再统一返工。",
        "上下文信息": "每轮开始先把路径、日志、环境和已有尝试一次性给够，减少 Agent 来回追问。",
        "结果验证": "收尾固定追问三件事：改了什么、怎么验证、还有什么没验。",
        "回看确认": "每轮结束都让 Agent 回报一次结果证据和剩余风险，别停在“已经改完”。",
        "复用套路": "把这轮顺手的起手话术、执行节奏和验收方式记下来，下轮继续复用。",
        "委托执行": "先把任务拆给 Agent 做一段，再回来只盯方向、验收和风险，不要全程手动接管。",
        "并行推进": "遇到中等以上复杂任务时，主动拆成两到三个并行子问题，不要只让一个 Agent 顺排往下做。",
        "工具调用": "凡是能读文件、跑命令、查日志验证的环节，都要求 Agent 先动工具再下判断。",
        "系统打法": "别只盯一轮任务，把起手、执行、验证和复盘连成一套固定打法。",
        "上下文布置": "在开局前先把文件范围、约束和验收方式布置好，让后续每轮都沿同一主线推进。",
        "真实项目回流": "每完成一轮真实任务，都回收一次结果和踩坑，把它们写回下一轮协作规则。",
        "补救适配": "一旦卡住就先给三个缩范围方案，再选最短路径继续推进，不要原地硬拧。",
        "方法沉淀": "把高频有效的做法沉淀成固定模板、skill 或常驻协作规则。",
        "团队复制": "把你这套做法写成别人也能复用的步骤，让同事照着就能跑出接近结果。",
    }
    return (
        drill_map.get(first_habit, f"下一轮刻意强化“{first_habit}”，别只靠临场发挥。"),
        drill_map.get(second_habit, f"下一轮刻意强化“{second_habit}”，别只靠临场发挥。"),
    )


def _rank_number(level: str) -> int:
    try:
        return int(str(level).replace("L", ""))
    except ValueError:
        return 0


def _list_or_default(value, default: list[str]) -> list[str]:
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        if items:
            return items
    return default


def _merge_growth_lines(user_certificate, assistant_certificate) -> list[str]:
    merged: list[str] = []
    for item in _certificate_list(user_certificate, "growth_plan") + _certificate_list(assistant_certificate, "growth_plan"):
        cleaned = _xianxiaize_growth(item)
        if cleaned and cleaned not in merged:
            merged.append(cleaned)
    return merged[:2] or ["先守住一条主线，把最短的那块板补上，再看下一轮能不能升级。"]


def _xianxiaize_growth(text: str) -> str:
    cleaned = " ".join((text or "").split())
    replacements = {
        "要求 AI 说明“改了什么、怎么验、哪里还没验”": "每轮结束都把改了什么、怎么验证、哪里还没验交代清楚。",
        "鼓励 AI 先读仓库、跑命令、看真实日志，再给方案": "先读仓库、跑命令、看日志，再给方案，别一上来只讲思路。",
        "让 AI 在下一轮任务里强制执行“实现 -> 验证 -> 回报”节奏": "下一轮强制走“实现 -> 验证 -> 回报”三步，不要停在半路。",
        "每一轮收功时，都要附上看得见的凭据": "每轮结束都留下看得见的验证结果。",
        "下次闭关前，先把诉求写成“目标 + 约束 + 输出物 + 验收”四段式": "下次起手前，先把目标、边界、输出物和验收写清楚。",
        "待下一轮问答结束，再来看境界变化": "等下一轮做完，再回来看自己有没有升级。",
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


def _metric_card_behavior_en(name: str, polarity: str, track: str) -> str:
    mapping = USER_CARD_BEHAVIOR_TEXT_EN if track == "user" else ASSISTANT_CARD_BEHAVIOR_TEXT_EN
    return mapping.get(name, {}).get(polarity, "still needs more real samples")


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
        f" 亮点是{user_top_name}和{assistant_top_name}：你{user_top_text}，AI {assistant_top_text}。"
        f" 下一步补{user_low_name}和{assistant_low_name}：你{user_low_text}，AI {assistant_low_text}。"
    )


def _compose_card_ability_summary_en(
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
        f" The strongest signals in this window are {user_top_name} and {assistant_top_name}: you {user_top_text}, and the agent side {assistant_top_text}."
        f" The main blockers to the next level are {user_low_name} and {assistant_low_name}: you {user_low_text}, and the agent side {assistant_low_text}."
    )


def _compose_axis_ability_summary(level_text: str, secondary_summary: dict[str, object]) -> str:
    top_axes = [str(item.get("label", "")) for item in secondary_summary.get("top_axes", []) if isinstance(item, dict)]
    weak_axes = [str(item.get("label", "")) for item in secondary_summary.get("weak_axes", []) if isinstance(item, dict)]
    strong = "、".join(top_axes[:2])
    weak = "、".join(weak_axes[:2])
    text = level_text
    if strong:
        text += f" 这轮 16 维里最稳的是{strong}。"
    if weak:
        text += f" 当前最该补的是{weak}。"
    return text


def _compose_axis_card_summary(level_text: str, secondary_summary: dict[str, object]) -> str:
    top_axes = [str(item.get("label", "")) for item in secondary_summary.get("top_axes", []) if isinstance(item, dict)]
    weak_axes = [str(item.get("label", "")) for item in secondary_summary.get("weak_axes", []) if isinstance(item, dict)]
    strong = "、".join(top_axes[:2])
    weak = "、".join(weak_axes[:2])
    text = level_text
    if strong:
        text += f" 当前强项是{strong}。"
    if weak:
        text += f" 下一步先补{weak}。"
    return text


def _compose_axis_card_summary_en(level_text: str, secondary_summary: dict[str, object]) -> str:
    top_axes = [str(item.get("label", "")) for item in secondary_summary.get("top_axes", []) if isinstance(item, dict)]
    weak_axes = [str(item.get("label", "")) for item in secondary_summary.get("weak_axes", []) if isinstance(item, dict)]
    strong = ", ".join(top_axes[:2])
    weak = ", ".join(weak_axes[:2])
    text = level_text
    if strong:
        text += f" The strongest 16-axis signals are {strong}."
    if weak:
        text += f" The next gaps to fix are {weak}."
    return text


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


def _card_ability_text_en(rank: str) -> str:
    return CARD_ABILITY_LIBRARY_EN.get(rank, "You already have a collaboration style that can be reused with consistency.")


def _card_verdict(rank: str) -> str:
    return CARD_VERDICT_LIBRARY.get(rank, "这一层已经有稳定可复用的协作做法。")


def _card_verdict_en(rank: str) -> str:
    return CARD_VERDICT_LIBRARY_EN.get(rank, "People at this level already have a stable and reusable collaboration style.")


def _card_breakthrough_text(rank: str, user_low_name: str, assistant_low_name: str) -> str:
    focus = NEXT_LEVEL_FOCUS_LIBRARY.get(rank, "下一层看的是把这套协作继续练稳。")
    return (
        f"{focus}"
        f" 下一轮先盯住{user_low_name}和{assistant_low_name}，"
        f"把目标、执行、验证接成一条更完整的闭环。"
    )


def _card_breakthrough_text_en(rank: str, user_low_name: str, assistant_low_name: str) -> str:
    focus = NEXT_LEVEL_FOCUS_LIBRARY_EN.get(rank, "The next layer depends on keeping this collaboration style stable and repeatable.")
    return (
        f"{focus}"
        f" In the next round, watch {user_low_name} and {assistant_low_name} first,"
        f" and connect goal, execution, and validation into one clean loop."
    )


def _metric_label_en(name: str, track: str) -> str:
    mapping = USER_LABELS_EN if track == "user" else ASSISTANT_LABELS_EN
    return mapping.get(name, name)


def _card_language(messages: list[Message]) -> str:
    user_text = "\n".join(message.text for message in messages if getattr(message, "role", "") == "user")
    lowered = user_text.lower()
    if any(token in lowered for token in ["english", "in english", "use english", "write in english", "英文"]):
        return "en"
    english_words = len(re.findall(r"\b[a-zA-Z]{3,}\b", user_text))
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", user_text))
    if english_words >= 24 and cjk_chars <= max(12, english_words // 8):
        return "en"
    return "zh"




def _image_concepts(messages: list[Message]) -> list[str]:
    text = "\n".join(message.text.lower() for message in messages if getattr(message, "role", "") == "user")
    hits: list[tuple[str, int, list[str]]] = []
    for name, keywords in IMAGE_CONCEPT_GROUPS.items():
        matched = [keyword for keyword in keywords if keyword.lower() in text]
        if matched:
            hits.append((name, len(matched), matched[:4]))
    hits.sort(key=lambda item: item[1], reverse=True)
    if not hits:
        return ["当前样本里没有额外宣发要求，这张卡主要依据真实阶段、等级与突破方向生成。"]
    lines = []
    for name, _, keywords in hits[:4]:
        joined = "、".join(dict.fromkeys(keywords))
        lines.append(f"{name}：{IMAGE_CONCEPT_NOTES.get(name, '这一类要求在轨迹里被反复提及。')} 命中词包括 {joined}。")
    return lines


def _modern_agent_signal_lines(*, messages: list[Message], total_messages: int, tool_calls: int) -> list[str]:
    text = "\n".join(message.text.lower() for message in messages)
    lines: list[str] = []
    for signal in MODERN_AGENT_SIGNALS.values():
        if any(keyword.lower() in text for keyword in signal["keywords"]):
            lines.append(signal["line"])
    if tool_calls >= 4:
        lines.append("这轮工具调用已经比较密，协作形态更接近 agentic coding，而不是纯聊天式问答。")
    if total_messages >= 18:
        lines.append("这轮消息长度已经跨过短回合范围，蒸馏重点应放在长链路推进、交接和收尾，而不是单句 prompt 技巧。")
    deduped: list[str] = []
    for line in lines:
        if line not in deduped:
            deduped.append(line)
    return deduped[:4]


def _fmt_int(value: int) -> str:
    return f"{int(value):,}"


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}
