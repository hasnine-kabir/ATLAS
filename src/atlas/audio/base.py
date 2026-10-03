"""Abstract port for Audio capture."""

from __future__ import annotations

from typing import Protocol


class AudioSource(Protocol):
    """Port for audio capture."""

    def record_until_released(self, sample_rate: int = 16000) -> bytes:
        """Record audio until a stopping condition is met. Return PCM bytes."""
        ...
