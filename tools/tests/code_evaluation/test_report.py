"""Test evaluation report module."""

import json
import unittest
from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.code_evaluation.report import (
    EvaluationReport,
    EvaluationResult,
    write_evaluation_report_for_student_comments,
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

    def test_write_evaluation_reports_for_one_item_should_write_json_and_mds(
        self,
    ) -> None:
        self.fs.create_dir("report")
        gitlab_project = GitlabProject(Path("report"), GitlabProjectFake())

        write_evaluation_reports([EvaluationReport(gitlab_project, 1, [])], "base")

        self.assertTrue(Path("report/base.md").exists())
        self.assertTrue(Path("report/base.json").exists())

    def test_write_evaluation_reports_base_report_should_contain_more_than_student_report(
        self,
    ) -> None:
        self.fs.create_dir("report")
        gitlab_project = GitlabProject(Path("report"), GitlabProjectFake())

        write_evaluation_reports([EvaluationReport(gitlab_project, 1, [])], "base")

        self.assertIn("Overall score:", Path("report/base.md").read_text())

    def test_write_evaluation_report_for_student_comments__two_reports__should_write_two_comment_sections(self) -> None:
        self.fs.create_dir("workspace")
        gitlab_project = GitlabProject(Path("workspace/project_1"), GitlabProjectFake("1234"))
        gitlab_project2 = GitlabProject(Path("workspace/project_2"), GitlabProjectFake("5678"))

        write_evaluation_report_for_student_comments(
            [
                EvaluationReport(gitlab_project, 1, []),
                EvaluationReport(gitlab_project2, 1, [EvaluationResult("foo", 0, 1, comment="this caused the fail")]),
            ],
            Path("workspace"),
        )

        md_report = Path("workspace/evaluation_report_comments_for_students.md").read_text()
        print(md_report)
        self.assertIn("## Comments for Project 1234", md_report)
        self.assertIn("Overall score: 0/0", md_report)
        self.assertIn("## Comments for Project 5678", md_report)
        self.assertIn("this caused the fail", md_report)


class EvaluationReportTest(unittest.TestCase):
    """Evaluation report test."""

    def setUp(self) -> None:
        self.gitlab_project = GitlabProject(Path("test"), GitlabProjectFake("1234", "https://test.com"))

    def test_score_empty_results_zero(self) -> None:
        unit = EvaluationReport(self.gitlab_project, 1, [])
        self.assertEqual(0, unit.score)
        self.assertEqual(0, unit.max_score)

    def test_score_non_empty_results(self) -> None:
        unit = EvaluationReport(
            self.gitlab_project,
            1,
            [
                EvaluationResult("one", 2, 2),
                EvaluationResult("two", 0, 1),
                EvaluationResult("three", 1, 1),
            ],
        )
        self.assertEqual(3, unit.score)
        self.assertEqual(4, unit.max_score)
        self.assertEqual(1, unit.homework_number)

    def test_score_unique_score_counts(self) -> None:
        unit = EvaluationReport(
            self.gitlab_project,
            1,
            [
                EvaluationResult("one", 1, 1),
                EvaluationResult("one", 1, 1),
                EvaluationResult("two", 1, 1),
                EvaluationResult("two", 0, 1),
            ],
        )
        self.assertEqual(2, unit.score)
        self.assertEqual(3, unit.max_score)

    def test_to_json(self) -> None:
        unit = EvaluationReport(
            self.gitlab_project,
            1,
            [
                EvaluationResult("foo", 2, 2),
                EvaluationResult("bar", 0, 1, comment="this caused the fail"),
            ],
        )
        self.assertEqual(
            json.dumps(
                {
                    "repo_path": "test",
                    "project_id": "1234",
                    "url": "https://test.com",
                    "homework_number": 1,
                    "score": 2,
                    "max_score": 3,
                    "results": [
                        {"name": "foo", "score": 2, "max_score": 2, "comment": ""},
                        {"name": "bar", "score": 0, "max_score": 1, "comment": "this caused the fail"},
                    ],
                },
                indent=4,
            ),
            unit.to_json(),
        )

    def test_print_report_header(self) -> None:
        unit = EvaluationReport(self.gitlab_project, 3, [])
        self.assertEqual("Homework 3 Evaluation Report", unit.print_report_header())

    def test_to_md_for_empty_results_should_be_empty_json_array(self) -> None:
        unit = EvaluationReport(self.gitlab_project, 3, [])

        md_report = unit.to_md()

        self.assertIn("# Homework 3 Evaluation Report", md_report)
        self.assertIn("https://test.com", md_report)
        self.assertIn("Overall:", md_report)
        self.assertIn('"results": []', md_report)
        self.assertIn("Student Section", md_report)

    def test_print_student_section(self) -> None:
        unit = EvaluationReport(
            self.gitlab_project,
            1,
            [
                EvaluationResult("foo", 2, 2),
                EvaluationResult("bar", 0, 1, comment="this caused the fail"),
            ],
        )

        student_section = unit.print_student_section()

        self.assertIn("### Homework 1 Evaluation Report", student_section)
        self.assertIn("Overall score: 2/3", student_section)
        self.assertIn("this caused the fail", student_section)
        self.assertNotIn("foo", student_section)
