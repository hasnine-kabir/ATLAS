"""Main application voice loop."""

from __future__ import annotations

import logging
import time

from atlas.audio.base import AudioSource
from atlas.composer import ResponseComposer
from atlas.nlu.rules import RulesRouter
from atlas.stt.base import SpeechToText
from atlas.telemetry import PerformanceMetrics, TelemetrySink
from atlas.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class AtlasApp:
    """The central application loop for ATLAS."""

    def __init__(
        self,
        audio_source: AudioSource,
        stt: SpeechToText,
        router: RulesRouter,
        registry: ToolRegistry,
        composer: ResponseComposer,
        telemetry: TelemetrySink,
        vocabulary_hint: list[str] | None = None,
    ) -> None:
        self._source = audio_source
        self._stt = stt
        self._router = router
        self._registry = registry
        self._composer = composer
        self._telemetry = telemetry
        self._vocabulary = vocabulary_hint or []

    def run_once(self) -> bool:
        """Run one full iteration of the PTT voice loop.

        Returns False if the user asked to quit.
        """
        t_start_total = time.perf_counter()

        # 1. Capture audio
        t0 = time.perf_counter()
        audio_bytes = self._source.record_until_released(sample_rate=16000)
        audio_ms = (time.perf_counter() - t0) * 1000.0
        
        if not audio_bytes:
            return True

        # 2. Transcribe
        t0 = time.perf_counter()
        transcript = self._stt.transcribe(
            audio_bytes,
            sample_rate=16000,
            vocabulary_hint=self._vocabulary,
        )
        stt_ms = (time.perf_counter() - t0) * 1000.0

        if not transcript:
            logger.info("Empty transcript. No action.")
            print("I didn't catch that.")
            return True

        print(f"\nUser: {transcript} (stt: {stt_ms:.2f}ms)")
        
        # Check hardcoded exit command
        if transcript.lower().strip() in ("exit", "quit"):
            print("Goodbye.")
            return False

        # 3. Route
        t0 = time.perf_counter()
        intent = self._router.route(transcript)
        nlu_ms = (time.perf_counter() - t0) * 1000.0

        if intent is None:
            logger.info("Unrecognized command: %s", transcript)
            msg = "I'm not sure what you mean."
            print(f"ATLAS: {msg}")
            self._emit_telemetry(audio_ms, stt_ms, nlu_ms, 0.0, 0.0, t_start_total, len(transcript), "unknown")
            return True

        # 4. Execute
        t0 = time.perf_counter()
        result = self._registry.execute(intent)
        tool_ms = (time.perf_counter() - t0) * 1000.0

        print(f"ATLAS: {result.say}")

        # 5. Speak
        t0 = time.perf_counter()
        self._composer.handle_result(result)
        tts_ms = (time.perf_counter() - t0) * 1000.0

        self._emit_telemetry(audio_ms, stt_ms, nlu_ms, tool_ms, tts_ms, t_start_total, len(transcript), intent.tool)
        return True

    def _emit_telemetry(
        self,
        audio_ms: float,
        stt_ms: float,
        nlu_ms: float,
        tool_ms: float,
        tts_ms: float,
        t_start_total: float,
        transcript_length: int,
        intent_tool: str,
    ) -> None:
        total_ms = (time.perf_counter() - t_start_total) * 1000.0
        metrics = PerformanceMetrics(
            audio_ms=audio_ms,
            stt_ms=stt_ms,
            nlu_ms=nlu_ms,
            tool_ms=tool_ms,
            tts_ms=tts_ms,
            total_ms=total_ms,
            transcript_length=transcript_length,
            intent=intent_tool,
        )
        self._telemetry.record_performance(metrics)

    def run_loop(self) -> None:
        """Run the voice loop indefinitely."""
        print("ATLAS is ready. Press and hold your PTT hotkey to speak.\n")
        running = True
        while running:
            try:
                running = self.run_once()
            except KeyboardInterrupt:
                print("\nGoodbye.")
                break
            except Exception as exc:
                logger.exception("Error in voice loop: %s", exc)
