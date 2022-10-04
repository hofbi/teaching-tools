"""Repo utils test."""


import shutil
from unittest.mock import MagicMock, patch

from sel_tools.config import GIT_MAIN_BRANCH
from sel_tools.utils.repo import GitRepo
from tests.helper import GitTestCase


class GitRepoTest(GitTestCase):
    """Git repo test."""

    def __create_file_and_commit(self, file_name: str) -> None:
        self.repo_path.joinpath(file_name).touch()
        self.repo.index.add([file_name])
        self.repo.index.commit(f"add {file_name}")

    def test_is_repo_git_folder_true(self) -> None:
        unit = GitRepo(self.repo_path)
        self.assertTrue(unit.is_repo())

    def test_is_repo_no_git_folder_false(self) -> None:
        shutil.rmtree(self.repo_path / ".git")
        unit = GitRepo(self.repo_path)
        self.assertFalse(unit.is_repo())

    def test_clone__from_other_repo__should_contain_test_file(self) -> None:
        self.__create_file_and_commit("test.txt")
        unit = GitRepo(self.workspace / "test")

        unit.clone(str(self.repo_path))

        self.assertTrue(unit.path.joinpath("test.txt").exists())

    def test_clone__from_other_repo_and_branch__should_contain_test_file(self) -> None:
        self.repo.git.checkout(b="foo")
        self.__create_file_and_commit("test.txt")
        unit = GitRepo(self.workspace / "test", branch="foo")

        unit.clone(str(self.repo_path))

        self.assertTrue(unit.path.joinpath("test.txt").exists())

    def test_pull__from_other_repo__should_contain_test_file(self) -> None:
        unit = GitRepo(self.workspace / "test")
        self.__create_file_and_commit("test.txt")
        unit.clone(str(self.repo_path))

        self.__create_file_and_commit("test2.txt")
        self.assertFalse(unit.path.joinpath("test2.txt").exists())

        unit.pull()

        self.assertTrue(unit.path.joinpath("test2.txt").exists())

    def test_fetch_from__other_repo__should_contain_test_file(self) -> None:
        self.__create_file_and_commit("test.txt")
        unit = GitRepo(self.workspace / "test")

        with patch(
            "sel_tools.utils.repo.GitRepo.authenticate_http_url",
            MagicMock(return_value=self.repo_path),
        ):
            unit.fetch_from(str(self.repo_path))

        self.assertTrue(unit.path.joinpath("test.txt").exists())

    @patch("subprocess.check_call")
    def test_fetch_from__url__should_have_pull_call_with_args(
        self, clone_mock: MagicMock
    ) -> None:
        GitRepo(self.repo_path).fetch_from("https://url.git")
        clone_mock.assert_called_with(
            f"git pull https://gitlab-ci-token:$GITLAB_TOKEN@url.git {GIT_MAIN_BRANCH}",
            shell=True,
            cwd=self.repo_path,
        )

    def test_authenticate_http_url__https_url__should_contain_gitlab_token(
        self,
    ) -> None:
        url = GitRepo.authenticate_http_url("https://url.git")
        self.assertIn("gitlab-ci-token", url)
