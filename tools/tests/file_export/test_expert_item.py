"""Export item module tests."""

from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.file_export.config import EXPORT_BEGIN, EXPORT_END
from sel_tools.file_export.export_item import export_items, visit_exported_item

TEST_CONTENT = f"""
// {EXPORT_BEGIN}
// foo bar
// {EXPORT_END}
// always there
"""


class ExportFilesTest(TestCase):
    """Test for file export main module functions."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.exported_item = Path("export")
        self.fs.create_dir(self.exported_item)
        self.test_file = self.exported_item / "test.cpp"
        self.fs.create_file(str(self.test_file), contents=TEST_CONTENT)

    def test_visit_exported_item_keep_solutions_should_be_there(self) -> None:
        visit_exported_item(self.exported_item, keep_solutions=True)

        self.assertIn("foo bar", self.test_file.read_text())
        self.assertIn("always there", self.test_file.read_text())

    def test_visit_exported_item_remove_solutions_should_be_removed(self) -> None:
        visit_exported_item(self.exported_item, keep_solutions=False)

        self.assertNotIn("foo bar", self.test_file.read_text())
        self.assertIn("always there", self.test_file.read_text())

    def test_visit_exported_item_remove_solutions_empty_file_still_empty(self) -> None:
        self.fs.create_dir("foo")
        self.fs.create_file("foo/empty.txt")

        visit_exported_item(Path("foo"), keep_solutions=False)

        self.assertEqual("", Path("foo/empty.txt").read_text())

    def test_export_items_empty_repo_list_nothing_exported(self) -> None:
        disk_usage_before = self.fs.get_disk_usage().used

        export_items(self.exported_item, [], False)

        self.assertEqual(disk_usage_before, self.fs.get_disk_usage().used)

    def test_export_items_two_repos_correctly_exported(self) -> None:
        self.fs.create_dir("repo1")
        self.fs.create_dir("repo2")

        export_items(self.exported_item, [Path("repo1"), Path("repo2")], False)

        self.assertTrue(Path("repo1").joinpath("test.cpp").exists())
        self.assertTrue(Path("repo2").joinpath("test.cpp").exists())
