"""YAML sidecar configs for each built-in template."""

from __future__ import annotations

from pathlib import Path

_TEMPLATE_DIR = Path(__file__).resolve().parent


def template_dir(name: str) -> Path:
    """Return the directory for a named template package.

    Args:
        name: Template folder name (e.g. ``modern``).

    Returns:
        Absolute path to the template directory.
    """
    return _TEMPLATE_DIR / name
