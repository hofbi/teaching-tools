"""Test repository fetching module."""

import json
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import GITLAB_SERVER_URL
from sel_tools.gitlab_api.fetch_repo import fetch_repo, fetch_repos
from sel_tools.utils.repo import GitlabProject, GitRepo


class FetchRepoTest(TestCase):
    """Fetch repo test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.workspace = Path("workspace")
        self.student_repos_file = Path("student_repos.json")
        self.student_repos_file_content = [
            {"id": 234, "name": "foo"},
            {"id": 567, "name": "bar"},
        ]
        self.fs.create_file(
            self.student_repos_file,
            contents=json.dumps(self.student_repos_file_content),
        )

    @staticmethod
    def create_git_repo_mock(is_repo: bool) -> MagicMock:
        git_repo_mock = MagicMock()
        git_repo_mock.is_repo.return_value = is_repo
        git_repo_mock.path = Path("test")
        git_repo_mock.pull = MagicMock()
        git_repo_mock.clone = MagicMock()
        return git_repo_mock

    def test_fetch_repo_is_repo_pull(self) -> None:
        git_repo_mock = self.create_git_repo_mock(True)
        gitlab_project_mock = MagicMock()
        result = fetch_repo(git_repo_mock, gitlab_project_mock)
        git_repo_mock.pull.assert_called_once()
        self.assertEqual(GitlabProject(Path("test"), gitlab_project_mock), result)

    def test_fetch_repo_is_no_repo_clone(self) -> None:
        git_repo_mock = self.create_git_repo_mock(False)
        gitlab_project_mock = MagicMock()
        result = fetch_repo(git_repo_mock, gitlab_project_mock)
        git_repo_mock.clone.assert_called_once()
        self.assertEqual(GitlabProject(Path("test"), gitlab_project_mock), result)

    @patch("sel_tools.gitlab_api.fetch_repo.fetch_repo")
    def test_fetch_repos(self, mock_fetch_repo: MagicMock) -> None:
        mock_fetch_repo.return_value = Path("test")
        with patch("gitlab.Gitlab", MagicMock(return_value=MagicMock())) as mock_gitlab:
            repo_paths = fetch_repos(
                self.workspace, self.student_repos_file, "my_gitlab_token"
            )

        mock_gitlab.assert_called_once_with(
            GITLAB_SERVER_URL, private_token="my_gitlab_token"
        )
        expected_calls = [
            call(
                GitRepo(self.workspace / str(student_repo["name"])), student_repo["id"]
            )
            for student_repo in self.student_repos_file_content
        ]
        mock_fetch_repo.has_calls(expected_calls, any_order=True)
        self.assertListEqual(repo_paths, [Path("test"), Path("test")])
