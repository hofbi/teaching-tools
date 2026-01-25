"""Tests for gitlab commit creation."""

from pathlib import Path
from unittest.mock import MagicMock

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.gitlab_api.create_repo import (
    AVATAR_PATH,
    create_repos,
    get_repo_settings,
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

        student_repos, group_name = create_repos(self.input_dir, "base_name", 3425, 3, mock_instance)

        self.assertEqual(len(student_repos), 3)
        self.assertEqual("group", group_name)
        for student_repo in student_repos:
            self.assertIn("name", student_repo)
            self.assertIn("id", student_repo)
            self.assertIn("branch", student_repo)
            self.assertEqual(student_repo["branch"], "master")

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
