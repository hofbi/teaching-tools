"""Cpp code evaluation jobs."""

import re
from pathlib import Path
from typing import ClassVar

import git

from sel_tools.code_evaluation.jobs.common import (
    EvaluationJob,
    run_shell_command,
    run_shell_command_with_output,
)
from sel_tools.config import CMAKE_MODULE_PATH, HW_BUILD_FOLDER
from sel_tools.file_export.copy_item import copy_item
from sel_tools.utils.config import CMAKELISTS_FILE_NAME
from sel_tools.utils.files import FileTree, FileVisitor


class CMakeBuildJob(EvaluationJob):
    """Job for compiling the project."""

    name = "CMake Build"

    def __init__(self, weight: int = 1, cmake_options: str = "") -> None:
        super().__init__(weight)
        self.__cmake_options = cmake_options

    def _run(self, repo_path: Path) -> int:
        build_folder = repo_path / HW_BUILD_FOLDER
        build_folder.mkdir(parents=True, exist_ok=True)
        if run_shell_command(f"cmake {self.__cmake_options} ..", build_folder) == 0:
            self._comment = f"CMake step failed with option {self.__cmake_options}: Make sure cmake .. passes."
            return 0
        if run_shell_command("make", build_folder) == 0:
            self._comment = "Make step failed: Make sure you build passes when calling make."
            return 0
        return 1


class MakeTestJob(EvaluationJob):
    """Job for running make test."""

    name = "Make Test"
    dependencies: ClassVar[list[EvaluationJob]] = [CMakeBuildJob()]

    def _run(self, repo_path: Path) -> int:
        build_folder = repo_path / HW_BUILD_FOLDER
        score, output = run_shell_command_with_output("make test", build_folder)
        if score != 0 and not output:
            self._comment = "No tests registered: Make sure you have tests registered in CMakeLists.txt."
            return 0
        if score != 0 and "No tests were found" in output:
            self._comment = "No tests were found: Make sure you have tests registered in CMakeLists.txt."
            return 0
        return score


class ClangFormatTestJob(EvaluationJob):
    """Job for checking the code format."""

    name = "Clang Format Check"

    def _run(self, repo_path: Path) -> int:
        return run_shell_command(
            rf"find . -type f -regex '.*\.\(cpp\|hpp\|cu\|c\|cc\|h\)' -not -path '*/{HW_BUILD_FOLDER}/*' "
            "| xargs clang-format --style=file -i --dry-run --Werror",
            repo_path,
        )


class CodeCoverageTestJob(EvaluationJob):
    """Job for checking the code coverage."""

    name = "Code Coverage"
    dependencies: ClassVar[list[EvaluationJob]] = [CMakeBuildJob(cmake_options="-DCMAKE_BUILD_TYPE=Debug")]

    def __init__(self, weight: int = 1, min_coverage: int = 75) -> None:
        super().__init__(weight)
        self.__min_coverage = min_coverage

    @staticmethod
    def parse_total_coverage(coverage_file: Path) -> int:
        coverage_file_pattern = r"TOTAL.*\s(\d*)%"
        text = coverage_file.read_text()
        coverage = re.search(coverage_file_pattern, text, re.DOTALL)
        return int(coverage.group(1)) if coverage else 0

    def _run(self, repo_path: Path) -> int:
        coverage_file = repo_path.resolve() / HW_BUILD_FOLDER / "report.txt"
        if (score := run_shell_command(f"gcovr -o {coverage_file}", repo_path)) == 0:
            self._comment = "Coverage failed report generation failed."
            return score
        coverage = self.parse_total_coverage(coverage_file)
        self._comment = f"Code coverage: {coverage}%. We require at least {self.__min_coverage}%."
        return int(coverage > self.__min_coverage)


class ClangTidyTestJob(EvaluationJob):
    """Job for checking with clang tidy."""

    name = "Clang Tidy Check"

    def _run(self, repo_path: Path) -> int:
        hw_cmake_module_path = repo_path / "hw_cmake"
        hw_cmake_module_path.mkdir(parents=True, exist_ok=True)
        copy_item(CMAKE_MODULE_PATH / "ClangTidy.cmake", hw_cmake_module_path / "ClangTidy.cmake")
        cmake_lists = repo_path / CMAKELISTS_FILE_NAME

        if not cmake_lists.exists():
            self._comment = (
                f"{CMAKELISTS_FILE_NAME} not found: Make sure you project has a {CMAKELISTS_FILE_NAME} file."
            )
            return 0

        content = cmake_lists.read_text()
        content += "\n"
        content += f"list(APPEND CMAKE_MODULE_PATH ${{PROJECT_SOURCE_DIR}}/{hw_cmake_module_path.stem})\n"
        content += "include(ClangTidy)\n"
        cmake_lists.write_text(content)
        score = CMakeBuildJob().run(repo_path)[-1].score
        git.Repo(repo_path).git.restore(".")  # Undo all changes
        return score


class CleanRepoJob(EvaluationJob):
    """Job for checking if build files were committed."""

    name = "Clean Repo Check"

    class CleanRepoVisitor(FileVisitor):
        """Check if build files are committed."""

        def __init__(self) -> None:
            self.__is_clean: bool = True
            self.__build_folder = f"/{HW_BUILD_FOLDER}/"
            self.__dirty_suffixes = [".make", ".includecache"]
            self.__dirty_file_names = ["CMakeCache.txt", "cmake_install.cmake"]
            self.__dirty_directories = ["/CMakeFiles/", ".dir/"]

        @property
        def is_clean(self) -> bool:
            return self.__is_clean

        def visit_file(self, file: Path) -> None:
            if self.__build_folder in str(file):
                return
            self.__is_clean = self.__is_clean and (
                file.name not in self.__dirty_file_names
                and file.suffix not in self.__dirty_suffixes
                and all(directory not in str(file) for directory in self.__dirty_directories)
            )

    class SourceFilesCountVisitor(FileVisitor):
        """Count the number of source files."""

        def __init__(self, max_source_file_count: int) -> None:
            self.__max_source_file_count = max_source_file_count
            self.__source_file_count = 0
            self.__build_folder = f"/{HW_BUILD_FOLDER}/"

        @property
        def is_below_max_source_file_count(self) -> bool:
            return self.__source_file_count < self.__max_source_file_count

        def visit_file(self, file: Path) -> None:
            if self.__build_folder in str(file):
                return
            self.__source_file_count += 1

    def _run(self, repo_path: Path) -> int:
        clean_repo_visitor = CleanRepoJob.CleanRepoVisitor()
        source_file_count_visitor = CleanRepoJob.SourceFilesCountVisitor(100)
        file_tree = FileTree(repo_path)
        file_tree.accept(clean_repo_visitor)
        file_tree.accept(source_file_count_visitor)
        if not clean_repo_visitor.is_clean:
            self._comment = (
                "We found build files committed to the repository. "
                "Make sure that any files produced by the build system are not committed. "
                "If you already have, make sure you remove them."
            )
            return 0
        if not source_file_count_visitor.is_below_max_source_file_count:
            self._comment = (
                "We found too many third party source files committed to the repository. "
                "Check if you really need them or if there is another way to include them."
            )
            return 0
        return 1
