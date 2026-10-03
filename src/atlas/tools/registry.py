"""Tool registry: maps intent tool names to handler functions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from atlas.contracts import ToolResult
from atlas.nlu.contracts import Intent


def _unknown_tool(tool_name: str) -> ToolResult:
    """Produce a failure result for an unregistered tool."""
    return ToolResult(ok=False, say=f"I don't know how to do that ({tool_name}).")


class ToolRegistry:
    """Central registry of named tool handlers.

    Each handler is a callable that accepts an ``args`` dict and returns
    a ``ToolResult``.  The registry looks up the handler by the intent's
    ``tool`` field and delegates execution.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[dict[str, Any]], ToolResult]] = {}

    def register(
        self,
        name: str,
        handler: Callable[[dict[str, Any]], ToolResult],
    ) -> None:
        """Register *handler* under *name*."""
        self._handlers[name] = handler

    def execute(self, intent: Intent) -> ToolResult:
        """Execute the handler for *intent*, or return a failure result."""
        handler = self._handlers.get(intent.tool)
        if handler is None:
            return _unknown_tool(intent.tool)
        return handler(intent.args)
