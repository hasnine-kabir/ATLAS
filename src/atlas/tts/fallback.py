"""TTS Manager with fallback support."""

from __future__ import annotations

import logging

from atlas.tts.base import TextToSpeech

logger = logging.getLogger(__name__)


class FallbackTTS:
    """Wraps a primary TTS engine and falls back to a secondary on error."""

    def __init__(self, primary: TextToSpeech, fallback: TextToSpeech) -> None:
        self._primary = primary
        self._fallback = fallback

    def speak(self, text: str) -> None:
        """Try the primary engine; fall back to the secondary if it fails."""
        try:
            self._primary.speak(text)
        except Exception as exc:
            logger.warning(
                "Primary TTS failed (%s), falling back to secondary.",
                exc,
            )
            try:
                self._fallback.speak(text)
            except Exception as fallback_exc:
                logger.error("Fallback TTS also failed: %s", fallback_exc)
