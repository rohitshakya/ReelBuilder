"""FFmpeg filter graph helpers."""

from __future__ import annotations


def overlay_position(
    position: str,
    *,
    margin: int = 40,
) -> str:
    """Map a named watermark position to an FFmpeg overlay expression.

    Args:
        position: One of top_left, top_right, bottom_left, bottom_right, center.
        margin: Pixel margin from edges.

    Returns:
        FFmpeg ``overlay=x:y`` coordinate expression (without the filter name).
    """
    m = margin
    mapping = {
        "top_left": f"{m}:{m}",
        "top_right": f"W-w-{m}:{m}",
        "bottom_left": f"{m}:H-h-{m}",
        "bottom_right": f"W-w-{m}:H-h-{m}",
        "center": "(W-w)/2:(H-h)/2",
    }
    return mapping.get(position, mapping["bottom_right"])


def scale_watermark_filter(scale: float, video_width: int) -> str:
    """Build a scale filter for the watermark image.

    Args:
        scale: Watermark width as a fraction of video width.
        video_width: Output video width in pixels.

    Returns:
        FFmpeg scale filter string.
    """
    target_w = max(1, int(video_width * scale))
    return f"scale={target_w}:-1"
