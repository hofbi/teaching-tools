"""Tests for gitlab projects action runner."""

import contextlib
import datetime
import io
from pathlib import Path
from typing import ClassVar

from gitlab_projects import parse_arguments
from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import REPO_DIR


class ArgumentParserTest(TestCase):
    """Tests for gitlab projects CLI argument parser."""

    SUB_COMMANDS: ClassVar[list[str]] = [
        "create_issues",
        "comment_issue",
        "fetch_code",
        "evaluate_code",
        "upload_files",
        "commit_changes",
        "add_users",
    ]

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("config_file.json")

    def test_missing_command(self) -> None:
        stderr = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parse_arguments(["foo.py"])
        self.assertTrue("arguments are required: actions" in stderr.getvalue())

    def test_invalid_choice(self) -> None:
        stderr = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parse_arguments(["foo.py", "blub"])
        self.assertTrue("invalid choice: 'blub'" in stderr.getvalue())

    def test_common_missing_config_file(self) -> None:
        for actions in ArgumentParserTest.SUB_COMMANDS:
            with self.subTest(actions):
                stderr = io.StringIO()
                with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
                    parse_arguments(f"foo.py {actions} -t 123 missing_config_file.json".split(" "))
                self.assertTrue("can't open 'missing_config_file.json'" in stderr.getvalue())

    def test_common_missing_token(self) -> None:
        for actions in ArgumentParserTest.SUB_COMMANDS:
            with self.subTest(actions):
                stderr = io.StringIO()
                with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
                    parse_arguments(f"foo.py {actions} config_file.json".split(" "))
                self.assertTrue("arguments are required" in stderr.getvalue())
                self.assertTrue("gitlab-token" in stderr.getvalue())


class CreateIssuesArgumentParserTest(TestCase):
    """Tests for create_issues subparser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("config_file.json")
        self.fs.create_file("issue_slide.md")

    def test_create_issues_valid_parameters(self) -> None:
        args = parse_arguments(
            ["foo.py", "create_issues", "-t", "123", "config_file.json", "-i", "issue_slide.md", "-n", "1"]
        )

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.issue_md_slides.name, "issue_slide.md")
        self.assertEqual(args.homework_number, 1)
        self.assertEqual(args.due_date, None)

    def test_create_issues_with_due_date(self) -> None:
        args = parse_arguments(
            [
                "foo.py",
                "create_issues",
                "-t",
                "12",
                "config_file.json",
                "-i",
                "issue_slide.md",
                "-n",
                "1",
                "-d",
                "2021",
                "1",
                "28",
            ]
        )

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "12")
        self.assertEqual(args.issue_md_slides.name, "issue_slide.md")
        self.assertEqual(args.homework_number, 1)
        self.assertEqual(args.due_date, datetime.date.fromisoformat("2021-01-28"))

    def test_create_issues_out_of_allowed_homework_number_range(self) -> None:
        stderr = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parse_arguments(["foo.py", "create_issues", "-t", "123", "config_file.json", "-i", "not_there.md"])
        self.assertIn("can't open 'not_there.md'", stderr.getvalue())


class CommentIssuesArgumentParserTest(TestCase):
    """Tests for comment_issue subparser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("config_file.json")

    def test_comment_issue_valid_parameters(self) -> None:
        args = parse_arguments(
            ["foo.py", "comment_issue", "-t", "123", "config_file.json", "-i", "42", "-m", "message"]
        )

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.issue_number, 42)
        self.assertEqual(args.message, "message")
        self.assertIsNone(args.state_event)

    def test_comment_issue_close(self) -> None:
        args = parse_arguments(
            ["foo.py", "comment_issue", "-t", "123", "config_file.json", "-i", "42", "-m", "message", "-s", "close"]
        )

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.issue_number, 42)
        self.assertEqual(args.message, "message")
        self.assertEqual(args.state_event, "close")

    def test_comment_issue_reopen(self) -> None:
        args = parse_arguments(
            ["foo.py", "comment_issue", "-t", "123", "config_file.json", "-i", "42", "-m", "message", "-s", "reopen"]
        )

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.issue_number, 42)
        self.assertEqual(args.message, "message")
        self.assertEqual(args.state_event, "reopen")


class FetchCodeArgumentParserTest(TestCase):
    """Tests for fetch_code subparser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("config_file.json")
        self.fs.create_dir("workspace")

    def test_fetch_code_minimal_valid_parameters(self) -> None:
        args = parse_arguments(["foo.py", "fetch_code", "-t", "123", "config_file.json"])

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.workspace, REPO_DIR / "workspace")

    def test_fetch_code_max_valid_parameters(self) -> None:
        args = parse_arguments(["foo.py", "fetch_code", "-t", "123", "config_file.json", "-w", "workspace"])

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.workspace, Path("workspace"))


class EvaluateCodeArgumentParserTest(TestCase):
    """Tests for evaluate_code subparser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("config_file.json")
        self.fs.create_dir("workspace")

    def test_evaluate_code_minimal_valid_parameters(self) -> None:
        args = parse_arguments(["foo.py", "evaluate_code", "-t", "123", "-n", "1", "config_file.json"])

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.workspace, REPO_DIR / "workspace")
        self.assertEqual(1, args.homework_number)
        self.assertIsNone(args.date_last_homework)
        self.assertIsNone(args.evaluation_date)

    def test_evaluate_code_max_valid_parameters(self) -> None:
        args = parse_arguments(
            [
                "foo.py",
                "evaluate_code",
                "-t",
                "123",
                "config_file.json",
                "-w",
                "workspace",
                "-n",
                "2",
                "-d",
                "2021",
                "11",
                "15",
                "-e",
                "2021",
                "11",
                "24",
            ]
        )

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.workspace, Path("workspace"))
        self.assertEqual(args.homework_number, 2)
        self.assertEqual(args.date_last_homework, datetime.date.fromisoformat("2021-11-15"))
        self.assertEqual(args.evaluation_date, datetime.date.fromisoformat("2021-11-24"))


class UploadFilesArgumentParserTest(TestCase):
    """Tests for upload_files subparser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("config_file.json")
        self.fs.create_dir("source")

    def test_upload_files_minimal_valid_parameters(self) -> None:
        args = parse_arguments(["foo.py", "upload_files", "-t", "123", "-s", "source", "config_file.json"])
        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.source_path, Path("source"))


class CommitChangesArgumentParserTest(TestCase):
    """Tests for commit_changes subparser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("config_file.json")
        self.fs.create_dir("workspace")
        self.fs.create_dir("source")

    def test_commit_changes_minimal_valid_parameters(self) -> None:
        args = parse_arguments(
            ["foo.py", "commit_changes", "-t", "123", "-s", "source", "-m", "message", "config_file.json"]
        )

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.source_path, Path("source"))
        self.assertEqual(args.message, "message")
        self.assertEqual(args.workspace, REPO_DIR / "workspace")
        self.assertFalse(args.keep_solutions)

    def test_commit_changes_max_valid_parameters(self) -> None:
        args = parse_arguments(
            [
                "foo.py",
                "commit_changes",
                "-t",
                "123",
                "-s",
                "source",
                "-m",
                "message",
                "config_file.json",
                "-w",
                "workspace",
                "-k",
            ]
        )

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.gitlab_token, "123")
        self.assertEqual(args.source_path, Path("source"))
        self.assertEqual(args.message, "message")
        self.assertEqual(args.workspace, Path("workspace"))
        self.assertTrue(args.keep_solutions)


class AddUsersArgumentParserTest(TestCase):
    """Tests for add_users subparser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("config_file.json")
        self.fs.create_file("student_group.csv")

    def test_add_users_minimal_valid_parameters(self) -> None:
        args = parse_arguments(["foo.py", "add_users", "-t", "123", "config_file.json", "student_group.csv"])

        self.assertEqual(args.student_repo_info_file.file_path, "config_file.json")
        self.assertEqual(args.student_group_info_file.file_path, "student_group.csv")
        self.assertEqual(args.gitlab_token, "123")
