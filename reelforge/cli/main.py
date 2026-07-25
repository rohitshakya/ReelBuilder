"""Typer CLI entrypoint for ReelForge."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from reelforge import __version__
from reelforge.models.config import ProjectConfig
from reelforge.models.enums import Preset, TemplateName
from reelforge.renderer.pipeline import RenderPipeline
from reelforge.templates import apply_template, list_templates
from reelforge.utils.ffmpeg import FFmpegNotFoundError, ensure_ffmpeg
from reelforge.utils.logging import setup_logging
from reelforge.utils.progress import ProgressReporter

app = typer.Typer(
    name="reelforge",
    help="Forge cinematic vertical videos from image folders.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"ReelForge {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """ReelForge — cinematic reels from images."""


@app.command("version")
def version_cmd() -> None:
    """Print the installed ReelForge version."""
    console.print(f"ReelForge {__version__}")


@app.command("templates")
def templates_cmd() -> None:
    """List built-in visual templates."""
    table = Table(title="ReelForge Templates", show_header=True)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description")
    for item in list_templates():
        table.add_row(item["name"], item["description"])
    console.print(table)


@app.command("preview")
def preview_cmd(
    images: Path = typer.Option(
        ...,
        "--images",
        "-i",
        help="Folder of slide images.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="YAML project config.",
        exists=True,
        dir_okay=False,
    ),
) -> None:
    """Preview the slide sequence without rendering video."""
    from reelforge.utils.images import ImageLoader

    cfg = ProjectConfig.from_yaml(config) if config else ProjectConfig()
    loader = ImageLoader(workers=cfg.workers)
    sequence = loader.load(images, duration=cfg.animation.duration)

    table = Table(title=f"Preview — {len(sequence)} slides", show_header=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("File")
    table.add_column("Size", justify="right")
    table.add_column("Orientation")
    table.add_column("Duration", justify="right")

    for slide in sequence:
        table.add_row(
            str(slide.index + 1),
            slide.name,
            f"{slide.width}×{slide.height}",
            slide.orientation.value,
            f"{slide.duration:.1f}s",
        )
    console.print(table)
    console.print(
        f"[dim]Estimated runtime ≈ {sequence.total_duration:.1f}s "
        f"(before transitions)[/dim]"
    )


@app.command("render")
def render_cmd(
    images: Path = typer.Option(
        ...,
        "--images",
        "-i",
        help="Folder of slide images.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output: Path = typer.Option(
        Path("reel.mp4"),
        "--output",
        "-o",
        help="Output MP4 path.",
    ),
    music: Path | None = typer.Option(
        None,
        "--music",
        "-m",
        help="Background music file.",
        exists=True,
        dir_okay=False,
    ),
    template: TemplateName = typer.Option(
        TemplateName.MODERN,
        "--template",
        "-t",
        help="Visual template.",
        case_sensitive=False,
    ),
    preset: Preset = typer.Option(
        Preset.INSTAGRAM,
        "--preset",
        "-p",
        help="Export preset (instagram / youtube_shorts / tiktok).",
        case_sensitive=False,
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="YAML project config.",
        exists=True,
        dir_okay=False,
    ),
    watermark: Path | None = typer.Option(
        None,
        "--watermark",
        "-w",
        help="Logo watermark image.",
        exists=True,
        dir_okay=False,
    ),
    duration: float | None = typer.Option(
        None,
        "--duration",
        "-d",
        help="Per-slide duration in seconds.",
        min=0.5,
    ),
    seed: int | None = typer.Option(
        None,
        "--seed",
        help="RNG seed for reproducible random motion.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable debug logging.",
    ),
) -> None:
    """Render a cinematic vertical reel from an image folder."""
    setup_logging(verbose=verbose)

    try:
        ensure_ffmpeg()
    except FFmpegNotFoundError as exc:
        console.print(f"[red bold]Error:[/] {exc}")
        raise typer.Exit(code=1) from exc

    cfg = ProjectConfig.from_yaml(config) if config else ProjectConfig()
    cfg = apply_template(cfg, template)
    cfg = cfg.merge_cli_overrides(
        images=images,
        output=output,
        music=music,
        export_preset=preset,
        seed=seed,
    )
    if watermark is not None:
        cfg.watermark.path = watermark
    if duration is not None:
        cfg.animation.duration = duration

    console.print(
        f"[bold]ReelForge[/] · template=[cyan]{template.value}[/] · "
        f"preset=[cyan]{preset.value}[/] · "
        f"{cfg.video.width}×{cfg.video.height} @ {cfg.video.fps}fps"
    )

    pipeline = RenderPipeline(cfg)
    try:
        with ProgressReporter(console) as reporter:
            result = pipeline.render(
                images_dir=images,
                output=output,
                progress=reporter,
            )
    except (FileNotFoundError, ValueError, OSError) as exc:
        console.print(f"[red bold]Render failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green bold]✓[/] Wrote [bold]{result.output_path}[/] "
        f"({result.slide_count} slides, {result.duration:.1f}s, "
        f"{result.frame_count} frames)"
    )


def run() -> None:
    """Console-script entrypoint."""
    app()


if __name__ == "__main__":
    run()
