"""SAPI text-to-speech adapter using pyttsx3."""

from __future__ import annotations

import logging

import pyttsx3

logger = logging.getLogger(__name__)


class SAPITextToSpeech:
    """Windows SAPI TTS engine."""

    def __init__(self, rate: float = 1.0) -> None:
        self._engine = pyttsx3.init()
        # Scale default rate (usually 200 wpm) by the config multiplier.
        default_rate = self._engine.getProperty("rate")
        self._engine.setProperty("rate", int(default_rate * rate))

    def speak(self, text: str) -> None:
        """Synthesize and play *text* synchronously."""
        logger.debug("SAPI speaking: %s", text)
        self._engine.say(text)
        self._engine.runAndWait()
