"""Diff creation module tests."""

import unittest
from datetime import date, datetime
from pathlib import Path

from sel_tools.diff_creation.create_diff import DiffCreator, create_diff
from tests.helper import GitTestCase


class CreateDiffTest(unittest.TestCase):
    """Create diff module test."""

    def test_create__diff_date_since_last_homework_none_should_return_empty_list(
        self,
    ) -> None:
        result = create_diff([Path()], None, None)

        self.assertListEqual([], result)

    def test_create__diff_date_since_last_homework_none_but_eval_date_should_return_empty_list(
        self,
    ) -> None:
        result = create_diff([Path()], None, date(2021, 11, 24))

        self.assertListEqual([], result)

    def test_create__diff_no_paths_should_return_empty_list(self) -> None:
        result = create_diff([], date(2021, 11, 17), date(2021, 11, 24))

        self.assertListEqual([], result)


class DiffCreatorTest(GitTestCase):
    """Diff Creator Test."""

    def setUp(self) -> None:
        super().setUp()
        self.repo.index.commit("init", commit_date=datetime(2021, 11, 11).isoformat())

    def test_create__init_repo_should_have_total_diff_only(self) -> None:
        unit = DiffCreator(self.repo_path)

        result = unit.create(date(2021, 11, 10), None)

        self.assertEqual(self.repo_path, result.repo_path)
        self.assertEqual(1, len(result.diffs))
        self.assertEqual("init", result.diffs[0].message)
        self.assertEqual("total", result.diffs[0].author)

    def test_create__no_commits_since_last_homework_should_have_no_diffs(self) -> None:
        unit = DiffCreator(self.repo_path)

        result = unit.create(date(2021, 11, 12), None)

        self.assertListEqual([], result.diffs)

    def test_create__three_commits_and_two_since_last_homework_should_have_two_plus_total_diffs(
        self,
    ) -> None:
        self.repo.index.commit("second", commit_date=datetime(2021, 11, 13).isoformat())
        self.repo.index.commit("third", commit_date=datetime(2021, 11, 14).isoformat())
        unit = DiffCreator(self.repo_path)

        result = unit.create(date(2021, 11, 12), None)

        self.assertEqual(3, len(result.diffs))
        self.assertEqual("total", result.diffs[0].author)
        self.assertEqual("third", result.diffs[1].message)
        self.assertEqual("second", result.diffs[2].message)

    def test_create__two_commits_and_two_since_last_homework_diff_should_be_adding_content(
        self,
    ) -> None:
        self.repo_path.joinpath("test.txt").touch()
        self.repo.index.add(["test.txt"])
        self.repo.index.commit(
            "add test.txt", commit_date=datetime(2021, 11, 13).isoformat()
        )
        self.repo_path.joinpath("test.txt").write_text("line 1\nline 2\nline 3\n")
        self.repo.index.add(["test.txt"])
        self.repo.index.commit(
            "edit test.txt", commit_date=datetime(2021, 11, 14).isoformat()
        )
        unit = DiffCreator(self.repo_path)

        result = unit.create(date(2021, 11, 12), None)

        self.assertIn("+line 1\n+line 2\n+line 3", result.diffs[1].patch)

    def test_create__three_commits_and_one_between_both_dates_should_have_one_plus_total_diffs(
        self,
    ) -> None:
        self.repo.index.commit("second", commit_date=datetime(2021, 11, 13).isoformat())
        self.repo.index.commit("third", commit_date=datetime(2021, 11, 15).isoformat())
        unit = DiffCreator(self.repo_path)

        result = unit.create(date(2021, 11, 12), date(2021, 11, 14))

        self.assertEqual(2, len(result.diffs))
        self.assertEqual("total", result.diffs[0].author)
        self.assertEqual("second", result.diffs[1].message)

    def test_create__commits_with_one_ignored_file_should_not_be_in_total_diff(
        self,
    ) -> None:
        self.repo.index.commit("commit", commit_date=datetime(2021, 11, 13).isoformat())
        self.repo_path.joinpath("test.txt").write_text("should be there\n")
        self.repo_path.joinpath("ignore.txt").write_text("ignore me\n")
        self.repo.index.add(["test.txt", "ignore.txt"])
        self.repo.index.commit(
            "add files", commit_date=datetime(2021, 11, 14).isoformat()
        )
        unit = DiffCreator(self.repo_path, exclude="ignore.txt")

        result = unit.create(date(2021, 11, 12), None)

        self.assertEqual(3, len(result.diffs))

        self.assertIn("should be there", result.diffs[0].patch)
        self.assertNotIn("ignore me", result.diffs[0].patch)

        self.assertIn("should be there", result.diffs[1].patch)
        self.assertIn("ignore me", result.diffs[1].patch)

    def test_create__commits_with_ignored_folder_should_not_be_in_total_diff(
        self,
    ) -> None:
        self.repo.index.commit("commit", commit_date=datetime(2021, 11, 13).isoformat())
        self.repo_path.joinpath("test.txt").write_text("should be there\n")
        build_folder = self.repo_path / "build"
        build_folder.mkdir(exist_ok=True, parents=True)
        build_folder.joinpath("ignore.txt").write_text("ignore me\n")
        build_folder.joinpath("test.txt").write_text("me too\n")
        self.repo.index.add(["test.txt", "build"])
        self.repo.index.commit(
            "add files and build", commit_date=datetime(2021, 11, 14).isoformat()
        )

        unit = DiffCreator(self.repo_path, exclude="build")
        result = unit.create(date(2021, 11, 12), None)

        self.assertEqual(3, len(result.diffs))

        self.assertIn("should be there", result.diffs[0].patch)
        self.assertNotIn("ignore me", result.diffs[0].patch)
        self.assertNotIn("me too", result.diffs[0].patch)

        self.assertIn("should be there", result.diffs[1].patch)
        self.assertIn("ignore me", result.diffs[1].patch)
        self.assertIn("me too", result.diffs[1].patch)
