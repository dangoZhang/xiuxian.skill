# portrait.skill

---

> "把你的运行卷宗投入炉中，照见你与 AI 的气脉、资质、境界与下一轮该如何破境。"

我会为你把一轮真实协作，炼成一张可复测的画像。

![License](https://img.shields.io/badge/License-MIT-f4c542)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Codex](https://img.shields.io/badge/Codex-Skill-111111)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-7C3AED)
![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8BC34A)

提供你的运行原材料（Codex、Claude Code、OpenCode、Cursor、VS Code 会话文件）加上真实协作记录  
生成一张真正能复测的修仙画像 / AI 协作能力证书  
看清你和 AI 是如何配合、卡在哪里、下一轮该怎么闭关

⚠️ 本项目用于个人协作复盘、成长追踪与方法训练，不用于伪造履历、冒充真人或输出隐私数据。

[安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [English](./README_EN.md)

---

## 安装

```bash
git clone https://github.com/dangoZhang/portrait.skill
cd portrait.skill
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 使用

先扫描本机默认卷宗目录：

```bash
python3 -m portrait_skill.cli scan
```

分析最新卷宗：

```bash
python3 -m portrait_skill.cli analyze --source codex --certificate both
python3 -m portrait_skill.cli analyze --source cc --certificate both
python3 -m portrait_skill.cli analyze --source cursor --certificate both
python3 -m portrait_skill.cli analyze --source vscode --certificate both
```

读取全部或指定时间范围的会话来炼化：

```bash
python3 -m portrait_skill.cli analyze --source codex --all --certificate both
python3 -m portrait_skill.cli analyze --source codex --since 2026-04-01 --until 2026-04-09 --certificate both
```

聚合定级默认会排除消息数过少的小样本会话，并按高位分位取级，不直接吃单次最高分。

指定某个文件：

```bash
python3 -m portrait_skill.cli analyze \
  --path ~/.codex/archived_sessions/rollout-xxx.jsonl \
  --certificate both
```

对比前后两轮闭关，看有没有破境：

```bash
python3 -m portrait_skill.cli compare \
  --before ./cycle-1.jsonl \
  --after ./cycle-2.jsonl \
  --certificate both
```

## 效果示例

你会得到两类结果：

- 修仙画像：炼气、筑基、金丹、元婴、化神等境界判断
- AI 协作能力证书：`L1-L8` 能力等级，以及执行、工具、承接、补救、闭环等能力判断

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
