<div align="center">

# 修仙.skil

> *"赛博修仙时代，你修到了哪一层？"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Codex](https://img.shields.io/badge/Codex-Skill-111111)](https://developers.openai.com/codex/skills)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![Download ZIP](https://img.shields.io/badge/Download-ZIP-2EA44F)](https://github.com/dangoZhang/xiuxian.skill/archive/refs/heads/main.zip)

<br>

读取真实运行卷宗<br>
蒸馏你与 AI 的协作轨迹<br>
给出一张大字突出 **境界** 与 **等级** 的修仙卡

<br>

支持最近一次、全部会话、指定时间窗炼化<br>
支持 Codex、Claude Code、OpenCode、OpenClaw、Cursor、VS Code

[安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [境界与等级](#境界与等级) · [English](README_EN.md)

</div>

---

## 支持的运行卷宗

| 来源 | 默认位置 | 备注 |
|------|----------|------|
| Codex | `~/.codex/archived_sessions/` `~/.codex/sessions/` | 读取 `.jsonl` 会话 |
| Claude Code | `~/.claude/projects/` | 读取项目卷宗 |
| OpenCode | 本地 `opencode.db` 或导出会话 | 支持最近一次与聚合 |
| OpenClaw | `~/.openclaw/agents/main/sessions/*.jsonl` | 读取 `.jsonl` 会话 |
| Cursor | `workspaceStorage/` | 读取工作区轨迹 |
| VS Code | `workspaceStorage/` | 读取 Copilot / Agent 轨迹 |

---

## 安装

### 一键安装

```bash
npx skills add https://github.com/dangoZhang/xiuxian.skill -a codex -a claude-code -a cursor -a opencode -a openclaw
```

### 手动安装

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

```bash
mkdir -p .github/skills
git clone https://github.com/dangoZhang/xiuxian.skill.git .github/skills/xiuxian-skill
```

---

## 使用

装好后，直接对 Agent 说：

```text
给我一个我最近和 AI 协作的境界
```

```text
炼一下我 2026-04-01 到 2026-04-10 的 Codex 卷宗
```

```text
给我一张修仙卡
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
| 0-11 | 凡人 | L1 | 仍在试手，AI 还没真正入炉 |
| 12-23 | 感气 | L2 | 开始知道问法会改变结果 |
| 24-35 | 炼气 | L3 | 已能稳定炼成简单差事 |
| 36-47 | 筑基 | L4 | 常见路数可重复跑通 |
| 48-59 | 金丹 | L5 | 开始把常用术式封成法门 |
| 60-69 | 元婴 | L6 | 分身已能先替你行过一段路 |
| 70-77 | 化神 | L7 | 可同时役使多具分身与法器 |
| 78-85 | 炼虚 | L8 | 开始经营能力层与系统层章法 |
| 86-91 | 合体 | L9 | 能进入真实场域并持续回流 |
| 92-100 | 大乘 | L10 | 法门已可复制给团队或客户 |

---

<div align="center">

MIT License © [dangoZhang](https://github.com/dangoZhang)

</div>
