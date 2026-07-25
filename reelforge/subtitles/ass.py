"""ASS subtitle document stub (Phase 2 — animated captions)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ASSDocument:
    """Minimal ASS document container for Phase 2.

    Full animated captions (word highlighting, typewriter) land in Phase 2.
    """

    header: str = "[Script Info]\nScriptType: v4.00+\n"
    events: list[str] = field(default_factory=list)

    def write(self, path: Path) -> None:
        """Write a minimal ASS file.

        Args:
            path: Destination ``.ass`` path.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        body = (
            self.header
            + "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )
        body += "\n".join(self.events)
        path.write_text(body, encoding="utf-8")
