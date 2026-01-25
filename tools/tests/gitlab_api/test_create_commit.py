"""Tests for gitlab repo creation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import GIT_MAIN_BRANCH
from sel_tools.gitlab_api.create_commit import (
    create_gitlab_commit_data_with_all_files_from,
    upload_files,
)


class CreateCommitTest(TestCase):
    """Tests for gitlab repo creation."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.input_dir = Path("input")
        self.fs.create_dir(self.input_dir)

    def tearDown(self) -> None:
        create_gitlab_commit_data_with_all_files_from.cache_clear()

    def test_create_gitlab_commit_data_with_all_files_from_empty_folder(self) -> None:
        self.assertDictEqual(
            {},
            create_gitlab_commit_data_with_all_files_from(self.input_dir, "Commit message", GIT_MAIN_BRANCH),
        )

    def test_create_gitlab_commit_data_with_all_files_from_filled_folder(self) -> None:
        self.fs.create_file(self.input_dir / "README.md", contents="Initial readme")
        self.fs.create_file(self.input_dir / "include" / "header.h", contents="#define if while")

        actions = create_gitlab_commit_data_with_all_files_from(self.input_dir, "Initial commit", GIT_MAIN_BRANCH)

        self.assertEqual(actions["branch"], GIT_MAIN_BRANCH)
        self.assertEqual(actions["commit_message"], "Initial commit")
        self.assertEqual(len(actions["actions"]), 2)

        actual_actions_sorted = sorted(actions["actions"], key=lambda x: x["file_path"])
        expected_actions_sorted = sorted(
            [
                {
                    "action": "create",
                    "content": "Initial readme",
                    "file_path": "README.md",
                },
                {
                    "action": "create",
                    "content": "#define if while",
                    "file_path": "include/header.h",
                },
            ],
            key=lambda x: x["file_path"],
        )
        self.assertEqual(actual_actions_sorted, expected_actions_sorted)

    def test_create_gitlab_commit_with_file_on_different_branch(self) -> None:
        self.fs.create_file(self.input_dir / "README.md", contents="Initial readme")

        actions = create_gitlab_commit_data_with_all_files_from(self.input_dir, "Initial commit", "other_branch")

        self.assertDictEqual(
            actions,
            {
                "branch": "other_branch",
                "commit_message": "Initial commit",
                "actions": [
                    {
                        "action": "create",
                        "content": "Initial readme",
                        "file_path": "README.md",
                    }
                ],
            },
        )

    @patch("sel_tools.gitlab_api.create_commit.create_commit")
    def test_create_upload_files(self, mock_create_commit: MagicMock) -> None:
        student_repos = [{"id": 234, "name": ""}, {"id": 567, "name": ""}]
        source_folder = Path("source")
        self.fs.create_dir(source_folder)
        self.fs.create_file(source_folder / "test.txt")

        upload_files(source_folder, student_repos, MagicMock())

        self.assertEqual(2, mock_create_commit.call_count)
