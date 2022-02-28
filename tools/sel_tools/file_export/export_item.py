"""Copy files and folders and apply postprocessing on the targets"""

from pathlib import Path
from typing import List

from sel_tools.file_export.copy_item import copy_item
from sel_tools.file_export.file_content_remover import SolutionsRemoverVisitor
from sel_tools.file_export.formatter import FormatterVisitor
from sel_tools.utils.files import FileTree


def export_items(source: Path, repo_paths: List[Path], keep_solutions: bool) -> None:
    """Export all files of source into every repo"""
    for repo in repo_paths:
        # TODO maybe we need to make the repo clean
        copy_item(source, repo)
        # TODO file visitor should probably ignore the .git folder
        # https://gitlab.lrz.de/markusprojects/software-engineering/-/issues/82
        visit_exported_item(repo, keep_solutions)


def visit_exported_item(output_dir: Path, keep_solutions: bool) -> None:
    """Apply visitors on the file tree copied"""
    output_file_tree = FileTree(output_dir)
    if not keep_solutions:
        output_file_tree.accept(SolutionsRemoverVisitor())

    output_file_tree.accept(FormatterVisitor())
