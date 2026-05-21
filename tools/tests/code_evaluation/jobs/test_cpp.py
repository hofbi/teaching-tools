"""Cpp code evaluation jobs test."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.code_evaluation.jobs.cpp import (
    CMAKE_MODULE_PATH,
    HW_BUILD_FOLDER,
    ClangFormatTestJob,
    ClangTidyTestJob,
    CleanRepoJob,
    CMakeBuildJob,
    CodeCoverageTestJob,
    MakeTestJob,
    RelativeIncludeJob,
)
from sel_tools.utils.files import CMAKELISTS_FILE_NAME


def coverage_file_content(total_coverage: int) -> str:
    """Get coverage test file content."""
    return f"""
test/main.cpp                                  4       4   100%
test/simple_test.cpp                           3       3   100%
------------------------------------------------------------------------------
TOTAL                                       1131    1122    {total_coverage}%
------------------------------------------------------------------------------
"""


class CMakeBuildJobTest(TestCase):
    """Tests for CMake build job."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.unit = CMakeBuildJob()
        self.repo_path = Path("repo")
        self.build_folder = self.repo_path / HW_BUILD_FOLDER

    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command",
        MagicMock(return_value=1),
    )
    def test_run_impl_success(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(1, result[0].score)
        self.assertTrue(self.build_folder.is_dir())
        self.assertEqual("", result[0].comment)

    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command",
        MagicMock(return_value=0),
    )
    def test_run_impl_fail(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[0].score)
        self.assertTrue(self.build_folder.is_dir())
        self.assertIn("CMake", result[0].comment)

    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command",
        MagicMock(side_effect=[1, 0]),
    )
    def test_run_impl_fail_cmake_passed(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[0].score)
        self.assertTrue(self.build_folder.is_dir())
        self.assertNotIn("CMake step failed", result[0].comment)
        self.assertIn("Make step failed", result[0].comment)

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command")
    def test_call_with_cmake_options(self, mock: MagicMock) -> None:
        unit = CMakeBuildJob(cmake_options="-DARG_TEST=ON")
        unit.run(self.repo_path)
        self.assertIn("-DARG_TEST=ON", mock.call_args_list[0].args[0])
        self.assertEqual(2, len(mock.call_args_list))


class ClangTidyTestJobTest(TestCase):
    """Tests for the clang-tidy test job."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.unit = ClangTidyTestJob()
        self.repo_path = Path("repo")
        self.build_folder = self.repo_path / HW_BUILD_FOLDER
        self.fs.create_file(self.repo_path / ".clang-tidy")
        self.fs.create_file(CMAKE_MODULE_PATH / "ClangTidy.cmake")

    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command",
        MagicMock(return_value=1),
    )
    @patch("git.Repo", MagicMock())
    def test_run_impl_success(self) -> None:
        cmake_list = self.repo_path / CMAKELISTS_FILE_NAME
        self.fs.create_file(cmake_list)
        result = self.unit.run(self.repo_path)
        self.assertEqual(1, result[0].score)
        # This test only works because we mock git.Repo
        # otherwise the test would fail because the file is restored
        self.assertIn("include(ClangTidy)", cmake_list.read_text())

    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command",
        MagicMock(return_value=1),
    )
    def test_run_impl_fail_cmake_list_does_not_exist(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[0].score)
        self.assertIn("CMakeLists.txt not found", result[0].comment)

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command", MagicMock(return_value=1))
    def test_run_impl_fail_missing_clang_tidy_file(self) -> None:
        (self.repo_path / ".clang-tidy").unlink()
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[0].score)
        self.assertIn("`.clang-tidy` not found", result[0].comment)
        self.assertIn("Common pitfall", result[0].comment)


class ClangFormatTestJobTest(TestCase):
    """Tests for the clang-format test job."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.unit = ClangFormatTestJob()
        self.repo_path = Path("repo")
        self.fs.create_file(self.repo_path / ".clang-format")

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command", MagicMock(return_value=1))
    def test_run_impl_fail_missing_clang_format_file(self) -> None:
        (self.repo_path / ".clang-format").unlink()
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[0].score)
        self.assertIn("`.clang-format` not found", result[0].comment)
        self.assertIn("Common pitfall", result[0].comment)

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command", MagicMock(return_value=1))
    def test_run_impl_success(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(1, result[0].score)
        self.assertEqual("", result[0].comment)

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command", MagicMock(return_value=0))
    def test_run_impl_fail_formatting(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[0].score)
        self.assertIn("Clang format check failed", result[0].comment)


class MakeTestJobTest(TestCase):
    """Tests for make test job."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.unit = MakeTestJob()
        self.repo_path = Path("repo")

    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command",
        MagicMock(return_value=1),
    )
    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command_with_output",
        MagicMock(return_value=(1, "")),
    )
    def test_run_impl_with_empty_console_output_should_return_0(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[-1].score)

    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command",
        MagicMock(return_value=1),
    )
    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command_with_output",
        MagicMock(return_value=(1, "No tests were found!!!")),
    )
    def test_run_impl_with_no_tests_found_console_output_should_return_0(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[-1].score)

    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command",
        MagicMock(return_value=1),
    )
    @patch(
        "sel_tools.code_evaluation.jobs.cpp.run_shell_command_with_output",
        MagicMock(return_value=(1, "something")),
    )
    def test_run_impl_with_some_console_output_should_return_0(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(1, result[-1].score)


class CodeCoverageTestJobTest(TestCase):
    """Tests for code coverage."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.unit = CodeCoverageTestJob()
        self.repo_path = Path("repo")

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command_with_output", MagicMock(return_value=(1, "")))
    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command", MagicMock(return_value=0))
    def test_run_impl_failing_shell_command(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[-1].score)

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command_with_output", MagicMock(return_value=(1, "")))
    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command", MagicMock(return_value=1))
    @patch("sel_tools.code_evaluation.jobs.cpp.CodeCoverageTestJob.parse_total_coverage", MagicMock(return_value=95))
    def test_run_impl_success(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(1, result[-1].score)

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command_with_output", MagicMock(return_value=(1, "")))
    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command", MagicMock(return_value=1))
    @patch("sel_tools.code_evaluation.jobs.cpp.CodeCoverageTestJob.parse_total_coverage", MagicMock(return_value=15))
    def test_run_impl_fail_below_coverage_limit(self) -> None:
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[-1].score)

    def test_parse_total_coverage(self) -> None:
        for coverage in [0, 30, 95]:
            with (
                self.subTest(coverage),
                patch(
                    "pathlib.Path.read_text",
                    MagicMock(return_value=coverage_file_content(coverage)),
                ),
            ):
                self.assertEqual(coverage, self.unit.parse_total_coverage(Path()))

    @patch("pathlib.Path.read_text", MagicMock(return_value=""))
    def test_parse_total_coverage_empty_file(self) -> None:
        self.assertEqual(0, self.unit.parse_total_coverage(Path()))

    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command_with_output", MagicMock(return_value=(1, "")))
    @patch("sel_tools.code_evaluation.jobs.cpp.run_shell_command")
    def test_gcovr_runs_from_build_folder_with_correct_options(self, mock_run_shell_command: MagicMock) -> None:
        mock_run_shell_command.return_value = 1
        self.fs.create_file(self.repo_path / HW_BUILD_FOLDER / "report.txt", contents=coverage_file_content(95))
        self.unit.run(self.repo_path)
        # gcovr should be called with correct options from build folder
        gcovr_call = mock_run_shell_command.call_args_list[-1]
        gcovr_cmd = gcovr_call.args[0]
        gcovr_cwd = gcovr_call.args[1]
        self.assertIn("--root", gcovr_cmd)
        self.assertIn("--exclude _deps", gcovr_cmd)
        self.assertEqual(self.repo_path / HW_BUILD_FOLDER, gcovr_cwd)


class CleanRepoJobTest(TestCase):
    """Tests for clean repo."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.unit = CleanRepoJob()
        self.repo_path = Path("repo")
        self.clean_files = [
            self.repo_path / "CMakeLists.txt",
            self.repo_path / "main.cpp",
            self.repo_path / "test" / "main.cpp",
            self.repo_path / "include" / "header.h",
        ]
        self.dirty_files = [
            self.repo_path / "CMakeCache.txt",
            self.repo_path / "cmake_install.cmake",
            self.repo_path / "foo.make",
            self.repo_path / "CXX.includecache",
            self.repo_path / "CMakeFiles" / "DependInfo.cmake",
            self.repo_path / "foo.dir" / "DependInfo.cmake",
        ]
        self.clean_files_with_build_folder = [
            *self.clean_files,
            self.repo_path / HW_BUILD_FOLDER / "cmake_install.cmake",
        ]

    def __create_repo(self, files: list[Path]) -> None:
        for file in files:
            self.fs.create_file(file)

    def test_clean_repo_visitor_no_files(self) -> None:
        visitor = CleanRepoJob.CleanRepoVisitor()
        self.assertTrue(visitor.is_clean)

    def test_clean_repo_visitor_source_files_only(self) -> None:
        for file in self.clean_files:
            with self.subTest(file):
                visitor = CleanRepoJob.CleanRepoVisitor()
                visitor.visit_file(file)
                self.assertTrue(visitor.is_clean)

    def test_clean_repo_visitor_build_files_only(self) -> None:
        for file in self.dirty_files:
            with self.subTest(file):
                visitor = CleanRepoJob.CleanRepoVisitor()
                visitor.visit_file(file)
                self.assertFalse(visitor.is_clean)

    def test_clean_repo_visitor_clean_files_with_build_folder(self) -> None:
        for file in self.clean_files_with_build_folder:
            with self.subTest(file):
                visitor = CleanRepoJob.CleanRepoVisitor()
                visitor.visit_file(file)
                self.assertTrue(visitor.is_clean)

    def test_source_file_count_visitor_no_files(self) -> None:
        visitor = CleanRepoJob.SourceFilesCountVisitor(10)
        self.assertTrue(visitor.is_below_max_source_file_count)

    def test_source_file_count_visitor_limit_at_one_and_four_visits_should_be_false(
        self,
    ) -> None:
        visitor = CleanRepoJob.SourceFilesCountVisitor(1)
        for file in self.clean_files:
            visitor.visit_file(file)
        self.assertFalse(visitor.is_below_max_source_file_count)

    def test_source_file_count_visitor_limit_at_ten_and_four_visits_should_be_false(
        self,
    ) -> None:
        visitor = CleanRepoJob.SourceFilesCountVisitor(10)
        for file in self.clean_files:
            visitor.visit_file(file)
        self.assertTrue(visitor.is_below_max_source_file_count)

    def test_source_file_count_visitor_visiting_only_build_files_should_be_true(
        self,
    ) -> None:
        visitor = CleanRepoJob.SourceFilesCountVisitor(1)
        visitor.visit_file(self.repo_path / HW_BUILD_FOLDER / "point.cpp")
        visitor.visit_file(self.repo_path / HW_BUILD_FOLDER / "angle.cpp")
        self.assertTrue(visitor.is_below_max_source_file_count)

    def test_clean_repo_visitor_source_and_build_files(self) -> None:
        visitor = CleanRepoJob.CleanRepoVisitor()
        for file in self.dirty_files + self.clean_files:
            visitor.visit_file(file)
        self.assertFalse(visitor.is_clean)

    def test_run_impl_dirty_files_should_fail(self) -> None:
        self.__create_repo(self.dirty_files)
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[0].score)

    def test_run_impl_clean_files_should_pass(self) -> None:
        self.__create_repo(self.clean_files)
        result = self.unit.run(self.repo_path)
        self.assertEqual(1, result[0].score)


class RelativeIncludeJobTest(TestCase):
    """Tests for relative include check."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.unit = RelativeIncludeJob()
        self.repo_path = Path("repo")

    def test_visitor_no_relative_include_returns_no_offending_files(self) -> None:
        visitor = RelativeIncludeJob.RelativeIncludeVisitor()
        visitor.visit_file(
            Path(self.fs.create_file(self.repo_path / "main.cpp", contents="#include <gtest/gtest.h>\n").path)
        )
        self.assertEqual([], visitor.offending_files)

    def test_visitor_with_relative_include_returns_offending_file(self) -> None:
        visitor = RelativeIncludeJob.RelativeIncludeVisitor()
        cpp_file = Path(self.fs.create_file(self.repo_path / "main.cpp", contents='#include "../include/foo.h"\n').path)
        visitor.visit_file(cpp_file)
        self.assertEqual([cpp_file], visitor.offending_files)

    def test_visitor_with_current_dir_relative_include_returns_offending_file(self) -> None:
        visitor = RelativeIncludeJob.RelativeIncludeVisitor()
        cpp_file = Path(self.fs.create_file(self.repo_path / "main.cpp", contents='#include "./foo/bar.h"\n').path)
        visitor.visit_file(cpp_file)
        self.assertEqual([cpp_file], visitor.offending_files)

    def test_visitor_skips_non_cpp_files(self) -> None:
        visitor = RelativeIncludeJob.RelativeIncludeVisitor()
        visitor.visit_file(
            Path(self.fs.create_file(self.repo_path / "CMakeLists.txt", contents='#include "../foo"\n').path)
        )
        self.assertEqual([], visitor.offending_files)

    def test_run_no_relative_includes_should_pass(self) -> None:
        self.fs.create_file(
            self.repo_path / "src" / "main.cpp", contents="#include <angle.h>\n#include <gtest/gtest.h>\n"
        )
        result = self.unit.run(self.repo_path)
        self.assertEqual(1, result[0].score)
        self.assertEqual("", result[0].comment)

    def test_run_with_relative_include_should_fail(self) -> None:
        self.fs.create_file(
            self.repo_path / "test" / "angle_test.cpp",
            contents='#include "../include/angle.h"\n#include <gtest/gtest.h>\n',
        )
        result = self.unit.run(self.repo_path)
        self.assertEqual(0, result[0].score)
        self.assertIn("Relative include", result[0].comment)
        self.assertIn("angle_test.cpp", result[0].comment)
