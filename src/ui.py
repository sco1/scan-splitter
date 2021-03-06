import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import click
import typer
from src import io


scansplitter_cli = typer.Typer()


def _prompt_for_file(title: str, start_dir: Path = Path()) -> Path:  # pragma: no cover
    """Open a Tk file selection dialog to prompt the user to select a single file for processing."""
    root = tk.Tk()
    root.withdraw()

    picked = filedialog.askopenfilename(  # type: ignore[no-untyped-call]  # stubs need mypy bump
        title=title,
        initialdir=start_dir,
        multiple=False,
        filetypes=[
            ("Composite Scan Data", "*.txt"),
            ("All Files", "*.*"),
        ],
    )

    if not picked:
        raise click.ClickException("No file selected for parsing, aborting.")

    return Path(picked)


def _prompt_for_dir(start_dir: Path = Path()) -> Path:  # pragma: no cover
    """Open a Tk file selection dialog to prompt the user to select a directory for processing."""
    root = tk.Tk()
    root.withdraw()

    picked = filedialog.askdirectory(  # type: ignore[no-untyped-call]  # stubs need mypy bump
        title="Select directory for batch processing",
        initialdir=start_dir,
    )

    if not picked:
        raise click.ClickException("No directory selected for parsing, aborting.")

    return Path(picked)


@scansplitter_cli.command()
def single(
    scan_filepath: Path = typer.Option(None, exists=True, file_okay=True, dir_okay=False),
) -> None:
    """
    Split the specified scan file into its anthro & landmark components.

    If no file is specified, the user will be prompted to select one.
    """
    if scan_filepath is None:
        scan_filepath = _prompt_for_file(title="Select scan file to slice")

    io.file_split_pipeline(scan_filepath)


@scansplitter_cli.command()
def batch(
    scan_dir: Path = typer.Option(None, exists=True, file_okay=False, dir_okay=True),
    pattern: str = typer.Option("*_composite.txt"),
    recurse: bool = False,
) -> None:
    """
    Batch process all scans in the specified directory.

    If no processing directory is specified, the user will be prompted to select one.

    Recursive processing may be optionally specified (Default: `False`).
    """
    if scan_dir is None:
        scan_dir = _prompt_for_dir()

    io.batch_split_pipeline(scan_dir, pattern=pattern, recurse=recurse)


@scansplitter_cli.command()
def aggregate(
    anthro_dir: Path = typer.Option(None, exists=True, file_okay=False, dir_okay=True),
    new_row_names: Path = typer.Option(None, exists=True, file_okay=True, dir_okay=False),
    location_fill: str = "",
    pattern: str = typer.Option("*_composite.anthro.csv"),
    recurse: bool = False,
) -> None:
    """
    Aggregate a directory of split anthro measurement files into a single CSV.

    If no processing directory is specified, the user will be prompted to select one.

    Recursive processing may be optionally specified (Default: `False`).
    """
    if anthro_dir is None:
        anthro_dir = _prompt_for_dir()

    io.anthro_measure_aggregation_pipeline(
        anthro_dir,
        new_row_names=new_row_names,
        location_fill=location_fill,
        pattern=pattern,
        recurse=recurse,
    )


@scansplitter_cli.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    Split composite scan file(s) into separate landmark & measurement files.

    Invocation without args prompts the user to select a scan directory, then runs through the
    default batch & aggregation pipelines.
    """
    if not ctx.invoked_subcommand:
        anthro_dir = _prompt_for_dir()
        io.batch_split_pipeline(anthro_dir)
        io.anthro_measure_aggregation_pipeline(anthro_dir)


if __name__ == "__main__":  # pragma: no cover
    scansplitter_cli()
