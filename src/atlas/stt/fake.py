"""Fake STT engine for tests."""

from __future__ import annotations


class FakeSpeechToText:
    """Returns predetermined transcriptions instead of processing audio."""

    def __init__(self) -> None:
        self.transcriptions: list[str] = []
        self._next_result: str = ""

    def set_next_result(self, text: str) -> None:
        """Set the text to return on the next transcribe call."""
        self._next_result = text

    def transcribe(
        self,
        audio_data: bytes,
        sample_rate: int,
        vocabulary_hint: list[str] | None = None,
    ) -> str:
        """Return the pre-configured string."""
        self.transcriptions.append(self._next_result)
        return self._next_result
