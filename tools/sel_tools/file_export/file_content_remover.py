"""Remove block(s) within delimiters defined in config file from file or multiline
string."""

import re
from pathlib import Path

from sel_tools.file_export.config import EXPORT_BEGIN, EXPORT_END
from sel_tools.utils.files import FileVisitor, is_cpp


class SolutionsRemoverVisitor(FileVisitor):
    """Remove.

    - block(s) within delimiters defined in config file from file
    - clang tidy comments
    """

    def visit_file(self, file: Path) -> None:
        text_with_reduced_content = remove_lines_within_limiters_from_string(file.read_text())
        if is_cpp(file):
            text_with_reduced_content = remove_clang_tidy_comment_lines(text_with_reduced_content)
        file.write_text(text_with_reduced_content)


def remove_lines_within_limiters_from_string(multiline_string: str) -> str:
    """Remove block(s) within delimiters defined in config file from multiline
    string."""
    minimal_length_between_markers_pattern = r"\n[\S ]*" + EXPORT_BEGIN + r".*?[\S ]*" + EXPORT_END
    return re.sub(minimal_length_between_markers_pattern, "", multiline_string, flags=re.DOTALL)


def remove_clang_tidy_comment_lines(multiline_string: str) -> str:
    """Remove clang-tidy comments from multiline string."""
    clang_tidy_nolint_end_of_line = "  // NOLINT.*?\n"
    multiline_string = re.sub(clang_tidy_nolint_end_of_line, "\n", multiline_string, flags=re.DOTALL)

    clang_tidy_nolint_next_line = "// NOLINTNEXTLINE.*?\n"
    return re.sub(clang_tidy_nolint_next_line, "", multiline_string, flags=re.DOTALL)
