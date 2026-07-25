"""Prepare output canvases with cover-fit and blur backgrounds."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

from reelforge.utils.logging import get_logger

logger = get_logger("renderer.canvas")


class CanvasPreparer:
    """Resize images onto a fixed canvas with optional blurred fill.

    When the source aspect ratio does not match the output, the image is
    letterboxed/pillarboxed over a heavily blurred, scaled copy of itself —
    the classic CapCut / Instagram Reels look.
    """

    def __init__(
        self,
        width: int = 1080,
        height: int = 1920,
        *,
        blur_radius: float = 40.0,
        background_color: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        self.width = width
        self.height = height
        self.blur_radius = blur_radius
        self.background_color = background_color

    def prepare(self, image_path: Path | str) -> Image.Image:
        """Load an image and compose it onto the output canvas.

        Args:
            image_path: Path to the source image.

        Returns:
            RGB PIL image at exactly ``(width, height)``.
        """
        path = Path(image_path)
        with Image.open(path) as raw:
            src = raw.convert("RGB")
        return self.compose(src)

    def compose(self, src: Image.Image) -> Image.Image:
        """Compose a loaded RGB image onto the canvas.

        Args:
            src: Source RGB image.

        Returns:
            Canvas-sized RGB image.
        """
        src = src.convert("RGB")
        target_ratio = self.width / self.height
        src_ratio = src.width / src.height

        # Background: cover-fill + blur
        bg = self._cover_resize(src, self.width, self.height)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))

        # Foreground: contain-fit (fit inside, preserve aspect)
        fg = self._contain_resize(src, self.width, self.height)
        offset_x = (self.width - fg.width) // 2
        offset_y = (self.height - fg.height) // 2
        bg.paste(fg, (offset_x, offset_y))

        logger.debug(
            "Composed canvas %dx%d (src ratio %.3f vs target %.3f)",
            self.width,
            self.height,
            src_ratio,
            target_ratio,
        )
        return bg

    @staticmethod
    def _cover_resize(img: Image.Image, width: int, height: int) -> Image.Image:
        """Scale so the image covers the entire canvas, then center-crop."""
        scale = max(width / img.width, height / img.height)
        new_w = max(1, int(round(img.width * scale)))
        new_h = max(1, int(round(img.height * scale)))
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        return resized.crop((left, top, left + width, top + height))

    @staticmethod
    def _contain_resize(img: Image.Image, width: int, height: int) -> Image.Image:
        """Scale so the image fits entirely inside the canvas."""
        scale = min(width / img.width, height / img.height)
        new_w = max(1, int(round(img.width * scale)))
        new_h = max(1, int(round(img.height * scale)))
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)
