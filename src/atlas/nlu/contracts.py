"""Data contracts for the NLU subsystem."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class Intent:
    """A resolved user intent from either the rules engine or LLM."""

    tool: str
    args: dict[str, Any]
    source: Literal["rule", "llm"]
    confidence: float = 1.0
