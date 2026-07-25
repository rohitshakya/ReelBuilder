"""Pydantic models for project configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Self

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from reelforge.models.enums import (
    KenBurnsMovement,
    Preset,
    TemplateName,
    TransitionType,
)


class VideoConfig(BaseModel):
    """Output video dimensions and encoding settings."""

    width: int = Field(default=1080, ge=240, le=7680)
    height: int = Field(default=1920, ge=240, le=7680)
    fps: int = Field(default=30, ge=1, le=120)
    codec: str = Field(default="libx264")
    pixel_format: str = Field(default="yuv420p")
    crf: int = Field(default=18, ge=0, le=51)
    preset: str = Field(default="medium")
    hardware_accel: bool = Field(
        default=True,
        description="Use hardware-accelerated encoding when available.",
    )

    @property
    def size(self) -> tuple[int, int]:
        """Return (width, height) tuple."""
        return self.width, self.height

    @property
    def aspect_ratio(self) -> float:
        """Return width / height."""
        return self.width / self.height


class AnimationConfig(BaseModel):
    """Ken Burns / motion settings applied per slide."""

    type: str = Field(default="kenburns")
    movement: KenBurnsMovement = Field(default=KenBurnsMovement.RANDOM)
    duration: float = Field(default=3.0, gt=0.1, le=60.0)
    zoom_factor: float = Field(
        default=1.15,
        ge=1.0,
        le=2.0,
        description="Maximum zoom scale for Ken Burns.",
    )
    easing: str = Field(default="ease_in_out")


class TransitionConfig(BaseModel):
    """Inter-slide transition settings."""

    type: TransitionType = Field(default=TransitionType.CROSSFADE)
    duration: float = Field(default=0.5, ge=0.0, le=5.0)


class AudioConfig(BaseModel):
    """Background music and audio mix settings."""

    path: Path | None = None
    volume: float = Field(default=0.7, ge=0.0, le=2.0)
    fade_in: float = Field(default=1.0, ge=0.0, le=30.0)
    fade_out: float = Field(default=2.0, ge=0.0, le=30.0)
    auto_trim: bool = Field(
        default=True,
        description="Trim or loop music to match video duration.",
    )
    loop: bool = Field(default=True)

    @field_validator("path", mode="before")
    @classmethod
    def _coerce_path(cls, value: Any) -> Path | None:
        if value is None or value == "":
            return None
        return Path(value)


class WatermarkConfig(BaseModel):
    """Logo watermark overlay settings."""

    path: Path | None = None
    opacity: float = Field(default=0.7, ge=0.0, le=1.0)
    scale: float = Field(
        default=0.12,
        gt=0.0,
        le=0.5,
        description="Watermark width as fraction of video width.",
    )
    margin: int = Field(default=40, ge=0)
    position: str = Field(
        default="bottom_right",
        description=("One of: top_left, top_right, bottom_left, bottom_right, center."),
    )

    @field_validator("path", mode="before")
    @classmethod
    def _coerce_path(cls, value: Any) -> Path | None:
        if value is None or value == "":
            return None
        return Path(value)


class ProgressBarConfig(BaseModel):
    """On-screen progress indicator settings."""

    enabled: bool = True
    height: int = Field(default=6, ge=1, le=40)
    color: str = Field(default="#FFFFFF")
    background_color: str = Field(default="#00000080")
    position: str = Field(default="bottom")
    show_counter: bool = Field(
        default=True,
        description="Show 'Slide N / Total' text overlay.",
    )


class ProjectConfig(BaseModel):
    """Root configuration for a ReelForge render job."""

    video: VideoConfig = Field(default_factory=VideoConfig)
    animation: AnimationConfig = Field(default_factory=AnimationConfig)
    transition: TransitionConfig = Field(default_factory=TransitionConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    watermark: WatermarkConfig = Field(default_factory=WatermarkConfig)
    progress_bar: ProgressBarConfig = Field(default_factory=ProgressBarConfig)
    template: TemplateName = Field(default=TemplateName.MODERN)
    export_preset: Preset = Field(
        default=Preset.CUSTOM,
        description="Platform preset. Non-custom values force 1080×1920@30.",
    )
    images_dir: Path | None = None
    output: Path = Field(default=Path("reel.mp4"))
    cache_dir: Path = Field(default=Path(".reelforge_cache"))
    workers: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Thread pool size for image preprocessing.",
    )
    seed: int | None = Field(
        default=None,
        description="RNG seed for reproducible random movements/transitions.",
    )

    @field_validator("images_dir", "output", "cache_dir", mode="before")
    @classmethod
    def _coerce_paths(cls, value: Any) -> Path | None:
        if value is None or value == "":
            return None
        return Path(value)

    @model_validator(mode="after")
    def _apply_export_preset(self) -> Self:
        """Override dimensions when a platform preset is selected."""
        if self.export_preset == Preset.CUSTOM:
            return self
        presets: dict[Preset, tuple[int, int, int]] = {
            Preset.INSTAGRAM: (1080, 1920, 30),
            Preset.YOUTUBE_SHORTS: (1080, 1920, 30),
            Preset.TIKTOK: (1080, 1920, 30),
        }
        if self.export_preset in presets:
            w, h, fps = presets[self.export_preset]
            self.video.width = w
            self.video.height = h
            self.video.fps = fps
        return self

    @classmethod
    def from_yaml(cls, path: Path | str) -> ProjectConfig:
        """Load configuration from a YAML file.

        Args:
            path: Path to a YAML configuration file.

        Returns:
            Parsed ProjectConfig instance.

        Raises:
            FileNotFoundError: If the path does not exist.
            ValueError: If the YAML is invalid or empty.
        """
        config_path = Path(path)
        if not config_path.is_file():
            msg = f"Config file not found: {config_path}"
            raise FileNotFoundError(msg)

        with config_path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)

        if raw is None:
            return cls()
        if not isinstance(raw, dict):
            msg = f"Config root must be a mapping, got {type(raw).__name__}"
            raise ValueError(msg)
        return cls.model_validate(raw)

    def to_yaml(self, path: Path | str) -> None:
        """Write configuration to a YAML file.

        Args:
            path: Destination path for the YAML file.
        """
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        data = self.model_dump(mode="json")
        with out.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, default_flow_style=False, sort_keys=False)

    def merge_cli_overrides(self, **overrides: Any) -> ProjectConfig:
        """Return a copy with non-None CLI overrides applied.

        Args:
            **overrides: Field names mapped to override values.

        Returns:
            New ProjectConfig with overrides merged in.
        """
        data = self.model_dump(mode="python")
        for key, value in overrides.items():
            if value is None:
                continue
            if key == "music":
                data.setdefault("audio", {})["path"] = value
            elif key == "images":
                data["images_dir"] = value
            elif key in data:
                data[key] = value
            elif "." in key:
                # Nested override like "animation.duration"
                parts = key.split(".")
                cursor: dict[str, Any] = data
                for part in parts[:-1]:
                    cursor = cursor.setdefault(part, {})
                cursor[parts[-1]] = value
        return ProjectConfig.model_validate(data)
