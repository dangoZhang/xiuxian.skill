from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import re
import unicodedata

from .models import Message


SECONDARY_SKILL_FIELDS = [
    {
        "id": "goal_framing",
        "label": "目标 framing",
        "layer": "任务定义层",
        "weight": 1.0,
        "description": "用户是否能把目标、边界、验收和起手动作说清。",
        "anchors": {
            0: "只有模糊需求，目标和验收都不稳。",
            2: "目标和部分约束已出现，但起手动作或验收还不完整。",
            4: "目标、边界、验收和起手动作都清楚，agent 可直接接手。",
        },
    },
    {
        "id": "context_supply",
        "label": "上下文供给",
        "layer": "任务定义层",
        "weight": 1.0,
        "description": "路径、文件、背景、样例、时间窗和历史是否给够。",
        "anchors": {
            0: "几乎不给上下文，agent 需要边做边猜。",
            2: "能给部分路径、文件或背景，但仍有缺口。",
            4: "路径、文件、背景和历史一次给够，来回确认很少。",
        },
    },
    {
        "id": "constraint_governance",
        "label": "约束治理",
        "layer": "任务定义层",
        "weight": 0.9,
        "description": "必须项、禁忌、优先级、兼容性和风格约束是否明确。",
        "anchors": {
            0: "限制条件很少，执行边界不清。",
            2: "有部分必须项或禁忌，但优先级不够清楚。",
            4: "必须项、禁忌、优先级和兼容要求都可直接执行。",
        },
    },
    {
        "id": "communication_compression",
        "label": "沟通压缩度",
        "layer": "任务定义层",
        "weight": 0.7,
        "description": "是否偏好短句、人话、结论优先和少铺垫。",
        "anchors": {
            0: "表达散、长、低密度，关键信息埋得深。",
            2: "会要求简洁，但并不稳定。",
            4: "长期偏好短句、高密度、结论优先的表达。",
        },
    },
    {
        "id": "execution_preference",
        "label": "执行默认",
        "layer": "执行控制层",
        "weight": 1.0,
        "description": "默认先讲方案还是先动手，是否偏好直接推进。",
        "anchors": {
            0: "长期停在解释或讨论里。",
            2: "愿意直接做，但仍经常先讲一大段方案。",
            4: "默认先执行，再回报，说明不挡路。",
        },
    },
    {
        "id": "task_decomposition",
        "label": "任务拆解",
        "layer": "执行控制层",
        "weight": 0.9,
        "description": "是否会把任务拆步、排主次、明确下一步。",
        "anchors": {
            0: "几乎不拆任务，推进路径模糊。",
            2: "能列步骤，但对执行收敛帮助一般。",
            4: "会稳定拆步、排优先级，并持续收束下一步。",
        },
    },
    {
        "id": "tool_orchestration",
        "label": "工具编排",
        "layer": "执行控制层",
        "weight": 1.0,
        "description": "是否倾向读文件、跑命令、查日志、用脚本和工具链推进。",
        "anchors": {
            0: "几乎不用工具，主要靠口头判断。",
            2: "会用少量工具验证，但覆盖面有限。",
            4: "文件、命令、日志、脚本和连接器会联动使用。",
        },
    },
    {
        "id": "context_carry",
        "label": "上下文承接",
        "layer": "执行控制层",
        "weight": 0.9,
        "description": "长回合里是否能续住主线，沿用刚才的上下文继续推进。",
        "anchors": {
            0: "回合一长就容易丢主线。",
            2: "大体能续住，但长链路仍会掉线。",
            4: "长回合仍能稳定沿用上下文，不容易跑偏。",
        },
    },
    {
        "id": "iteration_repair",
        "label": "迭代修正",
        "layer": "执行控制层",
        "weight": 1.0,
        "description": "发现偏差后如何修，是否能短回合纠偏继续推。",
        "anchors": {
            0: "偏了以后修得慢，甚至不修。",
            2: "会修正，但常常改得太大或太慢。",
            4: "能快速定位关键偏差，最小修正后继续推进。",
        },
    },
    {
        "id": "failure_recovery",
        "label": "失败恢复",
        "layer": "执行控制层",
        "weight": 0.9,
        "description": "遇到阻力后是否会 fallback、缩范围、换打法保住主链路。",
        "anchors": {
            0: "一遇阻力就停住或原地打转。",
            2: "有 fallback 意识，但恢复不稳定。",
            4: "能在失败后快速缩范围、换路并保持推进。",
        },
    },
    {
        "id": "verification_loop",
        "label": "验证闭环",
        "layer": "结果闭环层",
        "weight": 1.0,
        "description": "是否会给测试、日志、证据和未验证项。",
        "anchors": {
            0: "几乎不验证，停在“看起来差不多”。",
            2: "有部分验证，但回报不完整。",
            4: "会交代怎么验、证据在哪、还有什么没验。",
        },
    },
    {
        "id": "deliverable_packaging",
        "label": "产物落地",
        "layer": "结果闭环层",
        "weight": 0.9,
        "description": "是否会把结果落成 README、脚本、JSON、卡片、导出包等清晰产物。",
        "anchors": {
            0: "主要停在口头结论，没有稳定产物。",
            2: "能落出单个产物，但交付链还不完整。",
            4: "会稳定产出可交付、可复用的一组结果文件。",
        },
    },
    {
        "id": "handoff_memory",
        "label": "交接与记忆",
        "layer": "结果闭环层",
        "weight": 0.9,
        "description": "是否重视跨轮连续性、snapshot、导出包和结果 skill 接管。",
        "anchors": {
            0: "每轮几乎重来，没有交接意识。",
            2: "会引用上次结果，但机制还不稳。",
            4: "有明确的跨轮交接、导出包或结果 skill 接管信号。",
        },
    },
    {
        "id": "abstraction_reuse",
        "label": "抽象复用",
        "layer": "结果闭环层",
        "weight": 1.0,
        "description": "是否会把一次成功沉成 skill、模板、规则、模块或流程。",
        "anchors": {
            0: "一次一做，很少沉淀抽象。",
            2: "会抽局部套路，但复用层还浅。",
            4: "能主动沉成 skill、模板、流程和模块。",
        },
    },
    {
        "id": "autonomous_push",
        "label": "自主推进深度",
        "layer": "杠杆放大量",
        "weight": 1.0,
        "description": "在少追问条件下，是否能连续推进多步。",
        "anchors": {
            0: "基本每一步都要追问。",
            2: "能推进 2 到 3 步，但复杂度一高就掉。",
            4: "少追问下仍能稳定推进多步并主动补关键动作。",
        },
    },
    {
        "id": "workflow_orchestration",
        "label": "并行与工作流化",
        "layer": "杠杆放大量",
        "weight": 1.0,
        "description": "是否出现多 agent、多工具、自动化、可复制流程等更高阶能力信号。",
        "anchors": {
            0: "仍以单线程聊天推进为主。",
            2: "已有少量并行、自动化或工作流信号。",
            4: "多 agent、多工具、工作流和传播链路都已进入主流程。",
        },
    },
]

FIELD_BY_ID = {field["id"]: field for field in SECONDARY_SKILL_FIELDS}
LAYER_ORDER = ["任务定义层", "执行控制层", "结果闭环层", "杠杆放大量"]
TAG_LABELS = {
    "goal_framing": "目标先收束",
    "context_supply": "上下文给够",
    "execution_preference": "直接动手",
    "verification_loop": "结果可验证",
    "tool_orchestration": "证据优先",
    "iteration_repair": "短回合修正",
    "autonomous_push": "多步推进",
    "workflow_orchestration": "工作流化",
}

AXIS_PATTERNS = {
    "goal_framing": [r"目标", r"边界", r"验收", r"输出物?", r"结果", r"起手", r"先.*?(确认|说清|整理)", r"帮我.*总结"],
    "context_supply": [r"/", r"路径", r"文件", r"仓库", r"背景", r"样例", r"示例", r"时间窗", r"历史", r"记录", r"session", r"jsonl"],
    "constraint_governance": [r"不要", r"别", r"必须", r"只保留", r"优先", r"兼容", r"约束", r"限制", r"不能", r"风格"],
    "communication_compression": [r"简洁", r"直接", r"人话", r"短句", r"结论优先", r"少废话", r"压缩", r"概括", r"别.*?解释"],
    "execution_preference": [r"直接", r"动手", r"开始做", r"先做", r"先跑", r"先读", r"先别讲", r"重构", r"实现", r"生成"],
    "task_decomposition": [r"拆成", r"分成", r"步骤", r"分步", r"阶段", r"下一步", r"计划", r"里程碑", r"todo"],
    "tool_orchestration": [r"读文件", r"跑命令", r"日志", r"脚本", r"tool", r"工具", r"rg\b", r"pytest", r"python", r"git", r"mcp", r"connector", r"browser", r"web"],
    "context_carry": [r"继续", r"沿用", r"刚才", r"上一轮", r"上一步", r"基于刚才", r"延续", r"主线", r"承接"],
    "iteration_repair": [r"修正", r"偏差", r"偏航", r"重做", r"补", r"调整", r"迭代", r"改一条", r"继续推进"],
    "failure_recovery": [r"fallback", r"兜底", r"补救", r"缩范围", r"换方案", r"换路", r"失败", r"卡住", r"绕过", r"最小可运行"],
    "verification_loop": [r"验证", r"测试", r"证据", r"日志", r"检查", r"确认", r"没验", r"未验证", r"risk", r"verify", r"test", r"run"],
    "deliverable_packaging": [r"README", r"readme", r"报告", r"分享卡", r"卡片", r"脚本", r"json", r"png", r"svg", r"SKILL", r"PROFILE", r"导出包", r"bundle"],
    "handoff_memory": [r"上次", r"记住", r"记忆", r"snapshot", r"导出包", r"结果 skill", r"接管", r"handoff", r"跨轮", r"历史"],
    "abstraction_reuse": [r"\bskill\b", r"模板", r"模块", r"流程", r"workflow", r"schema", r"规范", r"规则", r"可复用", r"沉淀"],
    "autonomous_push": [r"稳定推进", r"多步", r"连续", r"先推进", r"自己先做", r"一段工作", r"先干一段", r"持续往前"],
    "workflow_orchestration": [r"多 agent", r"多个 agent", r"并行", r"异步", r"自动化", r"workflow", r"delegate", r"后台", r"schedule", r"队列"],
}

ACTIVE_SUMMARIES = {
    "goal_framing": "起手偏好先说清目标、边界和验收，再让 agent 接手执行。",
    "context_supply": "偏好把路径、文件、背景和历史直接交给 agent，减少来回确认。",
    "constraint_governance": "会主动把必须项、禁忌和优先级讲清，避免执行时跑偏。",
    "communication_compression": "偏好短句、人话、结论优先的沟通方式。",
    "execution_preference": "更偏好直接动手、直接出结果，解释不要挡在执行前面。",
    "task_decomposition": "会把任务拆成连续步骤，并持续收束下一步动作。",
    "tool_orchestration": "倾向让 agent 读文件、跑命令、查日志、落脚本，而不是停在口头判断。",
    "context_carry": "长回合里会沿用刚才的主线继续推进，不希望上下文断掉。",
    "iteration_repair": "倾向短回合迭代，看到偏差就补一条关键修正继续推进。",
    "failure_recovery": "遇到阻力时会缩范围、换打法或 fallback，尽量保住主链路。",
    "verification_loop": "默认要可验证结果，最好顺带交代验证方式和未验证项。",
    "deliverable_packaging": "偏好把结果落成 README、脚本、JSON、卡片或导出包这类明确产物。",
    "handoff_memory": "在意跨轮连续性，接手时希望先读取历史、snapshot、导出包或结果 skill。",
    "abstraction_reuse": "会把一次成功沉成 skill、模板、流程、规则或模块，方便继续复用。",
    "autonomous_push": "希望 agent 少追问地连续推进多步，而不是每一步都停下来确认。",
    "workflow_orchestration": "已经开始出现并行、多 agent、自动化或工作流化的高阶信号。",
}

INSUFFICIENT_SUMMARIES = {
    "goal_framing": "当前记录里，目标 framing 还没有稳定证据。",
    "context_supply": "当前记录里，上下文供给信号还不够稳定。",
    "constraint_governance": "当前记录里，约束治理信号还不够明确。",
    "communication_compression": "当前记录里，沟通压缩度偏好还不够明确。",
    "execution_preference": "当前记录里，执行默认信号还不够稳定。",
    "task_decomposition": "当前记录里，任务拆解能力信号还不够多。",
    "tool_orchestration": "当前记录里，工具编排信号还不够充分。",
    "context_carry": "当前记录里，上下文承接信号还不够稳定。",
    "iteration_repair": "当前记录里，迭代修正信号还不够多。",
    "failure_recovery": "当前记录里，失败恢复信号还不够明确。",
    "verification_loop": "当前记录里，验证闭环信号还不够稳定。",
    "deliverable_packaging": "当前记录里，产物落地信号还不够充分。",
    "handoff_memory": "当前记录里，交接与记忆信号还不够稳定。",
    "abstraction_reuse": "当前记录里，抽象复用信号还不够明确。",
    "autonomous_push": "当前记录里，自主推进深度还缺少足够证据。",
    "workflow_orchestration": "当前记录里，并行和工作流化信号还不够多。",
}


def build_secondary_skill_distillation(
    *,
    messages: list[Message],
    display_name: str,
    source: str,
    rank: str,
    generated_at: str,
    models: list[str] | None = None,
    compression_mode: str = "first_two_sentences",
) -> dict[str, object]:
    compressed = [_compress_message(message, compression_mode=compression_mode) for message in messages if message.text.strip()]
    result_skill_name = result_skill_slug(display_name)
    result_skill_title = result_skill_title_from_display(display_name)
    axis_matches = _precompute_axis_matches(compressed)
    axes = [
        _build_axis(field, compressed, total_count=len(compressed), axis_matches=axis_matches)
        for field in SECONDARY_SKILL_FIELDS
    ]
    top_user_examples = [item["compressed"] for item in compressed if item["role"] == "user"][:8]
    top_assistant_examples = [item["compressed"] for item in compressed if item["role"] == "assistant"][:8]
    return {
        "version": 2,
        "display_name": display_name,
        "result_skill_name": result_skill_name,
        "result_skill_title": result_skill_title,
        "source": source,
        "rank": rank,
        "generated_at": generated_at,
        "compression_mode": compression_mode,
        "message_count": len(messages),
        "user_message_count": sum(1 for item in compressed if item["role"] == "user"),
        "assistant_message_count": sum(1 for item in compressed if item["role"] == "assistant"),
        "models": models or [],
        "fields": SECONDARY_SKILL_FIELDS,
        "axes": axes,
        "layer_scores": _build_layer_scores(axes),
        "user_prompt_samples": top_user_examples,
        "assistant_reply_samples": top_assistant_examples,
        "secondary_skill_contract": {
            "identity": f"按 {display_name} 这套 vibecoding 习惯推进任务，不做人设扮演。",
            "default_behavior": _build_default_behavior(axes),
            "guardrails": _build_guardrails(axes),
            "prompt_examples": _build_prompt_examples(display_name),
        },
    }


def render_secondary_skill_markdown(distillation: dict[str, object]) -> str:
    axes = distillation.get("axes") if isinstance(distillation, dict) else []
    if not isinstance(axes, list):
        axes = []
    layer_scores = distillation.get("layer_scores") if isinstance(distillation, dict) else []
    if not isinstance(layer_scores, list):
        layer_scores = []

    lines = [
        f"# {distillation.get('result_skill_title') or result_skill_title_from_display(str(distillation.get('display_name') or 'distilled'))}",
        "",
        "## 这份二级 skill 蒸馏了什么",
        "",
    ]
    for layer in LAYER_ORDER:
        layer_fields = [field for field in SECONDARY_SKILL_FIELDS if field["layer"] == layer]
        labels = "、".join(field["label"] for field in layer_fields)
        lines.append(f"- {layer}：{labels}")

    if layer_scores:
        lines.extend(["", "## 各层得分", ""])
        for item in layer_scores:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- {item.get('layer', '未知层')}：`{item.get('average_score', 0):.2f}/4`"
                f" · 已观测 `{item.get('observed_dimensions', 0)}` / `{item.get('dimension_count', 0)}` 维"
            )

    lines.extend(["", "## 当前蒸馏结果", ""])
    grouped_axes: dict[str, list[dict[str, object]]] = defaultdict(list)
    for axis in axes:
        if isinstance(axis, dict):
            grouped_axes[str(axis.get("layer") or "未分层")].append(axis)

    for layer in LAYER_ORDER:
        layer_axes = grouped_axes.get(layer, [])
        if not layer_axes:
            continue
        lines.extend([f"### {layer}", ""])
        for axis in layer_axes:
            lines.append(f"#### {axis.get('label', axis.get('id', 'axis'))}")
            lines.append(
                f"- 评分：`{axis.get('score', 0)}/4` · 置信度：`{axis.get('confidence', 0.0):.2f}`"
                f" · 证据：`{axis.get('evidence_count', 0)}` 条"
            )
            lines.append(f"- 判断：{axis.get('summary', '')}")
            anchors = axis.get("anchors")
            if isinstance(anchors, dict):
                lines.append(
                    f"- 锚点：`0` {anchors.get(0, '')} `2` {anchors.get(2, '')} `4` {anchors.get(4, '')}"
                )
            examples = axis.get("examples")
            if isinstance(examples, list):
                for item in examples[:2]:
                    lines.append(f"- 证据：{item}")
            lines.append("")

    contract = distillation.get("secondary_skill_contract", {})
    if isinstance(contract, dict):
        lines.extend(["## 二级 skill 默认行为", ""])
        for item in contract.get("default_behavior", []):
            lines.append(f"- {item}")
        lines.extend(["", "## Guardrails", ""])
        for item in contract.get("guardrails", []):
            lines.append(f"- {item}")
        lines.extend(["", "## Good Prompts", ""])
        for item in contract.get("prompt_examples", []):
            lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def build_readme_profile_panel(source: dict[str, object]) -> dict[str, object]:
    insights, distillation = _panel_sources(source)
    axes = distillation.get("axes") if isinstance(distillation, dict) else []
    if not isinstance(axes, list):
        axes = []
    axis_map = {axis.get("id"): axis for axis in axes if isinstance(axis, dict) and axis.get("id")}
    rank = str((insights or {}).get("rank") or distillation.get("rank") or "L1")
    display_name = str(
        source.get("display_name")
        or _dict_get(_dict_get(source, "transcript"), "display_name")
        or distillation.get("display_name")
        or "你"
    )
    facts = _build_profile_facts(display_name, rank, axis_map, insights=insights)

    panel = {
        "title": "你怎么和 AI 协作",
        "display_name": display_name,
        "rank": rank,
        "tags": _readme_tags(axis_map),
        "facts": facts,
        "paragraphs": _render_profile_paragraphs(facts),
        "bullets": _readme_bullets(axis_map),
    }
    panel["llm_prompt"] = _build_profile_llm_prompt(panel)
    return panel


def _panel_sources(source: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    if not isinstance(source, dict):
        return {}, {}
    insights = source.get("insights")
    secondary = source.get("secondary_skill")
    if isinstance(secondary, dict):
        return (insights if isinstance(insights, dict) else {}), secondary
    return {}, source


def _dict_get(source: object, key: str) -> object:
    if isinstance(source, dict):
        return source.get(key)
    return None


def _precompute_axis_matches(compressed: list[dict[str, str]]) -> list[set[str]]:
    results: list[set[str]] = []
    for item in compressed:
        matched: set[str] = set()
        for axis_id in AXIS_PATTERNS:
            if axis_id == "communication_compression":
                continue
            if _message_matches_axis(item["compressed"], axis_id):
                matched.add(axis_id)
        results.append(matched)
    return results


def _weighted_evidence_count(matched_indexes: list[int], axis_matches: list[set[str]]) -> float:
    total = 0.0
    for index in matched_indexes:
        overlap = len(axis_matches[index]) if index < len(axis_matches) else 0
        total += 1.0 / max(overlap, 1) ** 0.5
    return total


def _build_communication_axis(
    field: dict[str, object],
    compressed: list[dict[str, str]],
    *,
    total_count: int,
) -> dict[str, object]:
    user_messages = [item["compressed"] for item in compressed if item["role"] == "user" and item["compressed"].strip()]
    score, avg_length = _score_communication_compression(user_messages)
    examples = user_messages[:4]
    evidence_count = len(user_messages)
    coverage_ratio = round(len(user_messages) / max(total_count, 1), 4)
    confidence = 0.25 if not user_messages else round(min(0.4 + min(0.35, len(user_messages) * 0.06), 0.9), 2)
    if not user_messages:
        summary = INSUFFICIENT_SUMMARIES["communication_compression"]
    elif score >= 3:
        summary = "真实消息本身就偏短句、高密度、结论优先，不主要靠口头强调简洁。"
    elif score == 2:
        summary = f"沟通压缩度中等，消息平均长度约 {avg_length} 字，已经有结论优先倾向。"
    else:
        summary = f"真实消息仍偏长，消息平均长度约 {avg_length} 字，压缩风格还不够稳定。"
    return {
        "id": "communication_compression",
        "label": field["label"],
        "layer": field["layer"],
        "weight": field["weight"],
        "description": field["description"],
        "anchors": field["anchors"],
        "score": score,
        "coverage_ratio": coverage_ratio,
        "confidence": confidence,
        "summary": summary,
        "evidence_count": evidence_count,
        "weighted_evidence_count": round(float(evidence_count), 3),
        "user_evidence_count": evidence_count,
        "assistant_evidence_count": 0,
        "examples": examples,
    }


def _score_communication_compression(user_messages: list[str]) -> tuple[int, int]:
    if not user_messages:
        return 0, 0
    avg_length = round(sum(len(message) for message in user_messages) / len(user_messages))
    short_ratio = sum(1 for message in user_messages if len(message) <= 90) / len(user_messages)
    concise_ratio = sum(1 for message in user_messages if len(message.splitlines()) <= 6 and len(message) <= 140) / len(user_messages)
    if avg_length <= 90 and short_ratio >= 0.6:
        return 4, avg_length
    if avg_length <= 130 and concise_ratio >= 0.5:
        return 3, avg_length
    if avg_length <= 200:
        return 2, avg_length
    return 1, avg_length

def _build_axis(
    field: dict[str, object],
    compressed: list[dict[str, str]],
    *,
    total_count: int,
    axis_matches: list[set[str]],
) -> dict[str, object]:
    axis_id = str(field["id"])
    if axis_id == "communication_compression":
        return _build_communication_axis(field, compressed, total_count=total_count)
    matched = [item for item in compressed if _message_matches_axis(item["compressed"], axis_id)]
    matched_indexes = [index for index, item in enumerate(compressed) if _message_matches_axis(item["compressed"], axis_id)]
    role_counter = Counter(item["role"] for item in matched)
    weighted_evidence = _weighted_evidence_count(matched_indexes, axis_matches)
    score = _score_axis(matched, total_count=total_count, weighted_evidence=weighted_evidence)
    coverage_ratio = round(weighted_evidence / max(total_count, 1), 4)
    return {
        "id": axis_id,
        "label": field["label"],
        "layer": field["layer"],
        "weight": field["weight"],
        "description": field["description"],
        "anchors": field["anchors"],
        "score": score,
        "coverage_ratio": coverage_ratio,
        "confidence": _confidence(matched, weighted_evidence=weighted_evidence),
        "summary": _summarize_axis(axis_id, matched, score),
        "evidence_count": len(matched),
        "weighted_evidence_count": round(weighted_evidence, 3),
        "user_evidence_count": role_counter.get("user", 0),
        "assistant_evidence_count": role_counter.get("assistant", 0),
        "examples": [item["compressed"] for item in matched[:4]],
    }


def _build_layer_scores(axes: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for axis in axes:
        if isinstance(axis, dict):
            grouped[str(axis.get("layer") or "未分层")].append(axis)

    results: list[dict[str, object]] = []
    for layer in LAYER_ORDER:
        items = grouped.get(layer, [])
        if not items:
            continue
        weighted_total = sum(float(item.get("weight", 1.0) or 1.0) * int(item.get("score", 0) or 0) for item in items)
        total_weight = sum(float(item.get("weight", 1.0) or 1.0) for item in items) or 1.0
        results.append(
            {
                "layer": layer,
                "average_score": round(weighted_total / total_weight, 2),
                "dimension_count": len(items),
                "observed_dimensions": sum(1 for item in items if int(item.get("evidence_count", 0) or 0) > 0),
            }
        )
    return results


def _score_axis(matched: list[dict[str, str]], *, total_count: int, weighted_evidence: float) -> int:
    if weighted_evidence <= 0:
        return 0
    count = len(matched)
    if total_count <= 12:
        if count <= 1:
            score = 1
        elif weighted_evidence <= 1.25:
            score = 2
        elif weighted_evidence <= 2.5:
            score = 3
        else:
            score = 4
    else:
        ratio = weighted_evidence / max(total_count, 1)
        if ratio >= 0.12:
            score = 4
        elif ratio >= 0.04:
            score = 3
        elif ratio >= 0.01:
            score = 2
        else:
            score = 1
    role_count = len({item["role"] for item in matched})
    if count >= 3 and role_count == 2 and score < 4:
        score += 1
    return min(score, 4)


def _confidence(matched: list[dict[str, str]], *, weighted_evidence: float) -> float:
    count = len(matched)
    role_count = len({item["role"] for item in matched})
    if count == 0:
        return 0.25
    confidence = 0.35 + min(0.45, weighted_evidence * 0.12) + (0.1 if role_count == 2 else 0.0)
    return round(min(confidence, 0.95), 2)


def _summarize_axis(axis_id: str, matched: list[dict[str, str]], score: int) -> str:
    del matched
    if score <= 0:
        return INSUFFICIENT_SUMMARIES[axis_id]
    if score == 1:
        return f"已有初步信号，说明{_trim_tail(ACTIVE_SUMMARIES[axis_id])}。"
    return ACTIVE_SUMMARIES[axis_id]


def _build_default_behavior(axes: list[dict[str, object]]) -> list[str]:
    by_id = {axis["id"]: axis for axis in axes if isinstance(axis, dict) and axis.get("id")}
    lines = [
        _axis_summary(by_id, "goal_framing"),
        _axis_summary(by_id, "context_supply"),
        _axis_summary(by_id, "execution_preference"),
        _axis_summary(by_id, "verification_loop"),
        _axis_summary(by_id, "tool_orchestration"),
        _axis_summary(by_id, "iteration_repair"),
    ]
    return _dedupe(lines)


def _build_guardrails(axes: list[dict[str, object]]) -> list[str]:
    by_id = {axis["id"]: axis for axis in axes if isinstance(axis, dict) and axis.get("id")}
    lines = [
        _axis_summary(by_id, "constraint_governance")
        if _axis_score(by_id, "constraint_governance") > 0
        else "如果用户已经写了必须项、禁忌或优先级，执行时优先遵守这些边界。",
        _axis_summary(by_id, "communication_compression")
        if _axis_score(by_id, "communication_compression") > 0
        else "如果用户没有特别指定风格，默认短句、人话、结论优先。",
        "如果事实不够，先补文件、日志或命令结果，不要硬猜。",
    ]
    return _dedupe(lines)


def _build_prompt_examples(display_name: str) -> list[str]:
    return [
        f"按 {display_name} 这套 vibecoding 习惯和我一起推进这个任务。",
        "先收束目标、边界、验收，再直接开始做。",
        "先读相关文件并给我可验证结果，不要只讲方案。",
        "如果发现偏差，只补一条最关键修正，然后继续推进。",
    ]


PROFILE_LEVEL_SUMMARY = {
    "L1": "还在用单轮问答试手",
    "L2": "已经开始形成基本 prompt 手感",
    "L3": "能把简单任务稳定做完",
    "L4": "常见任务可以多步推进",
    "L5": "开始把顺手打法沉成模板",
    "L6": "已经能把一段具体工作交给 agent 先做",
    "L7": "能调动多 agent、多工具协同推进",
    "L8": "开始做系统级能力和工作流设计",
    "L9": "能把 agent 拉进真实业务回路",
    "L10": "这套方法已经能稳定复制给团队",
}


def _build_profile_facts(
    display_name: str,
    rank: str,
    axis_map: dict[str, dict[str, object]],
    *,
    insights: dict[str, object] | None = None,
) -> dict[str, str]:
    if insights:
        return {
            "opening": _compose_profile_paragraph_from_insights(display_name, rank, insights),
            "workflow": _compose_workflow_paragraph_from_insights(insights, axis_map),
            "impression": _compose_impression_paragraph_from_insights(insights, axis_map),
        }
    return {
        "opening": _compose_profile_paragraph(display_name, rank, axis_map),
        "workflow": _compose_workflow_paragraph(axis_map),
        "impression": _compose_impression_paragraph(axis_map),
    }


def _render_profile_paragraphs(facts: dict[str, str]) -> list[str]:
    return [item for item in (facts.get("opening"), facts.get("workflow"), facts.get("impression")) if item]


def _build_profile_llm_prompt(panel: dict[str, object]) -> str:
    facts = panel.get("facts")
    if not isinstance(facts, dict):
        facts = {}
    tags = panel.get("tags")
    if not isinstance(tags, list):
        tags = []
    bullets = panel.get("bullets")
    if not isinstance(bullets, list):
        bullets = []
    display_name = str(panel.get("display_name") or "用户")
    rank = str(panel.get("rank") or "L1")
    prompt_lines = [
        "你是 README 文案编辑器，要把结构化画像润色成接近仓库首页英雄区的人话文案。",
        "要求：",
        "- 只保留 3 段短段落。",
        "- 第一段必须先给等级结论，再进入协作画像。",
        "- 风格要像资深工程师在讲协作方式，短句，高密度，结论优先。",
        "- 不要发明结构化事实里没有的信息。",
        "- 保留 code agent、prompt、L4 这类关键技术词。",
        "- 禁止使用“不是……而是……”句式。",
        "",
        "结构化画像：",
        f"- 用户：{display_name}",
        f"- 等级：{rank}",
        f"- 标签：{', '.join(str(item) for item in tags)}",
        f"- 开场事实：{facts.get('opening', '')}",
        f"- 执行事实：{facts.get('workflow', '')}",
        f"- 总体判断：{facts.get('impression', '')}",
    ]
    if bullets:
        prompt_lines.append(f"- 补充要点：{'；'.join(str(item) for item in bullets)}")
    prompt_lines.extend(["", "输出：只给 3 段最终文案，不要解释。"])
    return "\n".join(prompt_lines)


def _compose_profile_paragraph_from_insights(display_name: str, rank: str, insights: dict[str, object]) -> str:
    claim = _primary_claim_from_insights(insights, rank)
    habit_lines = _list_of_strings(insights.get("habit_profile_lines"))
    if habit_lines:
        return f"{display_name}，你的水平已经达到了{rank}级，{claim}。{_strip_prefix(habit_lines[0])}"
    return f"{display_name}，你的水平已经达到了{rank}级，{claim}。"


def _compose_workflow_paragraph_from_insights(
    insights: dict[str, object],
    axis_map: dict[str, dict[str, object]],
) -> str:
    habit_lines = _list_of_strings(insights.get("habit_profile_lines"))
    if len(habit_lines) >= 2:
        return _strip_prefix(habit_lines[1])
    return _compose_workflow_paragraph(axis_map)


def _compose_impression_paragraph_from_insights(
    insights: dict[str, object],
    axis_map: dict[str, dict[str, object]],
) -> str:
    habit_lines = _list_of_strings(insights.get("habit_profile_lines"))
    breakthrough_lines = _list_of_strings(insights.get("breakthrough_lines"))
    if len(habit_lines) >= 3 and breakthrough_lines:
        return f"{_strip_prefix(habit_lines[2])} {breakthrough_lines[0]}"
    if len(habit_lines) >= 3:
        return _strip_prefix(habit_lines[2])
    return _compose_impression_paragraph(axis_map)


def _primary_claim_from_insights(insights: dict[str, object], rank: str) -> str:
    ability_text = str(insights.get("ability_text") or "").strip()
    for separator in (" 这轮最亮眼的是", " The strongest signals"):
        if separator in ability_text:
            ability_text = ability_text.split(separator, 1)[0].strip()
            break
    ability_text = ability_text.rstrip("。.")
    return ability_text or PROFILE_LEVEL_SUMMARY.get(rank, "当前任务已经能稳定推进")


def _list_of_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _strip_prefix(text: str) -> str:
    cleaned = str(text or "").strip()
    for prefix in ("起手习惯：", "推进习惯：", "容易掉点的地方："):
        if cleaned.startswith(prefix):
            return cleaned[len(prefix) :].strip()
    return cleaned


def _compose_profile_paragraph(display_name: str, rank: str, axis_map: dict[str, dict[str, object]]) -> str:
    framing = _axis_score(axis_map, "goal_framing") >= 2
    context = _axis_score(axis_map, "context_supply") >= 2
    execute = _axis_score(axis_map, "execution_preference") >= 2
    verify = _axis_score(axis_map, "verification_loop") >= 2

    opening = f"{display_name}，你的水平已经达到了{rank}级，{PROFILE_LEVEL_SUMMARY.get(rank, '当前任务已经能稳定推进')}，落实代码。"
    if framing and context and execute and verify:
        return (
            f"{opening} 你和 AI 对话时，起手就像在写一条可执行的 prompt："
            "先把目标、边界、验收和交付物钉住，再把路径、文件、背景和样例交给 code agent，"
            "让它接手时不用反复猜上下文。"
        )
    if framing and context:
        return (
            f"{opening} 你最突出的地方是 prompt 起手很稳。"
            "给 AI 下任务前，会先把目标和上下文摆好，让 code agent 一上来就知道先做什么。"
        )
    return f"{opening} 你的习惯是先把任务主线说清，再让 AI 顺着结果继续往下做。"


def _compose_workflow_paragraph(axis_map: dict[str, dict[str, object]]) -> str:
    tool = _axis_score(axis_map, "tool_orchestration") >= 2
    repair = _axis_score(axis_map, "iteration_repair") >= 2
    decompose = _axis_score(axis_map, "task_decomposition") >= 2
    autonomous = _axis_score(axis_map, "autonomous_push") >= 2

    if tool and repair and decompose:
        tail = "遇到偏差时，也更愿意补一条关键修正后继续推，不会把整轮工作打散重来。"
        if autonomous:
            tail = "遇到偏差时，会补一条关键修正继续推，而且通常希望 agent 少追问、多干活。"
        return (
            "具体到执行层，你给 code agent 的指令偏短、偏硬、偏落地。"
            "你会催着 agent 去读文件、跑命令、查日志，把任务拆成连续的小步，"
            f"{tail}"
        )
    if tool:
        return "具体到执行层，你明显更信证据而不是空讲。凡是能读文件、跑命令、查日志的地方，都会先让 code agent 动手，再根据结果补 prompt。"
    return "具体到执行层，你的对话节奏偏短回合、重落地，重点是先让 AI 做出结果，再按反馈继续改 prompt。"


def _compose_impression_paragraph(axis_map: dict[str, dict[str, object]]) -> str:
    strong = []
    if _axis_score(axis_map, "goal_framing") >= 2:
        strong.append("先收束任务")
    if _axis_score(axis_map, "context_supply") >= 2:
        strong.append("上下文给得足")
    if _axis_score(axis_map, "verification_loop") >= 2:
        strong.append("对结果有验收")
    if _axis_score(axis_map, "tool_orchestration") >= 2:
        strong.append("判断前先看证据")

    weak = []
    for axis_id, label in [
        ("iteration_repair", "偏了之后的修正速度"),
        ("handoff_memory", "跨轮交接"),
        ("autonomous_push", "长链路连续推进"),
        ("failure_recovery", "遇阻时的换路能力"),
    ]:
        score = _axis_score(axis_map, axis_id)
        if 0 < score < 2:
            weak.append(label)

    if strong and weak:
        return f"整体看，你很会驱动 AI 干活，强在{'、'.join(strong[:3])}；如果还想把这套 prompt 习惯继续打磨，下一步最该补的是{'、'.join(weak[:2])}。"
    if strong:
        return f"整体看，你已经很会带着 code agent 往前做事，强在{'、'.join(strong[:3])}，所以合作时很容易快速进入有效工作状态。"
    return ""


def _readme_tags(axis_map: dict[str, dict[str, object]]) -> list[str]:
    candidate_ids = [
        "goal_framing",
        "context_supply",
        "execution_preference",
        "verification_loop",
        "tool_orchestration",
        "iteration_repair",
        "autonomous_push",
        "workflow_orchestration",
    ]
    scored = [
        (axis_id, int(axis_map.get(axis_id, {}).get("score", 0) or 0))
        for axis_id in candidate_ids
        if axis_id in axis_map
    ]
    scored.sort(key=lambda item: (-item[1], candidate_ids.index(item[0])))
    tags = [TAG_LABELS[axis_id] for axis_id, score in scored if score >= 2 and axis_id in TAG_LABELS]
    return tags[:4]


def _readme_bullets(axis_map: dict[str, dict[str, object]]) -> list[str]:
    lines: list[str] = []
    if _axis_score(axis_map, "goal_framing") >= 2:
        lines.append("写 prompt 时会先把目标、边界和验收钉住。")
    if _axis_score(axis_map, "context_supply") >= 2:
        lines.append("给 code agent 下指令时，路径、文件和背景通常会一次性交代清楚。")
    if _axis_score(axis_map, "tool_orchestration") >= 2:
        lines.append("更信文件、命令和日志里的证据，不爱把 prompt 写成空话。")
    if _axis_score(axis_map, "verification_loop") >= 2:
        lines.append("收尾会追问验证结果和未验证项，不满足于“看起来差不多”。")
    return lines[:3]


def _axis_summary(axis_map: dict[str, dict[str, object]], axis_id: str) -> str:
    axis = axis_map.get(axis_id)
    if not isinstance(axis, dict):
        return INSUFFICIENT_SUMMARIES[axis_id]
    return str(axis.get("summary") or INSUFFICIENT_SUMMARIES[axis_id])


def _axis_score(axis_map: dict[str, dict[str, object]], axis_id: str) -> int:
    axis = axis_map.get(axis_id)
    if not isinstance(axis, dict):
        return 0
    return int(axis.get("score", 0) or 0)


def _trim_tail(text: str) -> str:
    cleaned = str(text or "").strip()
    return cleaned[:-1] if cleaned.endswith("。") else cleaned


def _compress_message(message: Message, *, compression_mode: str) -> dict[str, str]:
    return {
        "role": message.role,
        "compressed": compress_message_text(message.text, role=message.role, compression_mode=compression_mode),
    }


def compress_message_text(text: str, *, role: str, compression_mode: str = "first_two_sentences") -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    cleaned = re.sub(r"```[\s\S]*?```", " [代码块略] ", cleaned)
    if not cleaned:
        return ""
    if role == "user":
        return cleaned
    if compression_mode == "first_two_sentences":
        return _first_two_sentences(cleaned)
    if compression_mode == "assistant_brief" and role == "assistant":
        return _assistant_brief(cleaned)
    return _first_two_sentences(cleaned)


def _first_two_sentences(text: str) -> str:
    sentences = [item.strip() for item in re.split(r"(?<=[。！？.!?])", text) if item.strip()]
    if not sentences:
        return text[:180]
    return " ".join(sentences[:2])[:180]


def _assistant_brief(text: str) -> str:
    return _first_two_sentences(text)


def _message_matches_axis(text: str, axis_id: str) -> bool:
    patterns = AXIS_PATTERNS.get(axis_id, [])
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def result_skill_title_from_display(display_name: str) -> str:
    clean = display_name.strip() or "distilled"
    return clean if clean.endswith(".skill") else f"{clean}.skill"


def result_skill_slug(display_name: str) -> str:
    base = re.sub(r"\.skill$", "", display_name.strip(), flags=re.IGNORECASE)
    normalized = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii").lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    if normalized:
        return normalized[:48].rstrip("-") or "vibecoding-profile"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:8]
    return f"vibecoding-profile-{digest}"
