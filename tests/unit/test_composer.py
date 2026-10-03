"""Tests for ResponseComposer."""

import pytest

from atlas.composer import ResponseComposer
from atlas.contracts import ToolResult
from atlas.tts.fake import FakeTextToSpeech


@pytest.fixture
def tts() -> FakeTextToSpeech:
    return FakeTextToSpeech()


def test_composer_speaks_result(tts: FakeTextToSpeech) -> None:
    """It routes ToolResult.say to the TTS engine."""
    composer = ResponseComposer(tts=tts, enabled=True)
    result = ToolResult(ok=True, say="Test speech")

    composer.handle_result(result)

    assert tts.spoken == ["Test speech"]


def test_composer_skips_when_disabled(tts: FakeTextToSpeech) -> None:
    """It does not call the TTS engine when disabled."""
    composer = ResponseComposer(tts=tts, enabled=False)
    result = ToolResult(ok=True, say="Test speech")

    composer.handle_result(result)

    assert tts.spoken == []


def test_composer_skips_empty_say(tts: FakeTextToSpeech) -> None:
    """It does not call TTS if say is empty."""
    composer = ResponseComposer(tts=tts, enabled=True)
    result = ToolResult(ok=True, say="")

    composer.handle_result(result)

    assert tts.spoken == []
