"""Gitlab evaluation jobs"""

from pathlib import Path
from typing import List

from sel_tools.code_evaluation.jobs.common import EvaluationJob
from sel_tools.config import GIT_MAIN_BRANCH
from sel_tools.utils.repo import GitlabProject


class CIStatusTestJob(EvaluationJob):
    """Job for checking the CI status"""

    name = "CI Status Check"

    def __init__(
        self,
        gitlab_projects: List[GitlabProject],
        branch: str = GIT_MAIN_BRANCH,
        weight: int = 1,
    ) -> None:
        super().__init__(weight)
        self.__gitlab_projects = {
            project.local_path.stem: project.gitlab_project
            for project in gitlab_projects
        }
        self.__branch = branch

    def _run(self, repo_path: Path) -> int:
        project = self.__gitlab_projects[repo_path.stem]
        return int(project.pipelines.list(ref=self.__branch)[0].status == "success")
