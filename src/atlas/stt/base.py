"""Abstract port for Speech-to-Text engines."""

from __future__ import annotations

from typing import Protocol


class SpeechToText(Protocol):
    """Port for speech recognition."""

    def transcribe(
        self, audio_data: bytes, sample_rate: int, vocabulary_hint: list[str] | None = None
    ) -> str:
        """Transcribe PCM *audio_data* and return the recognized text."""
        ...
