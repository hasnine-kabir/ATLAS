"""Configuration loading from ``config/atlas.yaml``."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

_DEFAULT_CONFIG_PATH: Path = Path(__file__).resolve().parent.parent.parent / "config" / "atlas.yaml"


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load the full configuration dictionary from *atlas.yaml*.

    Returns an empty dict when the file does not exist or is not a mapping.
    """
    path = config_path or _DEFAULT_CONFIG_PATH
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        return {}
    return cast(dict[str, Any], raw)


def load_app_aliases(config_path: Path | None = None) -> dict[str, str]:
    """Return the ``apps`` alias mapping from config.

    Each key is a spoken name (e.g. ``"notepad"``) and each value is the
    executable or URI protocol to launch (e.g. ``"notepad.exe"``).
    """
    config = load_config(config_path)
    raw_apps = config.get("apps")
    if not isinstance(raw_apps, dict):
        return {}
    return cast(dict[str, str], raw_apps)
