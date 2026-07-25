"""Unit tests for transitions and canvas preparation."""

from __future__ import annotations

from PIL import Image

from reelforge.models.enums import TransitionType
from reelforge.renderer.canvas import CanvasPreparer
from reelforge.transition.base import TransitionContext
from reelforge.transition.factory import TransitionFactory


def test_canvas_blur_fill_landscape() -> None:
    preparer = CanvasPreparer(width=108, height=192, blur_radius=5)
    src = Image.new("RGB", (400, 200), color=(200, 50, 50))
    canvas = preparer.compose(src)
    assert canvas.size == (108, 192)
    assert canvas.mode == "RGB"


def test_canvas_portrait_passthrough_size() -> None:
    preparer = CanvasPreparer(width=108, height=192, blur_radius=5)
    src = Image.new("RGB", (108, 192), color=(10, 200, 10))
    canvas = preparer.compose(src)
    assert canvas.size == (108, 192)


def test_crossfade_frame_count() -> None:
    transition = TransitionFactory.create(TransitionType.CROSSFADE)
    assert transition is not None
    a = Image.new("RGB", (64, 64), color=(255, 0, 0))
    b = Image.new("RGB", (64, 64), color=(0, 0, 255))
    ctx = TransitionContext(width=64, height=64, fps=10, duration=0.5)
    frames = transition.render(a, b, ctx)
    assert len(frames) == 5
    assert frames[0].size == (64, 64)


def test_all_concrete_transitions_render() -> None:
    a = Image.new("RGB", (32, 32), (1, 2, 3))
    b = Image.new("RGB", (32, 32), (3, 2, 1))
    ctx = TransitionContext(width=32, height=32, fps=10, duration=0.3)
    for kind in (
        TransitionType.FADE,
        TransitionType.CROSSFADE,
        TransitionType.SLIDE,
        TransitionType.PUSH,
        TransitionType.ZOOM,
    ):
        tr = TransitionFactory.create(kind)
        assert tr is not None
        frames = tr.render(a, b, ctx)
        assert len(frames) >= 1
