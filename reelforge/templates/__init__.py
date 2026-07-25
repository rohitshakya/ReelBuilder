"""Built-in visual templates."""

from __future__ import annotations

from typing import Any

from reelforge.models.config import (
    AnimationConfig,
    ProgressBarConfig,
    ProjectConfig,
    TransitionConfig,
)
from reelforge.models.enums import KenBurnsMovement, TemplateName, TransitionType

# Template definitions: each controls fonts, colors, transitions, animation.
_TEMPLATES: dict[TemplateName, dict[str, Any]] = {
    TemplateName.MINIMAL: {
        "description": "Clean and restrained — soft fades, gentle zoom.",
        "animation": AnimationConfig(
            movement=KenBurnsMovement.ZOOM_IN,
            duration=3.5,
            zoom_factor=1.08,
        ),
        "transition": TransitionConfig(type=TransitionType.FADE, duration=0.6),
        "progress_bar": ProgressBarConfig(
            enabled=True,
            height=4,
            color="#FFFFFF",
            background_color="#00000040",
            show_counter=False,
        ),
        "fonts": {"title": "Helvetica", "body": "Helvetica"},
        "colors": {"accent": "#FFFFFF", "background": "#000000"},
    },
    TemplateName.MODERN: {
        "description": "Bold CapCut-style energy — random Ken Burns + crossfades.",
        "animation": AnimationConfig(
            movement=KenBurnsMovement.RANDOM,
            duration=3.0,
            zoom_factor=1.15,
        ),
        "transition": TransitionConfig(type=TransitionType.CROSSFADE, duration=0.45),
        "progress_bar": ProgressBarConfig(
            enabled=True,
            height=6,
            color="#FF2D55",
            background_color="#00000080",
            show_counter=True,
        ),
        "fonts": {"title": "Montserrat", "body": "Inter"},
        "colors": {"accent": "#FF2D55", "background": "#0A0A0A"},
    },
    TemplateName.DOCUMENTARY: {
        "description": "Slow pans and long fades for storytelling.",
        "animation": AnimationConfig(
            movement=KenBurnsMovement.PAN_RIGHT,
            duration=4.5,
            zoom_factor=1.10,
        ),
        "transition": TransitionConfig(type=TransitionType.FADE, duration=1.0),
        "progress_bar": ProgressBarConfig(
            enabled=True,
            height=3,
            color="#E8DCC8",
            background_color="#00000060",
            show_counter=True,
        ),
        "fonts": {"title": "Georgia", "body": "Georgia"},
        "colors": {"accent": "#E8DCC8", "background": "#1A1A1A"},
    },
    TemplateName.DARK: {
        "description": "High-contrast dark theme with zoom transitions.",
        "animation": AnimationConfig(
            movement=KenBurnsMovement.ZOOM_IN,
            duration=2.8,
            zoom_factor=1.20,
        ),
        "transition": TransitionConfig(type=TransitionType.ZOOM, duration=0.5),
        "progress_bar": ProgressBarConfig(
            enabled=True,
            height=5,
            color="#00E5FF",
            background_color="#111111CC",
            show_counter=True,
        ),
        "fonts": {"title": "Space Grotesk", "body": "IBM Plex Sans"},
        "colors": {"accent": "#00E5FF", "background": "#050505"},
    },
    TemplateName.TECH: {
        "description": "Snappy cuts and push transitions for product demos.",
        "animation": AnimationConfig(
            movement=KenBurnsMovement.ZOOM_OUT,
            duration=2.5,
            zoom_factor=1.12,
        ),
        "transition": TransitionConfig(type=TransitionType.PUSH, duration=0.35),
        "progress_bar": ProgressBarConfig(
            enabled=True,
            height=6,
            color="#7CFF6B",
            background_color="#0D1117CC",
            show_counter=True,
        ),
        "fonts": {"title": "JetBrains Mono", "body": "IBM Plex Sans"},
        "colors": {"accent": "#7CFF6B", "background": "#0D1117"},
    },
    TemplateName.EDUCATION: {
        "description": "Clear pacing with slides — ideal for lessons.",
        "animation": AnimationConfig(
            movement=KenBurnsMovement.PAN_DOWN,
            duration=4.0,
            zoom_factor=1.08,
        ),
        "transition": TransitionConfig(type=TransitionType.SLIDE, duration=0.5),
        "progress_bar": ProgressBarConfig(
            enabled=True,
            height=8,
            color="#4C6EF5",
            background_color="#E9ECEFCC",
            show_counter=True,
        ),
        "fonts": {"title": "Nunito", "body": "Nunito"},
        "colors": {"accent": "#4C6EF5", "background": "#F8F9FA"},
    },
}


def list_templates() -> list[dict[str, str]]:
    """Return summary info for all built-in templates.

    Returns:
        List of dicts with ``name`` and ``description`` keys.
    """
    return [
        {"name": name.value, "description": meta["description"]}
        for name, meta in _TEMPLATES.items()
    ]


def get_template(name: TemplateName | str) -> dict[str, Any]:
    """Fetch a template definition.

    Args:
        name: Template name enum or string.

    Returns:
        Template metadata dict.

    Raises:
        KeyError: If the template does not exist.
    """
    key = TemplateName(name) if isinstance(name, str) else name
    if key not in _TEMPLATES:
        msg = f"Unknown template: {name}"
        raise KeyError(msg)
    return _TEMPLATES[key]


def apply_template(config: ProjectConfig, name: TemplateName | str) -> ProjectConfig:
    """Return a config copy with template defaults applied.

    Args:
        config: Base project configuration.
        name: Template to apply.

    Returns:
        New ProjectConfig with animation/transition/progress overrides.
    """
    meta = get_template(name)
    data = config.model_dump(mode="python")
    data["template"] = TemplateName(name) if isinstance(name, str) else name
    data["animation"] = meta["animation"].model_dump(mode="python")
    data["transition"] = meta["transition"].model_dump(mode="python")
    data["progress_bar"] = meta["progress_bar"].model_dump(mode="python")
    return ProjectConfig.model_validate(data)
