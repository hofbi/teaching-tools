"""Test issue creation module."""

import json
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import GITLAB_SERVER_URL
from sel_tools.gitlab_api.create_issue import (
    create_issue,
    create_issues,
    get_issue_dict,
)
from sel_tools.utils.task import Task

TASKS = [
    Task("1", "Desc", "Doc"),
    Task("2", "Description", "Documentation"),
]


class IssueCreatorTest(TestCase):
    """Issue creator test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    @staticmethod
    def test_create_issue() -> None:
        gitlab_project_mock = MagicMock()
        gitlab_project_mock.issues.create = MagicMock()
        create_issue(
            Task("Title", "Do stuff", "reference", date(2000, 1, 1), "", []),
            gitlab_project_mock,
        )
        gitlab_project_mock.issues.create.assert_called_once_with(
            {
                "title": "Title",
                "description": "Do stuff\n## Documentation\nreference",
                "due_date": "2000-01-01",
                "labels": [],
            }
        )

    @patch("sel_tools.gitlab_api.create_issue.create_issue")
    def test_create_issues_should_be_called_four_times(self, mock_create_issue: MagicMock) -> None:
        student_repos_file = Path("student_repos.json")
        self.fs.create_file(
            student_repos_file,
            contents=json.dumps([{"id": 234, "name": ""}, {"id": 567, "name": ""}]),
        )

        with patch("gitlab.Gitlab", MagicMock(return_value=MagicMock())) as mock_gitlab:
            create_issues(TASKS, student_repos_file, "my_gitlab_token")

        mock_gitlab.assert_called_once_with(GITLAB_SERVER_URL, private_token="my_gitlab_token")
        self.assertEqual(4, mock_create_issue.call_count, msg="2 calls for projects times 2 for the tasks")

    def test_create_issues_does_not_modify_tasks(self) -> None:
        student_repos_file = Path("student_repos.json")
        self.fs.create_file(
            student_repos_file,
            contents=json.dumps([{"id": 234, "name": ""}, {"id": 567, "name": ""}]),
        )

        def modify_task_description(task: Task, _: Any) -> None:
            task.description += "additional text"

        original_tasks = deepcopy(TASKS)
        with (
            patch("gitlab.Gitlab", MagicMock(return_value=MagicMock())),
            patch("sel_tools.gitlab_api.create_issue.create_issue", modify_task_description),
        ):
            create_issues(TASKS, student_repos_file, "my_gitlab_token")

        self.assertEqual(original_tasks, TASKS)

    def test_get_gitlab_issue_dict_minimum_fields(self) -> None:
        task = Task("sit", "amet", "consec")
        self.assertEqual(
            get_issue_dict(task),
            {
                "title": "sit",
                "description": "amet\n## Documentation\nconsec",
                "due_date": "",
                "labels": [],
            },
        )

    def test_get_gitlab_issue_dict_all_fields(self) -> None:
        task = Task("sit", "amet", "consec", date(2000, 12, 31), "adipi")
        self.assertEqual(
            get_issue_dict(task),
            {
                "title": "sit",
                "description": "amet\n## Documentation\nconsec",
                "due_date": "2000-12-31",
                "labels": ["adipi"],
            },
        )
