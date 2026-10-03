"""Piper ONNX text-to-speech adapter."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import sounddevice as sd
from piper import PiperVoice

logger = logging.getLogger(__name__)


class PiperTextToSpeech:
    """Piper local ONNX TTS engine."""

    def __init__(self, model_path: str | Path, config_path: str | Path) -> None:
        model_path = Path(model_path)
        config_path = Path(config_path)

        if not model_path.exists() or not config_path.exists():
            msg = f"Piper model missing at {model_path}"
            raise FileNotFoundError(msg)

        logger.debug("Loading Piper model: %s", model_path)
        self._voice = PiperVoice.load(str(model_path), str(config_path))
        self._sample_rate = self._voice.config.sample_rate

    def speak(self, text: str) -> None:
        """Synthesize and play *text* synchronously."""
        logger.debug("Piper speaking: %s", text)

        # Synthesize audio stream and play it using sounddevice.
        with sd.OutputStream(samplerate=self._sample_rate, channels=1, dtype="int16") as stream:
            for chunk in self._voice.synthesize(text):
                int_data = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)
                stream.write(int_data)
