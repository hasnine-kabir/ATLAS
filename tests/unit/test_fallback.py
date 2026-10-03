"""Tests for TTS fallback wrapper."""

import logging

import pytest

from atlas.tts.fake import FakeTextToSpeech
from atlas.tts.fallback import FallbackTTS


@pytest.fixture
def primary() -> FakeTextToSpeech:
    return FakeTextToSpeech()


@pytest.fixture
def secondary() -> FakeTextToSpeech:
    return FakeTextToSpeech()


@pytest.fixture
def fallback_tts(primary: FakeTextToSpeech, secondary: FakeTextToSpeech) -> FallbackTTS:
    return FallbackTTS(primary, secondary)


def test_fallback_uses_primary_when_successful(
    fallback_tts: FallbackTTS,
    primary: FakeTextToSpeech,
    secondary: FakeTextToSpeech,
) -> None:
    """It routes speech to the primary engine and does not use fallback."""
    fallback_tts.speak("Hello")
    assert primary.spoken == ["Hello"]
    assert secondary.spoken == []


def test_fallback_uses_secondary_when_primary_fails(
    fallback_tts: FallbackTTS,
    primary: FakeTextToSpeech,
    secondary: FakeTextToSpeech,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """It routes speech to the secondary engine and logs a warning if primary fails."""
    primary.set_fail(True)

    with caplog.at_level(logging.WARNING):
        fallback_tts.speak("Hello")

    assert primary.spoken == []
    assert secondary.spoken == ["Hello"]
    assert "Primary TTS failed" in caplog.text


def test_fallback_swallows_secondary_failure(
    fallback_tts: FallbackTTS,
    primary: FakeTextToSpeech,
    secondary: FakeTextToSpeech,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """It logs an error but does not crash if both engines fail."""
    primary.set_fail(True)
    secondary.set_fail(True)

    with caplog.at_level(logging.ERROR):
        fallback_tts.speak("Hello")

    assert primary.spoken == []
    assert secondary.spoken == []
    assert "Fallback TTS also failed" in caplog.text
