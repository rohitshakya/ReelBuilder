"""Integration test for a tiny end-to-end render (requires FFmpeg)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from PIL import Image

from reelforge.models.config import (
    AnimationConfig,
    ProjectConfig,
    TransitionConfig,
    VideoConfig,
)
from reelforge.models.enums import KenBurnsMovement, TransitionType
from reelforge.renderer.pipeline import RenderPipeline

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None,
    reason="FFmpeg not installed",
)


def _make_slides(folder: Path, count: int = 3) -> None:
    colors = [(220, 60, 60), (60, 180, 80), (60, 100, 220)]
    for i in range(count):
        img = Image.new("RGB", (640, 480), color=colors[i % len(colors)])
        img.save(folder / f"{i + 1:03d}.png")


def test_render_tiny_reel(tmp_path: Path) -> None:
    slides = tmp_path / "slides"
    slides.mkdir()
    _make_slides(slides, 3)
    out = tmp_path / "out.mp4"
    cache = tmp_path / "cache"

    cfg = ProjectConfig(
        video=VideoConfig(width=240, height=426, fps=10, hardware_accel=False),
        animation=AnimationConfig(
            movement=KenBurnsMovement.ZOOM_IN,
            duration=0.4,
            zoom_factor=1.1,
        ),
        transition=TransitionConfig(type=TransitionType.CROSSFADE, duration=0.1),
        images_dir=slides,
        output=out,
        cache_dir=cache,
        workers=2,
        seed=1,
    )
    cfg.progress_bar.enabled = True
    cfg.progress_bar.show_counter = True

    result = RenderPipeline(cfg).render()
    assert result.output_path == out
    assert out.is_file()
    assert out.stat().st_size > 0
    assert result.slide_count == 3
    assert result.frame_count > 0
