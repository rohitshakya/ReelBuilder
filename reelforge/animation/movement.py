"""Camera movement planning for Ken Burns animations."""

from __future__ import annotations

import random
from dataclasses import dataclass

from reelforge.models.enums import KenBurnsMovement

# Concrete movements (excludes RANDOM)
_CONCRETE_MOVEMENTS: tuple[KenBurnsMovement, ...] = (
    KenBurnsMovement.ZOOM_IN,
    KenBurnsMovement.ZOOM_OUT,
    KenBurnsMovement.PAN_LEFT,
    KenBurnsMovement.PAN_RIGHT,
    KenBurnsMovement.PAN_UP,
    KenBurnsMovement.PAN_DOWN,
)


@dataclass(frozen=True, slots=True)
class CropWindow:
    """Normalized crop window describing a Ken Burns keyframe.

    Coordinates are fractions of the source image (0.0–1.0).
    ``x``, ``y`` are the top-left of the crop; ``w``, ``h`` are size.
    """

    x: float
    y: float
    w: float
    h: float

    def clamp(self) -> CropWindow:
        """Return a copy clamped to the unit square."""
        w = min(max(self.w, 0.01), 1.0)
        h = min(max(self.h, 0.01), 1.0)
        x = min(max(self.x, 0.0), 1.0 - w)
        y = min(max(self.y, 0.0), 1.0 - h)
        return CropWindow(x=x, y=y, w=w, h=h)


def resolve_movement(
    movement: KenBurnsMovement,
    rng: random.Random | None = None,
) -> KenBurnsMovement:
    """Resolve RANDOM to a concrete movement.

    Args:
        movement: Requested movement (may be RANDOM).
        rng: Optional RNG for reproducibility.

    Returns:
        A concrete KenBurnsMovement value.
    """
    if movement != KenBurnsMovement.RANDOM:
        return movement
    picker = rng or random.Random()
    return picker.choice(_CONCRETE_MOVEMENTS)


def easing_ease_in_out(t: float) -> float:
    """Smoothstep ease-in-out curve.

    Args:
        t: Progress in [0, 1].

    Returns:
        Eased progress in [0, 1].
    """
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


class MovementPlanner:
    """Plan start/end crop windows for a Ken Burns movement.

    Attributes:
        zoom_factor: Maximum scale applied during zoom movements.
    """

    def __init__(self, zoom_factor: float = 1.15) -> None:
        self.zoom_factor = zoom_factor

    def plan(
        self,
        movement: KenBurnsMovement,
        *,
        rng: random.Random | None = None,
    ) -> tuple[CropWindow, CropWindow]:
        """Compute start and end crop windows.

        Args:
            movement: Concrete or RANDOM movement.
            rng: Optional RNG for reproducibility.

        Returns:
            ``(start, end)`` crop windows in normalized coordinates.
        """
        resolved = resolve_movement(movement, rng)
        z = self.zoom_factor
        # Zoomed crop size (smaller crop = zoomed in)
        zw, zh = 1.0 / z, 1.0 / z

        full = CropWindow(0.0, 0.0, 1.0, 1.0)
        center_zoom = CropWindow(
            x=(1.0 - zw) / 2.0,
            y=(1.0 - zh) / 2.0,
            w=zw,
            h=zh,
        ).clamp()

        if resolved == KenBurnsMovement.ZOOM_IN:
            return full, center_zoom
        if resolved == KenBurnsMovement.ZOOM_OUT:
            return center_zoom, full
        if resolved == KenBurnsMovement.PAN_LEFT:
            start = CropWindow(1.0 - zw, (1.0 - zh) / 2.0, zw, zh).clamp()
            end = CropWindow(0.0, (1.0 - zh) / 2.0, zw, zh).clamp()
            return start, end
        if resolved == KenBurnsMovement.PAN_RIGHT:
            start = CropWindow(0.0, (1.0 - zh) / 2.0, zw, zh).clamp()
            end = CropWindow(1.0 - zw, (1.0 - zh) / 2.0, zw, zh).clamp()
            return start, end
        if resolved == KenBurnsMovement.PAN_UP:
            start = CropWindow((1.0 - zw) / 2.0, 1.0 - zh, zw, zh).clamp()
            end = CropWindow((1.0 - zw) / 2.0, 0.0, zw, zh).clamp()
            return start, end
        if resolved == KenBurnsMovement.PAN_DOWN:
            start = CropWindow((1.0 - zw) / 2.0, 0.0, zw, zh).clamp()
            end = CropWindow((1.0 - zw) / 2.0, 1.0 - zh, zw, zh).clamp()
            return start, end

        # Fallback
        return full, center_zoom

    def interpolate(
        self,
        start: CropWindow,
        end: CropWindow,
        t: float,
        *,
        easing: str = "ease_in_out",
    ) -> CropWindow:
        """Interpolate between two crop windows.

        Args:
            start: Start crop.
            end: End crop.
            t: Linear progress in [0, 1].
            easing: Easing function name.

        Returns:
            Interpolated crop window.
        """
        t = easing_ease_in_out(t) if easing == "ease_in_out" else max(0.0, min(1.0, t))

        return CropWindow(
            x=start.x + (end.x - start.x) * t,
            y=start.y + (end.y - start.y) * t,
            w=start.w + (end.w - start.w) * t,
            h=start.h + (end.h - start.h) * t,
        ).clamp()
