"""Shared contract for every agent in the orchestration layer.

Each agent is a plain Python class with a single async `handle(...)` method
and a fixed-shape result. No agent framework (LangGraph/CrewAI/AutoGen) is
used on purpose: at this scale a transparent, debuggable custom router is
easier to reason about, test, and explain than an opaque framework, and it
has zero added dependencies.
"""

from dataclasses import dataclass, field
from typing import Any, Literal

AgentName = Literal["intake", "planner", "vision", "progress", "safety", "remedy", "router"]


@dataclass
class AgentResult:
    agent: AgentName
    content: Any
    warnings: list[str] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
