"""Tests for block remover."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase as FsTestCase
from sel_tools.file_export.config import EXPORT_BEGIN, EXPORT_END
from sel_tools.file_export.file_content_remover import (
    SolutionsRemoverVisitor,
    remove_clang_tidy_comment_lines,
    remove_lines_within_limiters_from_string,
)


class SolutionsRemoverVisitorTest(FsTestCase):
    """Test for solution remover visitor."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    @patch(
        "sel_tools.file_export.file_content_remover.remove_clang_tidy_comment_lines",
        MagicMock(return_value="modified_data"),
    )
    def test_file_content_remover__is_cpp__should_remove(self) -> None:
        self.fs.create_file("foo.cpp", contents="some_data")

        unit = SolutionsRemoverVisitor()
        unit.visit_file(Path("foo.cpp"))

        self.assertEqual("modified_data", Path("foo.cpp").read_text())

    @patch(
        "sel_tools.file_export.file_content_remover.remove_clang_tidy_comment_lines",
        MagicMock(return_value="modified_data"),
    )
    def test_file_content_remover__is_not_cpp__should_not_remove(self) -> None:
        self.fs.create_file("foo.txt", contents="some_data")

        unit = SolutionsRemoverVisitor()
        unit.visit_file(Path("foo.txt"))

        self.assertEqual("some_data", Path("foo.txt").read_text())


class FileContentRemoverTest(unittest.TestCase):
    """Tests for file content remover module."""

    def test_cpp_block_removal(self) -> None:
        cpp_file_content = f"""#include <vector>

int main() {{
// {EXPORT_BEGIN}
float a{{}};
a = i;
// {EXPORT_END}
int i{{0}};

// {EXPORT_BEGIN}
bla
blabla
// {EXPORT_END}
}}
"""
        self.assertEqual(
            remove_lines_within_limiters_from_string(cpp_file_content),
            """#include <vector>

int main() {
int i{0};

}
""",
        )

    def test_cmake_block_removal(self) -> None:
        cmake_file_content = f"""cmake_minimum_required(VERSION 3.16)

# {EXPORT_BEGIN}
some
lines
to be removed
# {EXPORT_END}

content that stays
other stuff that stays
# {EXPORT_BEGIN}

short line to be removed
# {EXPORT_END}

staying_file_end()
"""

        self.assertEqual(
            remove_lines_within_limiters_from_string(cmake_file_content),
            """cmake_minimum_required(VERSION 3.16)


content that stays
other stuff that stays

staying_file_end()
""",
        )

    def test_file_block_removal_delimiters_at_beginning_of_line(self) -> None:
        file_content = f"""some
stuff
{EXPORT_BEGIN} is given
{EXPORT_END} and even

more stuff;
// comment
"""
        self.assertEqual(
            remove_lines_within_limiters_from_string(file_content),
            """some
stuff and even

more stuff;
// comment
""",
        )

    def test_file_without_block(self) -> None:
        file_content = "some\nstuff and some\n\nmore stuff;\n// comment\n"
        self.assertEqual(remove_lines_within_limiters_from_string(file_content), file_content)

    def test_file_with_incomplete_block(self) -> None:
        file_content = f"some\nstuff and some\n{EXPORT_BEGIN}\nmore stuff;\n// comment\n"
        self.assertEqual(remove_lines_within_limiters_from_string(file_content), file_content)

    def test_file_with_inverted_block(self) -> None:
        file_content = f"some\n{EXPORT_END}stuff and some\n{EXPORT_BEGIN}\nmore stuff;\n// comment\n"
        self.assertEqual(remove_lines_within_limiters_from_string(file_content), file_content)

    def test_remove_clang_tidy_comment_at_end_of_line(self) -> None:
        file_content = "badcode;  // NOLINT\ngoodcode;\n"
        self.assertEqual(remove_clang_tidy_comment_lines(file_content), "badcode;\ngoodcode;\n")

    def test_remove_specific_clang_tidy_comment_at_end_of_line(self) -> None:
        file_content = "badcode;  // NOLINT(some-test, some-other-test)\ngoodcode;"
        self.assertEqual(remove_clang_tidy_comment_lines(file_content), "badcode;\ngoodcode;")

    def test_do_not_remove_wrongly_formatted_clang_tidy_comment_at_end_of_line(
        self,
    ) -> None:
        file_content = "badcode; // NOLINT\ngoodcode;"  # only one space between ; and /
        self.assertEqual(remove_clang_tidy_comment_lines(file_content), file_content)

    def test_remove_clang_tidy_comment_line(self) -> None:
        file_content = "somecode;\n// NOLINTNEXTLINE\nbadcode;\ngoodcode;"
        self.assertEqual(
            remove_clang_tidy_comment_lines(file_content),
            "somecode;\nbadcode;\ngoodcode;",
        )

    def test_remove_specific_clang_tidy_comment_line(self) -> None:
        file_content = "somecode;\n// NOLINTNEXTLINE(some-test, some-other-test)\nbadcode;\ngoodcode;"
        self.assertEqual(
            remove_clang_tidy_comment_lines(file_content),
            "somecode;\nbadcode;\ngoodcode;",
        )

    def test_do_not_remove_wrongly_formatted_clang_tidy_comment_line(self) -> None:
        file_content = "somecode;\n//NOLINTNEXTLINE\nbadcode;\ngoodcode;"  # no space between / and N
        self.assertEqual(remove_clang_tidy_comment_lines(file_content), file_content)

    def test_remove_multiple_clang_tidy_comments(self) -> None:
        file_content = """somecode;
// NOLINTNEXTLINE(some-check)
badcode;
othercode;
worsecode;  // NOLINT(specific-check)
morecode;
worstcode;  // NOLINT
goodcode;
"""
        self.assertEqual(
            remove_clang_tidy_comment_lines(file_content),
            """somecode;
badcode;
othercode;
worsecode;
morecode;
worstcode;
goodcode;
""",
        )
