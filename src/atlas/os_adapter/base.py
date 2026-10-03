"""Abstract port for operating system interactions.

Concrete adapters (``WindowsOSAdapter``, ``FakeOSAdapter``) implement this
protocol so that core logic never touches the OS directly.
"""

from __future__ import annotations

from typing import Protocol


class OSAdapter(Protocol):
    """Port for operating system interactions."""

    def launch_app(self, target: str) -> None:
        """Launch an application by executable name, path, or URI protocol."""
        ...
