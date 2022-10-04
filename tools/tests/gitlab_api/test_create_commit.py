"""Tests for gitlab repo creation."""

import json
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import GIT_MAIN_BRANCH, GITLAB_SERVER_URL
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
            create_gitlab_commit_data_with_all_files_from(
                self.input_dir, "Commit message"
            ),
        )

    def test_create_gitlab_commit_data_with_all_files_from_filled_folder(self) -> None:
        self.fs.create_file(self.input_dir / "README.md", contents="Initial readme")
        self.fs.create_file(
            self.input_dir / "include" / "header.h", contents="#define if while"
        )

        actions = create_gitlab_commit_data_with_all_files_from(
            self.input_dir, "Initial commit"
        )

        self.assertDictEqual(
            actions,
            {
                "branch": GIT_MAIN_BRANCH,
                "commit_message": "Initial commit",
                "actions": [
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
            },
        )

    @patch("sel_tools.gitlab_api.comment_issue.create_comment")
    def test_create_upload_files(self, mock_create_commit: MagicMock) -> None:
        student_repos_file = Path("student_repos.json")
        self.fs.create_file(
            student_repos_file,
            contents=json.dumps([{"id": 234, "name": ""}, {"id": 567, "name": ""}]),
        )
        source_folder = Path("source")
        self.fs.create_dir(source_folder)
        self.fs.create_file(source_folder / "test.txt")

        with patch("gitlab.Gitlab", MagicMock(return_value=MagicMock())) as mock_gitlab:
            upload_files(source_folder, student_repos_file, "my_gitlab_token")

            mock_gitlab.assert_called_once_with(
                GITLAB_SERVER_URL, private_token="my_gitlab_token"
            )
        expected_calls = [
            call(source_folder, f"Add {source_folder}", student_repo_id)
            for student_repo_id in [234, 567]
        ]
        mock_create_commit.has_calls(expected_calls, any_order=True)
