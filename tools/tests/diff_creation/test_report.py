"""Diff report tests."""

from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.diff_creation.report import Diff, DiffReport, write_diff_reports, write_report_for_inactive_student_repos


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

    def test_write_report_for_inactive_student_repos__no_report__should_write_nothing(
        self,
    ) -> None:
        self.fs.create_dir("report")

        write_report_for_inactive_student_repos([], Path("report"))

        self.assertFalse(Path("report", "inactive_student_repos.md").exists())

    def test_write_report_for_inactive_student_repos__with_diffs__should_write_nothing(self) -> None:
        self.fs.create_dir("report")

        write_report_for_inactive_student_repos([DiffReport(Path("report", "repo"), [])], Path("report"))

        self.assertTrue(Path("report", "inactive_student_repos.md").exists())
        self.assertIn("repo", Path("report", "inactive_student_repos.md").read_text())

    def test_write_report_for_inactive_student_repos__with_diffs__should_write_report(self) -> None:
        self.fs.create_dir("report")

        write_report_for_inactive_student_repos(
            [DiffReport(Path("report", "repo"), [Diff("a", "a", "a", "a")])], Path("report")
        )

        self.assertFalse(Path("report", "inactive_student_repos.md").exists())


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

    def test_write_diff_patches_with_unicode_surrogates_should_handle_gracefully(
        self,
    ) -> None:
        problematic_patch = "+++a\n---b\n" + "\udce0\udce1\udce2"
        unit = DiffReport(self.path, [Diff("def", "author", "unicode test", problematic_patch)])

        unit.write_diff_patches()

        patch_content = self.path.joinpath("0-def.patch").read_text()
        self.assertIn("+++a", patch_content)
        self.assertIn("---b", patch_content)
        self.assertIsInstance(
            patch_content, str, msg="Surrogate characters should be replaced, content should be readable"
        )
        html_content = self.path.joinpath("0-def.html").read_text()
        self.assertIn("+++a", html_content)
        self.assertIsInstance(html_content, str)

    def test_has_diffs__empty_diffs__should_return_false(self) -> None:
        unit = DiffReport(self.path, [])

        self.assertFalse(unit.has_diffs)

    def test_has_diffs__with_diffs__should_return_true(self) -> None:
        unit = DiffReport(self.path, [Diff("a", "a", "a", "a"), Diff("b", "b", "b", "b")])

        self.assertTrue(unit.has_diffs)
