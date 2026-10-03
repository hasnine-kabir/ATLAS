"""Push-to-talk microphone capture."""

from __future__ import annotations

import logging
import queue
import time
from typing import Any

import keyboard
import sounddevice as sd

logger = logging.getLogger(__name__)


class PushToTalkSource:
    """Captures microphone audio while a hotkey is held down."""

    def __init__(self, hotkey: str = "ctrl+space") -> None:
        self.hotkey = hotkey

    def record_until_released(self, sample_rate: int = 16000) -> bytes:
        """Block until hotkey is pressed, record audio, stop on release.

        Returns PCM int16 bytes.
        """
        logger.info("Press and hold '%s' to speak...", self.hotkey)

        # Block until the hotkey is pressed
        keyboard.wait(self.hotkey)
        logger.info("Recording started. Release '%s' to stop.", self.hotkey)

        q: queue.Queue[bytes] = queue.Queue()

        def _callback(indata: Any, frames: int, time_info: Any, status: Any) -> None:
            if status:
                logger.warning("Audio status: %s", status)
            q.put(bytes(indata))

        # Start recording stream
        stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            callback=_callback,
        )

        with stream:
            # Poll while the hotkey is held down
            while keyboard.is_pressed(self.hotkey):
                time.sleep(0.05)

        logger.info("Recording stopped.")

        # Drain the queue
        chunks: list[bytes] = []
        while not q.empty():
            chunks.append(q.get_nowait())

        return b"".join(chunks)
