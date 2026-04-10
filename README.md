<div align="center">

# 修仙.skil

> *"先看清你的 vibecoding 到了哪一层，再决定要不要修仙。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Codex](https://img.shields.io/badge/Codex-Skill-111111)](https://developers.openai.com/codex/skills)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![Download ZIP](https://img.shields.io/badge/Download-ZIP-2EA44F)](https://github.com/dangoZhang/xiuxian.skill/archive/refs/heads/main.zip)

<br>

它评的不是你会不会聊天。<br>
它评的是你能不能把 AI 真正带进工作流，做出结果，留下验证，再继续突破。<br>

<br>

默认先用人话告诉你：你现在处在哪一层、强在哪、短在哪、下一步该怎么练。<br>
如果你想晒图，它再把这些能力炼成一张修仙风格的分享卡。<br>

[安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [境界与等级](#境界与等级) · [English](README_EN.md)

</div>

---

## 项目介绍

`修仙.skil` 的核心不是“修仙”，而是 `vibecoding`。

`vibecoding` 很容易做得很轻，很快，也很飘。真正拉开差距的，是你会不会把目标讲清楚、把上下文喂够、让 Agent 真读文件真跑命令、最后逼它拿出验证结果。  
这个 skill 做的，就是从真实轨迹里把这些习惯蒸馏出来。

它默认输出三层东西：

- `境界`：你现在大概处在哪个阶段
- `等级`：你的协作稳定度大概到什么强度
- `突破建议`：下一轮最该补的一个动作

修仙叙事只在两种时候出现：

- 你主动问“我的境界如何”
- 你想要一张能分享的修仙卡

---

## 安装

```bash
npx skills add https://github.com/dangoZhang/xiuxian.skill -a codex -a claude-code -a cursor -a opencode -a openclaw
```

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/dangoZhang/xiuxian.skill.git ~/.codex/skills/xiuxian-skill
```

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/dangoZhang/xiuxian.skill.git ~/.claude/skills/xiuxian-skill
```

```bash
mkdir -p ~/.openclaw/skills
git clone https://github.com/dangoZhang/xiuxian.skill.git ~/.openclaw/skills/xiuxian-skill
```

---

## 使用

### 问境界

```text
看看我最近两周和 AI 协作到了什么境界。先用人话说清楚我现在最像哪一层，再给我一个修仙称号。
```

### 生成分享卡

```text
把我最近 10 天的 Codex 轨迹炼成一张分享卡。大字只保留境界和等级，其他内容帮我收成一眼能看懂的判词。
```

### 指导突破

```text
别只告诉我等级。结合我最近这轮轨迹，指出我最拖后腿的一个习惯，再给我 3 条下一轮立刻能照做的突破建议。
```

---

## 效果示例

<div align="center">
  <img src="./assets/readme/xiuxian-card.png" alt="修仙.skil 效果示例" width="54%" />
</div>

---

## 境界与等级

| 综合分段 | 境界 | 等级 | 这一层的人，不一样在哪 |
| --- | --- | --- | --- |
| 0-11 | 凡人 | L1 | 还停留在单轮提问，AI 更像临时工具 |
| 12-23 | 感气 | L2 | 已知道问法会改变结果，但稳定性还不够 |
| 24-35 | 炼气 | L3 | 能做成小任务，也会边做边补要求 |
| 36-47 | 筑基 | L4 | 常见任务能稳定推进到多步完成 |
| 48-59 | 金丹 | L5 | 开始把重复打法沉淀成可复用套路 |
| 60-69 | 元婴 | L6 | 会让 AI 先走一段，再回来收方向和结果 |
| 70-77 | 化神 | L7 | 能同时调动多 Agent 和工具并行推进 |
| 78-85 | 炼虚 | L8 | 开始搭能力、搭流程，不只是在做单次任务 |
| 86-91 | 合体 | L9 | 能把这套协作带进真实项目并持续修正 |
| 92-100 | 大乘 | L10 | 能把方法沉淀下来，稳定复制给团队 |

---

## 词汇表

- [AI / vibecoding / 修仙词汇表](./docs/lexicon.md)

---

<div align="center">

MIT License © [dangoZhang](https://github.com/dangoZhang)

</div>
