"""FFmpeg discovery and process execution helpers."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from reelforge.utils.logging import get_logger

logger = get_logger("utils.ffmpeg")


class FFmpegNotFoundError(RuntimeError):
    """Raised when the FFmpeg binary cannot be located on PATH."""


class FFmpegError(RuntimeError):
    """Raised when an FFmpeg process exits with a non-zero status."""

    def __init__(self, command: Sequence[str], returncode: int, stderr: str) -> None:
        self.command = list(command)
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(
            f"FFmpeg failed (exit {returncode}): {' '.join(command)}\n{stderr}"
        )


def ensure_ffmpeg() -> Path:
    """Locate the FFmpeg binary or raise.

    Returns:
        Absolute path to the ``ffmpeg`` executable.

    Raises:
        FFmpegNotFoundError: If FFmpeg is not installed.
    """
    path = shutil.which("ffmpeg")
    if path is None:
        raise FFmpegNotFoundError(
            "FFmpeg is required but was not found on PATH. "
            "Install it from https://ffmpeg.org/download.html"
        )
    return Path(path)


def ensure_ffprobe() -> Path:
    """Locate the ffprobe binary or raise.

    Returns:
        Absolute path to the ``ffprobe`` executable.

    Raises:
        FFmpegNotFoundError: If ffprobe is not installed.
    """
    path = shutil.which("ffprobe")
    if path is None:
        raise FFmpegNotFoundError(
            "ffprobe is required but was not found on PATH. "
            "It is typically installed alongside FFmpeg."
        )
    return Path(path)


def probe_duration(path: Path) -> float:
    """Return media duration in seconds via ffprobe.

    Args:
        path: Path to an audio or video file.

    Returns:
        Duration in seconds.
    """
    ffprobe = ensure_ffprobe()
    result = subprocess.run(
        [
            str(ffprobe),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise FFmpegError(["ffprobe", str(path)], result.returncode, result.stderr)
    return float(result.stdout.strip())


def detect_hw_encoder() -> str | None:
    """Detect an available hardware H.264 encoder.

    Returns:
        Encoder name (e.g. ``h264_videotoolbox``) or None.
    """
    ffmpeg = ensure_ffmpeg()
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-encoders"],
        capture_output=True,
        text=True,
        check=False,
    )
    encoders = result.stdout
    candidates = (
        "h264_videotoolbox",  # macOS
        "h264_nvenc",  # NVIDIA
        "h264_qsv",  # Intel
        "h264_amf",  # AMD
        "h264_vaapi",  # Linux VA-API
    )
    for name in candidates:
        if name in encoders:
            logger.debug("Detected hardware encoder: %s", name)
            return name
    return None


def run_ffmpeg(
    args: Sequence[str],
    *,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute an FFmpeg command.

    Args:
        args: Arguments after the ``ffmpeg`` binary (do not include ``ffmpeg``).
        check: If True, raise FFmpegError on non-zero exit.
        capture: If True, capture stdout/stderr.

    Returns:
        Completed process result.

    Raises:
        FFmpegNotFoundError: If FFmpeg is missing.
        FFmpegError: If the process fails and ``check`` is True.
    """
    ffmpeg = ensure_ffmpeg()
    command = [str(ffmpeg), "-hide_banner", "-y", *args]
    logger.debug("Running: %s", " ".join(command))

    result = subprocess.run(
        command,
        capture_output=capture,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise FFmpegError(command, result.returncode, result.stderr or "")
    return result
