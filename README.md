# portrait.skill

---

> "把你的运行卷宗投入炉中，照见你与 AI 的气脉、资质、境界与下一轮该如何破境。"

当 AI 像小说里的灵气复苏一样席卷人间，有人只看见热闹，有人已经开始修行。

![License](https://img.shields.io/badge/License-MIT-f4c542)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Codex](https://img.shields.io/badge/Codex-Skill-111111)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-7C3AED)
![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8BC34A)

提供你的运行原材料（Codex、Claude Code、OpenCode、Cursor、VS Code 会话文件）加上真实协作记录  
在这场 AI 灵气复苏里，炼出一张真正能复测的修仙画像 / AI 协作能力证书  
看清你和 AI 是如何配合、卡在哪一关、下一轮该如何闭关破境

⚠️ 本项目用于个人协作复盘、成长追踪与方法训练，不用于伪造履历、冒充真人或输出隐私数据。

[安装到-Agent](#安装到-agent) · [如何调用](#如何调用) · [效果示例](#效果示例) · [英文版](./README_EN.md)

---

## 安装到 Agent

这是一个给 Code Agent / LLM Agent 使用的 `skill`，不是面向最终用户手动敲命令的普通 Python 工具。

正确的使用方式是：

1. 把这个仓库安装到你的 Code Agent 工具里
2. 让 AI 读取本仓库中的 `SKILL.md`
3. 由 AI 自己调用内部实现去扫描、炼化、对比运行卷宗

主入口是：

- [SKILL.md](/Users/zty/my-project/xiuxianLLM/side-projects/portrait.skill/SKILL.md)

底层实现是：

- [portrait_skill/cli.py](/Users/zty/my-project/xiuxianLLM/side-projects/portrait.skill/portrait_skill/cli.py)

如果你的 Agent 工具支持“本地 skills / 自定义 skills / repo skills”，把整个 `portrait.skill` 目录加入对应技能目录即可。

## 如何调用

安装完成后，用户应该直接对 AI 说：

- “请用 `portrait.skill` 炼化我最近一周的 Codex 卷宗。”
- “请用 `portrait.skill` 给我生成修仙画像。”
- “我不想看修仙背景，请直接给我 AI 协作能力证书。”
- “请比较我 3 月和 4 月这两轮会话，看我有没有破境。”
- “请读取我全部 Codex 会话，排除低样本偏置后给我稳定高位等级。”

如果用户要指定时间范围，可以直接这样说：

- “请炼化我 2026-04-01 到 2026-04-09 的 Codex 会话。”
- “请只看最近两天，生成 AI 协作能力证书。”
- “请汇总我这个项目周期内的全部会话，给我稳定高位等级。”

如果用户要指定来源，可以直接这样说：

- “请读取我的 Codex 卷宗。”
- “请读取我的 Claude Code 会话文件。”
- “请读取我的 Cursor / VS Code chatSessions 卷宗。”

底层 CLI 仍然存在，但那是给 Agent 内部调用的实现细节，不是主交互方式。

Agent 内部通常会调用类似这些命令：

```bash
python3 -m portrait_skill.cli analyze --source codex --all --certificate both
python3 -m portrait_skill.cli analyze --source codex --since 2026-04-01 --until 2026-04-09 --certificate both
python3 -m portrait_skill.cli compare --before ./cycle-1.jsonl --after ./cycle-2.jsonl --certificate both
```

## 效果示例

你会得到两类结果：

- 修仙画像：炼气、筑基、金丹、元婴、化神等境界判断
- AI 协作能力证书：`L1-L8` 能力等级，以及执行、工具、承接、补救、闭环等能力判断

如果你喜欢修仙叙事，我们将为你在修仙世界里创作一张画像，让你看到自己如今的境界、气脉与破境方向。

如果你不喜欢修仙背景也没关系，我们将直接为你颁发一张 AI 协作能力证书，用更直接的方式告诉你，你和 AI 现在处在什么协作层级，强项和短板分别是什么。

如果运行文件里带模型信息，还会额外标出：

- 灵根
- 资质
- 炉主模型

仓库内自带一个最小样本：

```bash
python3 -m portrait_skill.cli analyze \
  --path examples/demo_codex_session.jsonl \
  --certificate both \
  --output examples/demo_report.md
```

## 支持的卷宗

- Codex：`~/.codex/archived_sessions/*.jsonl`、`~/.codex/sessions/**/rollout-*.jsonl`
- Claude Code：导出的 JSON / JSONL 会话文件
- OpenCode：JSON / JSONL 会话文件
- Cursor：常见 `workspaceStorage/*/chatSessions/*.json`
- VS Code / Copilot Chat：常见 `workspaceStorage/*/chatSessions/*.json`

其中 `Codex` 当前最稳。其余来源支持默认目录发现和手动 `--path` 投喂，实际效果取决于会话文件 schema。

## 你会得到什么

- 当前等级
- 核心标签
- 判定依据
- 下一轮闭关任务
- 前后周期对比时的破境判断

## 隐私

本项目不依赖服务端，默认本地运行。

输出报告会自动把家目录脱敏成 `~`，其他绝对路径只显示文件名。公开演示时，仍建议只使用脱敏日志或合成样本。
