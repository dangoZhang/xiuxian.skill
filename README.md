<div align="center">

# vibecoding.skill

> *"蒸馏你的 vibecoding 记录，看你与 AI 的协作达到了什么等级。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Codex](https://img.shields.io/badge/Codex-Skill-111111)](https://developers.openai.com/codex/skills)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![OpenCode](https://img.shields.io/badge/OpenCode-Ready-1991FF)](https://opencode.ai)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Ready-0F766E)](https://github.com/openclaw/openclaw)
[![Cursor](https://img.shields.io/badge/Cursor-Ready-222222)](https://cursor.com/docs/context/skills)
[![Download ZIP](https://img.shields.io/badge/Download-ZIP-2EA44F)](https://github.com/dangoZhang/vibecoding.skill/archive/refs/heads/main.zip)

<br>

[中文](./README.md) · [English](./README_EN.md)

<br>

### 效果示例

<img src="./assets/readme/vibecoding-card.png" alt="vibecoding.skill 效果示例" width="54%" />

<br>

你每天都在和 AI 一起写代码、改需求、补文档、跑任务。<br>
`vibecoding.skill` 会把这段真实记录压成一份结果：你到了哪一级，你的习惯是什么，下一步该怎么升。<br>

</div>

---

## 项目介绍

`vibecoding.skill` 是一个装进 Code Agent 里的 skill。它会读取你最近一段时间和 AI 的真实协作记录，然后给出一份很直接的判断。

你能拿它做四件事：

- 看你现在的 vibecoding 等级到了哪一级
- 蒸馏你自己的协作习惯，或者模仿别人的做事节奏
- 根据你最近的记录，给出下一轮最值得刻意练的动作
- 导出一份可以直接分享给别人安装的 vibecoding skill 包

它会直接告诉你：

- 你现在大概在什么水平
- 你最稳定的习惯是什么
- 你最容易拖慢协作的动作是什么
- 如果想继续升级，下一轮该先补哪一步

你不用填问卷，也不用自己打分。把最近一段时间的真实记录交给它，它会直接给你报告、等级判断、分享卡和升级建议。

如果你要把某个人的 vibecoding 习惯交给别人继续用，优先分享导出的 skill 包。`md` 适合阅读，skill 包适合直接安装进 Agent。

默认输出先说人话。修仙风格只是彩蛋，只有你主动要求时才会打开。

---

## 安装

下面这些安装方式都已经实机验证可用。

### Codex

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a codex
```

### Claude Code

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a claude-code
```

### Cursor

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a cursor
```

### OpenCode

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a opencode
```

### OpenClaw

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a openclaw
```

### 多平台一起安装

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a codex -a claude-code -a cursor -a opencode -a openclaw
```

装好之后，直接对 Agent 说下面这些话就可以。

---

## 你可以这样用

```text
帮我看看我最近 14 天和 AI 协作到了什么等级，顺便说清楚我最稳定的习惯和最拖后腿的问题。
```

```text
把我最近两周的 vibecoding 习惯蒸出来。以后再和我一起做事时，尽量按我这套节奏来。
```

```text
我给你一份同事和 AI 的协作记录。先总结他的习惯，再告诉我他为什么能稳定到这个等级。
```

```text
只看 2026-04-01 到 2026-04-10 这段时间，帮我出一份报告，再看看我和前一段时间比有没有进步。
```

```text
给我一张我最近这周的 vibecoding 分享卡，文案短一点，但要把核心判断写清楚。
```

```text
如果我想把自己的 vibecoding 等级再往上提一档，下一轮最值得刻意练的动作是什么？
```

```text
如果我的目标是 L7，你结合我最近这段记录，直接告诉我还差哪些关键习惯，再给我一个能照着练的计划。
```

```text
把我最近两周的 vibecoding 习惯导出成一个可分享的 skill 包。我想直接发给同事安装，也顺手给我一份摘要和分享卡。
```

### 彩蛋

```text
如果有彩蛋版的话，也顺手帮我做一张修仙风格的分享卡。
```

---

## 导出和分享

如果你想把这套 vibecoding 习惯交给别人继续用，推荐导出成一整包：

- 给 Agent 直接安装：分享整个导出目录，或打成 zip 分享。
- 给人快速阅读：分享 `PROFILE.md`。
- 给人看完整判断：分享 `REPORT.md`。
- 发群或发社交平台：分享 `assets/vibecoding-card.png`。

导出的 skill 包里会同时带上：

- `SKILL.md`：可直接安装的技能入口
- `PROFILE.md`：压缩后的习惯画像
- `REPORT.md`：完整报告
- `snapshot.json`：结构化结果
- `assets/`：分享卡

---

## 等级对照

| 等级 | 这一层的人，已经不一样在哪 | 彩蛋境界 |
| --- | --- | --- |
| L1 | 还把 AI 当玩具，不当生产力 | 凡人 |
| L2 | 开始知道提问方式会改变结果 | 感气 |
| L3 | 已经有 prompt 手感，能稳定做简单任务 | 炼气 |
| L4 | 开始有固定 workflow，同类任务能反复跑 | 筑基 |
| L5 | 开始把自己的做法封成 skill、模板或模块 | 金丹 |
| L6 | 开始拥有“能替自己先干一段活”的分身 | 元婴 |
| L7 | 能同时调多个 agent、多个工具协同完成任务 | 化神 |
| L8 | 不再做单任务优化，开始做能力层和世界模型 | 炼虚 |
| L9 | 人负责判断和担责，agent 负责执行和回流 | 合体 |
| L10 | 能把自己的方法复制给团队或客户 | 大乘 |

---

<div align="center">

MIT License © [dangoZhang](https://github.com/dangoZhang)

</div>
