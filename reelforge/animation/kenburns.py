"""Ken Burns frame generation over prepared canvases."""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from reelforge.animation.movement import CropWindow, MovementPlanner
from reelforge.models.enums import KenBurnsMovement
from reelforge.utils.logging import get_logger

logger = get_logger("animation.kenburns")


@dataclass(frozen=True, slots=True)
class KenBurnsFrame:
    """A single rendered frame from a Ken Burns animation.

    Attributes:
        index: Zero-based frame index.
        image: RGB PIL image at output resolution.
    """

    index: int
    image: Image.Image


class KenBurnsAnimator:
    """Generate Ken Burns animated frames from a prepared canvas image.

    The input image is expected to already match the output canvas size
    (with blur-fill applied if needed). The animator crops and resizes
    according to the planned movement path.
    """

    def __init__(
        self,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        zoom_factor: float = 1.15,
        easing: str = "ease_in_out",
    ) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.easing = easing
        self.planner = MovementPlanner(zoom_factor=zoom_factor)

    @property
    def zoom_factor(self) -> float:
        """Maximum zoom scale."""
        return self.planner.zoom_factor

    def frame_count(self, duration: float) -> int:
        """Return number of frames for a given duration.

        Args:
            duration: Slide duration in seconds.

        Returns:
            Frame count (at least 1).
        """
        return max(1, int(round(duration * self.fps)))

    def generate(
        self,
        canvas: Image.Image,
        movement: KenBurnsMovement,
        duration: float,
        *,
        rng: random.Random | None = None,
    ) -> list[KenBurnsFrame]:
        """Generate all frames for a slide.

        Args:
            canvas: Prepared RGB image at (or larger than) output size.
            movement: Ken Burns movement to apply.
            duration: Slide duration in seconds.
            rng: Optional RNG for reproducible RANDOM movements.

        Returns:
            List of KenBurnsFrame objects.
        """
        start, end = self.planner.plan(movement, rng=rng)
        n = self.frame_count(duration)
        src = np.asarray(canvas.convert("RGB"))
        frames: list[KenBurnsFrame] = []

        for i in range(n):
            t = 0.0 if n == 1 else i / (n - 1)
            crop = self.planner.interpolate(start, end, t, easing=self.easing)
            frame_img = self._crop_and_resize(src, crop)
            frames.append(KenBurnsFrame(index=i, image=frame_img))

        logger.debug(
            "Generated %d Ken Burns frames (%s, %.2fs)",
            n,
            movement.value,
            duration,
        )
        return frames

    def write_frames(
        self,
        frames: list[KenBurnsFrame],
        output_dir: Path,
        *,
        prefix: str = "frame",
    ) -> list[Path]:
        """Write frames to disk as sequential PNGs.

        Args:
            frames: Frames to write.
            output_dir: Destination directory.
            prefix: Filename prefix.

        Returns:
            List of written file paths.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        for frame in frames:
            path = output_dir / f"{prefix}_{frame.index:06d}.png"
            frame.image.save(path, format="PNG")
            paths.append(path)
        return paths

    def _crop_and_resize(
        self,
        src: np.ndarray,
        crop: CropWindow,
    ) -> Image.Image:
        """Crop a numpy RGB array using a normalized window and resize."""
        h, w = src.shape[:2]
        x0 = int(crop.x * w)
        y0 = int(crop.y * h)
        x1 = int((crop.x + crop.w) * w)
        y1 = int((crop.y + crop.h) * h)

        # Ensure at least 1px
        x1 = max(x1, x0 + 1)
        y1 = max(y1, y0 + 1)

        cropped = src[y0:y1, x0:x1]
        img = Image.fromarray(cropped)
        return img.resize((self.width, self.height), Image.Resampling.LANCZOS)
