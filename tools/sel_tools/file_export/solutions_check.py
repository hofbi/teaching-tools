"""Check that solutions are not published by accident."""

from pathlib import Path

from sel_tools.file_export.config import EXPORT_BEGIN, EXPORT_END
from sel_tools.utils.files import FileTree, FileVisitor


class CheckForSolutionsCodeVisitor(FileVisitor):
    """Check if file contains solution code."""

    def __init__(self) -> None:
        self.__has_solutions_code = False

    def visit_file(self, file: Path) -> None:
        content = file.read_text()
        self.__has_solutions_code = EXPORT_BEGIN in content or EXPORT_END in content

    @property
    def has_solutions_code(self) -> bool:
        return self.__has_solutions_code


def check_code_for_solutions_code(source_path: Path, publish_solutions: bool) -> None:
    """Check the code to be published for solutions marker."""
    if publish_solutions:
        return

    source_file_tree = FileTree(source_path)
    solutions_check_visitor = CheckForSolutionsCodeVisitor()
    source_file_tree.accept(solutions_check_visitor)
    if solutions_check_visitor.has_solutions_code:
        msg = "Solutions code found in the source code"
        raise ValueError(msg)
