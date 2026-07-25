"""Logging helpers for ReelForge."""

from __future__ import annotations

import logging
import sys
from typing import TextIO


def setup_logging(
    level: int = logging.INFO,
    stream: TextIO | None = None,
    *,
    verbose: bool = False,
) -> None:
    """Configure the root logger for CLI usage.

    Args:
        level: Base logging level.
        stream: Output stream (defaults to stderr).
        verbose: If True, force DEBUG level.
    """
    if verbose:
        level = logging.DEBUG

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    root = logging.getLogger("reelforge")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the reelforge namespace.

    Args:
        name: Module or component name (e.g. ``renderer.ffmpeg``).

    Returns:
        Configured logger instance.
    """
    if name.startswith("reelforge."):
        return logging.getLogger(name)
    return logging.getLogger(f"reelforge.{name}")
