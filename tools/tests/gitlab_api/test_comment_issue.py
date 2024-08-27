"""Test issue comment module."""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import GITLAB_SERVER_URL
from sel_tools.gitlab_api.comment_issue import comment_issues, create_comment
from sel_tools.utils.comment import Comment


class CommentIssueTest(TestCase):
    """Issue comment module test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_comment_issue_should_have_message(self) -> None:
        gitlab_project_mock = MagicMock()
        issue_mock = MagicMock()
        gitlab_project_mock.issues.get.return_value = issue_mock
        issue_mock.notes.create = MagicMock()
        create_comment(Comment(42, "message"), gitlab_project_mock)

        issue_mock.notes.create.assert_called_once_with({"body": "message"})
        self.assertNotEqual("close", issue_mock.state_event)

    def test_comment_issue_with_close_should_have_state_event_closed(self) -> None:
        gitlab_project_mock = MagicMock()
        issue_mock = MagicMock()
        gitlab_project_mock.issues.get.return_value = issue_mock
        issue_mock.notes.create = MagicMock()
        create_comment(Comment(42, "message", state_event="close"), gitlab_project_mock)

        issue_mock.notes.create.assert_called_once_with({"body": "message"})
        self.assertEqual("close", issue_mock.state_event)

    def test_comment_issue_with_reopen_should_have_state_event_reopen(self) -> None:
        gitlab_project_mock = MagicMock()
        issue_mock = MagicMock()
        gitlab_project_mock.issues.get.return_value = issue_mock
        issue_mock.notes.create = MagicMock()
        create_comment(Comment(42, "message", state_event="reopen"), gitlab_project_mock)

        issue_mock.notes.create.assert_called_once_with({"body": "message"})
        self.assertEqual("reopen", issue_mock.state_event)

    @patch("sel_tools.gitlab_api.comment_issue.create_comment")
    def test_comment_issues_should_be_called_twice(self, mock_comment_issue: MagicMock) -> None:
        student_repos_file = Path("student_repos.json")
        self.fs.create_file(
            student_repos_file,
            contents=json.dumps([{"id": 234, "name": ""}, {"id": 567, "name": ""}]),
        )
        comment = Comment(42, "message")

        with patch("gitlab.Gitlab", MagicMock(return_value=MagicMock())) as mock_gitlab:
            comment_issues(comment, student_repos_file, "my_gitlab_token")

        mock_gitlab.assert_called_once_with(GITLAB_SERVER_URL, private_token="my_gitlab_token")
        self.assertEqual(2, mock_comment_issue.call_count)

    def test_comment_issues_does_not_modify_comment(self) -> None:
        student_repos_file = Path("student_repos.json")
        self.fs.create_file(
            student_repos_file,
            contents=json.dumps([{"id": 234, "name": ""}, {"id": 567, "name": ""}]),
        )
        comment = Comment(42, "message")

        def modify_comment_message(comment: Comment, _: Any) -> None:
            comment.message += "additional text"

        original_comment = deepcopy(comment)
        with (
            patch("gitlab.Gitlab", MagicMock(return_value=MagicMock())),
            patch("sel_tools.gitlab_api.comment_issue.create_comment", modify_comment_message),
        ):
            comment_issues(comment, student_repos_file, "my_gitlab_token")

        self.assertEqual(original_comment, comment)
