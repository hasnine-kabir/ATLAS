"""Fake TTS engine for tests."""

from __future__ import annotations


class FakeTextToSpeech:
    """Records spoken text instead of playing audio."""

    def __init__(self) -> None:
        self.spoken: list[str] = []
        self._should_fail = False

    def set_fail(self, fail: bool = True) -> None:
        """Configure the fake to raise an exception on next speak."""
        self._should_fail = fail

    def speak(self, text: str) -> None:
        """Record *text*, raising if configured to fail."""
        if self._should_fail:
            raise RuntimeError("Fake TTS failure")
        self.spoken.append(text)
