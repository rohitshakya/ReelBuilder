"""CLI smoke tests (no FFmpeg required for help/version)."""

from __future__ import annotations

from typer.testing import CliRunner

from reelforge.cli.main import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "ReelForge" in result.stdout


def test_templates_command() -> None:
    result = runner.invoke(app, ["templates"])
    assert result.exit_code == 0
    assert "modern" in result.stdout
    assert "minimal" in result.stdout


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "render" in result.stdout
