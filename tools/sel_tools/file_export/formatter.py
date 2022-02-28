"""Formatter module"""

from pathlib import Path
from shutil import which
from subprocess import run

from sel_tools.utils.files import FileVisitor, is_cmake, is_cpp


class FormatterVisitor(FileVisitor):
    """Format file. Auto-selects formatter depending on file suffix.
    Formats cpp and cmake, ignores other file types"""

    def visit_file(self, file: Path) -> None:
        if is_cpp(file):
            apply_clang_format(file)
        elif is_cmake(file):
            apply_cmake_format(file)


def apply_clang_format(file: Path) -> None:
    """Apply clang-format with default config in place to file"""
    if which("clang-format"):
        run(f"clang-format -i {file}", shell=True)


def apply_cmake_format(file: Path) -> None:
    """Apply cmake-format with default config in place to file"""
    if which("cmake-format"):
        run(f"cmake-format -i {file}", shell=True)
