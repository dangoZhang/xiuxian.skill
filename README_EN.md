# portrait.skill

---

> "Throw your real runtime transcripts into the furnace, then reveal the collaboration root, aptitude, realm, and the next breakthrough path."

Turn one real AI collaboration cycle into a reusable portrait.

![License](https://img.shields.io/badge/License-MIT-f4c542)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Codex](https://img.shields.io/badge/Codex-Skill-111111)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-7C3AED)
![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8BC34A)

Feed runtime materials from Codex, Claude Code, OpenCode, Cursor, or VS Code  
Generate a cultivation portrait or an AI collaboration capability certificate  
See how you and AI actually work together, where you stall, and how to break through next cycle

⚠️ This project is for personal collaboration review, growth tracking, and workflow training. Do not use it for identity spoofing, privacy abuse, or deceptive claims.

[Install](#install) · [Usage](#usage) · [Example](#example) · [中文](./README.md)

---

## Install

```bash
git clone https://github.com/dangoZhang/portrait.skill
cd portrait.skill
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
python3 -m portrait_skill.cli scan
python3 -m portrait_skill.cli analyze --source codex --certificate both
python3 -m portrait_skill.cli compare --before ./cycle-1.jsonl --after ./cycle-2.jsonl --certificate both
```

## Example

```bash
python3 -m portrait_skill.cli analyze \
  --path examples/demo_codex_session.jsonl \
  --certificate both \
  --output examples/demo_report.md
```

## Privacy

Everything runs locally by default.

The report automatically redacts the home directory as `~`, and other absolute paths are reduced to filenames when possible.
