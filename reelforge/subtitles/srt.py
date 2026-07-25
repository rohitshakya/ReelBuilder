"""SRT subtitle parsing (Phase 2 foundation)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SRTCue:
    """A single SRT subtitle cue."""

    index: int
    start: float
    end: float
    text: str


@dataclass
class SRTDocument:
    """Parsed SRT document."""

    cues: list[SRTCue]

    def __len__(self) -> int:
        return len(self.cues)


_TIMESTAMP = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*" r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})"
)


def _ts_to_seconds(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(path: Path | str) -> SRTDocument:
    """Parse an SRT file into an SRTDocument.

    Args:
        path: Path to an ``.srt`` file.

    Returns:
        Parsed document with timed cues.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    srt_path = Path(path)
    if not srt_path.is_file():
        raise FileNotFoundError(srt_path)

    text = srt_path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues: list[SRTCue] = []

    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        idx_line = lines[0].strip()
        ts_line = lines[1].strip()
        body = "\n".join(lines[2:]).strip()
        match = _TIMESTAMP.match(ts_line)
        if not match:
            continue
        try:
            index = int(idx_line)
        except ValueError:
            index = len(cues) + 1
        g = match.groups()
        start = _ts_to_seconds(g[0], g[1], g[2], g[3])
        end = _ts_to_seconds(g[4], g[5], g[6], g[7])
        cues.append(SRTCue(index=index, start=start, end=end, text=body))

    return SRTDocument(cues=cues)
