"""Fake audio source for testing."""

from __future__ import annotations


class FakeAudioSource:
    """Returns pre-recorded bytes instead of capturing from a mic."""

    def __init__(self) -> None:
        self._next_audio = b""

    def set_next_audio(self, audio: bytes) -> None:
        """Set the audio bytes to return on next capture."""
        self._next_audio = audio

    def record_until_released(self, sample_rate: int = 16000) -> bytes:
        """Return the mocked audio bytes."""
        return self._next_audio
