"""Rule-based fast-path intent router.

Matches normalized utterances against a table of regex templates.
Target latency: under 50 ms, works fully offline.
"""

from __future__ import annotations

import re
from typing import Any

from atlas.nlu.contracts import Intent
from atlas.nlu.normalize import normalize_text

# ---------------------------------------------------------------------------
# Rule patterns — each is tried in order; first match wins.
# ---------------------------------------------------------------------------
_OPEN_PATTERN = re.compile(r"^(?:open|launch|start)\s+(.+)$")


class RulesRouter:
    """Match normalized utterances against rule templates.

    Returns an ``Intent`` on a successful match, or ``None`` when no rule
    applies (allowing fallback to the LLM router).
    """

    def __init__(self, app_aliases: dict[str, str]) -> None:
        # Lowercase all alias keys for case-insensitive lookup.
        self._aliases: dict[str, str] = {k.lower(): v for k, v in app_aliases.items()}

    def route(self, utterance: str) -> Intent | None:
        """Route an utterance to an ``Intent``, or ``None`` if no rule matches."""
        normalized = normalize_text(utterance)
        if not normalized:
            return None

        match = _OPEN_PATTERN.match(normalized)
        if match:
            app_name = match.group(1).strip()
            return self._resolve_open_app(app_name)

        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_open_app(self, app_name: str) -> Intent:
        """Build an ``open_app`` Intent, attaching the resolved target if aliased."""
        args: dict[str, Any] = {"app": app_name}
        key = app_name.lower()
        if key in self._aliases:
            args["target"] = self._aliases[key]
        return Intent(
            tool="open_app",
            args=args,
            source="rule",
            confidence=1.0,
        )
