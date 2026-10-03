"""Tool handler for launching applications."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from atlas.contracts import ToolResult
from atlas.os_adapter.base import OSAdapter


def make_open_app_handler(
    adapter: OSAdapter,
) -> Callable[[dict[str, Any]], ToolResult]:
    """Create an ``open_app`` handler bound to *adapter*.

    The returned callable expects ``args`` with at least::

        {"app": "<spoken name>", "target": "<executable or URI>"}

    If ``target`` is missing the app was not found in the alias table.
    """

    def open_app(args: dict[str, Any]) -> ToolResult:
        app_name: str = str(args.get("app", ""))
        target: str | None = args.get("target")

        if not target:
            return ToolResult(
                ok=False,
                say=f"I couldn't find an app called {app_name}.",
            )

        try:
            adapter.launch_app(target)
        except Exception as exc:
            return ToolResult(
                ok=False,
                say=f"I tried to open {app_name}, but something went wrong: {exc}",
            )

        # Pretty-print the display name (strip extension, title-case).
        display = app_name.replace(".exe", "").replace(".cmd", "").title()
        return ToolResult(ok=True, say=f"Opening {display}.")

    return open_app
