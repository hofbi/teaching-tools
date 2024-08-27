"""Repository utilities."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

import git
from gitlab.v4.objects.projects import Project

from sel_tools.config import GIT_MAIN_BRANCH


@dataclass(frozen=True)
class GitlabProject:
    """Helper class for local gitlab project."""

    local_path: Path
    gitlab_project: Project


class GitRepo:
    """Git repository helper class."""

    HTTPS_LEAD = "https://"

    class PrintProgress(git.RemoteProgress):
        """Write the progress on the console."""

        def line_dropped(self, line: str) -> None:
            print(line)

    def __init__(self, path: Path, branch: str = GIT_MAIN_BRANCH) -> None:
        self.__path = path
        self.__branch = branch

    @property
    def path(self) -> Path:
        return self.__path

    @property
    def branch(self) -> str:
        return self.__branch

    def is_repo(self) -> bool:
        return (self.path / ".git").is_dir()

    @staticmethod
    def authenticate_http_url(url: str) -> str:
        return url.replace(GitRepo.HTTPS_LEAD, f"{GitRepo.HTTPS_LEAD}gitlab-ci-token:$GITLAB_TOKEN@")

    def fetch_from(self, url: str) -> None:
        # The reason for this process here is to avoid that git writes the token
        # into .git/config
        self.__path.mkdir(parents=True, exist_ok=True)
        if not self.is_repo():
            git.Repo.init(self.path)
        subprocess.check_call(
            f"git pull {self.authenticate_http_url(url)} {self.__branch}",
            shell=True,
            cwd=self.path,
        )

    def clone(self, url: str) -> None:
        git.Repo.clone_from(url, self.path, progress=GitRepo.PrintProgress(), branch=self.__branch)

    def pull(self) -> None:
        git.Repo(self.path).remote().pull(progress=GitRepo.PrintProgress())
