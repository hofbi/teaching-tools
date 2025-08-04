"""Common code evaluation job test."""

import unittest
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.code_evaluation.jobs.common import (
    run_shell_command,
    run_shell_command_with_output,
)
from sel_tools.code_evaluation.report import EvaluationResult

from tests.helper import ComplexJob, OverMaxPassingJob, SimpleFailingJob, SimplePassingJob


class EvaluationJobTest(unittest.TestCase):
    """Evaluation job test."""

    def test_simple_failing_job(self) -> None:
        unit = SimpleFailingJob()
        results = unit.run(Path())
        self.assertListEqual([EvaluationResult("simple_fail", 0, 1, "simple_fail: This caused the fail")], results)

    def test_simple_passing_job(self) -> None:
        unit = SimplePassingJob()
        results = unit.run(Path())
        self.assertListEqual([EvaluationResult("simple_pass", 1, 1)], results)

    def test_simple_passing_job_with_weight(self) -> None:
        unit = SimplePassingJob(3)
        results = unit.run(Path())
        self.assertListEqual([EvaluationResult("simple_pass", 3, 3)], results)

    def test_complex_job(self) -> None:
        unit = ComplexJob()
        results = unit.run(Path())
        self.assertListEqual(
            [
                EvaluationResult("simple_fail", 0, 1, "simple_fail: This caused the fail"),
                EvaluationResult("simple_pass", 2, 2),
                EvaluationResult("complex", 3, 3),
            ],
            results,
        )

    def test_over_max_passing_job__score_should_not_be_more_than_max(self) -> None:
        unit = OverMaxPassingJob()
        results = unit.run(Path())
        self.assertListEqual([EvaluationResult("over_max_pass", 1, 1)], results)


class JobsTest(TestCase):
    """Test for jobs module."""

    @patch("subprocess.check_call", MagicMock(return_value=0))
    def test_run_shell_command_success(self) -> None:
        result = run_shell_command("make", Path())
        self.assertEqual(1, result)

    @patch("subprocess.check_call", MagicMock(side_effect=CalledProcessError(2, "")))
    def test_run_shell_command_fail(self) -> None:
        result = run_shell_command("make", Path())
        self.assertEqual(0, result)

    @patch("subprocess.check_output", MagicMock(return_value=b"success"))
    def test_run_shell_command_with_output_success(self) -> None:
        result = run_shell_command_with_output("make", Path())
        self.assertEqual((1, "success"), result)

    @patch(
        "subprocess.check_output",
        MagicMock(side_effect=CalledProcessError(2, "", output=b"fail")),
    )
    def test_run_shell_command_with_output_fail(self) -> None:
        result = run_shell_command_with_output("make", Path())
        self.assertEqual((0, "fail"), result)
