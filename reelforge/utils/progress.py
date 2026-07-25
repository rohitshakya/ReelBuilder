"""Rich-based progress reporting for the CLI."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


class ProgressReporter:
    """Wrap Rich progress bars for slide-level render status.

    Attributes:
        console: Rich console used for output.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console(stderr=True)
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None

    def __enter__(self) -> ProgressReporter:
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=28),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=self.console,
        )
        self._progress.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        if self._progress is not None:
            self._progress.stop()
            self._progress = None
            self._task_id = None

    def start(self, total: int, description: str = "Rendering slides") -> None:
        """Begin a progress task.

        Args:
            total: Total number of units of work.
            description: Task label shown in the bar.
        """
        if self._progress is None:
            msg = "ProgressReporter must be used as a context manager"
            raise RuntimeError(msg)
        self._task_id = self._progress.add_task(description, total=total)

    def update(
        self,
        advance: float = 1.0,
        *,
        description: str | None = None,
        slide: int | None = None,
        total_slides: int | None = None,
    ) -> None:
        """Advance the progress bar.

        Args:
            advance: Amount to advance.
            description: Optional new description.
            slide: Current slide number (1-based) for label formatting.
            total_slides: Total slide count for label formatting.
        """
        if self._progress is None or self._task_id is None:
            return

        kwargs: dict[str, Any] = {"advance": advance}
        if slide is not None and total_slides is not None:
            kwargs["description"] = f"Slide {slide} / {total_slides}"
        elif description is not None:
            kwargs["description"] = description
        self._progress.update(self._task_id, **kwargs)

    def print(self, message: str) -> None:
        """Print a status line above the progress bar.

        Args:
            message: Text to display.
        """
        if self._progress is not None:
            self._progress.console.print(message)
        else:
            self.console.print(message)
