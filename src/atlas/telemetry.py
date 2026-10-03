"""Telemetry and performance tracking."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PerformanceMetrics:
    """Records the duration (in milliseconds) of each pipeline phase."""

    audio_ms: float
    stt_ms: float
    nlu_ms: float
    tool_ms: float
    tts_ms: float
    total_ms: float
    transcript_length: int
    intent: str


class TelemetrySink(Protocol):
    """Port for recording telemetry events."""

    def record_performance(self, metrics: PerformanceMetrics) -> None:
        """Record a pipeline execution metric."""
        ...


class JSONTelemetrySink:
    """Appends performance metrics as JSON lines to a file."""

    def __init__(self, log_path: str | Path) -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record_performance(self, metrics: PerformanceMetrics) -> None:
        """Append the metrics dict to the JSONL file."""
        data = {
            "audio_ms": round(metrics.audio_ms, 2),
            "stt_ms": round(metrics.stt_ms, 2),
            "nlu_ms": round(metrics.nlu_ms, 2),
            "tool_ms": round(metrics.tool_ms, 2),
            "tts_ms": round(metrics.tts_ms, 2),
            "total_ms": round(metrics.total_ms, 2),
            "transcript_length": metrics.transcript_length,
            "intent": metrics.intent,
        }
        
        # Also log at INFO level so we can see it in standard output
        logger.info("Telemetry: %s", json.dumps(data))

        try:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
        except OSError as exc:
            logger.error("Failed to write telemetry: %s", exc)


class FakeTelemetrySink:
    """Records metrics in memory for testing."""

    def __init__(self) -> None:
        self.metrics: list[PerformanceMetrics] = []

    def record_performance(self, metrics: PerformanceMetrics) -> None:
        """Store the metrics."""
        self.metrics.append(metrics)
