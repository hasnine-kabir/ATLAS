"""Windows 11 OS adapter using native APIs.

This adapter is the real implementation used at runtime.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


class WindowsOSAdapter:
    """Concrete OS adapter for Windows 11."""

    def launch_app(self, target: str) -> None:
        """Launch *target* via ``os.startfile`` (executables, folders, URIs)."""
        logger.info("Launching: %s", target)
        os.startfile(target)
