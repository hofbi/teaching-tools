"""Test add user module."""

from unittest.mock import MagicMock, call

import gitlab
from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.file_parsing.student_group_parser import Student
from sel_tools.gitlab_api.add_user import (
    add_students_to_repos,
    find_gitlab_users_of_students,
)

from tests.helper import STUDENT1, STUDENT2, GitlabUserFake, GitlabUserManagerFake

STUDENT_NO_GITLAB_ACC = {
    "Last name": "rst",
    "First name": "abc",
    "matriculation-id": "01234567",
    "Email address": "abc.rst@mytum.de",
    "Group": "Standardgruppe 123456",
    "Choice": "Group 2",
}
STUDENT_MISSING_GROUP = {
    "Last name": "rst",
    "First name": "opq",
    "matriculation-id": "01235813",
    "Email address": "opq.rst@tum.de",
    "Group": "Standardgruppe 123456",
    "Choice": "Group 3",
}


class AddUserTest(TestCase):
    """Tests for adding GitLab users to projects."""

    def _create_student_with_gitlab_user(
        self, student_dict: dict, gl_user: GitlabUserFake
    ) -> Student:
        student = Student.from_dict(student_dict)
        student.gitlab_user = gl_user
        return student

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.mock_instance = MagicMock()
        self.mock_instance.user1 = GitlabUserFake(
            "12345",
            STUDENT1["Email address"],
            f"{STUDENT1['First name']} {STUDENT1['Last name']}",
        )
        self.mock_instance.user2 = GitlabUserFake(
            "35711",
            STUDENT2["Email address"],
            f"{STUDENT2['First name']} {STUDENT2['Last name']}",
        )
        self.mock_instance.user3 = GitlabUserFake(
            "35711",
            STUDENT_MISSING_GROUP["Email address"],
            f"{STUDENT_MISSING_GROUP['First name']} {STUDENT_MISSING_GROUP['Last name']}",
        )
        self.mock_instance.users = GitlabUserManagerFake(
            [
                self.mock_instance.user1,
                self.mock_instance.user2,
                self.mock_instance.user3,
            ]
        )
        self.mock_repo1 = MagicMock()
        self.mock_repo1.name = "sel-homework_1"
        self.mock_repo1.members.create = MagicMock()
        self.mock_repo2 = MagicMock()
        self.mock_repo2.name = "sel-homework_2"
        self.mock_repo2.members.create = MagicMock()

    def test_find_gitlab_users_of_students(self) -> None:
        students = [Student.from_dict(STUDENT1), Student.from_dict(STUDENT2)]
        students_with_users = [
            self._create_student_with_gitlab_user(
                STUDENT1,
                self.mock_instance.user1,
            ),
            self._create_student_with_gitlab_user(
                STUDENT2,
                self.mock_instance.user2,
            ),
        ]
        self.assertListEqual(
            students_with_users,
            find_gitlab_users_of_students(self.mock_instance, students),
        )

    def test_find_gitlab_users_of_students_invalid_user(self) -> None:
        students = [
            Student.from_dict(STUDENT1),
            Student.from_dict(STUDENT_NO_GITLAB_ACC),
        ]
        students_with_users = [
            self._create_student_with_gitlab_user(
                STUDENT1,
                self.mock_instance.user1,
            )
        ]
        self.assertListEqual(
            students_with_users,
            find_gitlab_users_of_students(self.mock_instance, students),
        )

    def test_add_students_to_repos__for_two_valid_students_should_add_both(
        self,
    ) -> None:
        students = [
            self._create_student_with_gitlab_user(
                STUDENT1,
                self.mock_instance.user1,
            ),
            self._create_student_with_gitlab_user(
                STUDENT2,
                self.mock_instance.user2,
            ),
        ]
        repo_from_group_id = {1: self.mock_repo1, 2: self.mock_repo2}
        add_students_to_repos(students, repo_from_group_id)
        self.mock_repo1.members.create.assert_has_calls(
            [
                call(
                    {"user_id": "12345", "access_level": gitlab.const.DEVELOPER_ACCESS}
                ),
            ]
        )
        self.mock_repo2.members.create.assert_has_calls(
            [
                call(
                    {"user_id": "35711", "access_level": gitlab.const.DEVELOPER_ACCESS}
                ),
            ]
        )

    def test_add_students_to_repos__for_an_invalid_students_should_raise(
        self,
    ) -> None:
        students = [
            self._create_student_with_gitlab_user(
                STUDENT1,
                self.mock_instance.user1,
            ),
            self._create_student_with_gitlab_user(
                STUDENT_MISSING_GROUP,
                self.mock_instance.user3,
            ),
        ]
        repo_from_group_id = {1: self.mock_repo1, 2: self.mock_repo2}
        with self.assertRaises(KeyError):
            add_students_to_repos(students, repo_from_group_id)
