"""Copy file or folder with support for an ignore file."""

import shutil
from collections.abc import Callable
from pathlib import Path

from sel_tools.file_export.config import EXPORT_IGNORE


def copy_item(source: Path, dest: Path) -> None:
    """Copy file or folder 'source' with support for an ignore file to dest."""
    if source.is_file():
        shutil.copyfile(str(source), str(dest), follow_symlinks=False)
    else:
        ignored_items = get_ignored_items_from(source)
        shutil.copytree(
            str(source),
            str(dest),
            symlinks=False,
            dirs_exist_ok=True,
            ignore=ignore_files(ignored_items),
        )


def get_ignored_items_from(folder: Path) -> set[Path]:
    """Get list of ignored items from export ignore file with absolute paths."""
    ignore_file = folder / EXPORT_IGNORE
    if not ignore_file.exists():
        return set()

    ignore_file_lines = ignore_file.read_text().splitlines()
    non_empty_lines = list(filter(None, ignore_file_lines))
    non_empty_lines.append(f"**/{EXPORT_IGNORE}")
    ignore_list = [
        file
        for ignore_file_line in non_empty_lines
        for file in folder.glob(ignore_file_line)
    ]

    return {item.resolve() for item in ignore_list}


def ignore_files(ignore_set: set[Path]) -> Callable:
    """Create callable for ignoring files with shutil.copytree."""

    def ignore_callable(directory: str, contents: list[str]) -> list[str]:
        """Callable for ignoring files with shutil.copytree."""
        return [
            item
            for item in contents
            if Path(directory).joinpath(item).resolve() in ignore_set
        ]

    return ignore_callable
