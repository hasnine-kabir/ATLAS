"""Abstract port for Text-to-Speech engines."""

from __future__ import annotations

from typing import Protocol


class TextToSpeech(Protocol):
    """Port for text-to-speech synthesis and playback."""

    def speak(self, text: str) -> None:
        """Synthesize and play *text*. Blocks until playback completes."""
        ...
