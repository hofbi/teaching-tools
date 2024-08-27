"""Cpp code evaluation jobs."""

import re
from pathlib import Path
from typing import ClassVar

from sel_tools.code_evaluation.jobs.common import (
    EvaluationJob,
    run_shell_command,
    run_shell_command_with_output,
)
from sel_tools.config import CMAKE_MODULE_PATH, HW_BUILD_FOLDER
from sel_tools.file_export.copy_item import copy_item
from sel_tools.utils.config import CMAKELISTS_FILE_NAME
from sel_tools.utils.files import FileTree, FileVisitor, is_cpp


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
            self._comment = f"CMake step failed with option {self.__cmake_options}"
            return 0
        if run_shell_command("make", build_folder) == 0:
            self._comment = "Make step failed"
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
            self._comment = "No tests registered"
            return 0
        if score != 0 and "No tests were found" in output:
            self._comment = "No tests were found"
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
            self._comment = "Coverage failed"
            return score
        coverage = self.parse_total_coverage(coverage_file)
        self._comment = f"Code coverage: {coverage}%"
        return int(coverage > self.__min_coverage)


class ClangTidyTestJob(EvaluationJob):
    """Job for checking with clang tidy."""

    name = "Clang Tidy Check"

    def _run(self, repo_path: Path) -> int:
        copy_item(CMAKE_MODULE_PATH, repo_path)
        cmake_lists = repo_path / CMAKELISTS_FILE_NAME

        if not cmake_lists.exists():
            self._comment = f"{CMAKELISTS_FILE_NAME} not found"
            return 0

        content = cmake_lists.read_text()
        content += "\n"
        content += f"list(APPEND CMAKE_MODULE_PATH ${{PROJECT_SOURCE_DIR}}/{CMAKE_MODULE_PATH.stem})\n"
        content += "include(ClangTidy)\n"
        cmake_lists.write_text(content)
        return CMakeBuildJob().run(repo_path)[-1].score


class OOPTestJob(EvaluationJob):
    """Job for checking if all OOP is used."""

    name = "OOP Check"

    class OOPVisitor(FileVisitor):
        """Check if given cpp files are OOP."""

        def __init__(self) -> None:
            self.__struct_usages: int = 0

        @property
        def is_oop(self) -> bool:
            return self.__struct_usages == 0

        def visit_file(self, file: Path) -> None:
            if is_cpp(file):
                cpp_content = file.read_text()
                self.__struct_usages += self.find_struct_usages(cpp_content)

        @staticmethod
        def find_struct_usages(file_content: str) -> int:
            # TODO this is probably a very weak check
            # but we can improve in the future with more checks
            return len(re.findall(r"\sstruct\s", file_content, re.DOTALL))

    def _run(self, repo_path: Path) -> int:
        oop_visitor = OOPTestJob.OOPVisitor()
        FileTree(repo_path).accept(oop_visitor)
        return int(oop_visitor.is_oop)


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
            self._message = "Build files committed"
            return 0
        if not source_file_count_visitor.is_below_max_source_file_count:
            self._message = "Committed to many third party source file"
            return 0
        return 1
