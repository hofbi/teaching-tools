"""Test repository fetching module."""

import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from sel_tools.config import GIT_MAIN_BRANCH
from sel_tools.gitlab_api.fetch_repo import fetch_repo, fetch_repos
from sel_tools.utils.repo import GitlabProject


class FetchRepoTest(TestCase):
    """Fetch repo test."""

    def setUp(self) -> None:
        self.workspace = Path("workspace")
        self.student_config = [
            {"id": 234, "name": "foo", "branch": "develop"},
            {"id": 567, "name": "bar"},  # No branch specified
        ]

    @patch.dict(os.environ, {"CI": ""}, clear=True)
    def test_fetch_repo_is_repo_pull(self) -> None:
        git_repo_mock = MagicMock()
        git_repo_mock.is_repo.return_value = True
        git_repo_mock.path = Path("test")
        git_repo_mock.pull = MagicMock()
        gitlab_project_mock = MagicMock()

        result = fetch_repo(git_repo_mock, gitlab_project_mock)

        git_repo_mock.pull.assert_called_once()
        self.assertEqual(GitlabProject(Path("test"), gitlab_project_mock), result)

    @patch.dict(os.environ, {"CI": ""}, clear=True)
    def test_fetch_repo_is_no_repo_clone(self) -> None:
        git_repo_mock = MagicMock()
        git_repo_mock.is_repo.return_value = False
        git_repo_mock.path = Path("test")
        git_repo_mock.clone = MagicMock()
        gitlab_project_mock = MagicMock()

        result = fetch_repo(git_repo_mock, gitlab_project_mock)

        git_repo_mock.clone.assert_called_once()
        self.assertEqual(GitlabProject(Path("test"), gitlab_project_mock), result)

    @patch.dict(os.environ, {"CI": "true"})
    def test_fetch_repo_ci_environment_fetch_from(self) -> None:
        git_repo_mock = MagicMock()
        git_repo_mock.is_repo.return_value = False
        git_repo_mock.path = Path("test")
        git_repo_mock.fetch_from = MagicMock()
        gitlab_project_mock = MagicMock()
        gitlab_project_mock.http_url_to_repo = "this should be an url"

        result = fetch_repo(git_repo_mock, gitlab_project_mock)

        git_repo_mock.fetch_from.assert_called_once_with("this should be an url")
        self.assertEqual(GitlabProject(Path("test"), gitlab_project_mock), result)

    @patch("sel_tools.gitlab_api.fetch_repo.fetch_repo")
    def test_fetch_repos_without_branch_should_use_default_branch(self, mock_fetch_repo: MagicMock) -> None:
        mock_fetch_repo.return_value = Path("test")
        repo_paths = fetch_repos(self.workspace, self.student_config, MagicMock())

        self.assertEqual(mock_fetch_repo.call_count, 2)

        git_repo_arg = mock_fetch_repo.call_args_list[1][0][0]
        self.assertEqual(git_repo_arg.branch, GIT_MAIN_BRANCH)
        self.assertEqual(git_repo_arg.path, self.workspace / str(self.student_config[1]["name"]))
        self.assertEqual(2, len(repo_paths))

    @patch("sel_tools.gitlab_api.fetch_repo.fetch_repo")
    def test_fetch_repos_with_branch_should_use_specified_branch(self, mock_fetch_repo: MagicMock) -> None:
        mock_fetch_repo.return_value = Path("test")
        repo_paths = fetch_repos(self.workspace, self.student_config, MagicMock())

        self.assertEqual(mock_fetch_repo.call_count, 2)

        git_repo_arg = mock_fetch_repo.call_args_list[0][0][0]
        self.assertEqual(git_repo_arg.branch, "develop")
        self.assertEqual(git_repo_arg.path, self.workspace / str(self.student_config[0]["name"]))
        self.assertEqual(2, len(repo_paths))
