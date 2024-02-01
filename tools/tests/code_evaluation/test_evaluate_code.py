"""Test evaluate code module."""

from datetime import date, datetime

from sel_tools.code_evaluation.evaluate_code import CodeEvaluator
from sel_tools.utils.repo import GitlabProject

from tests.helper import ComplexJob, GitlabProjectFake, GitTestCase, SimplePassingJob


class CodeEvaluatorTest(GitTestCase):
    """Code evaluator test."""

    def setUp(self) -> None:
        super().setUp()
        self.gitlab_project = GitlabProject(self.repo_path, GitlabProjectFake())
        self.test_file = self.repo_path / "test.txt"
        self.test_file.touch()
        self.repo.index.add(["test.txt"])
        self.repo.index.commit("init", commit_date=datetime(2021, 11, 11).isoformat())

    def __write_to_test_file_and_commit(
        self, file_content: str, commit_date: date
    ) -> None:
        self.test_file.write_text(file_content)
        self.repo.index.add([self.test_file.name])
        self.repo.index.commit("edit test.txt", commit_date=commit_date.isoformat())

    def test_evaluate_no_jobs_empty_report(self) -> None:
        report = CodeEvaluator([], self.gitlab_project).evaluate(None)
        self.assertEqual(self.repo_path, report.repo_path)
        self.assertEqual(0, report.score)
        self.assertFalse(report.results)

    def test_evaluate_one_job(self) -> None:
        report = CodeEvaluator([SimplePassingJob()], self.gitlab_project).evaluate(None)
        self.assertEqual(self.repo_path, report.repo_path)
        self.assertEqual(1, report.score)
        self.assertEqual(1, len(report.results))

    def test_evaluate_two_jobs(self) -> None:
        report = CodeEvaluator(
            [SimplePassingJob(), ComplexJob(2)], self.gitlab_project
        ).evaluate(None)
        self.assertEqual(self.repo_path, report.repo_path)
        self.assertEqual(9, report.score)
        self.assertEqual(4, len(report.results))

    def test_evaluate_one_job_with_eval_date(self) -> None:
        self.__write_to_test_file_and_commit("line 1\nline 2", datetime(2021, 11, 14))
        CodeEvaluator([SimplePassingJob()], self.gitlab_project).evaluate(
            date(2021, 11, 13)
        )
        self.assertEqual("", self.test_file.read_text())

    def test_evaluate_one_job_with_eval_date_and_two_prior_commits(self) -> None:
        self.__write_to_test_file_and_commit("line 1\nline 2", datetime(2021, 11, 12))
        self.__write_to_test_file_and_commit("some other stuff", datetime(2021, 11, 15))
        CodeEvaluator([SimplePassingJob()], self.gitlab_project).evaluate(
            date(2021, 11, 14)
        )
        self.assertEqual("line 1\nline 2", self.test_file.read_text())

    def test_evaluate_one_job_without_eval_date_should_be_at_latest_commit(
        self,
    ) -> None:
        self.__write_to_test_file_and_commit("line 1\nline 2", datetime(2021, 11, 14))
        CodeEvaluator([SimplePassingJob()], self.gitlab_project).evaluate(None)
        self.assertEqual("line 1\nline 2", self.test_file.read_text())

    def test_constructor_from_job_list_should_copy_that_list(self) -> None:
        job_list = [SimplePassingJob(), ComplexJob(2)]
        evaluator_one = CodeEvaluator(job_list, self.gitlab_project)
        evaluator_two = CodeEvaluator(job_list, self.gitlab_project)

        self.assertNotEqual(evaluator_one.__dict__, evaluator_two.__dict__)
