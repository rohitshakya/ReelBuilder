"""FFmpeg-based video encoding."""

from __future__ import annotations

from pathlib import Path

from reelforge.models.config import VideoConfig
from reelforge.utils.ffmpeg import detect_hw_encoder, run_ffmpeg
from reelforge.utils.logging import get_logger

logger = get_logger("renderer.encoder")


class VideoEncoder:
    """Encode frame sequences and mux audio into final MP4 files."""

    def __init__(self, config: VideoConfig) -> None:
        self.config = config

    def encode_frames(
        self,
        frame_pattern: str,
        output_path: Path,
        *,
        audio_path: Path | None = None,
        start_number: int = 0,
    ) -> Path:
        """Encode a numbered PNG sequence into an H.264 MP4.

        Args:
            frame_pattern: FFmpeg glob/pattern, e.g. ``frame_%06d.png``.
            output_path: Destination MP4 path.
            audio_path: Optional AAC audio bed to mux.
            start_number: First frame index.

        Returns:
            Path to the encoded file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        codec = self._resolve_codec()
        args: list[str] = [
            "-framerate",
            str(self.config.fps),
            "-start_number",
            str(start_number),
            "-i",
            frame_pattern,
        ]
        if audio_path is not None:
            args.extend(["-i", str(audio_path)])

        args.extend(
            [
                "-c:v",
                codec,
                "-pix_fmt",
                self.config.pixel_format,
            ]
        )

        # CRF / quality — software only; HW encoders use different knobs
        if codec == "libx264":
            args.extend(
                [
                    "-crf",
                    str(self.config.crf),
                    "-preset",
                    self.config.preset,
                ]
            )
        elif codec == "h264_videotoolbox":
            args.extend(["-b:v", "8M"])
        elif codec in {"h264_nvenc", "h264_qsv", "h264_amf"}:
            args.extend(["-cq", str(self.config.crf), "-b:v", "0"])

        if audio_path is not None:
            args.extend(["-c:a", "aac", "-b:a", "192k", "-shortest"])
        else:
            args.append("-an")

        args.extend(["-movflags", "+faststart", str(output_path)])
        run_ffmpeg(args)
        logger.info("Encoded video → %s", output_path)
        return output_path

    def mux(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
    ) -> Path:
        """Mux a silent video with an audio bed.

        Args:
            video_path: Silent video file.
            audio_path: Audio file.
            output_path: Final muxed output.

        Returns:
            Path to the muxed file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        run_ffmpeg(
            [
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(output_path),
            ]
        )
        return output_path

    def apply_watermark(
        self,
        video_path: Path,
        watermark_path: Path,
        output_path: Path,
        *,
        opacity: float = 0.7,
        scale: float = 0.12,
        position: str = "bottom_right",
        margin: int = 40,
    ) -> Path:
        """Overlay a logo watermark onto a video.

        Args:
            video_path: Source video.
            watermark_path: Logo image (PNG with alpha preferred).
            output_path: Destination path.
            opacity: Logo opacity 0–1.
            scale: Logo width as fraction of video width.
            position: Named position string.
            margin: Edge margin in pixels.

        Returns:
            Path to watermarked video.
        """
        from reelforge.renderer.filters import overlay_position, scale_watermark_filter

        pos = overlay_position(position, margin=margin)
        scale_f = scale_watermark_filter(scale, self.config.width)
        # Scale watermark, apply opacity, overlay
        filter_complex = (
            f"[1:v]{scale_f},format=rgba,"
            f"colorchannelmixer=aa={opacity}[wm];"
            f"[0:v][wm]overlay={pos}"
        )
        run_ffmpeg(
            [
                "-i",
                str(video_path),
                "-i",
                str(watermark_path),
                "-filter_complex",
                filter_complex,
                "-c:a",
                "copy",
                "-movflags",
                "+faststart",
                str(output_path),
            ]
        )
        return output_path

    def _resolve_codec(self) -> str:
        """Pick software or hardware H.264 encoder."""
        if self.config.hardware_accel:
            hw = detect_hw_encoder()
            if hw is not None:
                logger.info("Using hardware encoder: %s", hw)
                return hw
        return self.config.codec
