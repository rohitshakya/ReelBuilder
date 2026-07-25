"""Unit tests for configuration models."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from reelforge.models.config import ProjectConfig, VideoConfig
from reelforge.models.enums import Preset, TemplateName


def test_default_video_is_vertical_hd() -> None:
    video = VideoConfig()
    assert video.width == 1080
    assert video.height == 1920
    assert video.fps == 30
    assert video.size == (1080, 1920)


def test_project_config_from_yaml(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(
        yaml.dump(
            {
                "video": {"width": 1080, "height": 1920, "fps": 24},
                "animation": {"duration": 2.5, "movement": "zoom_in"},
                "transition": {"type": "fade", "duration": 0.3},
                "template": "minimal",
            }
        ),
        encoding="utf-8",
    )
    cfg = ProjectConfig.from_yaml(path)
    assert cfg.video.fps == 24
    assert cfg.animation.duration == 2.5
    assert cfg.template == TemplateName.MINIMAL


def test_from_yaml_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        ProjectConfig.from_yaml("/nonexistent/config.yaml")


def test_export_preset_forces_dimensions() -> None:
    cfg = ProjectConfig(
        video=VideoConfig(width=720, height=1280, fps=60),
        export_preset=Preset.TIKTOK,
    )
    assert cfg.video.width == 1080
    assert cfg.video.height == 1920
    assert cfg.video.fps == 30


def test_merge_cli_overrides() -> None:
    cfg = ProjectConfig()
    merged = cfg.merge_cli_overrides(
        images=Path("./slides"),
        music=Path("song.mp3"),
        output=Path("out.mp4"),
    )
    assert merged.images_dir == Path("./slides")
    assert merged.audio.path == Path("song.mp3")
    assert merged.output == Path("out.mp4")


def test_to_yaml_roundtrip(tmp_path: Path) -> None:
    cfg = ProjectConfig(animation={"duration": 4.0})  # type: ignore[arg-type]
    out = tmp_path / "out.yaml"
    cfg.to_yaml(out)
    loaded = ProjectConfig.from_yaml(out)
    assert loaded.animation.duration == 4.0
