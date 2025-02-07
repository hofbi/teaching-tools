"""Gitlab evaluation jobs test."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock

from sel_tools.code_evaluation.jobs.gitlab import CIStatusTestJob
from sel_tools.utils.repo import GitlabProject


class CIStatusTestJobTest(unittest.TestCase):
    """Tests for CI status job."""

    def __create_fake_project_with_status(self, path: Path, status: str) -> GitlabProject:
        project_mock = MagicMock()
        status_mock = MagicMock()
        status_mock.status = status
        project_mock.pipelines.list = MagicMock(return_value=[status_mock])
        return GitlabProject(path, project_mock)

    def test_run_impl__path_does_not_exist_in_projects__should_raise(self) -> None:
        unit = CIStatusTestJob([])

        with self.assertRaises(KeyError):
            unit.run(Path("test"))

    def test_run_impl__valid_project_failing_ci__should_be_zero(self) -> None:
        mock_gitlab_project = self.__create_fake_project_with_status(Path("test"), "fail")
        unit = CIStatusTestJob([mock_gitlab_project])

        result = unit.run(Path("test"))
        self.assertEqual(0, result[0].score)

    def test_run_impl__valid_project_passing_ci__should_be_one(self) -> None:
        mock_gitlab_project = self.__create_fake_project_with_status(Path("test"), "success")
        unit = CIStatusTestJob([mock_gitlab_project])

        result = unit.run(Path("test"))
        self.assertEqual(1, result[0].score)

    def test_run_impl__valid_project_no_pipelines__should_be_zero(self) -> None:
        project_mock = MagicMock()
        project_mock.pipelines.list = MagicMock(return_value=[])
        mock_gitlab_project = GitlabProject(Path("test"), project_mock)

        unit = CIStatusTestJob([mock_gitlab_project])

        result = unit.run(Path("test"))
        self.assertEqual(0, result[0].score)
        self.assertIn("No pipelines", result[0].comment)
