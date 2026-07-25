"""End-to-end render pipeline: images → animated frames → MP4."""

from __future__ import annotations

import hashlib
import random
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from reelforge.animation.kenburns import KenBurnsAnimator
from reelforge.animation.movement import resolve_movement
from reelforge.audio.music import MusicMixer
from reelforge.models.config import ProjectConfig
from reelforge.models.enums import KenBurnsMovement, TransitionType
from reelforge.models.slide import Slide, SlideSequence
from reelforge.renderer.canvas import CanvasPreparer
from reelforge.renderer.encoder import VideoEncoder
from reelforge.renderer.overlays import draw_progress_bar, draw_slide_counter
from reelforge.transition.base import TransitionContext
from reelforge.transition.factory import TransitionFactory, resolve_transition
from reelforge.utils.images import ImageLoader
from reelforge.utils.logging import get_logger
from reelforge.utils.progress import ProgressReporter

logger = get_logger("renderer.pipeline")


@dataclass(frozen=True, slots=True)
class RenderResult:
    """Outcome of a successful render job."""

    output_path: Path
    slide_count: int
    duration: float
    frame_count: int


class RenderPipeline:
    """Orchestrate canvas prep, animation, transitions, audio, and encode.

    Business logic lives here; FFmpeg execution is delegated to
    :class:`~reelforge.renderer.encoder.VideoEncoder` and
    :class:`~reelforge.audio.music.MusicMixer`.
    """

    def __init__(self, config: ProjectConfig) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
        self.canvas = CanvasPreparer(
            width=config.video.width,
            height=config.video.height,
        )
        self.animator = KenBurnsAnimator(
            width=config.video.width,
            height=config.video.height,
            fps=config.video.fps,
            zoom_factor=config.animation.zoom_factor,
            easing=config.animation.easing,
        )
        self.encoder = VideoEncoder(config.video)
        self.music = MusicMixer()
        self.loader = ImageLoader(workers=config.workers)

    def render(
        self,
        images_dir: Path | str | None = None,
        output: Path | str | None = None,
        *,
        progress: ProgressReporter | None = None,
    ) -> RenderResult:
        """Run the full render pipeline.

        Args:
            images_dir: Override for ``config.images_dir``.
            output: Override for ``config.output``.
            progress: Optional Rich progress reporter.

        Returns:
            RenderResult with output metadata.

        Raises:
            ValueError: If no images directory is configured.
            FileNotFoundError: If paths are missing.
        """
        if images_dir is None and self.config.images_dir is None:
            raise ValueError("images_dir is required")
        images = Path(images_dir or self.config.images_dir)  # type: ignore[arg-type]
        out = Path(output or self.config.output)
        cache = self.config.cache_dir
        cache.mkdir(parents=True, exist_ok=True)

        frames_dir = cache / "frames"
        if frames_dir.exists():
            shutil.rmtree(frames_dir)
        frames_dir.mkdir(parents=True)

        sequence = self._load_sequence(images)
        if sequence.is_empty():
            raise ValueError("No slides to render")

        if progress:
            progress.start(len(sequence), description="Rendering slides")

        # Generate (or load cached) Ken Burns frames per slide
        slide_frames: list[list[Image.Image]] = []
        for slide in sequence:
            frames = self._render_slide(slide, cache)
            slide_frames.append(frames)
            if progress:
                progress.update(
                    slide=slide.index + 1,
                    total_slides=len(sequence),
                )

        composed = self._compose_with_transitions(sequence, slide_frames)
        final_frames = self._apply_overlays(composed, len(sequence))

        for i, frame in enumerate(final_frames):
            frame.save(frames_dir / f"frame_{i:06d}.png", format="PNG")

        total = len(final_frames)
        duration = total / self.config.video.fps

        audio_path: Path | None = None
        if self.config.audio.path is not None:
            audio_path = cache / "music_bed.m4a"
            self.music.prepare(self.config.audio, duration, audio_path)

        needs_watermark = self.config.watermark.path is not None
        encode_target = cache / "video_raw.mp4" if needs_watermark else out
        pattern = str(frames_dir / "frame_%06d.png")
        self.encoder.encode_frames(pattern, encode_target, audio_path=audio_path)

        if needs_watermark:
            wm = self.config.watermark
            assert wm.path is not None
            self.encoder.apply_watermark(
                encode_target,
                wm.path,
                out,
                opacity=wm.opacity,
                scale=wm.scale,
                position=wm.position,
                margin=wm.margin,
            )

        logger.info(
            "Render complete: %d slides, %.2fs, %d frames → %s",
            len(sequence),
            duration,
            total,
            out,
        )
        return RenderResult(
            output_path=out,
            slide_count=len(sequence),
            duration=duration,
            frame_count=total,
        )

    def _load_sequence(self, images_dir: Path) -> SlideSequence:
        """Load slides and resolve random movements/transitions."""
        duration = self.config.animation.duration
        default_mv = self.config.animation.movement
        default_tr = self.config.transition.type

        def mv_resolver(index: int) -> KenBurnsMovement:
            local = random.Random((self.config.seed or 0) + index * 97)
            return resolve_movement(default_mv, local)

        def tr_resolver(index: int) -> TransitionType:
            local = random.Random((self.config.seed or 0) + index * 193)
            return resolve_transition(default_tr, local)

        return self.loader.load(
            images_dir,
            duration=duration,
            movement=default_mv,
            transition=default_tr,
            movement_resolver=mv_resolver,
            transition_resolver=tr_resolver,
        )

    def _render_slide(self, slide: Slide, cache: Path) -> list[Image.Image]:
        """Prepare canvas and generate Ken Burns frames (with disk cache)."""
        cache_key = self._slide_cache_key(slide)
        slide_cache = cache / "slides" / cache_key
        meta = slide_cache / "done.marker"

        if meta.exists():
            paths = sorted(slide_cache.glob("frame_*.png"))
            if paths:
                logger.debug("Cache hit for slide %d (%s)", slide.index, slide.name)
                return [Image.open(p).convert("RGB") for p in paths]

        slide_cache.mkdir(parents=True, exist_ok=True)
        canvas = self.canvas.prepare(slide.path)
        kb_frames = self.animator.generate(
            canvas,
            slide.movement,
            slide.duration,
            rng=self.rng,
        )
        self.animator.write_frames(kb_frames, slide_cache)
        meta.write_text("ok", encoding="utf-8")
        return [f.image for f in kb_frames]

    def _compose_with_transitions(
        self,
        sequence: SlideSequence,
        slide_frames: list[list[Image.Image]],
    ) -> list[Image.Image]:
        """Concatenate slide frames with inter-slide transitions."""
        composed: list[Image.Image] = []
        tr_duration = self.config.transition.duration
        ctx = TransitionContext(
            width=self.config.video.width,
            height=self.config.video.height,
            fps=self.config.video.fps,
            duration=tr_duration,
        )

        for i, frames in enumerate(slide_frames):
            if i > 0 and tr_duration > 0:
                prev_slide = sequence[i - 1]
                transition = TransitionFactory.create(
                    prev_slide.transition_out, rng=self.rng
                )
                if transition is not None:
                    outgoing = slide_frames[i - 1][-1]
                    incoming = frames[0]
                    composed.extend(transition.render(outgoing, incoming, ctx))
            composed.extend(frames)

        return composed

    def _apply_overlays(
        self,
        frames: list[Image.Image],
        total_slides: int,
    ) -> list[Image.Image]:
        """Apply progress bar and slide counter to every frame."""
        total = len(frames)
        result: list[Image.Image] = []
        for i, frame in enumerate(frames):
            slide_num = min(
                total_slides,
                max(1, int(i / max(total, 1) * total_slides) + 1),
            )
            img = frame
            if self.config.progress_bar.enabled:
                img = draw_progress_bar(img, (i + 1) / total, self.config.progress_bar)
            if self.config.progress_bar.show_counter:
                img = draw_slide_counter(img, slide_num, total_slides)
            result.append(img)
        return result

    def _slide_cache_key(self, slide: Slide) -> str:
        """Stable cache key from path mtime, movement, and duration."""
        try:
            mtime = slide.path.stat().st_mtime_ns
        except OSError:
            mtime = 0
        raw = (
            f"{slide.path.resolve()}|{mtime}|{slide.movement.value}|"
            f"{slide.duration}|{self.config.animation.zoom_factor}|"
            f"{self.config.video.width}x{self.config.video.height}|"
            f"{self.config.video.fps}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


def preprocess_canvases(
    paths: list[Path],
    preparer: CanvasPreparer,
    workers: int = 4,
) -> dict[Path, Image.Image]:
    """Preprocess images onto canvases in parallel.

    Args:
        paths: Image paths.
        preparer: Canvas preparer instance.
        workers: Thread pool size.

    Returns:
        Mapping of path → prepared canvas.
    """
    results: dict[Path, Image.Image] = {}
    if workers <= 1:
        for path in paths:
            results[path] = preparer.prepare(path)
        return results

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(preparer.prepare, p): p for p in paths}
        for future in as_completed(futures):
            path = futures[future]
            results[path] = future.result()
    return results
