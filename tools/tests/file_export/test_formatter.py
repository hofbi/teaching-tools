"""Tests for formatter."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.file_export.formatter import (
    FormatterVisitor,
    apply_clang_format,
    apply_cmake_format,
)


class FormatterTest(TestCase):
    """Tests for formatter functions."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    @patch("sel_tools.file_export.formatter.apply_cmake_format")
    def test_cmake_format__is_cmake_lists__should_format(
        self, cmake_format_mock: MagicMock
    ) -> None:
        self.fs.create_file("CMakeLists.txt")

        unit = FormatterVisitor()
        unit.visit_file(Path("CMakeLists.txt"))

        cmake_format_mock.assert_called_once_with(Path("CMakeLists.txt"))

    @patch("sel_tools.file_export.formatter.apply_cmake_format")
    def test_cmake_format__is_cmake_module__should_format(
        self, cmake_format_mock: MagicMock
    ) -> None:
        self.fs.create_file("FooBar.cmake")

        unit = FormatterVisitor()
        unit.visit_file(Path("FooBar.cmake"))

        cmake_format_mock.assert_called_once_with(Path("FooBar.cmake"))

    @patch("sel_tools.file_export.formatter.apply_cmake_format")
    def test_cmake_format__is_cmake_lists__should_not_format(
        self, cmake_format_mock: MagicMock
    ) -> None:
        self.fs.create_file("some_thing.txt")

        unit = FormatterVisitor()
        unit.visit_file(Path("some_thing.txt"))

        cmake_format_mock.assert_not_called()

    def test_clang_format__is_cpp__should_format(self) -> None:
        for file in ["foo.h", "bar.hpp", "blub.cpp"]:
            with self.subTest(file):
                with patch(
                    "sel_tools.file_export.formatter.apply_clang_format"
                ) as clang_format_mock:
                    self.fs.create_file(file)

                    unit = FormatterVisitor()
                    unit.visit_file(Path(file))

                    clang_format_mock.assert_called_once_with(Path(file))

    @patch("sel_tools.file_export.formatter.apply_clang_format")
    def test_clang_format__is_not_cpp__should_not_format(
        self, clang_format_mock: MagicMock
    ) -> None:
        self.fs.create_file("some_thing.txt")

        unit = FormatterVisitor()
        unit.visit_file(Path("some_thing.txt"))

        clang_format_mock.assert_not_called()

    @staticmethod
    def test_apply_clang_format() -> None:
        file = Path("test_file")
        with patch("sel_tools.file_export.formatter.which", lambda _: True), patch(
            "sel_tools.file_export.formatter.run", MagicMock()
        ) as run_mock:
            apply_clang_format(file)
            run_mock.assert_called_once_with(
                "clang-format -i test_file", shell=True, check=True
            )

    @staticmethod
    def test_apply_cmake_format() -> None:
        file = Path("test_file")
        with patch("sel_tools.file_export.formatter.which", lambda _: True), patch(
            "sel_tools.file_export.formatter.run", MagicMock()
        ) as run_mock:
            apply_cmake_format(file)
            run_mock.assert_called_once_with(
                "cmake-format -i test_file", shell=True, check=True
            )
