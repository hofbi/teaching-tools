"""Parse group formation for adding students to Gitlab repositories."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from gitlab.v4.objects import User

INVALID_GROUP_CHOICES = ["Not answered yet", "Choice"]


@dataclass
class Student:
    """Student information."""

    first_name: str
    last_name: str
    mail_addr: str
    choice: str
    gitlab_user: User = None

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def valid_choice(self) -> bool:
        return self.choice not in INVALID_GROUP_CHOICES

    @property
    def group_id(self) -> int:
        if self.valid_choice:
            return int(self.choice.split(" ")[1])
        return -1

    @staticmethod
    def from_dict(student_dict: dict) -> "Student":
        return Student(
            student_dict["First name"],
            student_dict["Last name"],
            student_dict["Email address"],
            student_dict["Choice"],
        )


def get_student_groups_from_file(group_formation_file: Path) -> list[Student]:
    """Parse CSV file for group formation."""
    data = pd.read_csv(group_formation_file, delimiter=",|;", engine="python")
    students_arr = [Student.from_dict(row) for _, row in data.iterrows()]

    return [student for student in students_arr if student.valid_choice]
