"""Faster-whisper STT adapter."""

from __future__ import annotations

import logging

import numpy as np
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class FasterWhisperSTT:
    """Local STT engine using faster-whisper."""

    def __init__(
        self, model_size: str = "base.en", device: str = "cpu", compute_type: str = "int8"
    ) -> None:
        logger.debug(
            "Loading faster-whisper model '%s' on %s (%s)", model_size, device, compute_type
        )
        self._model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(
        self,
        audio_data: bytes,
        sample_rate: int,
        vocabulary_hint: list[str] | None = None,
    ) -> str:
        """Transcribe PCM int16 audio data."""
        if not audio_data:
            return ""

        # Convert 16-bit PCM bytes to float32 array in [-1.0, 1.0] expected by Whisper
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Optional vocabulary hint
        initial_prompt = ""
        if vocabulary_hint:
            initial_prompt = ", ".join(vocabulary_hint)

        logger.debug("Transcribing %d bytes of audio...", len(audio_data))
        segments, info = self._model.transcribe(
            audio_np,
            beam_size=1,  # Fast greedy decoding
            language="en",
            initial_prompt=initial_prompt,
            vad_filter=True,  # Helps filter out pure noise
        )

        text = " ".join(segment.text for segment in segments).strip()
        logger.debug("Transcript: '%s' (no_speech_prob: %.2f)", text, info.no_speech_prob)
        return text
