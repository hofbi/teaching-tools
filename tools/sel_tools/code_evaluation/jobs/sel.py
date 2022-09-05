"""Example evaluation job module.

This module is used by default for the `evaluate_code` task. Customize the
factory below to return the jobs you want to use for your evaluation
"""

from pathlib import Path
from typing import List

from sel_tools.code_evaluation.jobs.common import EvaluationJob
from sel_tools.code_evaluation.jobs.cpp import CleanRepoJob, CMakeBuildJob, MakeTestJob
from sel_tools.code_evaluation.jobs.factory import EvaluationJobFactory
from sel_tools.code_evaluation.jobs.gitlab import CIStatusTestJob
from sel_tools.utils.repo import GitlabProject


class ExampleJob(EvaluationJob):
    """Custom Example Job."""

    name = "Example"

    def _run(self, repo_path: Path) -> int:
        # Do whatevery you want to evaluate here
        # Return 0 for failures and a positive score for successful evaluations
        return 1


class ExampleEvaluationJobFactory(EvaluationJobFactory):
    """Example Evaluation Job Factory."""

    @staticmethod
    def create(
        gitlab_projects: list[GitlabProject], homework_number: int
    ) -> list[EvaluationJob]:
        homework_evaluations_jobs_map = {
            1: [CleanRepoJob(), CMakeBuildJob(), ExampleJob()],
            2: [CleanRepoJob(), MakeTestJob(), CIStatusTestJob(gitlab_projects)],
        }
        return homework_evaluations_jobs_map[homework_number]
