from __future__ import annotations

from statistics import mean

from .models import Analysis, Certificate, MetricScore, Persona, Transcript


REALM_LEVELS = [
    (0, "凡人"),
    (36, "炼气"),
    (48, "筑基"),
    (60, "金丹"),
    (72, "元婴"),
    (82, "化神"),
    (90, "炼虚"),
    (95, "合体"),
    (98, "大乘"),
]

AI_LEVELS = [
    (0, "对话木偶"),
    (36, "提示词学徒"),
    (48, "执行傀儡"),
    (60, "任务工匠"),
    (72, "工具驭者"),
    (82, "协作丹师"),
    (90, "推演司命"),
    (96, "破局宗师"),
]

LEVEL_TABLES = {
    "user": REALM_LEVELS,
    "assistant": AI_LEVELS,
}


def analyze_transcript(transcript: Transcript) -> Analysis:
    user_messages = [item for item in transcript.messages if item.role == "user"]
    assistant_messages = [item for item in transcript.messages if item.role == "assistant"]

    user_metrics = [
        MetricScore("目标清晰度", _score_clarity(user_messages), _explain_clarity(user_messages)),
        MetricScore("上下文供给", _score_context(user_messages), _explain_context(user_messages)),
        MetricScore("迭代修正力", _score_iteration(user_messages), _explain_iteration(user_messages)),
        MetricScore("验收意识", _score_verification(transcript, assistant_messages), _explain_verification(transcript)),
        MetricScore("协作节奏", _score_collaboration(user_messages, assistant_messages), _explain_collaboration(user_messages, assistant_messages)),
    ]

    assistant_metrics = [
        MetricScore("执行落地", _score_execution(assistant_messages), _explain_execution(assistant_messages)),
        MetricScore("工具调度", _score_tooling(transcript), _explain_tooling(transcript)),
        MetricScore("验证闭环", _score_verification(transcript, assistant_messages), _explain_verification(transcript)),
        MetricScore("上下文承接", _score_context_retention(user_messages, assistant_messages), _explain_context_retention(user_messages, assistant_messages)),
        MetricScore("补救适配", _score_recovery(user_messages, assistant_messages), _explain_recovery(user_messages, assistant_messages)),
    ]

    user_score = round(mean(metric.score for metric in user_metrics)) if user_metrics else 0
    assistant_score = round(mean(metric.score for metric in assistant_metrics)) if assistant_metrics else 0

    user_certificate = _build_user_certificate(user_score, user_metrics, transcript)
    assistant_certificate = _build_assistant_certificate(assistant_score, assistant_metrics, transcript)

    overview = (
        f"共解析 {len(transcript.messages)} 条有效消息，"
        f"用户 {len(user_messages)} 条，AI {len(assistant_messages)} 条，"
        f"工具调用 {transcript.tool_calls} 次。"
    )
    return Analysis(
        transcript=transcript,
        user_metrics=user_metrics,
        assistant_metrics=assistant_metrics,
        user_certificate=user_certificate,
        assistant_certificate=assistant_certificate,
        overview=overview,
    )


def level_rank(track: str, level: str) -> int:
    table = LEVEL_TABLES[track]
    for index, (_, name) in enumerate(table):
        if name == level:
            return index
    return -1


def compare_analyses(before: Analysis, after: Analysis) -> dict[str, object]:
    return {
        "overview": (
            f"对比两次会话：前次 {len(before.transcript.messages)} 条消息，"
            f"本次 {len(after.transcript.messages)} 条消息。"
        ),
        "user": _compare_track(before, after, track="user"),
        "assistant": _compare_track(before, after, track="assistant"),
    }


def _compare_track(before: Analysis, after: Analysis, track: str) -> dict[str, object]:
    before_certificate = before.user_certificate if track == "user" else before.assistant_certificate
    after_certificate = after.user_certificate if track == "user" else after.assistant_certificate
    before_metrics = before.user_metrics if track == "user" else before.assistant_metrics
    after_metrics = after.user_metrics if track == "user" else after.assistant_metrics

    deltas = []
    before_map = {item.name: item.score for item in before_metrics}
    after_map = {item.name: item.score for item in after_metrics}
    for name, before_score in before_map.items():
        after_score = after_map.get(name, before_score)
        deltas.append({"name": name, "before": before_score, "after": after_score, "delta": after_score - before_score})

    deltas.sort(key=lambda item: item["delta"], reverse=True)
    improved = [item for item in deltas if item["delta"] > 0]
    regressed = [item for item in deltas if item["delta"] < 0]

    before_rank = level_rank(track, before_certificate.level)
    after_rank = level_rank(track, after_certificate.level)
    score_delta = after_certificate.score - before_certificate.score

    if after_rank > before_rank:
        outcome = "破境成功"
    elif after_rank == before_rank and score_delta > 0:
        outcome = "境界未变，但功力上涨"
    elif score_delta == 0:
        outcome = "境界持平"
    else:
        outcome = "本轮未能突破"

    return {
        "title": before_certificate.title,
        "outcome": outcome,
        "before_level": before_certificate.level,
        "after_level": after_certificate.level,
        "before_score": before_certificate.score,
        "after_score": after_certificate.score,
        "score_delta": score_delta,
        "top_improvements": improved[:3],
        "top_regressions": regressed[:2],
        "next_focus": _compare_next_focus(improved, regressed, after_metrics),
    }


def _compare_next_focus(improved: list[dict[str, int]], regressed: list[dict[str, int]], after_metrics: list[MetricScore]) -> list[str]:
    lines: list[str] = []
    if improved:
        best = improved[0]
        lines.append(f"本轮涨幅最大的是“{best['name']}”，提升了 {best['delta']} 分。")
    if regressed:
        worst = regressed[0]
        lines.append(f"本轮回落最多的是“{worst['name']}”，下降了 {abs(worst['delta'])} 分。")
    weakest = sorted(after_metrics, key=lambda item: item.score)[:2]
    for item in weakest:
        if item.name == "验收意识":
            lines.append("下一轮继续强制每阶段附验证命令和可观察结果。")
        elif item.name == "验证闭环":
            lines.append("让 AI 在回报里固定写清“改了什么、怎么验、还有什么没验”。")
        elif item.name == "协作节奏":
            lines.append("把任务拆成更短的回合，单关验收后再推进。")
        elif item.name == "上下文承接":
            lines.append("连续回合重复关键目标词，降低上下文漂移。")
        elif item.name == "执行落地":
            lines.append("要求 AI 先做第一步实现，再给总结。")
        elif item.name == "目标清晰度":
            lines.append("把目标改写成“目标 + 约束 + 输出物 + 验收”。")
    deduped: list[str] = []
    for line in lines:
        if line not in deduped:
            deduped.append(line)
    return deduped[:3]


def _score_clarity(messages) -> int:
    if not messages:
        return 0
    lengths = [len(item.text) for item in messages]
    avg_len = mean(lengths)
    keyword_bonus = sum(any(token in item.text for token in ["目标", "希望", "需要", "请", "实现", "修复", "新增"]) for item in messages)
    score = 28
    score += min(int(avg_len / 8), 28)
    score += min(keyword_bonus * 4, 20)
    if any("\n" in item.text or "1." in item.text or "-" in item.text for item in messages):
        score += 12
    return min(score, 100)


def _score_context(messages) -> int:
    if not messages:
        return 0
    score = 20
    for item in messages:
        text = item.text
        if any(token in text for token in ["/", ".ts", ".py", ".md", "README", "src/", "tests/", "package.json"]):
            score += 8
        if any(token in text for token in ["环境", "仓库", "目录", "模型", "系统", "运行", "日志"]):
            score += 5
        if any(token in text for token in ["限制", "风格", "不要", "需要保留", "public", "private"]):
            score += 5
    return min(score, 100)


def _score_iteration(messages) -> int:
    if not messages:
        return 0
    score = 18 + min(len(messages) * 9, 45)
    refine_hits = sum(any(token in item.text for token in ["继续", "再", "改", "补", "调整", "优化", "下一步", "进一步"]) for item in messages)
    score += min(refine_hits * 8, 30)
    return min(score, 100)


def _score_verification(transcript: Transcript, assistant_messages) -> int:
    score = 12
    score += min(transcript.tool_calls * 7, 42)
    verification_hits = 0
    for item in assistant_messages:
        if any(token in item.text.lower() for token in ["test", "build", "验证", "检查", "smoke", "run", "git status"]):
            verification_hits += 1
    score += min(verification_hits * 8, 46)
    return min(score, 100)


def _score_collaboration(user_messages, assistant_messages) -> int:
    if not user_messages or not assistant_messages:
        return 25
    ratio = min(len(user_messages), len(assistant_messages)) / max(len(user_messages), len(assistant_messages))
    score = 35 + int(ratio * 35)
    if len(user_messages) >= 2 and len(assistant_messages) >= 2:
        score += 15
    if any(len(item.text) > 180 for item in user_messages):
        score += 10
    return min(score, 100)


def _score_execution(messages) -> int:
    if not messages:
        return 0
    score = 25 + min(len(messages) * 8, 35)
    action_hits = sum(any(token in item.text for token in ["我先", "接下来", "已", "完成", "会", "正在", "验证"]) for item in messages)
    score += min(action_hits * 6, 30)
    return min(score, 100)


def _score_tooling(transcript: Transcript) -> int:
    return min(18 + transcript.tool_calls * 12, 100)


def _score_context_retention(user_messages, assistant_messages) -> int:
    if not user_messages or not assistant_messages:
        return 20
    user_keywords = _collect_keywords(user_messages)
    assistant_keywords = _collect_keywords(assistant_messages)
    overlap = len(user_keywords & assistant_keywords)
    return min(24 + overlap * 8, 100)


def _score_recovery(user_messages, assistant_messages) -> int:
    friction = any(any(token in item.text for token in ["报错", "失败", "不对", "太难", "卡住", "问题"]) for item in user_messages)
    adaptation = any(any(token in item.text for token in ["方案", "改成", "先", "分步", "独立", "兼容", "回退"]) for item in assistant_messages)
    score = 38
    if friction:
        score += 18
    if adaptation:
        score += 26
    return min(score, 100)


def _collect_keywords(messages) -> set[str]:
    keywords: set[str] = set()
    for item in messages:
        for token in ["README", "skill", "repo", "git", "public", "证书", "日志", "解析", "用户", "AI", "协作", "境界"]:
            if token.lower() in item.text.lower():
                keywords.add(token.lower())
    return keywords


def _build_user_certificate(score: int, metrics: list[MetricScore], transcript: Transcript) -> Certificate:
    level = _pick_level(score, REALM_LEVELS)
    top = sorted(metrics, key=lambda item: item.score, reverse=True)
    low = sorted(metrics, key=lambda item: item.score)
    persona = Persona(
        title=f"{level}协作修士",
        subtitle="会给边界、会补上下文、愿意反复打磨",
        tags=_metric_tags(top[:3]),
        summary="你更像一位把 AI 当共同修炼对象的主导者，重点不在一次出奇迹，而在持续拉高回合质量。",
    )
    evidence = [
        f"目标最强项：{top[0].name} {top[0].score}/100，{top[0].rationale}",
        f"当前短板：{low[0].name} {low[0].score}/100，{low[0].rationale}",
        f"本次样本来自 {transcript.source}，共 {len(transcript.messages)} 条有效消息。",
    ]
    growth_plan = _growth_plan(low[:2], user_track=True)
    return Certificate(
        track="user",
        title="修仙画像",
        level=level,
        score=score,
        persona=persona,
        evidence=evidence,
        growth_plan=growth_plan,
    )


def _build_assistant_certificate(score: int, metrics: list[MetricScore], transcript: Transcript) -> Certificate:
    level = _pick_level(score, AI_LEVELS)
    top = sorted(metrics, key=lambda item: item.score, reverse=True)
    low = sorted(metrics, key=lambda item: item.score)
    persona = Persona(
        title=f"{level}型 AI 协作者",
        subtitle="偏执行、重闭环、看证据说话",
        tags=_metric_tags(top[:3]),
        summary="这类 AI 适合承担拆解、实现、验证与回收问题的工作，但仍需要你提供更高质量的上下文燃料。",
    )
    evidence = [
        f"AI 强项：{top[0].name} {top[0].score}/100，{top[0].rationale}",
        f"AI 可补位项：{low[0].name} {low[0].score}/100，{low[0].rationale}",
        f"工具调用累计 {transcript.tool_calls} 次。",
    ]
    growth_plan = _growth_plan(low[:2], user_track=False)
    return Certificate(
        track="assistant",
        title="AI 协作能力证书",
        level=level,
        score=score,
        persona=persona,
        evidence=evidence,
        growth_plan=growth_plan,
    )


def _pick_level(score: int, table: list[tuple[int, str]]) -> str:
    current = table[0][1]
    for threshold, name in table:
        if score >= threshold:
            current = name
    return current


def _metric_tags(metrics: list[MetricScore]) -> list[str]:
    mapping = {
        "目标清晰度": "指令清晰",
        "上下文供给": "上下文稳定",
        "迭代修正力": "回合耐久",
        "验收意识": "自带验收",
        "协作节奏": "回合同频",
        "执行落地": "执行型",
        "工具调度": "善用工具",
        "验证闭环": "闭环意识",
        "上下文承接": "承接上下文",
        "补救适配": "会拐弯",
    }
    return [mapping.get(item.name, item.name) for item in metrics]


def _growth_plan(metrics: list[MetricScore], user_track: bool) -> list[str]:
    plans: list[str] = []
    for item in metrics:
        if item.name == "目标清晰度":
            plans.append("下一周期把请求写成“目标 + 约束 + 输出物 + 验收”四段式。")
        elif item.name == "上下文供给":
            plans.append("把关键文件、路径、模型、运行方式一次给全，减少 AI 补问成本。")
        elif item.name == "迭代修正力":
            plans.append("每轮只改一个核心变量，并明确保留什么、不保留什么。")
        elif item.name == "验收意识":
            plans.append("要求 AI 在每个阶段附上验证命令或可观察结果。")
        elif item.name == "协作节奏":
            plans.append("把大目标拆成 3 个小关卡，每过一关就收一次结果。")
        elif item.name == "执行落地":
            plans.append("让 AI 先报第一步，再做实现，避免空泛总结。")
        elif item.name == "工具调度":
            plans.append("鼓励 AI 先读仓库、跑命令、看真实日志，再给方案。")
        elif item.name == "验证闭环":
            plans.append("要求 AI 说明“改了什么、怎么验、哪里还没验”。")
        elif item.name == "上下文承接":
            plans.append("在连续会话里重复目标名词，降低上下文漂移。")
        elif item.name == "补救适配":
            plans.append("遇到失败后先缩小范围，改成最小可用版本再突破。")
    if not plans:
        plans.append("继续累计高质量回合，下个周期冲击更高证书。")
    if user_track:
        plans.append("完成一轮新项目协作后，用最新日志再次 recertify。")
    else:
        plans.append("让 AI 在下一轮任务里强制执行“实现 -> 验证 -> 回报”节奏。")
    return plans[:3]


def _explain_clarity(messages) -> str:
    if not messages:
        return "没有用户消息，无法判断。"
    if any(len(item.text) > 120 for item in messages):
        return "存在较完整的任务描述，目标表达偏清晰。"
    return "能表达基本诉求，但还可以更早给出验收目标。"


def _explain_context(messages) -> str:
    hits = sum(any(token in item.text for token in ["/", ".md", ".py", ".ts", "仓库", "日志"]) for item in messages)
    if hits >= 2:
        return "用户提供了路径、文件或环境信息，AI 更容易落地。"
    return "上下文仍偏口语化，建议补路径、文件名和约束。"


def _explain_iteration(messages) -> str:
    if len(messages) >= 3:
        return "存在多轮补充或修正，具备持续打磨意识。"
    return "当前更像单轮指令，后续可增加定向修正。"


def _explain_verification(transcript: Transcript) -> str:
    if transcript.tool_calls >= 3:
        return "会话里有明显的读取、搜索或验证动作。"
    return "验证动作不算多，可以更主动要求测试与回收。"


def _explain_collaboration(user_messages, assistant_messages) -> str:
    if len(user_messages) >= 2 and len(assistant_messages) >= 2:
        return "双方回合同步，已经形成共同推进节奏。"
    return "互动回合偏少，适合拆小步增加反馈频率。"


def _explain_execution(messages) -> str:
    if any("完成" in item.text or "开始" in item.text for item in messages):
        return "AI 明显偏执行流，而非只做抽象建议。"
    return "AI 仍有总结倾向，可以要求先做再说。"


def _explain_tooling(transcript: Transcript) -> str:
    if transcript.tool_calls >= 4:
        return "AI 已经把工具当作主工作流的一部分。"
    if transcript.tool_calls >= 1:
        return "AI 有工具意识，但还未完全进入高强度执行节奏。"
    return "当前几乎没有工具痕迹。"


def _explain_context_retention(user_messages, assistant_messages) -> str:
    if _collect_keywords(user_messages) & _collect_keywords(assistant_messages):
        return "AI 基本承接了用户的关键主题词。"
    return "AI 对用户语境的复用度还不够。"


def _explain_recovery(user_messages, assistant_messages) -> str:
    has_issue = any(any(token in item.text for token in ["问题", "太难", "失败", "报错"]) for item in user_messages)
    if has_issue:
        return "会话里出现阻力后，AI 有调整路线的空间。"
    return "本次样本阻力较少，补救能力观测有限。"
