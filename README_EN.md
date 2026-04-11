<div align="center">

# vibecoding.skill

> *"Distill your vibecoding history and see what level your collaboration with AI has really reached."*

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

### Preview

<img src="./assets/readme/vibecoding-card.png" alt="vibecoding.skill preview" width="54%" />

<br>

You already write code, ship changes, fix bugs, and push tasks forward with AI every day.<br>
`vibecoding.skill` compresses that real collaboration history into one result: your level, your habits, and your next upgrade step.<br>

</div>

---

## Overview

`vibecoding.skill` is a skill for code agents. It reads your real collaboration history with AI and turns it into a direct, usable judgment.

You can use it to do four things:

- see your current vibecoding level
- distill your own collaboration habits or mimic someone else's
- get concrete guidance for the next level up
- export a shareable skill bundle that someone else can install directly

It tells you:

- where you roughly stand today
- which collaboration habits are already stable
- which habits are slowing you down
- what to train next if you want to level up

There is no questionnaire and no self-rating. Feed it real sessions, and it gives you a report, a level judgment, a share card, and an upgrade path.

If you want to pass someone's vibecoding style to another person or team, share the exported skill bundle. Markdown files are good for reading. The skill bundle is what another agent can actually install and use.

The default output stays plain and direct.

---

## Install

These install commands have already been verified.

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

### Install On Multiple Hosts

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a codex -a claude-code -a cursor -a opencode -a openclaw
```

After installation, just talk to your agent naturally.

---

## Example Prompts

```text
Look at my last 14 days of AI collaboration and tell me what level I'm at, plus my most stable habit and my biggest weak spot.
```

```text
Distill my vibecoding habits from the last two weeks. In future sessions, try to work with me in that rhythm.
```

```text
I have a coworker's collaboration history with AI. Summarize their habits first, then tell me why they are stable at this level.
```

```text
Only look at sessions from 2026-04-01 to 2026-04-10. Give me a report and tell me whether I improved compared with the previous window.
```

```text
Make me a vibecoding share card for the past week. Keep it concise, but make the key judgment obvious at a glance.
```

```text
If I want to move my vibecoding level up by one tier, what is the single most valuable habit to train next?
```

```text
If my target is L7, compare that target with my recent history and tell me which habits I am still missing, then give me a plan I can actually follow.
```

```text
Export my last two weeks of vibecoding habits as a shareable skill bundle. I want to send it to a teammate to install, and I also want a summary plus a share card.
```

---

## Export And Sharing

If you want someone else to continue working in the same style, export the whole bundle.

- To let another agent install it directly: share the exported directory or a zip archive.
- To let a person skim the distilled habits quickly: share `PROFILE.md`.
- To show the full reasoning and evidence: share `REPORT.md`.
- To post it in chat or on social media: share `assets/vibecoding-card.png`.

Each exported bundle includes:

- `SKILL.md`: installable skill entry
- `PROFILE.md`: condensed habit profile
- `REPORT.md`: full report
- `snapshot.json`: structured result
- `assets/`: share card assets

---

## Level Guide

| Level | What makes people at this level different |
| --- | --- |
| L1 | They still treat AI like a toy, not part of real production work. |
| L2 | They have noticed that prompting style changes the result. |
| L3 | They already have prompt feel and can complete simple tasks reliably. |
| L4 | They have a repeatable workflow for recurring task types. |
| L5 | They start packaging their own methods into skills, templates, or modules. |
| L6 | They already have an agent that can go do a chunk of work first. |
| L7 | They can coordinate multiple agents and tools on the same task. |
| L8 | They stop optimizing isolated tasks and start building capability layers and mental models. |
| L9 | The human owns judgment and accountability; the agent owns execution and feedback loops. |
| L10 | Their method can be copied and reused by a team or clients. |

---

<div align="center">

[中文](./README.md)

MIT License © [dangoZhang](https://github.com/dangoZhang)

</div>
