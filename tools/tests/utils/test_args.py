"""Test args module."""

import unittest
from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.utils.args import ArgumentParserFactory, dir_path, file_path


class ArgsTest(TestCase):
    """Args test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_dir_path__is_dir__input_path(self) -> None:
        self.fs.create_dir("test")
        self.assertEqual(Path("test"), dir_path("test"))

    def test_dir_path__is_file__raise_not_a_directory_error(self) -> None:
        self.fs.create_file("test")
        with self.assertRaises(NotADirectoryError):
            dir_path("test")

    def test_dir_path__does_not_exist__raise_not_a_directory_error(self) -> None:
        with self.assertRaises(NotADirectoryError):
            dir_path("test")

    def test_file_path__is_dir__input_path(self) -> None:
        self.fs.create_file("test.txt")
        self.assertEqual(Path("test.txt"), file_path("test.txt"))

    def test_file_path__is_file__raise_file_not_found_error(self) -> None:
        self.fs.create_dir("test")
        with self.assertRaises(FileNotFoundError):
            file_path("test")

    def test_file_path__does_not_exist__raise_file_not_found_error(self) -> None:
        with self.assertRaises(FileNotFoundError):
            file_path("test")


class ArgumentParserFactoryTest(unittest.TestCase):
    """Argument parser factory test."""

    def test_default_or_required_if_none__for_none_should_be_required_true(
        self,
    ) -> None:
        self.assertDictEqual(
            {"required": True}, ArgumentParserFactory.default_or_required_if_none(None)
        )

    def test_default_or_required_if_none__for_not_none_should_be_default(self) -> None:
        self.assertDictEqual(
            {"default": "test"},
            ArgumentParserFactory.default_or_required_if_none("test"),
        )
