"""Text normalization: lowercase, strip fillers, remove punctuation.

This module prepares raw user utterances for deterministic rule matching
by removing conversational padding, punctuation, and excess whitespace.
"""

from __future__ import annotations

import re

# Ordered longest-first so multi-word fillers are removed before their
# single-word components (e.g. "can you please" before "please").
_FILLER_PHRASES: list[str] = [
    "could you please",
    "can you please",
    "could you",
    "can you",
    "hey atlas",
    "hey",
    "please",
    "atlas",
]


def normalize_text(text: str) -> str:
    """Normalize user input for intent matching.

    Steps:
        1. Lowercase the entire string.
        2. Strip all punctuation (keep only word characters and spaces).
        3. Collapse runs of whitespace to a single space.
        4. Remove known filler words and phrases.
        5. Final whitespace collapse and strip.

    Returns an empty string when nothing meaningful remains.
    """
    result = text.lower()
    result = re.sub(r"[^\w\s]", "", result)
    result = re.sub(r"\s+", " ", result).strip()

    for filler in _FILLER_PHRASES:
        result = re.sub(r"\b" + re.escape(filler) + r"\b", "", result)

    result = re.sub(r"\s+", " ", result).strip()
    return result
