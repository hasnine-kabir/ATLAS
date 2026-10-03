"""Tests for the voice loop app."""

import pytest

from atlas.app import AtlasApp
from atlas.audio.fake import FakeAudioSource
from atlas.composer import ResponseComposer
from atlas.nlu.rules import RulesRouter
from atlas.stt.fake import FakeSpeechToText
from atlas.tools.registry import ToolRegistry
from atlas.tts.fake import FakeTextToSpeech


@pytest.fixture
def source() -> FakeAudioSource:
    return FakeAudioSource()


@pytest.fixture
def stt() -> FakeSpeechToText:
    return FakeSpeechToText()


@pytest.fixture
def router() -> RulesRouter:
    return RulesRouter({"notepad": "notepad.exe"})


@pytest.fixture
def registry() -> ToolRegistry:
    # Use a dummy handler
    from atlas.contracts import ToolResult

    def dummy(args):
        return ToolResult(ok=True, say="Mock opening")

    reg = ToolRegistry()
    reg.register("open_app", dummy)
    return reg


@pytest.fixture
def composer() -> ResponseComposer:
    return ResponseComposer(FakeTextToSpeech())


from atlas.telemetry import FakeTelemetrySink

@pytest.fixture
def telemetry() -> FakeTelemetrySink:
    return FakeTelemetrySink()

@pytest.fixture
def app(source, stt, router, registry, composer, telemetry) -> AtlasApp:
    return AtlasApp(source, stt, router, registry, composer, telemetry)


def test_app_empty_audio_yields_no_action(
    app: AtlasApp, source: FakeAudioSource, stt: FakeSpeechToText, capsys: pytest.CaptureFixture
) -> None:
    source.set_next_audio(b"")

    # Run once should return True (keep running)
    assert app.run_once() is True

    # stdout should say I didn't catch that if stt yielded nothing
    # Wait, if source yields empty bytes, it bails out before STT!
    # "if not audio_bytes: return True"
    out = capsys.readouterr().out
    assert "didn't catch that" not in out


def test_app_stt_empty_yields_no_action(
    app: AtlasApp, source: FakeAudioSource, stt: FakeSpeechToText, capsys: pytest.CaptureFixture
) -> None:
    source.set_next_audio(b"dummy audio")
    stt.set_next_result("")

    assert app.run_once() is True
    out = capsys.readouterr().out
    assert "didn't catch that" in out


def test_app_quit_command(
    app: AtlasApp, source: FakeAudioSource, stt: FakeSpeechToText, capsys: pytest.CaptureFixture
) -> None:
    source.set_next_audio(b"dummy audio")
    stt.set_next_result("quit")

    # Should return False to exit loop
    assert app.run_once() is False
    out = capsys.readouterr().out
    assert "Goodbye." in out


def test_app_valid_command(
    app: AtlasApp, source: FakeAudioSource, stt: FakeSpeechToText, capsys: pytest.CaptureFixture
) -> None:
    source.set_next_audio(b"dummy audio")
    stt.set_next_result("open notepad")

    assert app.run_once() is True
    out = capsys.readouterr().out
    assert "User: open notepad" in out
    assert "ATLAS: Mock opening" in out
