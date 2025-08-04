"""Common evaluation job interface and utilities."""

import itertools
import subprocess
from abc import ABCMeta, abstractmethod
from pathlib import Path

from sel_tools.code_evaluation.report import EvaluationResult


class EvaluationJob:
    """Interface for evaluation job.

    Children implement _run
    """

    __metaclass__ = ABCMeta

    def __init__(self, weight: int = 1) -> None:
        self.__weight: int = weight
        self._comment: str = ""

    def run(self, repo_path: Path) -> list[EvaluationResult]:
        deps_results = [job.run(repo_path) for job in self.dependencies]
        print(f"\nRunning {self.name} on {repo_path}")
        job_result_score = min(self._run(repo_path), self.max_run_score)
        return [
            *list(itertools.chain(*deps_results)),
            EvaluationResult(
                self.name, self.__weight * job_result_score, self.max_run_score * self.__weight, self.comment
            ),
        ]

    @property
    @abstractmethod
    def name(self) -> str:
        msg = "Don't call me, I'm abstract."
        raise NotImplementedError(msg)

    @property
    def max_run_score(self) -> int:
        return 1

    @property
    def comment(self) -> str:
        return f"{self.name}: {self._comment}" if self._comment else ""

    @property
    def dependencies(self) -> list["EvaluationJob"]:
        return []

    @abstractmethod
    def _run(self, repo_path: Path) -> int:
        msg = "Don't call me, I'm abstract."
        raise NotImplementedError(msg)


def run_shell_command(command: str, cwd: Path) -> int:
    """Run shell command."""
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError:
        return 0
    return 1


def run_shell_command_with_output(command: str, cwd: Path) -> tuple[int, str]:
    """Run shell command and get the output."""
    try:
        data = subprocess.check_output(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as ex:
        return 0, ex.output.decode("utf-8")
    return 1, data.decode("utf-8")
