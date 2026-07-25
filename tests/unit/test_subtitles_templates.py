"""Unit tests for SRT parsing and templates."""

from __future__ import annotations

from pathlib import Path

from reelforge.models.config import ProjectConfig
from reelforge.models.enums import TemplateName, TransitionType
from reelforge.subtitles.srt import parse_srt
from reelforge.templates import apply_template, list_templates


def test_list_templates_covers_all() -> None:
    names = {t["name"] for t in list_templates()}
    assert names == {t.value for t in TemplateName}


def test_apply_template_modern() -> None:
    cfg = apply_template(ProjectConfig(), TemplateName.MODERN)
    assert cfg.template == TemplateName.MODERN
    assert cfg.transition.type == TransitionType.CROSSFADE
    assert cfg.progress_bar.color == "#FF2D55"


def test_parse_srt(tmp_path: Path) -> None:
    path = tmp_path / "subs.srt"
    path.write_text(
        "1\n"
        "00:00:00,000 --> 00:00:01,500\n"
        "Hello world\n"
        "\n"
        "2\n"
        "00:00:01,500 --> 00:00:03,000\n"
        "Second line\n",
        encoding="utf-8",
    )
    doc = parse_srt(path)
    assert len(doc) == 2
    assert doc.cues[0].text == "Hello world"
    assert doc.cues[0].end == 1.5
    assert doc.cues[1].start == 1.5
