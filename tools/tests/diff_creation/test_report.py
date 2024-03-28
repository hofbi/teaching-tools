"""Diff report tests."""

from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.diff_creation.report import Diff, DiffReport, write_diff_reports


class ReportTest(TestCase):
    """Report module test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_write_diff_reports_for_empty_list_should_write_nothing(self) -> None:
        write_diff_reports([], "report")
        self.assertEqual(0, self.fs.get_disk_usage().used)

    def test_write_diff_reports_for_one_item_without_diffs_should_write_csv_only(
        self,
    ) -> None:
        self.fs.create_dir("report")

        write_diff_reports([DiffReport(Path("report"), [])], "base")

        self.assertTrue(Path("report/base.csv").exists())

    def test_write_diff_reports_for_one_item_with_2_diffs_should_write_csv_and_2_patches(
        self,
    ) -> None:
        self.fs.create_dir("report")

        write_diff_reports(
            [DiffReport(Path("report"), [Diff("a", "a", "a", "a"), Diff("b", "b", "b", "b")])],
            "base",
        )

        self.assertTrue(Path("report/base.csv").exists())
        self.assertEqual(2, len(list(Path("report").glob("*.patch"))))


class DiffReportTest(TestCase):
    """Diff report test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.path = Path("report")
        self.fs.create_dir(self.path)

    def test_generate_overview_table_without_diffs_should_contain_only_header(
        self,
    ) -> None:
        unit = DiffReport(self.path, [])

        table = unit.generate_overview_table()

        self.assertTrue(table.empty)

    def test_generate_overview_table_with_two_diffs_should_contain_two_diff_rows(
        self,
    ) -> None:
        unit = DiffReport(
            self.path,
            [
                Diff("abc", "author", "foo bar", ""),
                Diff("xyz", "paul", "blub", ""),
            ],
        )

        table = unit.generate_overview_table()

        self.assertIn("abc", table.values)
        self.assertIn("author", table.values)
        self.assertIn("foo bar", table.values)
        self.assertIn("xyz", table.values)
        self.assertIn("paul", table.values)
        self.assertIn("blub", table.values)

    def test_write_diff_patches_without_diffs_should_write_nothing(self) -> None:
        unit = DiffReport(self.path, [])

        unit.write_diff_patches()

        self.assertEqual(0, self.fs.get_disk_usage().used)

    def test_write_diff_patches_for_two_diffs_should_write_2_patches_and_2_html(
        self,
    ) -> None:
        unit = DiffReport(self.path, [Diff("a", "a", "a", "a"), Diff("b", "b", "b", "b")])

        unit.write_diff_patches()

        self.assertEqual(2, len(list(Path("report").glob("*.patch"))))
        self.assertEqual(2, len(list(Path("report").glob("*.html"))))

    def test_write_diff_patches_one_diff_should_write_one_patch_and_one_html(
        self,
    ) -> None:
        unit = DiffReport(self.path, [Diff("abc", "author", "foo bar", "+++a\n---b")])

        unit.write_diff_patches()

        self.assertIn("+++a\n---b", self.path.joinpath("0-abc.patch").read_text())
        self.assertIn("+++a", self.path.joinpath("0-abc.html").read_text())
        self.assertIn("---b", self.path.joinpath("0-abc.html").read_text())
