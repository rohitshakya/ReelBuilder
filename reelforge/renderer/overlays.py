"""Overlay helpers: progress bar and slide counter."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from reelforge.models.config import ProgressBarConfig


def _parse_color(
    color: str, fallback: tuple[int, int, int, int]
) -> tuple[int, int, int, int]:
    """Parse ``#RRGGBB`` or ``#RRGGBBAA`` into an RGBA tuple."""
    c = color.strip().lstrip("#")
    try:
        if len(c) == 6:
            r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            return r, g, b, 255
        if len(c) == 8:
            r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            a = int(c[6:8], 16)
            return r, g, b, a
    except ValueError:
        return fallback
    return fallback


def draw_progress_bar(
    image: Image.Image,
    progress: float,
    config: ProgressBarConfig,
) -> Image.Image:
    """Draw a progress bar onto a frame.

    Args:
        image: RGB/RGBA frame.
        progress: Completion fraction in [0, 1].
        config: Progress bar styling.

    Returns:
        Frame with progress bar (RGB).
    """
    if not config.enabled:
        return image.convert("RGB")

    progress = max(0.0, min(1.0, progress))
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = base.size
    bar_h = config.height
    y = h - bar_h if config.position == "bottom" else 0

    bg = _parse_color(config.background_color, (0, 0, 0, 128))
    fg = _parse_color(config.color, (255, 255, 255, 255))

    draw.rectangle((0, y, w, y + bar_h), fill=bg)
    draw.rectangle((0, y, int(w * progress), y + bar_h), fill=fg)

    composed = Image.alpha_composite(base, overlay)
    return composed.convert("RGB")


def draw_slide_counter(
    image: Image.Image,
    slide_number: int,
    total_slides: int,
    *,
    margin: int = 24,
) -> Image.Image:
    """Draw a ``Slide N / Total`` label in the top-left corner.

    Args:
        image: RGB frame.
        slide_number: 1-based current slide index.
        total_slides: Total number of slides.
        margin: Pixel margin from edges.

    Returns:
        Frame with counter text.
    """
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    text = f"Slide {slide_number} / {total_slides}"

    font: ImageFont.ImageFont | ImageFont.FreeTypeFont
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 28)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 10
    x, y = margin, margin
    draw.rounded_rectangle(
        (x - pad, y - pad, x + tw + pad, y + th + pad),
        radius=8,
        fill=(0, 0, 0, 140),
    )
    draw.text((x, y), text, fill=(255, 255, 255, 230), font=font)
    return Image.alpha_composite(base, overlay).convert("RGB")
