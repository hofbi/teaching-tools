"""Tests for gitlab commit creation."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import AVATAR_PATH, GITLAB_SERVER_URL
from sel_tools.gitlab_api.create_repo import (
    create_repos,
    get_repo_settings,
    store_student_repo_info_to_config_file,
)

from tests.helper import GitlabGroupFake


class CreateRepoTest(TestCase):
    """Tests for gitlab repo creation."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file(AVATAR_PATH)
        self.input_dir = Path("input")
        self.fs.create_dir(self.input_dir)

    def test_create_repos(self) -> None:
        mock_protected_branch = MagicMock()
        mock_protected_branch.name = "master"
        mock_project = MagicMock()
        mock_project.protectedbranches.create.return_value = mock_protected_branch
        mock_instance = MagicMock()
        mock_instance.projects.create.return_value = mock_project
        mock_instance.groups.get.return_value = GitlabGroupFake("group")

        with patch("gitlab.Gitlab", MagicMock(return_value=mock_instance)) as mock_gitlab:
            student_repos, group_name = create_repos(
                self.input_dir,
                "base_name",
                3425,
                3,
                "my_gitlab_token",
            )

        mock_gitlab.assert_called_once_with(GITLAB_SERVER_URL, private_token="my_gitlab_token")

        self.assertEqual(len(student_repos), 3)
        self.assertEqual("group", group_name)
        for student_repo in student_repos:
            self.assertIn("name", student_repo)
            self.assertIn("id", student_repo)
            self.assertIn("branch", student_repo)
            self.assertEqual(student_repo["branch"], "master")

    def test_store_student_repo_info_to_config_file(self) -> None:
        repo_info_dir = Path("config")
        self.fs.create_dir(repo_info_dir)

        config_file = store_student_repo_info_to_config_file(repo_info_dir, "group_name", [{"id": 1}, {"id": 2}])

        self.assertTrue(config_file.is_file())
        config_file_content = json.loads(config_file.read_text())
        self.assertListEqual(config_file_content, [{"id": 1}, {"id": 2}])

    def test_get_repo_settings(self) -> None:
        self.assertDictEqual(
            get_repo_settings(3234, "my_repo", 4),
            {
                "name": "my_repo_4",
                "description": "Software Engineering Lab Homework Group 4",
                "namespace_id": 3234,
                "jobs_enabled": True,
            },
        )
