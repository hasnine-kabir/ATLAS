"""Response composer for routing ToolResult speech to TTS."""

from __future__ import annotations

import logging

from atlas.contracts import ToolResult
from atlas.tts.base import TextToSpeech

logger = logging.getLogger(__name__)


class ResponseComposer:
    """Manages playing the spoken portion of a ToolResult."""

    def __init__(self, tts: TextToSpeech, enabled: bool = True) -> None:
        self._tts = tts
        self._enabled = enabled

    def handle_result(self, result: ToolResult) -> None:
        """Route the result's spoken text to TTS if enabled."""
        if not result.say:
            return

        if self._enabled:
            logger.debug("Speaking: %s", result.say)
            self._tts.speak(result.say)
        else:
            logger.debug("TTS disabled, skipping speech: %s", result.say)
