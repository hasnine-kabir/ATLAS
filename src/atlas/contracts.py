"""Shared data contracts for the ATLAS pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Risk(Enum):
    """Risk level assigned to every tool action.

    SAFE    — runs immediately, no confirmation needed.
    CONFIRM — requires a fresh spoken confirmation within the timeout window.
    BLOCKED — refused unconditionally; never exposed to the LLM.
    """

    SAFE = "safe"
    CONFIRM = "confirm"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ToolResult:
    """Outcome returned by every tool handler."""

    ok: bool
    say: str
    data: dict[str, Any] | None = None
