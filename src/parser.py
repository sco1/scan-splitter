from pathlib import Path

from rich.progress import track


def split_composite_file(composite_src: list[str]) -> tuple[list[str], list[str]]:
    """
    Split composite data file into its components.

    A composite data file is assumed to contain 3 chunks of data:
        1. Core measurements
        2. Custom measurements
        3. Landmark coordinates

    Core and custom measurements are joined into a single list of anthro measurements.

    Each section is assumed to contain one or more header lines, which start with `#`. All header
    lines are discarded.

    Data rows containing one or more `*` are assumed to be comments and are discarded.
    """
    out_chunks = []
    in_header = True  # File is assumed to start with a header
    for line in composite_src:
        if in_header:
            if line.startswith("#"):
                continue
            else:
                in_header = False
                chunk: list[str] = []

        if line.startswith("#"):
            out_chunks.append(chunk)
            in_header = True
            continue

        # All non-comment lines are assumed to lead off with a validitity flag (0 or 1) that we can
        # strip off, if present
        line = line.removeprefix("1  ").removeprefix("0  ")
        if line.startswith("*"):
            # Discard comments
            continue

        chunk.append(line)
    else:
        # Append the last chunk when we finish reading the file
        out_chunks.append(chunk)

    core, custom, landmark = out_chunks
    anthro = [*core, *custom]

    return anthro, landmark


def file_pipeline(in_file: Path) -> None:
    """"""
    composite_src = in_file.read_text().splitlines()
    anthro, landmark = split_composite_file(composite_src)

    base_stem = in_file.stem
    anthro_filepath = in_file.with_stem(f"{base_stem}.anthro")
    landmark_filepath = in_file.with_stem(f"{base_stem}.lmk")

    anthro_filepath.write_text("\n".join(anthro))
    landmark_filepath.write_text("\n".join(landmark))


def batch_pipeline(in_dir: Path, pattern: str = "*_composite.txt", recurse: bool = False) -> None:
    """"""
    if recurse:
        pattern = f"**/{pattern}"

    # Listify here to get progress
    composite_files = list(in_dir.glob(pattern))

    for composite_file in track(composite_files, description="Splitting..."):
        file_pipeline(composite_file)
