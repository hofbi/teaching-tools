"""Homework code evaluation module."""

import copy
import itertools
from datetime import date

import git
from sel_tools.code_evaluation.jobs.common import EvaluationJob
from sel_tools.code_evaluation.jobs.factory import EvaluationJobFactory
from sel_tools.code_evaluation.report import EvaluationReport
from sel_tools.utils.repo import GitlabProject
from tqdm import tqdm


def evaluate_code(
    eval_job_factory: type[EvaluationJobFactory],
    gitlab_projects: list[GitlabProject],
    homework_number: int,
    evaluation_date: date | None,
) -> list[EvaluationReport]:
    """Evaluate code for given repositories and homework number."""
    evaluation_jobs = eval_job_factory.create(gitlab_projects, homework_number)
    return [
        CodeEvaluator(evaluation_jobs, gitlab_project).evaluate(evaluation_date)
        for gitlab_project in tqdm(
            gitlab_projects, desc=f"Evaluating Homework {homework_number}"
        )
    ]


class CodeEvaluator:
    """Code evaluator class."""

    def __init__(self, jobs: list[EvaluationJob], gitlab_project: GitlabProject):
        # Perform a deepcopy to avoid artifact of old job runs
        self.__jobs = copy.deepcopy(jobs)
        self.__gitlab_project = gitlab_project
        self.__repo = git.Repo(gitlab_project.local_path)

    def evaluate(self, evaluation_date: date | None) -> EvaluationReport:
        self.__clean_repo()
        if evaluation_date is not None:
            self.__checkout_last_commit_before_eval_date(evaluation_date)
        return EvaluationReport(
            self.__gitlab_project,
            list(
                itertools.chain(
                    *[job.run(self.__gitlab_project.local_path) for job in self.__jobs]
                )
            ),
        )

    def __clean_repo(self) -> None:
        self.__repo.git.restore(".")
        self.__repo.git.clean("-xdf")

    def __checkout_last_commit_before_eval_date(self, evaluation_date: date) -> None:
        commits_before_eval_date = list(
            self.__repo.iter_commits(before=evaluation_date)
        )
        if commits_before_eval_date:
            self.__repo.git.checkout(commits_before_eval_date[0])
            self.__clean_repo()
