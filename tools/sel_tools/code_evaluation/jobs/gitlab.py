"""Gitlab evaluation jobs"""

from pathlib import Path
from typing import List

from sel_tools.code_evaluation.jobs.common import EvaluationJob
from sel_tools.config import GIT_MAIN_BRANCH
from sel_tools.utils.repo import GitlabProject


class CIStatusTestJob(EvaluationJob):
    """Job for checking the CI status"""

    name = "CI Status Check"

    def __init__(self, gitlab_projects: List[GitlabProject], weight: int = 1) -> None:
        super().__init__(weight)
        self.__gitlab_projects = {
            project.local_path.stem: project.gitlab_project
            for project in gitlab_projects
        }

    def _run(self, repo_path: Path) -> int:
        project = self.__gitlab_projects[repo_path.stem]
        return int(project.pipelines.list(ref=GIT_MAIN_BRANCH)[0].status == "success")
