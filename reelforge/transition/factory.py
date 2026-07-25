"""Transition factory and random resolution."""

from __future__ import annotations

import random

from reelforge.models.enums import TransitionType
from reelforge.transition.base import Transition
from reelforge.transition.fade import CrossfadeTransition, FadeTransition
from reelforge.transition.slide import PushTransition, SlideTransition
from reelforge.transition.zoom import ZoomTransition

_CONCRETE_TRANSITIONS: tuple[TransitionType, ...] = (
    TransitionType.FADE,
    TransitionType.CROSSFADE,
    TransitionType.SLIDE,
    TransitionType.PUSH,
    TransitionType.ZOOM,
)

_REGISTRY: dict[TransitionType, type[Transition]] = {
    TransitionType.FADE: FadeTransition,
    TransitionType.CROSSFADE: CrossfadeTransition,
    TransitionType.SLIDE: SlideTransition,
    TransitionType.PUSH: PushTransition,
    TransitionType.ZOOM: ZoomTransition,
}


def resolve_transition(
    transition_type: TransitionType,
    rng: random.Random | None = None,
) -> TransitionType:
    """Resolve RANDOM to a concrete transition type.

    Args:
        transition_type: Requested type (may be RANDOM).
        rng: Optional RNG for reproducibility.

    Returns:
        A concrete TransitionType (never RANDOM or NONE).
    """
    if transition_type == TransitionType.NONE:
        return TransitionType.NONE
    if transition_type != TransitionType.RANDOM:
        return transition_type
    picker = rng or random.Random()
    return picker.choice(_CONCRETE_TRANSITIONS)


class TransitionFactory:
    """Create Transition instances from enum values."""

    @staticmethod
    def create(
        transition_type: TransitionType,
        *,
        rng: random.Random | None = None,
    ) -> Transition | None:
        """Instantiate a transition, or None for NONE.

        Args:
            transition_type: Desired transition (RANDOM is resolved).
            rng: Optional RNG for RANDOM resolution.

        Returns:
            Transition instance, or None if type is NONE.
        """
        resolved = resolve_transition(transition_type, rng)
        if resolved == TransitionType.NONE:
            return None
        cls = _REGISTRY.get(resolved)
        if cls is None:
            msg = f"Unsupported transition type: {resolved}"
            raise ValueError(msg)
        return cls()
