from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


TERM_SOURCES = [
    {
        "name": "OpenAI Codex use cases",
        "url": "https://developers.openai.com/codex/use-cases",
        "keywords": ["codex", "workflow", "report", "cli", "review", "large codebases"],
    },
    {
        "name": "OpenAI GPT-5.2-Codex model",
        "url": "https://developers.openai.com/api/docs/models/gpt-5.2-codex",
        "keywords": ["agentic", "coding", "context window", "reasoning", "structured outputs", "function calling"],
    },
    {
        "name": "Anthropic Claude Code MCP",
        "url": "https://code.claude.com/docs/en/mcp",
        "keywords": ["mcp", "resources", "prompts", "tools", "list_changed", "output", "tokens"],
    },
    {
        "name": "Anthropic Claude Code slash commands",
        "url": "https://docs.anthropic.com/en/docs/claude-code/slash-commands",
        "keywords": ["agents", "memory", "compact", "mcp", "slash commands"],
    },
    {
        "name": "Cursor Rules",
        "url": "https://docs.cursor.com/context/rules",
        "keywords": ["rules", "memory", "project rules", "user rules", "workflow"],
    },
    {
        "name": "Cursor Memories",
        "url": "https://docs.cursor.com/en/context/memories",
        "keywords": ["memories", "tool calls", "context across sessions", "sidecar"],
    },
    {
        "name": "Cursor Background Agents",
        "url": "https://docs.cursor.com/en/background-agents",
        "keywords": ["background agents", "asynchronous", "remote", "follow-ups", "take over"],
    },
    {
        "name": "MCP Build Server",
        "url": "https://modelcontextprotocol.io/docs/develop/build-server",
        "keywords": ["resources", "tools", "prompts", "mcp servers", "client"],
    },
    {
        "name": "MCP Tools",
        "url": "https://modelcontextprotocol.io/specification/2025-06-18/server/tools",
        "keywords": ["model-controlled", "tools", "structured content", "resource links"],
    },
    {
        "name": "MCP Prompts",
        "url": "https://modelcontextprotocol.io/specification/draft/server/prompts",
        "keywords": ["prompts", "structured messages", "customize", "security"],
    },
]

TERM_CANON = {
    "agentic coding": ["agentic coding", "long-horizon", "coding tasks"],
    "background mode": ["background mode", "background agents", "asynchronous"],
    "rules": ["rules", "project rules", "user rules"],
    "memory": ["memory", "memories", "context across sessions", "cross sessions"],
    "mcp": ["mcp", "model context protocol"],
    "resources": ["resources", "resource links"],
    "tools": ["tools", "tool calls", "tool use", "model-controlled"],
    "prompts": ["prompts", "slash commands", "prompt templates"],
    "structured outputs": ["structured outputs", "structured content"],
    "context window": ["context window", "output tokens", "token"],
    "handoff": ["take over", "follow-ups", "compact", "handoff", "continue"],
}

FETCH_TIMEOUT_SECONDS = 8
FETCH_MAX_WORKERS = 6


@dataclass(slots=True)
class TermSnippet:
    source: str
    url: str
    keyword: str
    snippet: str


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if text:
            self.parts.append(text)

    def text(self) -> str:
        return "\n".join(self.parts)


def refresh_term_catalog(output_dir: str | Path) -> dict[str, str]:
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fetched_texts, failures = _fetch_source_texts()
    if failures:
        failed_names = ", ".join(item["name"] for item in failures)
        raise RuntimeError(f"refresh-terms failed because official sources were unavailable: {failed_names}")
    snippets = _fetch_snippets(fetched_texts)
    if not snippets:
        raise RuntimeError("refresh-terms failed because no terminology snippets could be extracted from the official sources.")
    term_rows = _build_term_rows(snippets)
    if not term_rows:
        raise RuntimeError("refresh-terms failed because no terminology rows could be built from the fetched sources.")
    markdown = _render_terms_markdown(fetched_at, term_rows)
    prompt = _render_term_prompt(fetched_at, term_rows)
    json_payload = {
        "fetched_at": fetched_at,
        "sources": TERM_SOURCES,
        "fetched_source_count": len(fetched_texts),
        "terms": term_rows,
    }

    markdown_path = root / "latest-agent-terms.md"
    json_path = root / "latest-agent-terms.json"
    prompt_path = root / "latest-agent-terms.prompt.md"
    markdown_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_path.write_text(prompt, encoding="utf-8")
    return {
        "terms_markdown": str(markdown_path),
        "terms_json": str(json_path),
        "terms_prompt": str(prompt_path),
    }


def _fetch_source_texts() -> tuple[dict[str, str], list[dict[str, str]]]:
    fetched_texts: dict[str, str] = {}
    failures: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=min(FETCH_MAX_WORKERS, len(TERM_SOURCES))) as executor:
        futures = {
            executor.submit(_fetch_text, str(source["url"])): source
            for source in TERM_SOURCES
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                text = future.result()
            except Exception as exc:
                failures.append(
                    {
                        "name": str(source["name"]),
                        "url": str(source["url"]),
                        "error": str(exc) or exc.__class__.__name__,
                    }
                )
                continue
            fetched_texts[str(source["url"])] = text
    return fetched_texts, failures


def _fetch_snippets(fetched_texts: dict[str, str]) -> list[TermSnippet]:
    snippets: list[TermSnippet] = []
    for source in TERM_SOURCES:
        text = fetched_texts.get(str(source["url"]), "")
        if not text:
            continue
        for keyword in source["keywords"]:
            snippet = _extract_snippet(text, keyword)
            if snippet:
                snippets.append(TermSnippet(source=source["name"], url=source["url"], keyword=keyword, snippet=snippet))
    return snippets


def _fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 vibecoding.skill term refresh",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
        html = response.read().decode("utf-8", errors="ignore")
    parser = _HTMLTextExtractor()
    parser.feed(html)
    text = parser.text()
    if not text.strip():
        raise ValueError(f"Empty response body for {url}")
    return text


def _extract_snippet(text: str, keyword: str) -> str:
    lowered = text.lower()
    target = keyword.lower()
    index = lowered.find(target)
    if index < 0:
        return ""
    start = max(0, index - 220)
    end = min(len(text), index + 280)
    snippet = text[start:end]
    snippet = re.sub(r"\s+", " ", snippet).strip()
    return snippet


def _build_term_rows(snippets: list[TermSnippet]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for term, aliases in TERM_CANON.items():
        matched = [snippet for snippet in snippets if any(alias in snippet.keyword.lower() or alias in snippet.snippet.lower() for alias in aliases)]
        if not matched:
            continue
        sources = []
        evidence = []
        for item in matched:
            if item.source not in sources:
                sources.append(item.source)
            if item.snippet not in evidence:
                evidence.append(item.snippet)
        rows.append(
            {
                "term": term,
                "aliases": aliases,
                "sources": sources,
                "summary": _summarize_term(term, aliases, evidence),
                "evidence": evidence[:3],
            }
        )
    return rows


def _summarize_term(term: str, aliases: list[str], evidence: list[str]) -> str:
    joined = " ".join(evidence).lower()
    if term == "agentic coding":
        return "强调长链路、带工具、可持续推进的编码协作。"
    if term == "background mode":
        return "把任务交给异步或远端 agent 持续推进，再回来接手。"
    if term == "rules":
        return "把长期有效的项目规则、用户偏好和 workflow 固化给 agent。"
    if term == "memory":
        return "把跨会话仍然有效的信息保留下来，减少重复解释。"
    if term == "mcp":
        return "让 agent 通过标准协议接入 tools、resources、prompts。"
    if term == "resources":
        return "把文件、文档、结构化上下文作为可引用资源交给 agent。"
    if term == "tools":
        return "让模型按上下文主动调用能力，而不是只做纯文本回答。"
    if term == "prompts":
        return "把可复用的工作流和指令模板显式暴露出来。"
    if term == "structured outputs":
        return "要求输出保持结构化，方便后续汇总、比对和自动处理。"
    if term == "context window":
        return "上下文和输出上限直接决定一次能吃下多少轨迹与证据。"
    if term == "handoff":
        return "支持压缩上下文、续接任务、异步接力和回到主线。"
    return f"围绕 {term} 的最新常见说法包括：{', '.join(aliases)}。"


def _render_terms_markdown(fetched_at: str, rows: list[dict[str, object]]) -> str:
    lines = [
        "# 最新 Agent 术语输入",
        "",
        f"- 更新时间：`{fetched_at}`",
        "- 来源：OpenAI / Anthropic / Cursor / MCP 官方文档",
        "",
        "| 术语 | 别名 | 用在 vibecoding 里是什么意思 | 官方来源 |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        aliases = ", ".join(row["aliases"])
        sources = ", ".join(row["sources"])
        lines.append(f"| {row['term']} | {aliases} | {row['summary']} | {sources} |")
    lines.extend(["", "## 证据摘录", ""])
    for row in rows:
        lines.append(f"### {row['term']}")
        for item in row["evidence"]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _render_term_prompt(fetched_at: str, rows: list[dict[str, object]]) -> str:
    lines = [
        "# 最新 Agent 术语注入 Prompt",
        "",
        f"词表更新时间：{fetched_at}",
        "",
        "你要做的事：",
        "- 先读取下面这份术语输入。",
        "- 只使用和 vibecoding、LLM agent、工具编排、跨会话协作直接相关的术语。",
        "- 写报告、画像、等级卡、升级建议时，优先使用这份词表里的最新常见说法。",
        "- 如果轨迹里没有出现对应行为，不要硬贴新词。",
        "- 如果新词会让句子变虚，就回到更直接的人话。",
        "",
        "术语输入：",
    ]
    for row in rows:
        lines.append(
            f"- {row['term']}：别名 {', '.join(row['aliases'])}；解释：{row['summary']}；来源：{', '.join(row['sources'])}"
        )
    return "\n".join(lines).strip() + "\n"
