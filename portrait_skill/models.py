from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class TokenUsage:
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0
    total_tokens: int = 0


@dataclass(slots=True)
class Message:
    role: str
    text: str
    timestamp: str | None = None
    meta: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class Transcript:
    source: str
    path: Path
    messages: list[Message]
    tool_calls: int = 0
    raw_event_count: int = 0
    models: list[str] = field(default_factory=list)
    providers: list[str] = field(default_factory=list)
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    display_name: str | None = None


@dataclass(slots=True)
class MetricScore:
    name: str
    score: int
    rationale: str


@dataclass(slots=True)
class Persona:
    title: str
    subtitle: str
    tags: list[str]
    summary: str


@dataclass(slots=True)
class Certificate:
    track: str
    title: str
    level: str
    score: int
    persona: Persona
    evidence: list[str]
    growth_plan: list[str]


@dataclass(slots=True)
class Analysis:
    transcript: Transcript
    user_metrics: list[MetricScore]
    assistant_metrics: list[MetricScore]
    user_certificate: Certificate
    assistant_certificate: Certificate
    overview: str
