"""Tests for file export CLI argument parser."""

from pathlib import Path

from export_files import parse_arguments
from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import REPO_DIR


class ArgumentParserTest(TestCase):
    """Tests for file export CLI argument parser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_minimum_parameter_set(self) -> None:
        self.fs.create_dir("sources")
        args = parse_arguments("foo.py sources".split(" "))

        self.assertEqual(args.source_path, Path("sources"))
        self.assertEqual(args.output_dir, REPO_DIR / "export")
        self.assertFalse(args.keep_solutions)

    def test_maximum_parameter_set(self) -> None:
        self.fs.create_dir("sources")
        args = parse_arguments("foo.py sources -o output -k".split(" "))

        self.assertEqual(args.source_path, Path("sources"))
        self.assertEqual(args.output_dir, Path("output"))
        self.assertTrue(args.keep_solutions)

    def test_non_existent_sources_folder(self) -> None:
        with self.assertRaises(NotADirectoryError):
            parse_arguments("foo.py sources".split(" "))
