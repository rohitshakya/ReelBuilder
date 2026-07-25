"""Slide and push transitions."""

from __future__ import annotations

from PIL import Image

from reelforge.models.enums import TransitionType
from reelforge.transition.base import Transition, TransitionContext


def _composite_horizontal(
    left: Image.Image,
    right: Image.Image,
    offset: int,
    width: int,
    height: int,
) -> Image.Image:
    """Compose two full frames with a horizontal offset (push/slide)."""
    canvas = Image.new("RGB", (width, height))
    canvas.paste(left, (-offset, 0))
    canvas.paste(right, (width - offset, 0))
    return canvas


class SlideTransition(Transition):
    """Incoming slide slides in from the right over a static outgoing frame."""

    @property
    def transition_type(self) -> TransitionType:
        return TransitionType.SLIDE

    def render(
        self,
        outgoing: Image.Image,
        incoming: Image.Image,
        context: TransitionContext,
    ) -> list[Image.Image]:
        n = context.frame_count
        w, h = context.width, context.height
        out = outgoing.convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
        inn = incoming.convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
        frames: list[Image.Image] = []
        for i in range(n):
            t = (i + 1) / n
            offset = int(w * (1.0 - t))
            canvas = out.copy()
            canvas.paste(inn, (offset, 0))
            # Mask the overlapping region so incoming covers outgoing
            frames.append(canvas)
        return frames


class PushTransition(Transition):
    """Outgoing is pushed left as incoming enters from the right."""

    @property
    def transition_type(self) -> TransitionType:
        return TransitionType.PUSH

    def render(
        self,
        outgoing: Image.Image,
        incoming: Image.Image,
        context: TransitionContext,
    ) -> list[Image.Image]:
        n = context.frame_count
        w, h = context.width, context.height
        out = outgoing.convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
        inn = incoming.convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
        frames: list[Image.Image] = []
        for i in range(n):
            t = (i + 1) / n
            offset = int(w * t)
            frames.append(_composite_horizontal(out, inn, offset, w, h))
        return frames
