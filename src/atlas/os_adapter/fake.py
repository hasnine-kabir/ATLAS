"""Fake OS adapter for deterministic testing.

Records every OS call instead of executing it, and can be configured
to simulate failures for specific targets.
"""

from __future__ import annotations


class FakeOSAdapter:
    """Records OS calls instead of executing them."""

    def __init__(self) -> None:
        self.launched: list[str] = []
        self._fail_on: set[str] = set()

    def set_fail_on(self, target: str) -> None:
        """Configure ``launch_app`` to raise ``OSError`` for *target*."""
        self._fail_on.add(target)

    def launch_app(self, target: str) -> None:
        """Record the launch; raise if configured to fail."""
        if target in self._fail_on:
            msg = f"Failed to launch {target}"
            raise OSError(msg)
        self.launched.append(target)
