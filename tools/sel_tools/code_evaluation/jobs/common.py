"""Common evaluation job interface and utilities"""

import itertools
import subprocess
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List, Tuple

from sel_tools.code_evaluation.report import EvaluationResult


class EvaluationJob:
    """Interface for evaluation job. Children implement _run"""

    __metaclass__ = ABCMeta

    def __init__(self, weight: int = 1) -> None:
        self.__weight: int = weight
        self._comment: str = ""

    def run(self, repo_path: Path) -> List[EvaluationResult]:
        deps_results = [job.run(repo_path) for job in self.dependencies]
        print(f"\nRunning {self.name} on {repo_path}")
        job_result_score = self._run(repo_path)
        return list(itertools.chain(*deps_results)) + [
            EvaluationResult(self.name, self.__weight * job_result_score, self.comment)
        ]

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError("Don't call me, I'm abstract.")

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def dependencies(self) -> List["EvaluationJob"]:
        return []

    @abstractmethod
    def _run(self, repo_path: Path) -> int:
        raise NotImplementedError("Don't call me, I'm abstract.")


def run_shell_command(command: str, cwd: Path) -> int:
    """Run shell command"""
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError:
        return 0
    return 1


def run_shell_command_with_output(command: str, cwd: Path) -> Tuple[int, str]:
    """Run shell command and get the output"""
    try:
        data = subprocess.check_output(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as ex:
        return 0, ex.output.decode("utf-8")
    return 1, data.decode("utf-8")
