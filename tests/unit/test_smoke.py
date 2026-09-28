import pytest

from atlas import __version__
from atlas.__main__ import build_parser, main


def test_version_string_defined() -> None:
    """Verify package version is properly defined."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0
    assert __version__ == "0.1.0"


def test_parser_has_version_flag() -> None:
    """Verify CLI parser exposes the --version flag."""
    parser = build_parser()
    actions = [action.dest for action in parser._actions]
    assert "version" in actions


def test_main_version_flag_exits_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify py -3.11 -m atlas --version outputs version and exits cleanly."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert f"atlas {__version__}" in captured.out or f"atlas {__version__}" in captured.err


def test_main_default_execution(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify default execution prints ready status and returns 0."""
    code = main([])
    assert code == 0
    captured = capsys.readouterr()
    assert f"ATLAS v{__version__} — ready." in captured.out
