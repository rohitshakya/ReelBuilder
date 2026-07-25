"""Slide domain models."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from reelforge.models.enums import ImageOrientation, KenBurnsMovement, TransitionType


class Slide(BaseModel):
    """A single image slide in the reel sequence."""

    index: int = Field(ge=0)
    path: Path
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    duration: float = Field(default=3.0, gt=0.0)
    movement: KenBurnsMovement = Field(default=KenBurnsMovement.ZOOM_IN)
    transition_out: TransitionType = Field(default=TransitionType.CROSSFADE)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def orientation(self) -> ImageOrientation:
        """Classify image orientation from pixel dimensions."""
        ratio = self.width / self.height
        if ratio < 0.95:
            return ImageOrientation.PORTRAIT
        if ratio > 1.05:
            return ImageOrientation.LANDSCAPE
        return ImageOrientation.SQUARE

    @computed_field  # type: ignore[prop-decorator]
    @property
    def aspect_ratio(self) -> float:
        """Return width / height."""
        return self.width / self.height

    @property
    def name(self) -> str:
        """Return the image filename."""
        return self.path.name


class SlideSequence(BaseModel):
    """Ordered collection of slides for a reel."""

    slides: list[Slide] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.slides)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self.slides)

    def __getitem__(self, index: int) -> Slide:
        return self.slides[index]

    @property
    def total_duration(self) -> float:
        """Sum of slide durations (excluding transition overlap adjustments)."""
        return sum(s.duration for s in self.slides)

    def is_empty(self) -> bool:
        """Return True when no slides are present."""
        return len(self.slides) == 0
