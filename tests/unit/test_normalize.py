"""Tests for text normalization and filler word stripping."""

import pytest

from atlas.nlu.normalize import normalize_text


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        ("open notepad", "open notepad"),
        ("OPEN NOTEPAD", "open notepad"),
        ("  open   notepad  ", "open notepad"),
        ("open notepad, please!", "open notepad"),
        ("hey, can you open notepad", "open notepad"),
        ("could you please launch chrome", "launch chrome"),
        ("atlas open notepad", "open notepad"),
        ("hey atlas please start calc", "start calc"),
        ("", ""),
        ("   ", ""),
        ("please", ""),
        ("hey can you please", ""),
        ("???!!!", ""),
    ],
)
def test_normalize_text(input_text: str, expected: str) -> None:
    """Ensure filler words, punctuation, casing, and excess whitespace are stripped."""
    assert normalize_text(input_text) == expected
