"""Test copy item module."""

from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.file_export.config import EXPORT_IGNORE
from sel_tools.file_export.copy_item import copy_item


class CopyItemTest(TestCase):
    """Copy Item Test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

        self.source_folder = Path("source")
        self.fs.create_file(self.source_folder / "main.cpp")
        self.fs.create_file(self.source_folder / "include" / "header.h")
        self.fs.create_file(self.source_folder / "requirements.txt")

        self.dest_folder = Path("output")
        self.output_file1 = self.dest_folder / "main.cpp"
        self.output_file2 = self.dest_folder / "include" / "header.h"
        self.output_file3 = self.dest_folder / "requirements.txt"

    def test_copy_single_file(self) -> None:
        source_file = Path("src_file")
        dest_file = Path("dst_file")
        self.fs.create_file(source_file)

        copy_item(source_file, dest_file)

        self.assertTrue(dest_file.is_file())

    def test_copy_all_files_of_tree(self) -> None:
        copy_item(self.source_folder, self.dest_folder)
        self.assertTrue(self.output_file1.is_file())
        self.assertTrue(self.output_file2.is_file())
        self.assertTrue(self.output_file3.is_file())

    def test_copy_non_ignored_files_of_tree(self) -> None:
        ignore_file = self.source_folder / EXPORT_IGNORE
        self.fs.create_file(ignore_file, contents="**/*.txt\n\nconfig.cfg\nbuild/\n")

        # These files should be ignored given the above ignore file
        self.fs.create_file(self.source_folder / "nested" / "folder" / "log.txt")
        self.fs.create_file(self.source_folder / "config.cfg")
        self.fs.create_file(self.source_folder / "build" / "binary")
        self.fs.create_file(self.source_folder / "build" / "out.a")

        copy_item(self.source_folder, self.dest_folder)

        # Copied files
        self.assertTrue(self.output_file1.is_file())
        self.assertTrue(self.output_file2.is_file())

        # Ignored items
        self.assertFalse(self.output_file3.exists())
        self.assertFalse((self.dest_folder / "config.cfg").exists())
        self.assertFalse((self.dest_folder / "nested" / "folder" / "log.txt").exists())
        self.assertFalse((self.dest_folder / "build").exists())
        self.assertFalse((self.dest_folder / EXPORT_IGNORE).is_file())
