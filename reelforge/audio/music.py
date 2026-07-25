"""Background music preparation via FFmpeg."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reelforge.models.config import AudioConfig
from reelforge.utils.ffmpeg import probe_duration, run_ffmpeg
from reelforge.utils.logging import get_logger

logger = get_logger("audio.music")


@dataclass(frozen=True, slots=True)
class MusicSpec:
    """Resolved music processing parameters."""

    source: Path
    target_duration: float
    volume: float
    fade_in: float
    fade_out: float
    loop: bool
    auto_trim: bool


class MusicMixer:
    """Prepare background music to match a video duration.

    Handles looping, trimming, volume, and fade in/out using FFmpeg.
    """

    def prepare(
        self,
        config: AudioConfig,
        video_duration: float,
        output_path: Path,
    ) -> Path | None:
        """Render a music bed matching ``video_duration``.

        Args:
            config: Audio configuration.
            video_duration: Final video length in seconds.
            output_path: Where to write the processed AAC/M4A file.

        Returns:
            Path to processed audio, or None if no music is configured.
        """
        if config.path is None:
            return None
        if not config.path.is_file():
            msg = f"Music file not found: {config.path}"
            raise FileNotFoundError(msg)

        spec = MusicSpec(
            source=config.path,
            target_duration=video_duration,
            volume=config.volume,
            fade_in=min(config.fade_in, video_duration / 2),
            fade_out=min(config.fade_out, video_duration / 2),
            loop=config.loop,
            auto_trim=config.auto_trim,
        )
        return self._render(spec, output_path)

    def _render(self, spec: MusicSpec, output_path: Path) -> Path:
        """Build and execute the FFmpeg filter graph for music."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        source_duration = probe_duration(spec.source)
        logger.info(
            "Preparing music: source=%.2fs target=%.2fs",
            source_duration,
            spec.target_duration,
        )

        filters: list[str] = []

        # Loop if needed and auto_trim/loop enabled
        input_args: list[str] = ["-i", str(spec.source)]
        if spec.loop and source_duration < spec.target_duration:
            # Use stream_loop to repeat enough times
            loops = int(spec.target_duration / source_duration) + 1
            input_args = ["-stream_loop", str(loops), "-i", str(spec.source)]

        # Trim to exact duration
        if spec.auto_trim:
            filters.append(f"atrim=0:{spec.target_duration:.6f}")
            filters.append("asetpts=PTS-STARTPTS")

        # Volume
        if abs(spec.volume - 1.0) > 1e-6:
            filters.append(f"volume={spec.volume}")

        # Fades
        if spec.fade_in > 0:
            filters.append(f"afade=t=in:st=0:d={spec.fade_in:.3f}")
        if spec.fade_out > 0:
            fade_start = max(0.0, spec.target_duration - spec.fade_out)
            filters.append(f"afade=t=out:st={fade_start:.3f}:d={spec.fade_out:.3f}")

        filter_complex = ",".join(filters) if filters else "anull"

        run_ffmpeg(
            [
                *input_args,
                "-af",
                filter_complex,
                "-t",
                f"{spec.target_duration:.6f}",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                str(output_path),
            ]
        )
        logger.info("Wrote music bed → %s", output_path)
        return output_path
