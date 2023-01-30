"""Tests for file utils."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, call

from pyfakefs.fake_filesystem_unittest import TestCase as FsTestCase
from sel_tools.utils.files import FileTree, FileVisitor, is_cmake, is_cpp


class FileVisitorTest(unittest.TestCase):
    """Test for abstract file visitor class."""

    def test_abstract(self) -> None:
        with self.assertRaises(NotImplementedError):
            unit = FileVisitor()  # type: ignore[abstract]
            unit.visit_file(Path())


class FileTreeTest(FsTestCase):
    """Tests recursive function caller function."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

        self.visitor_mock = MagicMock()
        self.visitor_mock.visit_file = MagicMock()

        self.folder = Path("folder")
        self.file1 = self.folder / "file"
        self.fs.create_file(self.file1)
        self.nested_folder = self.folder / "nested"
        self.file2 = self.nested_folder / "other_file"
        self.fs.create_file(self.file2)

    def test_call_recursive_solution_remover_on_file(self) -> None:
        unit = FileTree(self.file1)
        unit.accept(self.visitor_mock)
        self.visitor_mock.visit_file.assert_called_once_with(self.file1)

    def test_call_recursive_solution_remover_on_folder(self) -> None:
        unit = FileTree(self.folder)
        unit.accept(self.visitor_mock)
        self.visitor_mock.visit_file.assert_has_calls(
            [call(self.file1), call(self.file2)]
        )

    def test_call_recursive_solution_remover_on_folder_ignore_git(self) -> None:
        git_folder = self.folder / ".git"
        self.fs.create_file(git_folder / "ignore_file")
        self.fs.create_file(git_folder / "sub_dir" / "ignore_file")
        self.fs.create_file(self.folder / ".gitignore")

        unit = FileTree(self.folder)
        unit.accept(self.visitor_mock)

        self.assertNotIn(
            call(git_folder / "ignore_file"),
            self.visitor_mock.visit_file.call_args_list,
        )
        self.assertNotIn(
            call(git_folder / "sub_dir" / "ignore_file"),
            self.visitor_mock.visit_file.call_args_list,
        )
        self.assertIn(
            call(self.folder / ".gitignore"),
            self.visitor_mock.visit_file.call_args_list,
        )

    def test_call_recursive_solution_remover_on_not_existing_item_raise(self) -> None:
        unit = FileTree(Path("should_not_exist"))
        with self.assertRaises(FileNotFoundError):
            unit.accept(self.visitor_mock)
        self.visitor_mock.visit_file.assert_not_called()

    def test_rglob_but(self) -> None:
        self.fs.create_file(self.folder / ".gitignore")
        paths = list(FileTree(self.folder).rglob_but(".git"))
        self.assertListEqual(
            paths,
            sorted(
                [self.file1, self.file2, self.folder / ".gitignore", self.nested_folder]
            ),
        )


class FileTypeTest(unittest.TestCase):
    """Tests for functions determining the file type."""

    def test_is_cpp(self) -> None:
        for file in ["src/main.cpp", "header.h", "header.hpp"]:
            with self.subTest(file):
                self.assertTrue(is_cpp(Path(file)))

    def test_is_not_cpp(self) -> None:
        for file in ["main.cxx", "src/main.c", "main.CPP"]:
            with self.subTest(file):
                self.assertFalse(is_cpp(Path(file)))

    def test_is_cmake(self) -> None:
        for file in ["src/CMakeLists.txt", "cmake/gtest.cmake", "txt.cmake"]:
            with self.subTest(file):
                self.assertTrue(is_cmake(Path(file)))

    def test_is_not_cmake(self) -> None:
        for file in ["cmakelists.txt", "cmake/other.txt"]:
            with self.subTest(file):
                self.assertFalse(is_cmake(Path(file)))
