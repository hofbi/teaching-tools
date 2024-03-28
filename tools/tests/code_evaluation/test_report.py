"""Test evaluation report module."""

import json
import unittest
from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.code_evaluation.report import (
    EvaluationReport,
    EvaluationResult,
    write_evaluation_reports,
)
from sel_tools.utils.repo import GitlabProject

from tests.helper import GitlabProjectFake


class ReportTest(TestCase):
    """Report module test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_write_evaluation_reports_for_empty_list_should_write_nothing(self) -> None:
        write_evaluation_reports([], "report")
        self.assertEqual(0, self.fs.get_disk_usage().used)

    def test_write_evaluation_reports_for_one_item_should_write_json_and_md(
        self,
    ) -> None:
        self.fs.create_dir("report")
        gitlab_project = GitlabProject(Path("report"), GitlabProjectFake())

        write_evaluation_reports([EvaluationReport(gitlab_project, [])], "base")

        self.assertTrue(Path("report/base.md").exists())
        self.assertTrue(Path("report/base.json").exists())


class EvaluationReportTest(unittest.TestCase):
    """Evaluation report test."""

    def setUp(self) -> None:
        self.gitlab_project = GitlabProject(Path("test"), GitlabProjectFake("https://test.com"))

    def test_score_empty_results_zero(self) -> None:
        unit = EvaluationReport(self.gitlab_project, [])
        self.assertEqual(0, unit.score)

    def test_score_non_empty_results(self) -> None:
        unit = EvaluationReport(
            self.gitlab_project,
            [
                EvaluationResult("one", 2),
                EvaluationResult("two", 0),
                EvaluationResult("three", 1),
            ],
        )
        self.assertEqual(3, unit.score)

    def test_score_unique_score_counts(self) -> None:
        unit = EvaluationReport(
            self.gitlab_project,
            [
                EvaluationResult("one", 1),
                EvaluationResult("one", 1),
                EvaluationResult("two", 1),
                EvaluationResult("two", 0),
            ],
        )
        self.assertEqual(2, unit.score)

    def test_to_json(self) -> None:
        unit = EvaluationReport(
            self.gitlab_project,
            [
                EvaluationResult("foo", 2),
                EvaluationResult("bar", 0, comment="this caused the fail"),
            ],
        )
        self.assertEqual(
            json.dumps(
                {
                    "repo_path": "test",
                    "url": "https://test.com",
                    "score": 2,
                    "results": [
                        {"name": "foo", "score": 2, "comment": ""},
                        {"name": "bar", "score": 0, "comment": "this caused the fail"},
                    ],
                },
                indent=4,
            ),
            unit.to_json(),
        )

    def test_to_md_for_empty_results_should_be_empty_json_array(self) -> None:
        unit = EvaluationReport(self.gitlab_project, [])

        md_report = unit.to_md()

        self.assertIn("# Homework Evaluation Report", md_report)
        self.assertIn("https://test.com", md_report)
        self.assertIn("Overall:", md_report)
        self.assertIn('"results": []', md_report)
