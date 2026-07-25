"""Enumerations used across ReelForge configuration and rendering."""

from __future__ import annotations

from enum import StrEnum


class KenBurnsMovement(StrEnum):
    """Supported Ken Burns camera movements."""

    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    PAN_UP = "pan_up"
    PAN_DOWN = "pan_down"
    RANDOM = "random"


class TransitionType(StrEnum):
    """Supported inter-slide transitions."""

    FADE = "fade"
    CROSSFADE = "crossfade"
    SLIDE = "slide"
    PUSH = "push"
    ZOOM = "zoom"
    RANDOM = "random"
    NONE = "none"


class TemplateName(StrEnum):
    """Built-in visual templates."""

    MINIMAL = "minimal"
    MODERN = "modern"
    DOCUMENTARY = "documentary"
    DARK = "dark"
    TECH = "tech"
    EDUCATION = "education"


class Preset(StrEnum):
    """Export presets for popular vertical platforms."""

    INSTAGRAM = "instagram"
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    CUSTOM = "custom"


class ImageOrientation(StrEnum):
    """Detected image orientation relative to the output canvas."""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE = "square"
