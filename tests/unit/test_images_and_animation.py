"""Unit tests for image utilities and movement planning."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

from reelforge.animation.movement import MovementPlanner, resolve_movement
from reelforge.models.enums import ImageOrientation, KenBurnsMovement
from reelforge.utils.images import (
    detect_orientation,
    list_images,
    natural_sort_paths,
)


def test_natural_sort_paths() -> None:
    paths = [Path("img10.png"), Path("img2.png"), Path("img1.png")]
    sorted_paths = natural_sort_paths(paths)
    assert [p.name for p in sorted_paths] == ["img1.png", "img2.png", "img10.png"]


def test_detect_orientation() -> None:
    assert detect_orientation(1080, 1920) == ImageOrientation.PORTRAIT
    assert detect_orientation(1920, 1080) == ImageOrientation.LANDSCAPE
    assert detect_orientation(1000, 1000) == ImageOrientation.SQUARE


def test_list_images(tmp_path: Path) -> None:
    for name in ("003.png", "001.png", "002.png", "notes.txt"):
        (tmp_path / name).write_bytes(b"")
    # Empty files aren't valid images for ImageLoader, but list_images only checks ext
    found = list_images(tmp_path)
    assert [p.name for p in found] == ["001.png", "002.png", "003.png"]


def test_resolve_random_movement_is_deterministic() -> None:
    rng = random.Random(42)
    a = resolve_movement(KenBurnsMovement.RANDOM, rng)
    rng2 = random.Random(42)
    b = resolve_movement(KenBurnsMovement.RANDOM, rng2)
    assert a == b
    assert a != KenBurnsMovement.RANDOM


def test_movement_planner_zoom_in() -> None:
    planner = MovementPlanner(zoom_factor=1.2)
    start, end = planner.plan(KenBurnsMovement.ZOOM_IN)
    assert start.w == 1.0
    assert end.w < 1.0


def test_kenburns_generates_frames(tmp_path: Path) -> None:
    from reelforge.animation.kenburns import KenBurnsAnimator

    img = Image.new("RGB", (800, 1200), color=(40, 80, 160))
    path = tmp_path / "slide.png"
    img.save(path)

    animator = KenBurnsAnimator(width=108, height=192, fps=10, zoom_factor=1.1)
    frames = animator.generate(img.resize((108, 192)), KenBurnsMovement.ZOOM_IN, 0.5)
    assert len(frames) == 5
    assert frames[0].image.size == (108, 192)
