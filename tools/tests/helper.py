"""Test helper functions."""

import shutil
import unittest
from dataclasses import dataclass
from pathlib import Path

import git
from sel_tools.code_evaluation.jobs.common import EvaluationJob
from sel_tools.config import GIT_MAIN_BRANCH

STUDENT1 = {
    "Surname": "xyz",
    "First name": "uvw",
    "matriculation-id": "09876543",
    "Email address": "uvw.xyz@mytum.de",
    "Group": "Standardgruppe 123456",
    "Choice": "Group 1",
}
STUDENT2 = {
    "Surname": "äöü",
    "First name": "opq",
    "matriculation-id": "02358113",
    "Email address": "aeoeue.rst@tum.de",
    "Group": "Standardgruppe 123456",
    "Choice": "Group 2",
}


class GitTestCase(unittest.TestCase):
    """Git Test Case."""

    def setUp(self) -> None:
        self.workspace = Path(__file__).parent / "workspace"
        self.repo_path = self.workspace / "repo"
        self.workspace.mkdir(exist_ok=True, parents=True)
        self.repo = git.Repo.init(self.repo_path)
        self.repo.git.checkout(b=GIT_MAIN_BRANCH)

    def tearDown(self) -> None:
        # Delete repo and workspace
        shutil.rmtree(self.workspace)


class SimpleFailingJob(EvaluationJob):
    """Test job."""

    name = "simple_fail"

    def _run(self, repo_path: Path) -> int:
        self._comment = "This caused the fail"
        return 0


class SimplePassingJob(EvaluationJob):
    """Test job."""

    name = "simple_pass"

    def _run(self, repo_path: Path) -> int:
        return 1


class ComplexJob(EvaluationJob):
    """Test job."""

    name = "complex"
    dependencies = [SimpleFailingJob(), SimplePassingJob(2)]

    def _run(self, repo_path: Path) -> int:
        return 3


@dataclass
class GitlabProjectFake:
    """Fake for the Gitlab Project Object."""

    web_url: str = ""


@dataclass
class GitlabGroupFake:
    """Fake for the Gitlab Group Object."""

    path: str = ""


@dataclass
class GitlabUserFake:
    """Fake for the Gitlab User Object."""

    id: str = ""  # pylint: disable=invalid-name
    email: str = ""
    name: str = ""


@dataclass
class GitlabUserManagerFake:
    """Fake for the Gitlab User Manager Object."""

    user_list: list[GitlabUserFake]

    def list(self, search: str = "") -> list[GitlabUserFake]:
        if search == "":
            return []
        return [user for user in self.user_list if search in user.email]
