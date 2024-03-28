"""Add users to projects."""

import json
from pathlib import Path

import gitlab

from sel_tools.config import GITLAB_SERVER_URL
from sel_tools.file_parsing.student_group_parser import (
    Student,
    get_student_groups_from_file,
)


def add_users(student_repos_file: Path, student_group_file: Path, gitlab_token: str) -> None:
    """Add all students to repositories."""
    gitlab_instance = gitlab.Gitlab(GITLAB_SERVER_URL, private_token=gitlab_token)
    students = get_student_groups_from_file(student_group_file)
    students_found = find_gitlab_users_of_students(gitlab_instance, students)
    student_repos = json.loads(student_repos_file.read_text())
    repo_from_group_id = {
        int(repo["name"].split("_")[-1]): gitlab_instance.projects.get(repo["id"]) for repo in student_repos
    }
    add_students_to_repos(students_found, repo_from_group_id)


def find_gitlab_users_of_students(gitlab_instance: gitlab.Gitlab, students: list[Student]) -> list[Student]:
    """Return list of students with their Gitlab users."""
    for student in students:
        try:
            student.gitlab_user = gitlab_instance.users.list(search=student.mail_addr)[0]
        except IndexError:
            student.gitlab_user = None
            print(f"Student {student.name} with {student.mail_addr} not found!")
    return [student for student in students if student.gitlab_user is not None]


def add_students_to_repos(students: list[Student], repo_from_group_id: dict) -> None:
    """Add students to repositories."""
    print(f"Adding {len(students)} to their projects!")
    for student in students:
        repo = repo_from_group_id[student.group_id]
        repo.members.create(
            {
                "user_id": student.gitlab_user.id,
                "access_level": gitlab.const.DEVELOPER_ACCESS,
            }
        )
