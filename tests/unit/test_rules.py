"""Tests for fast-path rule-based intent routing."""

import pytest

from atlas.nlu.rules import RulesRouter


@pytest.fixture
def router() -> RulesRouter:
    aliases = {
        "notepad": "notepad.exe",
        "browser": "chrome.exe",
        "calc": "calc.exe",
        "code": "code.cmd",
    }
    return RulesRouter(app_aliases=aliases)


@pytest.mark.parametrize(
    "utterance",
    [
        "open notepad",
        "launch notepad",
        "start notepad please",
        "hey can you open Notepad",
        "atlas, please launch notepad",
    ],
)
def test_open_notepad_variants_resolve_to_open_app(router: RulesRouter, utterance: str) -> None:
    """Verify all natural variants resolve to open_app with app='notepad'."""
    intent = router.route(utterance)
    assert intent is not None
    assert intent.tool == "open_app"
    assert intent.args.get("app") == "notepad"
    assert intent.source == "rule"
    assert intent.confidence == 1.0


def test_alias_resolution(router: RulesRouter) -> None:
    """Verify configured aliases are recognized."""
    intent = router.route("open browser")
    assert intent is not None
    assert intent.tool == "open_app"
    assert intent.args.get("app") == "browser"
    assert intent.args.get("target") == "chrome.exe"


def test_unknown_command_returns_none(router: RulesRouter) -> None:
    """Non-matching commands return None to allow LLM fallback."""
    assert router.route("why is the sky blue") is None
    assert router.route("what time is it") is None


def test_empty_input_returns_none(router: RulesRouter) -> None:
    """Empty or filler-only input returns None."""
    assert router.route("") is None
    assert router.route("   ") is None
    assert router.route("please hey") is None
