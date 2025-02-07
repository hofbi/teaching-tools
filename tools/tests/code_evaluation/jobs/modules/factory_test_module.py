"""Test module."""

from sel_tools.code_evaluation.jobs.common import EvaluationJob
from sel_tools.code_evaluation.jobs.factory import EvaluationJobFactory
from sel_tools.utils.repo import GitlabProject

from tests.helper import SimplePassingJob


class TestFactory(EvaluationJobFactory):
    """Test factory."""

    @staticmethod
    def create(gitlab_projects: list[GitlabProject], homework_number: int) -> list[EvaluationJob]:
        evaluation_map: dict[int, list[EvaluationJob]] = {
            1: [],
            2: [SimplePassingJob()],
        }
        return evaluation_map[homework_number]
