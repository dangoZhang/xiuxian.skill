from __future__ import annotations

from pathlib import Path
from statistics import mean, median

from .models import Analysis, Certificate, MetricScore, Persona, Transcript


REALM_LEVELS = [
    (0, "凡人"),
    (12, "感气"),
    (24, "炼气"),
    (36, "筑基"),
    (48, "金丹"),
    (60, "元婴"),
    (70, "化神"),
    (78, "炼虚"),
    (86, "合体"),
    (92, "大乘"),
    (97, "渡劫"),
    (99, "飞升"),
]

REALM_DESCRIPTIONS = {
    "凡人": "还把 AI 当玩具，不当生产力",
    "感气": "开始知道提问方式会改变结果",
    "炼气": "已经有 prompt 手感，能稳定做简单任务",
    "筑基": "开始有固定流程，同类任务能反复跑通",
    "金丹": "开始把自己的做法封成技法 / 模板 / 模块",
    "元婴": "开始拥有“能替自己先干一段活”的分身",
    "化神": "能同时调多个分身、多个工具协同完成任务",
    "炼虚": "不再做单任务优化，开始做能力层和世界模型",
    "合体": "人负责判断和担责，分身负责执行和回流",
    "大乘": "能把自己的方法复制给团队或客户",
    "渡劫": "经得住真实业务、客户、异常、合规检验",
    "飞升": "工作方式已经被 AI 重写，不再只是“会用工具”",
}

REALM_AURAS = {
    "凡人": "气海未开",
    "感气": "灵机初动",
    "炼气": "气息渐稳",
    "筑基": "根骨已立",
    "金丹": "丹火初成",
    "元婴": "元神将显",
    "化神": "神念外放",
    "炼虚": "虚实相济",
    "合体": "人机同脉",
    "大乘": "道法成势",
    "渡劫": "雷劫临门",
    "飞升": "道成可传",
}

AI_LEVELS = [
    (0, "L1"),
    (16, "L2"),
    (28, "L3"),
    (40, "L4"),
    (52, "L5"),
    (64, "L6"),
    (74, "L7"),
    (82, "L8"),
    (90, "L9"),
    (96, "L10"),
]

AI_LEVEL_DESCRIPTIONS = {
    "L1": "仍以单轮问答为主",
    "L2": "开始知道提问方式会改变结果",
    "L3": "能稳定完成简单任务",
    "L4": "已经能重复跑通常见流程",
    "L5": "开始把经验封成模板或技法",
    "L6": "能先替你推进一段具体工作",
    "L7": "能协同多个分身与工具完成任务",
    "L8": "开始承担能力层与系统层工作",
    "L9": "能进入真实业务回路并持续回流",
    "L10": "方法已可复制到团队与客户场景",
}

LEVEL_TABLES = {
    "user": REALM_LEVELS,
    "assistant": AI_LEVELS,
}

METHOD_SEDIMENT_TOKENS = ["skill", "workflow", "模板", "模块", "sop", "章法", "复用", "标准化"]


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

    raw_user_score = round(mean(metric.score for metric in user_metrics)) if user_metrics else 0
    raw_assistant_score = round(mean(metric.score for metric in assistant_metrics)) if assistant_metrics else 0
    method_sediment = _has_method_sediment(transcript.messages)
    user_score = _cap_score_by_capability(
        "user",
        raw_user_score,
        _user_cap_rank(
            user_metrics,
            assistant_metrics,
            total_messages=len(transcript.messages),
            tool_calls=transcript.tool_calls,
            session_count=1,
            method_sediment=method_sediment,
        ),
    )
    assistant_score = _cap_score_by_capability(
        "assistant",
        raw_assistant_score,
        _assistant_cap_rank(
            assistant_metrics,
            total_messages=len(transcript.messages),
            tool_calls=transcript.tool_calls,
            session_count=1,
            method_sediment=method_sediment,
        ),
    )

    user_certificate = _build_user_certificate(user_score, user_metrics, transcript)
    assistant_certificate = _build_assistant_certificate(assistant_score, assistant_metrics, transcript)

    overview = (
        f"共解析 {len(transcript.messages)} 条有效消息，"
        f"用户 {len(user_messages)} 条，AI {len(assistant_messages)} 条，"
        f"工具调用 {transcript.tool_calls} 次。"
    )
    if transcript.token_usage.total_tokens:
        overview += f"累计消耗 {transcript.token_usage.total_tokens} token。"
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


def aggregate_analyses(analyses: list[Analysis], min_messages: int = 8) -> dict[str, object]:
    if not analyses:
        raise ValueError("No analyses to aggregate.")

    eligible = [item for item in analyses if len(item.transcript.messages) >= min_messages]
    pool = eligible or analyses
    dropped = len(analyses) - len(pool)
    total_messages = sum(len(item.transcript.messages) for item in pool)
    total_tool_calls = sum(item.transcript.tool_calls for item in pool)
    total_tokens = sum(item.transcript.token_usage.total_tokens for item in pool)
    total_input_tokens = sum(item.transcript.token_usage.input_tokens for item in pool)
    total_cached_input_tokens = sum(item.transcript.token_usage.cached_input_tokens for item in pool)
    total_output_tokens = sum(item.transcript.token_usage.output_tokens for item in pool)
    total_reasoning_output_tokens = sum(item.transcript.token_usage.reasoning_output_tokens for item in pool)

    user_metrics = _aggregate_metric_scores([item.user_metrics for item in pool])
    assistant_metrics = _aggregate_metric_scores([item.assistant_metrics for item in pool])

    raw_user_score = _stable_high_score([item.user_certificate.score for item in pool])
    raw_assistant_score = _stable_high_score([item.assistant_certificate.score for item in pool])

    models = _merge_unique(item for analysis in pool for item in analysis.transcript.models)
    providers = _merge_unique(item for analysis in pool for item in analysis.transcript.providers)
    method_sediment = any(_has_method_sediment(item.transcript.messages) for item in pool)
    user_score = _cap_score_by_capability(
        "user",
        raw_user_score,
        _user_cap_rank(
            user_metrics,
            assistant_metrics,
            total_messages=total_messages,
            tool_calls=total_tool_calls,
            session_count=len(pool),
            method_sediment=method_sediment,
        ),
    )
    assistant_score = _cap_score_by_capability(
        "assistant",
        raw_assistant_score,
        _assistant_cap_rank(
            assistant_metrics,
            total_messages=total_messages,
            tool_calls=total_tool_calls,
            session_count=len(pool),
            method_sediment=method_sediment,
        ),
    )

    overview = (
        f"共纳入 {len(pool)} 场会话，累计 {total_messages} 条有效消息，"
        f"工具调用 {total_tool_calls} 次。"
    )
    if total_tokens:
        overview += f"累计消耗 {total_tokens} token。"
    if dropped:
        overview += f" 另有 {dropped} 场低样本会话因消息数低于 {min_messages} 被排除。"

    return {
        "overview": overview,
        "sessions_total": len(analyses),
        "sessions_used": len(pool),
        "sessions_dropped": dropped,
        "min_messages": min_messages,
        "total_messages": total_messages,
        "total_tool_calls": total_tool_calls,
        "models": models,
        "providers": providers,
        "token_usage": {
            "input_tokens": total_input_tokens,
            "cached_input_tokens": total_cached_input_tokens,
            "output_tokens": total_output_tokens,
            "reasoning_output_tokens": total_reasoning_output_tokens,
            "total_tokens": total_tokens,
        },
        "user_metrics": user_metrics,
        "assistant_metrics": assistant_metrics,
        "user_certificate": _build_aggregate_certificate("user", user_score, user_metrics, len(pool), total_messages),
        "assistant_certificate": _build_aggregate_certificate("assistant", assistant_score, assistant_metrics, len(pool), total_messages),
    }


def infer_talent(transcript: Transcript) -> dict[str, str] | None:
    models = list(dict.fromkeys(transcript.models))
    if not models:
        return None
    primary = models[0]
    if len(models) > 1:
        root = "杂灵根"
        aptitude = f"多模型杂修（{len(models)} 炉并修）"
    else:
        lowered = primary.lower()
        if "gpt-5" in lowered or "claude-opus" in lowered:
            root = "天灵根"
            aptitude = "上品资质"
        elif "claude" in lowered or "gpt-4" in lowered or "gemini" in lowered:
            root = "地灵根"
            aptitude = "上中资质"
        elif any(token in lowered for token in ["deepseek", "qwen", "mistral", "llama"]):
            root = "玄灵根"
            aptitude = "中品资质"
        else:
            root = "异灵根"
            aptitude = "可塑资质"
    return {
        "root": root,
        "aptitude": aptitude,
        "primary_model": primary,
        "models": " / ".join(models[:4]),
    }


def infer_talent_from_models(models: list[str]) -> dict[str, str] | None:
    if not models:
        return None
    transcript = Transcript(source="aggregate", path=Path("."), messages=[], models=models)
    return infer_talent(transcript)


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


def _aggregate_metric_scores(metric_lists: list[list[MetricScore]]) -> list[MetricScore]:
    names = [item.name for item in metric_lists[0]]
    aggregated: list[MetricScore] = []
    for name in names:
        scores = [item.score for metrics in metric_lists for item in metrics if item.name == name]
        score = _stable_high_score(scores)
        rationale = f"基于 {len(scores)} 个样本高位聚合，中位数 {round(median(scores))}，高位分 {score}。"
        aggregated.append(MetricScore(name=name, score=score, rationale=rationale))
    return aggregated


def _stable_high_score(scores: list[int]) -> int:
    if not scores:
        return 0
    ordered = sorted(scores)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * 0.8) - 1))
    high_quantile = ordered[index]
    return max(round(median(ordered)), high_quantile)


def _merge_unique(items) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return seen


def _build_aggregate_certificate(
    track: str,
    score: int,
    metrics: list[MetricScore],
    session_count: int,
    total_messages: int,
) -> dict[str, object]:
    level = _pick_level(score, REALM_LEVELS if track == "user" else AI_LEVELS)
    top = sorted(metrics, key=lambda item: item.score, reverse=True)
    low = sorted(metrics, key=lambda item: item.score)
    if track == "user":
        persona_title = f"{level}协作修士"
        title = "修为判定"
        subtitle = REALM_DESCRIPTIONS[level]
        summary = f"这是你在多场真实协作里的稳定层次。当前已到 {level}，补齐短板后再看下一次突破。"
    else:
        persona_title = f"{level} 协作等级"
        title = "等级判定"
        subtitle = AI_LEVEL_DESCRIPTIONS[level]
        summary = "这是 AI 在长期协作样本里的稳定等级，不取单次峰值。"
    return {
        "track": track,
        "title": title,
        "level": level,
        "score": score,
        "persona": {
            "title": persona_title,
            "subtitle": subtitle,
            "tags": _metric_tags(top[:3]),
            "summary": summary,
        },
        "evidence": [
            f"共纳入 {session_count} 场会话，累计 {total_messages} 条有效消息。",
            f"定级采用高位分位聚合，不直接取单次最高分。",
            f"最强项：{top[0].name} {top[0].score}/100；当前短板：{low[0].name} {low[0].score}/100。",
        ],
        "growth_plan": _growth_plan(low[:2], user_track=(track == "user")),
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
    aura = REALM_AURAS[level]
    top_trait = _user_metric_phrase(top[0].name, style="tag")
    second_trait = _user_metric_phrase(top[1].name, style="tag") if len(top) > 1 else top_trait
    weak_trait = _user_metric_phrase(low[0].name, style="weak")
    persona = Persona(
        title=f"{level}修士",
        subtitle=REALM_DESCRIPTIONS[level],
        tags=[aura, top_trait, second_trait],
        summary=f"照此行迹，已入{level}之境，{aura}。你如今长于{top_trait}，但{weak_trait}仍是眼下短板，补齐此处后才好再望上境。",
    )
    evidence = [
        f"主修道法：{_user_metric_phrase(top[0].name, style='title')} {top[0].score}/100，{top[0].rationale}",
        f"待补关隘：{_user_metric_phrase(low[0].name, style='weak_title')} {low[0].score}/100，{low[0].rationale}",
        f"此番观测来自 {transcript.source}，共 {len(transcript.messages)} 条有效消息。",
    ]
    growth_plan = _growth_plan(low[:2], user_track=True)
    return Certificate(
        track="user",
        title="修为判定",
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
        title=f"{level} 协作等级",
        subtitle=AI_LEVEL_DESCRIPTIONS[level],
        tags=_metric_tags(top[:3], track="assistant"),
        summary="等级按真实会话稳定高位定级，用来判断当前可承担的协作强度。",
    )
    evidence = [
        f"当前最强项：{top[0].name} {top[0].score}/100，{top[0].rationale}",
        f"当前短板：{low[0].name} {low[0].score}/100，{low[0].rationale}",
        f"tool calls：{transcript.tool_calls}",
    ]
    growth_plan = _growth_plan(low[:2], user_track=False)
    return Certificate(
        track="assistant",
        title="等级判定",
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


def _pick_rank(score: int, table: list[tuple[int, str]]) -> int:
    current = 0
    for index, (threshold, _) in enumerate(table):
        if score >= threshold:
            current = index
    return current


def _cap_score_by_capability(track: str, score: int, cap_rank: int) -> int:
    table = LEVEL_TABLES[track]
    if cap_rank >= len(table) - 1:
        return score
    max_score = table[cap_rank + 1][0] - 1
    return min(score, max_score)


def _metric_map(metrics: list[MetricScore]) -> dict[str, int]:
    return {item.name: item.score for item in metrics}


def _has_method_sediment(messages) -> bool:
    text = " ".join(item.text.lower() for item in messages)
    return any(token in text for token in METHOD_SEDIMENT_TOKENS)


def _user_cap_rank(
    user_metrics: list[MetricScore],
    assistant_metrics: list[MetricScore],
    *,
    total_messages: int,
    tool_calls: int,
    session_count: int,
    method_sediment: bool,
) -> int:
    user_map = _metric_map(user_metrics)
    assistant_map = _metric_map(assistant_metrics)
    cap = 2
    if total_messages >= 4 and user_map.get("协作节奏", 0) >= 55 and user_map.get("上下文供给", 0) >= 40:
        cap = 3
    if method_sediment:
        cap = max(cap, 4)
    if assistant_map.get("执行落地", 0) >= 50 and tool_calls >= 1:
        cap = max(cap, 5)
    if assistant_map.get("执行落地", 0) >= 50 and assistant_map.get("工具调度", 0) >= 40 and tool_calls >= 2:
        cap = max(cap, 6)
    if assistant_map.get("工具调度", 0) >= 50 and assistant_map.get("上下文承接", 0) >= 45 and tool_calls >= 3:
        cap = max(cap, 7)
    if assistant_map.get("验证闭环", 0) >= 45 and assistant_map.get("补救适配", 0) >= 45 and tool_calls >= 4:
        cap = max(cap, 8)
    if session_count >= 3 and method_sediment and assistant_map.get("验证闭环", 0) >= 45:
        cap = max(cap, 9)
    if session_count >= 5 and assistant_map.get("验证闭环", 0) >= 55 and assistant_map.get("补救适配", 0) >= 55:
        cap = max(cap, 10)
    if session_count >= 8 and assistant_map.get("执行落地", 0) >= 60 and assistant_map.get("验证闭环", 0) >= 60 and assistant_map.get("工具调度", 0) >= 60:
        cap = max(cap, 11)
    return cap


def _assistant_cap_rank(
    assistant_metrics: list[MetricScore],
    *,
    total_messages: int,
    tool_calls: int,
    session_count: int,
    method_sediment: bool,
) -> int:
    assistant_map = _metric_map(assistant_metrics)
    cap = 2
    if total_messages >= 2 and assistant_map.get("执行落地", 0) >= 45:
        cap = 3
    if method_sediment:
        cap = max(cap, 4)
    if assistant_map.get("执行落地", 0) >= 50 and tool_calls >= 1:
        cap = max(cap, 5)
    if assistant_map.get("工具调度", 0) >= 40 and assistant_map.get("上下文承接", 0) >= 40 and tool_calls >= 2:
        cap = max(cap, 6)
    if assistant_map.get("工具调度", 0) >= 50 and assistant_map.get("补救适配", 0) >= 45 and tool_calls >= 3:
        cap = max(cap, 7)
    if assistant_map.get("验证闭环", 0) >= 45 and assistant_map.get("上下文承接", 0) >= 45 and tool_calls >= 4:
        cap = max(cap, 8)
    if session_count >= 3 and assistant_map.get("验证闭环", 0) >= 45 and assistant_map.get("执行落地", 0) >= 55:
        cap = max(cap, 9)
    if session_count >= 5 and assistant_map.get("验证闭环", 0) >= 55 and assistant_map.get("工具调度", 0) >= 55 and assistant_map.get("执行落地", 0) >= 60:
        cap = max(cap, 10)
    return cap


def _metric_tags(metrics: list[MetricScore], track: str = "assistant") -> list[str]:
    common_mapping = {
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
    xianxia_mapping = {
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
    mapping = xianxia_mapping if track == "user" else common_mapping
    return [mapping.get(item.name, item.name) for item in metrics]


def _xianxia_metric_name(name: str) -> str:
    mapping = {
        "目标清晰度": "心法",
        "上下文供给": "根基",
        "迭代修正力": "吐纳",
        "验收意识": "收功",
        "协作节奏": "同修",
    }
    return mapping.get(name, name)


def _user_metric_phrase(name: str, style: str = "tag") -> str:
    phrases = {
        "目标清晰度": {
            "tag": "道心坚定",
            "title": "道心坚定",
            "weak": "道心未定",
            "weak_title": "道心未定",
        },
        "上下文供给": {
            "tag": "根基稳固",
            "title": "根基稳固",
            "weak": "根基浮动",
            "weak_title": "根基浮动",
        },
        "迭代修正力": {
            "tag": "悟性渐开",
            "title": "悟性渐开",
            "weak": "悟性未开",
            "weak_title": "悟性未开",
        },
        "验收意识": {
            "tag": "收功谨慎",
            "title": "收功谨慎",
            "weak": "收功不稳",
            "weak_title": "收功不稳",
        },
        "协作节奏": {
            "tag": "气机相合",
            "title": "气机相合",
            "weak": "气机不顺",
            "weak_title": "气机不顺",
        },
        "执行落地": {
            "tag": "术法纯熟",
            "title": "术法纯熟",
            "weak": "术法生疏",
            "weak_title": "术法生疏",
        },
        "工具调度": {
            "tag": "驭器纯熟",
            "title": "驭器纯熟",
            "weak": "驭器未熟",
            "weak_title": "驭器未熟",
        },
        "验证闭环": {
            "tag": "收功圆满",
            "title": "收功圆满",
            "weak": "收功有缺",
            "weak_title": "收功有缺",
        },
        "上下文承接": {
            "tag": "气脉贯通",
            "title": "气脉贯通",
            "weak": "气脉不畅",
            "weak_title": "气脉不畅",
        },
        "补救适配": {
            "tag": "应变有方",
            "title": "应变有方",
            "weak": "应变不足",
            "weak_title": "应变不足",
        },
    }
    mapping = phrases.get(name)
    if not mapping:
        return name
    return mapping.get(style, mapping["tag"])


def _growth_plan(metrics: list[MetricScore], user_track: bool) -> list[str]:
    plans: list[str] = []
    for item in metrics:
        if item.name == "目标清晰度":
            plans.append("下次闭关前，先把诉求写成“目标 + 约束 + 输出物 + 验收”四段式。")
        elif item.name == "上下文供给":
            plans.append("把前因、条件与来路一并备齐，再开炉。")
        elif item.name == "迭代修正力":
            plans.append("每轮只动一个核心变量，守住其余条件，避免气机紊乱。")
        elif item.name == "验收意识":
            plans.append("每一轮收功时，都要附上看得见的凭据。")
        elif item.name == "协作节奏":
            plans.append("把大目标拆成三重关，每破一关便收一次结果。")
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
        plans.append("待下一轮问答结束，再来看境界变化。")
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
    return "验证动作不算多，可以更主动要求测试与确认结果。"


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
