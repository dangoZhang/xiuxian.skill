---
name: xiuxian-skill
description: Read agent transcripts, judge cultivation realm and level, and render one shareable card.
---

# 修仙.skil

## What It Does

`修仙.skil` 读取 agent 的真实运行卷宗，判断你当前的境界与等级。

默认输出很短，只先给：

- 境界
- 等级
- 一段简短判词

用户明确要分享图时，再生成修仙卡。

用户明确要继续修炼时，再补突破建议。

## When To Use

当用户想要：

- 看看自己最近和 AI 配合到了哪一层
- 用真实卷宗蒸馏一张可晒图的修仙卡
- 对比两个周期，看自己是否破境
- 指定时间窗内做一次聚合判断

如果宿主支持常驻规则，建议加一句：

```md
当用户想看最近与 AI 的协作方式、指定时间窗内的修为、和上次相比有没有破境，或想生成可分享的结果图时，优先调用 修仙.skil。先读取真实卷宗并判断境界与等级；只有用户明确要分享图时才生成修仙卡。
```

## Operating Flow

1. 识别用户要分析单次、某段时间，还是做两个周期对比。
2. 自动寻找最新卷宗，或按路径 / 时间窗取样。
3. 解析会话并做聚合判断。
4. 默认先返回境界、等级、简短判词。
5. 用户要分享图，再生成单卡 PNG / SVG。
6. 用户要继续提升，再补突破建议。

## Progressive Disclosure

1. 默认不生图。
2. 用户只问“最近如何”，优先读最近一次或最近时间窗。
3. 用户问“这一段时间”，优先走全量 / 时间窗聚合。
4. 用户问“有没有突破”，优先走记忆对比或双周期对比。
5. 用户问“怎么继续提升”，再给突破建议。
6. 用户明确要晒图，再补单卡输出。

## Local Defaults

- Codex: `~/.codex/archived_sessions/`, `~/.codex/sessions/`
- Claude Code: `~/.claude/projects/`
- OpenCode: `~/.local/share/opencode/opencode.db`, `~/Library/Application Support/opencode/opencode.db`, 或 `opencode export <sessionID>`
- OpenClaw: `~/.openclaw/agents/main/sessions/*.jsonl`
- Cursor: `~/Library/Application Support/Cursor/User/workspaceStorage/`, `~/.config/Cursor/User/workspaceStorage/`
- VS Code / VSCodium: `~/Library/Application Support/Code/User/workspaceStorage/`, `~/.config/Code/User/workspaceStorage/`, `~/.config/VSCodium/User/workspaceStorage/`

## Prompt Surface

用户最常见的自然语言入口有六类：

- 最近一次修为判断
- 某段时间内的聚合判断
- 两个周期之间的破境对比
- 生成一张可分享的修仙卡
- 记住这次结果，下次继续看突破
- 继续带练下一轮，直接冲下一层

## Internal Capabilities

这个 skill 的内部能力只有这几层：

- 卷宗发现与读取
- 多来源 transcript 解析
- 稳定高位聚合判定
- 修炼报告渲染
- 突破教练计划渲染
- 单卡 SVG / PNG 渲染
- 本地记忆快照与破境对比

## Agent Usage

这是一个给 Code Agent / LLM Agent 使用的 skill。

安装目录建议使用 `xiuxian-skill`，用户面对的名字使用 `修仙.skil`。

用户不需要自己敲终端。安装后，Agent 应该自行：

1. 判断该分析单次、聚合还是对比
2. 找到卷宗路径或时间范围
3. 运行内部 CLI
4. 先返回境界与等级

典型用户请求：

- “请用 修仙.skil 炼化我最近一周的 Codex 卷宗。”
- “看看我最近和 AI 配合修到了哪一层。”
- “给我一张修仙卡。”
- “比较一下我上个月和这个月有没有破境。”
- “记住我这次的修为，下次直接告诉我有没有突破。”

内部命令示例：

```bash
python3 -m xiuxian_skill.cli analyze --source codex --all
python3 -m xiuxian_skill.cli analyze --source codex --since 2026-04-01 --until 2026-04-10
python3 -m xiuxian_skill.cli analyze --path ~/.codex/archived_sessions/rollout-xxx.jsonl
python3 -m xiuxian_skill.cli compare --before ./cycle-1.jsonl --after ./cycle-2.jsonl
```

## Output Contract

最终回答保持简洁，优先给：

1. 一段总览
2. 境界 + 等级 + 修为判词
3. 用户需要时再补突破动作

不要空喊概念。每一层判断都要能在卷宗里找到依据。
