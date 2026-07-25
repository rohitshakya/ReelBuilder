"""ffmpeg.py — thin re-export kept for the documented package layout."""

from reelforge.utils.ffmpeg import (
    FFmpegError,
    FFmpegNotFoundError,
    detect_hw_encoder,
    ensure_ffmpeg,
    probe_duration,
    run_ffmpeg,
)

__all__ = [
    "FFmpegError",
    "FFmpegNotFoundError",
    "detect_hw_encoder",
    "ensure_ffmpeg",
    "probe_duration",
    "run_ffmpeg",
]
