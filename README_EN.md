<div align="center">

# vibecoding.skill

Distill the way you work with AI into a reusable capability.

Language:
[中文](./README.md) · [English](./README_EN.md)

Supported platforms:
<br />
<a href="#codex"><img src="https://img.shields.io/badge/Codex-0B0B0F?style=for-the-badge&logo=openai&logoColor=white" alt="Codex" /></a>
<a href="#claude-code"><img src="https://img.shields.io/badge/Claude_Code-1A1716?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code" /></a>
<a href="#opencode"><img src="https://img.shields.io/badge/OpenCode-111827?style=for-the-badge&logo=gnubash&logoColor=white" alt="OpenCode" /></a>
<a href="#openclaw"><img src="https://img.shields.io/badge/OpenClaw-0F172A?style=for-the-badge&logo=git&logoColor=white" alt="OpenClaw" /></a>
<a href="#cursor"><img src="https://img.shields.io/badge/Cursor-1F2937?style=for-the-badge&logo=cursor&logoColor=white" alt="Cursor" /></a>

</div>

<table>
<tr>
<td width="52%" valign="top">

### Your vibecoding profile

`L4` `Stable` `Goal-first` `Context-ready` `Verifiable output` `Evidence-first`

When you talk to AI, the opening usually reads like an executable prompt. You pin down the goal, boundary, acceptance, and deliverable first, then supply the needed context so the code agent can start without guessing.

Once execution begins, your instructions stay short, direct, and operational. If the agent can read files, run commands, or inspect logs, you prefer that over long discussion, then refine the prompt from evidence.

Overall, this is already a strong way to drive AI work. The current strengths are task framing, enough context, and clear acceptance. The next thing to improve is faster correction after drift, and steadier progress across longer chains.

</td>
<td width="48%" valign="top">

### Share Card

<img src="./assets/readme/vibecoding-card-en.png" alt="vibecoding.skill share card" width="100%" />

</td>
</tr>
</table>

## 1. What It Can Do

- Read real collaboration logs.
- Build a direct portrait first: use the raw trace to judge level, stage, strengths, and gaps.
- Distill vibecoding ability across 16 dimensions:
  goal framing, context supply, constraint governance, communication compression, execution preference, task decomposition, tool orchestration, context carry, iteration repair, failure recovery, verification loop, deliverable packaging, handoff memory, abstraction reuse, autonomous push, workflow orchestration.
- Build an indirect portrait second: keep the direct portrait as the primary truth source, then use the 16-dimension distillation to supply tags, summary-page copy, and share-bundle styling.
- Judge level and stage, then generate a dedicated vibecoding capability profile.
- Export a share bundle that turns your collaboration style into a capability others can share, showcase, and plug in immediately.
- Load someone else's shared capability so AI can enter that working rhythm fast and keep the task moving in the same style.
- Give an upgrade suggestion for the next cycle.

## 2. How To Install

### Codex

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a codex
```

### Claude Code

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a claude-code
```

### OpenCode

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a opencode
```

### OpenClaw

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a openclaw
```

### Cursor

```bash
mkdir -p .cursor/rules
curl -fsSL https://raw.githubusercontent.com/dangoZhang/vibecoding.skill/main/.cursor/rules/vibecoding-skill.mdc -o .cursor/rules/vibecoding-skill.mdc
```

### Environment Configuration

- Python: `3.10+`
- Install the project and dependencies:

```bash
python3 -m pip install -e .
```

- If you want to run the bundled test suite, install the test extra first:

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest -q
```

- Environment check:

```bash
python3 -m vibecoding_skill.cli doctor
```

## 3. Example Prompts And Responses

Below are five common use cases.

### 1. Distill My Profile

Prompt

```text
Look at my last two weeks of vibecoding and summarize my collaboration habits.
```

Live response

> This record is currently at vibecoding level `L4`, in the `stable` stage. Based on this sample, you can already push common tasks through multi-step execution with decent consistency, and AI has started to act as a real execution slot.
>
> The collaboration pattern is clear:
> - Strong opening. You define the goal, constraints, and deliverables early.
> - Fast progression. Once context is in place, AI starts acting directly.
> - Result-oriented. The requests stay grounded in concrete outputs.
> - Correction is still weaker, so `iteration repair` and `failure recovery` are the current gaps.

Notes:

- This "distill my profile" flow is the direct portrait. The main judgment comes from the raw trace.
- The README hero panel and exported profile page are indirect portraits, but they now reconcile to the direct portrait first and only use the 16-dimension model as a supporting layer.

### 2. Share My Capability

Prompt

```text
Export my recent collaboration style into a share bundle and give me one sentence the receiver should use.
```

Live response

> - Share bundle: `examples/generated/demo_codex_session-share-bundle`
> - Result skill call name: `vibecoding-profile-f11a0caa`
> - Result skill title: `码奸.skill`
> - Receiver sentence: `This is my teammate's exported bundle. Read the profile first, then call vibecoding-profile-f11a0caa and work with me in that style.`

### 3. Unpack And Apply Someone Else's Capability

Prompt

```text
This is my teammate's exported bundle. Read the profile first, then work with me in that style.
```

Live response

> I will use `vibecoding.skill` as the entry point first, then hand control to the result skill inside the exported bundle.
>
> Read these four files first, in order:
> 1. `PROFILE.md`
> 2. `REPORT.md`
> 3. `DISTILLED_SKILL.json`
> 4. `SKILL.md`
>
> The detected result skill call name is `vibecoding-profile-f11a0caa`, and the visible title is `码奸.skill`. After that, collaboration defaults to that style: frame the goal, boundary, and acceptance first, then act; prefer reading files, running commands, and shipping artifacts instead of staying in abstract planning.

### 4. Use The Skill To Rewrite A Coding Prompt

Prompt

```text
Call `vibecoding-profile-f11a0caa` and rewrite my current coding prompt so it matches this collaboration style better.
```

Live response

> I will first load and call `vibecoding-profile-f11a0caa` through `vibecoding.skill`, then rewrite your coding prompt so it matches that collaboration style more closely.
>
> Rewritten prompt:

```text
Use `vibecoding.skill` to load and call `vibecoding-profile-f11a0caa`, then help me fix the bug in this repo in that style. First use two short sentences to pin down the goal, boundary, and acceptance for this run, then start working right away: read the relevant files, run the necessary commands, inspect logs, locate the root cause, and finish the fix. Do not start with a long plan. If context is missing, pull files, logs, or command results first instead of guessing. If you spot drift, add only the single most important correction and continue. At the end, report only three things: what changed, how it was verified, and what is still unverified or risky.
```

### 5. Upgrade Suggestion

Prompt

```text
If I want to refine this collaboration style further, what should I train next?
```

Live response

> Train `iteration repair` first.
>
> Use this loop:
> 1. After each result, ask: `What is the biggest deviation right now?`
> 2. Add only `one` key correction.
> 3. If blocked, ask AI for `3 ways to narrow scope`, then continue with the shortest path.

## 4. Level Table

<table>
<tr>
<th>Level</th>
<th>Typical State</th>
</tr>
<tr>
<td><code>L1</code></td>
<td>Still mostly ad hoc prompting with no stable method.</td>
</tr>
<tr>
<td><code>L2</code></td>
<td>Already knows prompt wording changes results.</td>
</tr>
<tr>
<td><code>L3</code></td>
<td>Can complete simple tasks with some consistency.</td>
</tr>
<tr>
<td><code>L4</code></td>
<td>Can push common tasks through stable multi-step execution.</td>
</tr>
<tr>
<td><code>L5</code></td>
<td>Starts turning repeatable wins into skills, templates, or modules.</td>
</tr>
<tr>
<td><code>L6</code></td>
<td>Already has an agent that can take a chunk of work first.</td>
</tr>
<tr>
<td><code>L7</code></td>
<td>Can coordinate multiple agents and tools on the same task.</td>
</tr>
<tr>
<td><code>L8</code></td>
<td>Starts designing capability layers and longer workflows.</td>
</tr>
<tr>
<td><code>L9</code></td>
<td>The human owns judgment and accountability; the agent owns execution and feedback.</td>
</tr>
<tr>
<td><code>L10</code></td>
<td>The method can be copied reliably across a team or clients.</td>
</tr>
</table>

## 5. License And Project Tree

- [MIT License](./LICENSE)

Project structure:

```text
portrait.skill
├── .cursor
│   └── rules                              # Native Cursor rule entry
│       └── vibecoding-skill.mdc           # Main Cursor rule
├── README.md                              # Chinese launch page
├── README_EN.md                           # English launch page
├── SKILL.md                               # Skill entry instructions
├── LICENSE                                # Open-source license
├── pyproject.toml                         # Package config and dependencies
├── assets
│   └── readme                             # README visual assets
│       ├── vibecoding-card.png
│       ├── vibecoding-card.svg
│       ├── vibecoding-card-xianxia.png
│       └── vibecoding-card-xianxia.svg
├── docs
│   ├── latest-agent-terms.json
│   ├── latest-agent-terms.md
│   └── latest-agent-terms.prompt.md
├── examples
│   ├── demo_codex_session.jsonl           # Demo Codex log
│   └── generated                          # Generated examples
│       ├── demo-coach.md
│       ├── demo_codex_session-share-bundle # Shareable exported capability bundle
│       │   ├── DISTILLED_SKILL.json
│       │   ├── PROFILE.md
│       │   ├── README.md
│       │   ├── REPORT.md
│       │   ├── SKILL.md
│       │   ├── assets                     # Share card assets
│       │   └── snapshot.json              # Full structured snapshot
│       ├── demo_codex_session-xianxia-card # Xianxia-style card example
│       │   ├── report.json
│       │   ├── report.md
│       │   ├── vibecoding-card-xianxia.png
│       │   └── vibecoding-card-xianxia.svg
│       ├── demo-distilled.json
│       ├── demo-distilled.md
│       └── demo-report.md
├── tests                                  # Unit and CLI end-to-end tests
│   ├── test_cli_e2e.py
│   └── test_secondary_skill.py
└── vibecoding_skill                       # Core implementation
    ├── __init__.py
    ├── analyzer.py
    ├── cards.py
    ├── cli.py
    ├── distill.py
    ├── exporter.py
    ├── insights.py
    ├── luogu_palette.py
    ├── memory.py
    ├── models.py
    ├── parsers.py
    ├── renderer.py
    ├── secondary_skill.py
    ├── terms.py
    ├── themes.py
    └── xianxia.py
```
