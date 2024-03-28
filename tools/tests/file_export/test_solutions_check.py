"""Test solutions check module."""

from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.file_export.config import EXPORT_BEGIN, EXPORT_END
from sel_tools.file_export.solutions_check import (
    CheckForSolutionsCodeVisitor,
    check_code_for_solutions_code,
)


def _create_test_file_content(with_opening_marker: bool = False, with_closing_marker: bool = False) -> str:
    return f"""#include <vector>

int main() {{
    // {EXPORT_BEGIN if with_opening_marker else ""}
    Some solution code between markers
    // {EXPORT_END if with_closing_marker else ""}
    return 0;
}}
"""


class CheckForSolutionsCodeVisitorTest(TestCase):
    """Check for Solutions Code Visitor Test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_visit_file__empty_file__should_not_contain_solutions_code(self) -> None:
        self.fs.create_file("foo.cpp")
        unit = CheckForSolutionsCodeVisitor()

        unit.visit_file(Path("foo.cpp"))

        self.assertFalse(unit.has_solutions_code)

    def test_visit_file__file_without_solution_markers__should_not_contain_solutions_code(
        self,
    ) -> None:
        self.fs.create_file("foo.cpp", contents=_create_test_file_content())
        unit = CheckForSolutionsCodeVisitor()

        unit.visit_file(Path("foo.cpp"))

        self.assertFalse(unit.has_solutions_code)

    def test_visit_file__file_with_both_solution_markers__should_contain_solutions_code(
        self,
    ) -> None:
        cpp_file_content = _create_test_file_content(with_opening_marker=True, with_closing_marker=True)
        self.fs.create_file("foo.cpp", contents=cpp_file_content)
        unit = CheckForSolutionsCodeVisitor()

        unit.visit_file(Path("foo.cpp"))

        self.assertTrue(unit.has_solutions_code)

    def test_visit_file__file_with_one_solution_marker__should_contain_solutions_code(
        self,
    ) -> None:
        cpp_file_content = _create_test_file_content(with_opening_marker=True, with_closing_marker=False)
        self.fs.create_file("foo.cpp", contents=cpp_file_content)
        unit = CheckForSolutionsCodeVisitor()

        unit.visit_file(Path("foo.cpp"))

        self.assertTrue(unit.has_solutions_code)


class SolutionsCheckTest(TestCase):
    """Test for the solutions check functions."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file(
            "solutions_code/bar.cpp",
            contents=_create_test_file_content(with_opening_marker=True, with_closing_marker=True),
        )
        self.source_path_with_solutions = Path("solutions_code/")

    def test_check_code_for_solutions_code__solutions_code_with_publish_solutions__should_not_raise(
        self,
    ) -> None:
        check_code_for_solutions_code(self.source_path_with_solutions, publish_solutions=True)

    def test_check_code_for_solutions_code__solutions_code_without_publish_solutions__should_raise(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            check_code_for_solutions_code(self.source_path_with_solutions, publish_solutions=False)

    def test_check_code_for_solutions_code__non_solutions_code_with_publish_solutions__should_not_raise(
        self,
    ) -> None:
        no_solutions_inside = Path("no_solutions_inside")
        no_solutions_inside.mkdir()
        check_code_for_solutions_code(no_solutions_inside, publish_solutions=False)
