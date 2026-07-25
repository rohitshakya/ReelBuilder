"""Abstract transition interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from PIL import Image

from reelforge.models.enums import TransitionType


@dataclass(frozen=True, slots=True)
class TransitionContext:
    """Shared context passed to transition renderers.

    Attributes:
        width: Output frame width.
        height: Output frame height.
        fps: Frames per second.
        duration: Transition duration in seconds.
    """

    width: int
    height: int
    fps: int
    duration: float

    @property
    def frame_count(self) -> int:
        """Number of frames in the transition."""
        return max(1, int(round(self.duration * self.fps)))


class Transition(ABC):
    """Base class for inter-slide transitions."""

    @property
    @abstractmethod
    def transition_type(self) -> TransitionType:
        """Return the enum value for this transition."""

    @abstractmethod
    def render(
        self,
        outgoing: Image.Image,
        incoming: Image.Image,
        context: TransitionContext,
    ) -> list[Image.Image]:
        """Render transition frames from outgoing to incoming slide.

        Args:
            outgoing: Last frame of the previous slide.
            incoming: First frame of the next slide.
            context: Transition timing/size context.

        Returns:
            List of RGB frames covering the transition.
        """
