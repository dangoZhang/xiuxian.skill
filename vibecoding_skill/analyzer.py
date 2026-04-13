from __future__ import annotations

from pathlib import Path
import re
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

REALM_TO_STAGE = {
    "凡人": "试手期",
    "感气": "入门期",
    "炼气": "成形期",
    "筑基": "稳定期",
    "金丹": "复用期",
    "元婴": "委托期",
    "化神": "并行期",
    "炼虚": "系统期",
    "合体": "落地期",
    "大乘": "传承期",
    "渡劫": "传承期",
    "飞升": "传承期",
}

LEVEL_TABLES = {
    "user": REALM_LEVELS,
    "assistant": AI_LEVELS,
}

METHOD_SEDIMENT_TOKENS = ["skill", "workflow", "模板", "模块", "sop", "章法", "复用", "标准化"]
GOAL_TOKENS = ["目标", "想要", "希望", "需要", "实现", "修复", "新增", "生成", "重写", "改成"]
CONSTRAINT_TOKENS = ["约束", "限制", "必须", "不要", "保留", "兼容", "只能", "优先", "默认", "格式", "风格"]
ACCEPTANCE_TOKENS = ["验收", "验证", "测试", "跑通", "确认", "证明", "结果", "输出物", "可用", "正常工作", "review", "检查"]
ITERATION_TOKENS = ["继续", "再", "改", "补", "调整", "优化", "重写", "进一步", "迭代", "打磨", "删掉", "增强"]
REPO_TOKENS = ["readme", "agents.md", "skill.md", "pyproject.toml", "package.json", "仓库", "目录", "repo", "git", "commit", "pr", "issue"]
CONTEXT_TOKENS = ["环境", "日志", "模型", "provider", "token", "session", "会话", "运行", "路径", "截图", "数据", "文件", "样例", "示例", "db", "jsonl"]
HANDOFF_TOKENS = ["继续上次", "继续维护", "上次", "沿用", "记住", "记忆", "历史", "上一轮", "下一轮", "跨周期", "snapshot", "history", "handoff", "交接"]
DELEGATION_TOKENS = ["agent", "delegate", "并行", "同时", "分身", "多个工具", "多个 agent", "多 agent", "交给 ai", "交给 agent", "异步", "后台"]
WORKFLOW_TOKENS = METHOD_SEDIMENT_TOKENS + ["自动化", "导出", "bundle", "安装", "发布", "示例", "分享"]
EXECUTION_TOKENS = ["我先", "我会先", "先检查", "先读", "先跑", "接下来", "正在", "已完成", "已更新", "已修复", "开始做", "先做", "验证后", "回报"]
VERIFICATION_TOKENS = ["验证", "测试", "跑通", "编译", "compile", "build", "smoke", "检查", "确认", "git status", "通过", "失败", "风险", "没验", "证据"]
TOOL_TOKENS = ["tool", "工具", "读文件", "跑命令", "web", "search", "grep", "rg", "sed", "git", "python", "node", "mcp", "connector", "browser"]
ADAPTATION_TOKENS = ["改成", "回退", "兼容", "降级", "缩小范围", "最小", "兜底", "fallback", "备选", "补救", "绕过", "换方案", "切换", "重排"]
FRICTION_TOKENS = ["报错", "失败", "不对", "太难", "卡住", "问题", "异常", "冲突", "超出", "重叠", "看不清"]
TEACHING_TOKENS = ["分享", "导出", "给别人", "团队", "客户", "安装", "示例", "教程", "文档", "readme", "skill"]
CONTEXT_CARRY_TOKENS = ["刚才", "上一轮", "上一步", "这轮", "沿用", "继续", "基于刚才", "根据刚才", "延续"]
PLAN_TOKENS = ["步骤", "拆成", "分成", "分步", "阶段", "计划", "todo", "milestone", "roadmap", "下一步"]

PATH_LIKE_PATTERN = re.compile(
    r"(?:~?/[\w./-]+|[A-Za-z]:\\[\w.\\/-]+|[\w.-]+\.(?:py|ts|tsx|js|jsx|md|json|jsonl|yml|yaml|toml|sql|sh|svg|png))"
)
COMMAND_PATTERN = re.compile(
    r"\b(?:python3?|pytest|uv|npm|pnpm|yarn|npx|git|rg|sed|cat|ls|make|cargo|go test|bun|node)\b"
)
STRUCTURED_PATTERN = re.compile(r"(?:\n|^\s*[-*]\s+|^\s*\d+\.\s+|：\s*$)", re.MULTILINE)
ASCII_TERM_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9._/-]{2,}")


def analyze_transcript(transcript: Transcript) -> Analysis:
    user_messages = [item for item in transcript.messages if item.role == "user"]
    assistant_messages = [item for item in transcript.messages if item.role == "assistant"]
    signals = _extract_transcript_signals(transcript, user_messages, assistant_messages)

    user_metrics = [
        MetricScore("目标清晰度", _score_clarity(user_messages, signals), _explain_clarity(user_messages, signals)),
        MetricScore("上下文供给", _score_context(user_messages, signals), _explain_context(user_messages, signals)),
        MetricScore("迭代修正力", _score_iteration(user_messages, signals), _explain_iteration(user_messages, signals)),
        MetricScore("验收意识", _score_verification(transcript, assistant_messages, signals), _explain_verification(transcript, signals)),
        MetricScore("协作节奏", _score_collaboration(user_messages, assistant_messages, signals), _explain_collaboration(user_messages, assistant_messages, signals)),
    ]

    assistant_metrics = [
        MetricScore("执行落地", _score_execution(assistant_messages, signals), _explain_execution(assistant_messages, signals)),
        MetricScore("工具调度", _score_tooling(transcript, signals), _explain_tooling(transcript, signals)),
        MetricScore("验证闭环", _score_verification(transcript, assistant_messages, signals), _explain_verification(transcript, signals)),
        MetricScore("上下文承接", _score_context_retention(user_messages, assistant_messages, signals), _explain_context_retention(user_messages, assistant_messages, signals)),
        MetricScore("补救适配", _score_recovery(user_messages, assistant_messages, signals), _explain_recovery(user_messages, assistant_messages, signals)),
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
            signals=signals,
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
            signals=signals,
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


def display_level(track: str, level: str) -> str:
    if track == "user":
        return REALM_TO_STAGE.get(level, level)
    return level


def compare_analyses(before: Analysis, after: Analysis) -> dict[str, object]:
    return {
        "overview": (
            f"对比两次会话：前次 {len(before.transcript.messages)} 条消息，"
            f"本次 {len(after.transcript.messages)} 条消息。"
        ),
        "user": _compare_track(before, after, track="user"),
        "assistant": _compare_track(before, after, track="assistant"),
    }


def aggregate_analyses(
    analyses: list[Analysis],
    min_messages: int = 8,
    *,
    total_tool_calls_override: int | None = None,
    token_usage_override=None,
) -> dict[str, object]:
    if not analyses:
        raise ValueError("No analyses to aggregate.")

    eligible = [item for item in analyses if len(item.transcript.messages) >= min_messages]
    pool = eligible or analyses
    dropped = len(analyses) - len(pool)
    total_messages = sum(len(item.transcript.messages) for item in pool)
    total_tool_calls = total_tool_calls_override if total_tool_calls_override is not None else sum(item.transcript.tool_calls for item in pool)
    if token_usage_override is None:
        total_tokens = sum(item.transcript.token_usage.total_tokens for item in pool)
        total_input_tokens = sum(item.transcript.token_usage.input_tokens for item in pool)
        total_cached_input_tokens = sum(item.transcript.token_usage.cached_input_tokens for item in pool)
        total_output_tokens = sum(item.transcript.token_usage.output_tokens for item in pool)
        total_reasoning_output_tokens = sum(item.transcript.token_usage.reasoning_output_tokens for item in pool)
    else:
        total_tokens = int(getattr(token_usage_override, "total_tokens", 0) or 0)
        total_input_tokens = int(getattr(token_usage_override, "input_tokens", 0) or 0)
        total_cached_input_tokens = int(getattr(token_usage_override, "cached_input_tokens", 0) or 0)
        total_output_tokens = int(getattr(token_usage_override, "output_tokens", 0) or 0)
        total_reasoning_output_tokens = int(getattr(token_usage_override, "reasoning_output_tokens", 0) or 0)

    user_metrics = _aggregate_metric_scores([item.user_metrics for item in pool])
    assistant_metrics = _aggregate_metric_scores([item.assistant_metrics for item in pool])

    raw_user_score = _stable_high_score([item.user_certificate.score for item in pool])
    raw_assistant_score = _stable_high_score([item.assistant_certificate.score for item in pool])

    models = _merge_unique(item for analysis in pool for item in analysis.transcript.models)
    providers = _merge_unique(item for analysis in pool for item in analysis.transcript.providers)
    method_sediment = any(_has_method_sediment(item.transcript.messages) for item in pool)
    aggregate_signals = _aggregate_signals(pool)
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
            signals=aggregate_signals,
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
            signals=aggregate_signals,
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

    if track == "user":
        if after_rank > before_rank:
            outcome = "阶段升级"
        elif after_rank == before_rank and score_delta > 0:
            outcome = "阶段不变，但稳定度上升"
        elif score_delta == 0:
            outcome = "阶段持平"
        else:
            outcome = "本轮还未升级"
    else:
        if after_rank > before_rank:
            outcome = "等级提升"
        elif after_rank == before_rank and score_delta > 0:
            outcome = "等级未变，但稳定度上升"
        elif score_delta == 0:
            outcome = "等级持平"
        else:
            outcome = "本轮还未升级"

    return {
        "title": before_certificate.title,
        "outcome": outcome,
        "before_level": before_certificate.level,
        "after_level": after_certificate.level,
        "display_before_level": display_level(track, before_certificate.level),
        "display_after_level": display_level(track, after_certificate.level),
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


def _extract_transcript_signals(transcript: Transcript, user_messages, assistant_messages) -> dict[str, int]:
    return {
        "user_structured": _count_structured_messages(user_messages),
        "assistant_structured": _count_structured_messages(assistant_messages),
        "user_goal_hits": _count_messages_with_tokens(user_messages, GOAL_TOKENS),
        "user_constraint_hits": _count_messages_with_tokens(user_messages, CONSTRAINT_TOKENS),
        "user_acceptance_hits": _count_messages_with_tokens(user_messages, ACCEPTANCE_TOKENS),
        "user_iteration_hits": _count_messages_with_tokens(user_messages, ITERATION_TOKENS),
        "user_repo_hits": _count_messages_with_tokens(user_messages, REPO_TOKENS),
        "user_context_hits": _count_messages_with_tokens(user_messages, CONTEXT_TOKENS),
        "user_handoff_hits": _count_messages_with_tokens(user_messages, HANDOFF_TOKENS),
        "user_plan_hits": _count_plan_hits(user_messages),
        "user_path_hits": _count_path_like_messages(user_messages),
        "assistant_plan_hits": _count_plan_hits(assistant_messages),
        "assistant_execution_hits": _count_messages_with_tokens(assistant_messages, EXECUTION_TOKENS),
        "assistant_verification_hits": _count_messages_with_tokens(assistant_messages, VERIFICATION_TOKENS),
        "assistant_tool_hits": _count_messages_with_tokens(assistant_messages, TOOL_TOKENS),
        "assistant_adaptation_hits": _count_messages_with_tokens(assistant_messages, ADAPTATION_TOKENS),
        "assistant_delegation_hits": _count_messages_with_tokens(assistant_messages, DELEGATION_TOKENS),
        "assistant_context_carry_hits": _count_messages_with_tokens(assistant_messages, CONTEXT_CARRY_TOKENS),
        "repo_grounding_hits": _count_messages_with_tokens(transcript.messages, REPO_TOKENS) + _count_path_like_messages(transcript.messages),
        "workflow_hits": _count_messages_with_tokens(transcript.messages, WORKFLOW_TOKENS),
        "long_horizon_hits": _count_messages_with_tokens(transcript.messages, HANDOFF_TOKENS),
        "friction_hits": _count_messages_with_tokens(user_messages, FRICTION_TOKENS),
        "commands_hits": _count_command_like_messages(assistant_messages),
        "keyword_overlap": _shared_context_overlap(user_messages, assistant_messages),
        "teaching_hits": _count_messages_with_tokens(transcript.messages, TEACHING_TOKENS),
    }


def _aggregate_signals(analyses: list[Analysis]) -> dict[str, int]:
    merged: dict[str, int] = {}
    for analysis in analyses:
        transcript = analysis.transcript
        user_messages = [item for item in transcript.messages if item.role == "user"]
        assistant_messages = [item for item in transcript.messages if item.role == "assistant"]
        signals = _extract_transcript_signals(transcript, user_messages, assistant_messages)
        for key, value in signals.items():
            merged[key] = merged.get(key, 0) + value
    return merged


def _merge_unique(items) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return seen


def _count_messages_with_tokens(messages, tokens: list[str]) -> int:
    count = 0
    lowered_tokens = [token.lower() for token in tokens]
    for item in messages:
        text = _signal_text(item).lower()
        if any(token in text for token in lowered_tokens):
            count += 1
    return count


def _count_structured_messages(messages) -> int:
    return sum(1 for item in messages if STRUCTURED_PATTERN.search(_signal_text(item)))


def _count_path_like_messages(messages) -> int:
    return sum(1 for item in messages if PATH_LIKE_PATTERN.search(_signal_text(item)))


def _count_command_like_messages(messages) -> int:
    return sum(1 for item in messages if COMMAND_PATTERN.search(_signal_text(item)))


def _count_plan_hits(messages) -> int:
    hits = 0
    for item in messages:
        signal_text = _signal_text(item)
        text = signal_text.lower()
        if any(token in text for token in PLAN_TOKENS):
            hits += 1
            continue
        if re.search(r"先.{0,30}再", signal_text):
            hits += 1
            continue
        if STRUCTURED_PATTERN.search(signal_text) and any(token in text for token in ["目标", "约束", "输出", "验收"]):
            hits += 1
    return hits


def _shared_context_overlap(user_messages, assistant_messages) -> int:
    user_keywords = _collect_keywords(user_messages)
    assistant_keywords = _collect_keywords(assistant_messages)
    return len(user_keywords & assistant_keywords)


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
        persona_title = f"{level} 协作阶段"
        title = "阶段判定"
        subtitle = REALM_DESCRIPTIONS[level]
        summary = f"这是你在多场真实协作里的稳定阶段。当前已到 {level}，补齐短板后再看下一次升级。"
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


def _score_clarity(messages, signals: dict[str, int] | None = None) -> int:
    if not messages:
        return 0
    signals = signals or {}
    lengths = [len(item.text) for item in messages]
    avg_len = mean(lengths)
    score = 20
    score += min(int(avg_len / 7), 18)
    score += min(signals.get("user_goal_hits", 0) * 8, 22)
    score += min(signals.get("user_constraint_hits", 0) * 6, 16)
    score += min(signals.get("user_acceptance_hits", 0) * 7, 16)
    score += min(signals.get("user_plan_hits", 0) * 6, 12)
    score += min(signals.get("user_structured", 0) * 5, 12)
    return min(score, 100)


def _score_context(messages, signals: dict[str, int] | None = None) -> int:
    if not messages:
        return 0
    signals = signals or {}
    score = 18
    score += min(signals.get("user_repo_hits", 0) * 10, 24)
    score += min(signals.get("user_path_hits", 0) * 8, 20)
    score += min(signals.get("user_context_hits", 0) * 7, 18)
    score += min(signals.get("user_constraint_hits", 0) * 5, 12)
    score += min(signals.get("user_handoff_hits", 0) * 5, 10)
    return min(score, 100)


def _score_iteration(messages, signals: dict[str, int] | None = None) -> int:
    if not messages:
        return 0
    signals = signals or {}
    score = 16 + min(len(messages) * 7, 28)
    score += min(signals.get("user_iteration_hits", 0) * 8, 26)
    score += min(signals.get("user_plan_hits", 0) * 5, 12)
    score += min(signals.get("user_handoff_hits", 0) * 6, 12)
    return min(score, 100)


def _score_verification(transcript: Transcript, assistant_messages, signals: dict[str, int] | None = None) -> int:
    signals = signals or {}
    score = 14
    score += min(transcript.tool_calls * 6, 28)
    score += min(signals.get("assistant_verification_hits", 0) * 9, 28)
    score += min(signals.get("user_acceptance_hits", 0) * 8, 20)
    score += min(signals.get("commands_hits", 0) * 5, 10)
    return min(score, 100)


def _score_collaboration(user_messages, assistant_messages, signals: dict[str, int] | None = None) -> int:
    if not user_messages or not assistant_messages:
        return 25
    signals = signals or {}
    ratio = min(len(user_messages), len(assistant_messages)) / max(len(user_messages), len(assistant_messages))
    score = 30 + int(ratio * 24)
    score += min(min(len(user_messages), len(assistant_messages)) * 4, 16)
    score += min(signals.get("user_handoff_hits", 0) * 4, 8)
    score += min(signals.get("assistant_context_carry_hits", 0) * 5, 10)
    score += min(signals.get("assistant_delegation_hits", 0) * 6, 12)
    return min(score, 100)


def _score_execution(messages, signals: dict[str, int] | None = None) -> int:
    if not messages:
        return 0
    signals = signals or {}
    score = 20 + min(len(messages) * 5, 24)
    score += min(signals.get("assistant_execution_hits", 0) * 9, 28)
    score += min(signals.get("assistant_plan_hits", 0) * 5, 10)
    score += min(signals.get("commands_hits", 0) * 5, 12)
    return min(score, 100)


def _score_tooling(transcript: Transcript, signals: dict[str, int] | None = None) -> int:
    signals = signals or {}
    score = 16 + min(transcript.tool_calls * 10, 46)
    score += min(signals.get("assistant_tool_hits", 0) * 7, 20)
    score += min(signals.get("commands_hits", 0) * 4, 10)
    return min(score, 100)


def _score_context_retention(user_messages, assistant_messages, signals: dict[str, int] | None = None) -> int:
    if not user_messages or not assistant_messages:
        return 20
    signals = signals or {}
    score = 22
    score += min(signals.get("keyword_overlap", 0) * 6, 24)
    score += min(signals.get("assistant_context_carry_hits", 0) * 8, 24)
    score += min(signals.get("repo_grounding_hits", 0) * 3, 12)
    return min(score, 100)


def _score_recovery(user_messages, assistant_messages, signals: dict[str, int] | None = None) -> int:
    signals = signals or {}
    score = 26
    score += min(signals.get("friction_hits", 0) * 10, 24)
    score += min(signals.get("assistant_adaptation_hits", 0) * 10, 26)
    if signals.get("friction_hits", 0) and signals.get("assistant_adaptation_hits", 0):
        score += 14
    return min(score, 100)


def _collect_keywords(messages) -> set[str]:
    keywords: set[str] = set()
    for item in messages:
        signal_text = _signal_text(item)
        lowered = signal_text.lower()
        for token in ["readme", "skill", "repo", "git", "public", "证书", "日志", "解析", "用户", "ai", "协作", "等级", "agent", "workflow", "tool", "model", "token"]:
            if token in lowered:
                keywords.add(token)
        for match in ASCII_TERM_PATTERN.findall(signal_text):
            token = match.lower().strip("./")
            if len(token) >= 4 and ("/" in token or "." in token or token in {"codex", "claude", "cursor", "vscode", "opencode", "openclaw"}):
                keywords.add(token)
    return keywords


def _signal_text(message) -> str:
    meta = getattr(message, "meta", None)
    if isinstance(meta, dict):
        value = meta.get("signal_text")
        if isinstance(value, str) and value:
            return value
    return str(getattr(message, "text", "") or "")


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
        title="阶段判定",
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
    signals: dict[str, int] | None = None,
) -> int:
    signals = signals or {}
    user_map = _metric_map(user_metrics)
    assistant_map = _metric_map(assistant_metrics)
    cap = 2
    if total_messages >= 4 and user_map.get("协作节奏", 0) >= 55 and user_map.get("上下文供给", 0) >= 40:
        cap = 3
    if method_sediment or (
        signals.get("user_plan_hits", 0) >= 1 and signals.get("user_constraint_hits", 0) >= 1 and signals.get("user_acceptance_hits", 0) >= 1
    ):
        cap = max(cap, 4)
    if assistant_map.get("执行落地", 0) >= 50 and tool_calls >= 1 and user_map.get("验收意识", 0) >= 40:
        cap = max(cap, 5)
    if assistant_map.get("执行落地", 0) >= 55 and assistant_map.get("工具调度", 0) >= 45 and tool_calls >= 2 and signals.get("repo_grounding_hits", 0) >= 2:
        cap = max(cap, 6)
    if (
        assistant_map.get("工具调度", 0) >= 55
        and assistant_map.get("上下文承接", 0) >= 50
        and tool_calls >= 3
        and (signals.get("assistant_delegation_hits", 0) >= 1 or signals.get("assistant_context_carry_hits", 0) >= 2)
    ):
        cap = max(cap, 7)
    if (
        assistant_map.get("验证闭环", 0) >= 55
        and assistant_map.get("补救适配", 0) >= 50
        and tool_calls >= 4
        and signals.get("friction_hits", 0) >= 1
    ):
        cap = max(cap, 8)
    if (
        session_count >= 3
        and method_sediment
        and assistant_map.get("验证闭环", 0) >= 55
        and signals.get("workflow_hits", 0) >= 2
        and signals.get("long_horizon_hits", 0) >= 1
    ):
        cap = max(cap, 9)
    if (
        session_count >= 5
        and assistant_map.get("验证闭环", 0) >= 60
        and assistant_map.get("补救适配", 0) >= 55
        and user_map.get("验收意识", 0) >= 55
        and signals.get("teaching_hits", 0) >= 2
    ):
        cap = max(cap, 10)
    if (
        session_count >= 8
        and assistant_map.get("执行落地", 0) >= 65
        and assistant_map.get("验证闭环", 0) >= 65
        and assistant_map.get("工具调度", 0) >= 65
        and method_sediment
    ):
        cap = max(cap, 11)
    return cap


def _assistant_cap_rank(
    assistant_metrics: list[MetricScore],
    *,
    total_messages: int,
    tool_calls: int,
    session_count: int,
    method_sediment: bool,
    signals: dict[str, int] | None = None,
) -> int:
    signals = signals or {}
    assistant_map = _metric_map(assistant_metrics)
    cap = 2
    if total_messages >= 2 and assistant_map.get("执行落地", 0) >= 45:
        cap = 3
    if method_sediment or (signals.get("assistant_plan_hits", 0) >= 1 and signals.get("assistant_execution_hits", 0) >= 1):
        cap = max(cap, 4)
    if assistant_map.get("执行落地", 0) >= 52 and tool_calls >= 1 and signals.get("repo_grounding_hits", 0) >= 1:
        cap = max(cap, 5)
    if assistant_map.get("工具调度", 0) >= 45 and assistant_map.get("上下文承接", 0) >= 45 and tool_calls >= 2:
        cap = max(cap, 6)
    if (
        assistant_map.get("工具调度", 0) >= 55
        and assistant_map.get("补救适配", 0) >= 50
        and tool_calls >= 3
        and (signals.get("assistant_delegation_hits", 0) >= 1 or signals.get("assistant_tool_hits", 0) >= 2)
    ):
        cap = max(cap, 7)
    if (
        assistant_map.get("验证闭环", 0) >= 55
        and assistant_map.get("上下文承接", 0) >= 50
        and tool_calls >= 4
        and signals.get("commands_hits", 0) >= 1
    ):
        cap = max(cap, 8)
    if (
        session_count >= 3
        and assistant_map.get("验证闭环", 0) >= 55
        and assistant_map.get("执行落地", 0) >= 60
        and signals.get("long_horizon_hits", 0) >= 1
    ):
        cap = max(cap, 9)
    if (
        session_count >= 5
        and assistant_map.get("验证闭环", 0) >= 60
        and assistant_map.get("工具调度", 0) >= 60
        and assistant_map.get("执行落地", 0) >= 65
        and (signals.get("workflow_hits", 0) >= 2 or method_sediment)
    ):
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


def _explain_clarity(messages, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if not messages:
        return "没有用户消息，无法判断。"
    if signals.get("user_goal_hits", 0) and signals.get("user_constraint_hits", 0) and signals.get("user_acceptance_hits", 0):
        return "起手就把目标、约束和验收交代出来了，主线收得住。"
    if signals.get("user_structured", 0) or any(len(item.text) > 120 for item in messages):
        return "任务描述已有层次，目标表达基本清楚。"
    return "能说清大方向，但目标和验收还可以更早收束。"


def _explain_context(messages, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if signals.get("user_repo_hits", 0) + signals.get("user_path_hits", 0) >= 2 and signals.get("user_context_hits", 0) >= 1:
        return "路径、文件、环境和样例给得较全，AI 更容易直接进仓库干活。"
    if signals.get("user_repo_hits", 0) or signals.get("user_path_hits", 0):
        return "已经开始给仓库与文件线索了，但环境边界还能再补足。"
    return "上下文仍偏口语化，建议补路径、文件名和约束。"


def _explain_iteration(messages, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if signals.get("user_iteration_hits", 0) >= 2 and (signals.get("user_plan_hits", 0) >= 1 or signals.get("user_handoff_hits", 0) >= 1):
        return "会持续打磨，并且能沿着上一轮结果继续推进。"
    if len(messages) >= 3:
        return "存在多轮补充或修正，已经有持续调向意识。"
    return "当前更像单轮指令，后续可增加定向修正。"


def _explain_verification(transcript: Transcript, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if transcript.tool_calls >= 3 and signals.get("assistant_verification_hits", 0) >= 1:
        return "会话里有实际验证动作，也有对结果与风险的回报。"
    if signals.get("user_acceptance_hits", 0) >= 1:
        return "已经在主动追问验收，但验证证据还可以再实一点。"
    return "验证动作不算多，可以更主动要求测试与确认结果。"


def _explain_collaboration(user_messages, assistant_messages, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if len(user_messages) >= 2 and len(assistant_messages) >= 2 and signals.get("assistant_context_carry_hits", 0) >= 1:
        return "双方能接住上一轮上下文，推进节奏已经连起来了。"
    if len(user_messages) >= 2 and len(assistant_messages) >= 2:
        return "双方回合同步，已经形成共同推进节奏。"
    return "互动回合偏少，适合拆小步增加反馈频率。"


def _explain_execution(messages, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if signals.get("assistant_execution_hits", 0) >= 2 and signals.get("commands_hits", 0) >= 1:
        return "AI 会先落地动作，再回报过程和结果。"
    if any("完成" in item.text or "开始" in item.text for item in messages):
        return "AI 明显偏执行流，而非只做抽象建议。"
    return "AI 仍有总结倾向，可以要求先做再说。"


def _explain_tooling(transcript: Transcript, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if transcript.tool_calls >= 4 and signals.get("assistant_tool_hits", 0) >= 1:
        return "AI 已经把读文件、跑命令和验证工具接进主工作流。"
    if transcript.tool_calls >= 1:
        return "AI 有工具意识，但还未完全进入高强度执行节奏。"
    return "当前几乎没有工具痕迹。"


def _explain_context_retention(user_messages, assistant_messages, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if signals.get("keyword_overlap", 0) >= 2 and signals.get("assistant_context_carry_hits", 0) >= 1:
        return "AI 不只复述主题词，还能沿着前一轮上下文继续推进。"
    if _collect_keywords(user_messages) & _collect_keywords(assistant_messages):
        return "AI 基本承接了用户的关键主题词。"
    return "AI 对用户语境的复用度还不够。"


def _explain_recovery(user_messages, assistant_messages, signals: dict[str, int] | None = None) -> str:
    signals = signals or {}
    if signals.get("friction_hits", 0) >= 1 and signals.get("assistant_adaptation_hits", 0) >= 1:
        return "遇到阻力后有换打法、缩范围或兼容处理，补救动作是实的。"
    has_issue = any(any(token in item.text for token in ["问题", "太难", "失败", "报错"]) for item in user_messages)
    if has_issue:
        return "会话里出现阻力后，AI 有调整路线的空间。"
    return "本次样本阻力较少，补救能力观测有限。"
