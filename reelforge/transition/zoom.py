"""Zoom transition between slides."""

from __future__ import annotations

from PIL import Image

from reelforge.models.enums import TransitionType
from reelforge.transition.base import Transition, TransitionContext


class ZoomTransition(Transition):
    """Zoom into outgoing while crossfading to zoomed-out incoming."""

    @property
    def transition_type(self) -> TransitionType:
        return TransitionType.ZOOM

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
            # Outgoing zooms in (scale 1.0 → 1.4)
            out_scale = 1.0 + 0.4 * t
            ow, oh = int(w * out_scale), int(h * out_scale)
            scaled_out = out.resize((ow, oh), Image.Resampling.LANCZOS)
            left = (ow - w) // 2
            top = (oh - h) // 2
            cropped_out = scaled_out.crop((left, top, left + w, top + h))

            # Incoming zooms out (scale 1.4 → 1.0)
            in_scale = 1.4 - 0.4 * t
            iw, ih = int(w * in_scale), int(h * in_scale)
            scaled_in = inn.resize((iw, ih), Image.Resampling.LANCZOS)
            # Pad incoming onto canvas
            canvas_in = Image.new("RGB", (w, h))
            px, py = (w - iw) // 2, (h - ih) // 2
            canvas_in.paste(scaled_in, (px, py))

            frames.append(Image.blend(cropped_out, canvas_in, t))
        return frames
