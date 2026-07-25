"""Fade and crossfade transitions."""

from __future__ import annotations

from PIL import Image

from reelforge.models.enums import TransitionType
from reelforge.transition.base import Transition, TransitionContext


def _blend(a: Image.Image, b: Image.Image, alpha: float) -> Image.Image:
    """Alpha-blend two RGB images."""
    alpha = max(0.0, min(1.0, alpha))
    return Image.blend(a.convert("RGB"), b.convert("RGB"), alpha)


class FadeTransition(Transition):
    """Fade to black then fade in the next slide."""

    @property
    def transition_type(self) -> TransitionType:
        return TransitionType.FADE

    def render(
        self,
        outgoing: Image.Image,
        incoming: Image.Image,
        context: TransitionContext,
    ) -> list[Image.Image]:
        n = context.frame_count
        black = Image.new("RGB", (context.width, context.height), (0, 0, 0))
        out = outgoing.convert("RGB").resize(
            (context.width, context.height), Image.Resampling.LANCZOS
        )
        inn = incoming.convert("RGB").resize(
            (context.width, context.height), Image.Resampling.LANCZOS
        )
        frames: list[Image.Image] = []
        half = max(1, n // 2)
        for i in range(half):
            t = (i + 1) / half
            frames.append(_blend(out, black, t))
        remaining = n - half
        for i in range(remaining):
            t = (i + 1) / max(remaining, 1)
            frames.append(_blend(black, inn, t))
        return frames


class CrossfadeTransition(Transition):
    """Direct cross-dissolve between two slides."""

    @property
    def transition_type(self) -> TransitionType:
        return TransitionType.CROSSFADE

    def render(
        self,
        outgoing: Image.Image,
        incoming: Image.Image,
        context: TransitionContext,
    ) -> list[Image.Image]:
        n = context.frame_count
        out = outgoing.convert("RGB").resize(
            (context.width, context.height), Image.Resampling.LANCZOS
        )
        inn = incoming.convert("RGB").resize(
            (context.width, context.height), Image.Resampling.LANCZOS
        )
        return [_blend(out, inn, (i + 1) / n) for i in range(n)]
