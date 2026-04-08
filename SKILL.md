---
name: portrait.skill
description: Read Codex, Claude Code, or OpenCode transcript files, extract user-AI collaboration patterns, issue cultivation portraits or AI collaboration capability certificates, and guide the next breakthrough cycle.
---

# portrait.skill

## What It Does

`portrait.skill` reads agent runtime transcripts, scores collaboration quality, and issues two optional output tracks:

- User cultivation portrait
- AI collaboration capability certificate

It can also produce a next-cycle breakthrough plan and compare two cycles to judge whether the user or AI broke through.

## When To Use

Use this skill when the user wants to:

- analyze a Codex / Claude Code / OpenCode conversation file
- understand how they collaborate with AI
- get a gamified but evidence-based portrait or certificate
- improve collaboration quality over the next cycle
- compare multiple logs over time

## Operating Flow

1. Ask for the transcript path, or auto-detect the latest local file.
2. Ask which certificate they want: `user`, `assistant`, or `both`.
3. Parse the transcript and summarize:
   - user request style
   - context quality
   - iteration pattern
   - verification behavior
   - tool usage
   - recovery / adaptation
4. Issue the certificate in markdown with:
   - level
   - 画像
   - evidence
   - next breakthrough tasks
5. If the user wants growth guidance, turn the weakest dimensions into a 1-cycle training plan.
6. If the user provides two transcripts, compare them and report whether they upgraded.

## Local Defaults

- Codex: `~/.codex/archived_sessions/`, `~/.codex/sessions/`
- Claude Code: `~/.claude/projects/`
- OpenCode: `~/.local/share/opencode/project/`, `~/Library/Application Support/opencode/project/`
- Cursor: `~/Library/Application Support/Cursor/User/workspaceStorage/`, `~/.config/Cursor/User/workspaceStorage/`
- VS Code / VSCodium: `~/Library/Application Support/Code/User/workspaceStorage/`, `~/.config/Code/User/workspaceStorage/`, `~/.config/VSCodium/User/workspaceStorage/`

## Agent Usage

This repository is meant to be installed as an agent skill.

The user should not need to manually run terminal commands. After the skill is installed into their Code Agent tool, the agent should:

1. decide whether to analyze one session, aggregate many sessions, or compare two periods
2. find the right transcript source or path
3. run the internal CLI itself
4. return the result in concise user-facing language

Typical user requests:

- “请用 portrait.skill 炼化我最近一周的 Codex 卷宗。”
- “请给我修仙画像。”
- “我不要修仙风格，直接给我 AI 协作能力证书。”
- “请比较上个月和这个月，看我有没有升级。”

Internal commands for the agent to run when needed:

```bash
python3 -m portrait_skill.cli analyze --source codex --all --certificate both
python3 -m portrait_skill.cli analyze --source codex --since 2026-04-01 --until 2026-04-09 --certificate both
python3 -m portrait_skill.cli analyze --path ~/.codex/archived_sessions/rollout-xxx.jsonl --certificate user
python3 -m portrait_skill.cli compare --before ./cycle-1.jsonl --after ./cycle-2.jsonl --certificate both
```

## Output Contract

Keep the final answer concise and evidence-based. Prefer this structure:

1. one-paragraph overview
2. certificate section
3. 2 to 3 breakthrough tasks

Avoid empty hype. Every level claim must cite transcript evidence.
