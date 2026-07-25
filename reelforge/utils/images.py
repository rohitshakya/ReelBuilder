"""Image discovery, sorting, and loading utilities."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from natsort import natsorted
from PIL import Image

from reelforge.models.enums import ImageOrientation, KenBurnsMovement, TransitionType
from reelforge.models.slide import Slide, SlideSequence
from reelforge.utils.logging import get_logger

logger = get_logger("utils.images")

SUPPORTED_EXTENSIONS = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
)


def natural_sort_paths(paths: Sequence[Path]) -> list[Path]:
    """Sort paths using natural (human) ordering.

    Args:
        paths: Unsorted path sequence.

    Returns:
        Naturally sorted list (e.g. ``002.png`` before ``010.png``).
    """
    return list(natsorted(paths, key=lambda p: p.name))


def list_images(directory: Path | str) -> list[Path]:
    """List supported image files in a directory, naturally sorted.

    Args:
        directory: Folder containing slide images.

    Returns:
        Sorted list of image paths.

    Raises:
        FileNotFoundError: If the directory does not exist.
        ValueError: If no supported images are found.
    """
    root = Path(directory)
    if not root.is_dir():
        msg = f"Images directory not found: {root}"
        raise FileNotFoundError(msg)

    images = [
        p
        for p in root.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not images:
        msg = f"No supported images found in {root}"
        raise ValueError(msg)

    sorted_images = natural_sort_paths(images)
    logger.info("Found %d images in %s", len(sorted_images), root)
    return sorted_images


def detect_orientation(width: int, height: int) -> ImageOrientation:
    """Classify orientation from pixel dimensions.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        Detected orientation enum value.
    """
    ratio = width / height
    if ratio < 0.95:
        return ImageOrientation.PORTRAIT
    if ratio > 1.05:
        return ImageOrientation.LANDSCAPE
    return ImageOrientation.SQUARE


def _probe_image(path: Path) -> tuple[Path, int, int]:
    """Open an image briefly to read its dimensions."""
    with Image.open(path) as img:
        width, height = img.size
    return path, width, height


class ImageLoader:
    """Load and probe images into a SlideSequence.

    Attributes:
        workers: Thread-pool size for parallel probing.
    """

    def __init__(self, workers: int = 4) -> None:
        self.workers = workers

    def load(
        self,
        directory: Path | str,
        *,
        duration: float = 3.0,
        movement: KenBurnsMovement = KenBurnsMovement.RANDOM,
        transition: TransitionType = TransitionType.CROSSFADE,
        movement_resolver: Callable[[int], KenBurnsMovement] | None = None,
        transition_resolver: Callable[[int], TransitionType] | None = None,
    ) -> SlideSequence:
        """Discover images and build a SlideSequence.

        Args:
            directory: Folder of slide images.
            duration: Default per-slide duration in seconds.
            movement: Default Ken Burns movement (used when no resolver).
            transition: Default transition type (used when no resolver).
            movement_resolver: Optional per-index movement callback.
            transition_resolver: Optional per-index transition callback.

        Returns:
            Populated SlideSequence.
        """
        paths = list_images(directory)
        dims = self._probe_all(paths)

        slides: list[Slide] = []
        for index, (path, width, height) in enumerate(dims):
            mv = movement_resolver(index) if movement_resolver is not None else movement
            tr = (
                transition_resolver(index)
                if transition_resolver is not None
                else transition
            )
            slides.append(
                Slide(
                    index=index,
                    path=path,
                    width=width,
                    height=height,
                    duration=duration,
                    movement=mv,
                    transition_out=tr,
                )
            )
        return SlideSequence(slides=slides)

    def _probe_all(self, paths: Sequence[Path]) -> list[tuple[Path, int, int]]:
        """Probe image dimensions, optionally in parallel."""
        if self.workers <= 1 or len(paths) <= 1:
            return [_probe_image(p) for p in paths]

        results: dict[Path, tuple[int, int]] = {}
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(_probe_image, p): p for p in paths}
            for future in as_completed(futures):
                path, width, height = future.result()
                results[path] = (width, height)

        return [(p, *results[p]) for p in paths]
