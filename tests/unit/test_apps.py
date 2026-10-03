"""Tests for the app launcher tool handler."""

from typing import Any

import pytest

from atlas.os_adapter.fake import FakeOSAdapter
from atlas.tools.apps import make_open_app_handler


@pytest.fixture
def adapter() -> FakeOSAdapter:
    return FakeOSAdapter()


@pytest.fixture
def handler(adapter: FakeOSAdapter) -> Any:
    return make_open_app_handler(adapter)


def test_open_app_success(handler: Any, adapter: FakeOSAdapter) -> None:
    """It launches the target and returns a success result."""
    result = handler({"app": "notepad", "target": "notepad.exe"})
    assert result.ok is True
    assert result.say == "Opening Notepad."
    assert "notepad.exe" in adapter.launched


def test_open_app_missing_target(handler: Any, adapter: FakeOSAdapter) -> None:
    """It returns an error result if the target alias is missing."""
    result = handler({"app": "flarbnitz"})
    assert result.ok is False
    assert "couldn't find" in result.say
    assert "flarbnitz" in result.say
    assert not adapter.launched


def test_open_app_adapter_error(handler: Any, adapter: FakeOSAdapter) -> None:
    """It catches adapter exceptions and returns a graceful failure result."""
    adapter.set_fail_on("broken.exe")
    result = handler({"app": "broken app", "target": "broken.exe"})
    assert result.ok is False
    assert "went wrong" in result.say
    assert "broken app" in result.say
