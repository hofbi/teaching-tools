"""Parse group formation for adding students to Gitlab repositories"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

INVALID_GROUP_CHOICES = ["Not answered yet", "Choice"]


@dataclass
class Student:
    """Student information"""

    first_name: str
    surname: str
    mail_addr: str
    choice: str

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.surname}"

    @property
    def valid_chioce(self) -> bool:
        return self.choice not in INVALID_GROUP_CHOICES

    @property
    def group_id(self) -> int:
        if self.valid_chioce:
            return int(self.choice.split(" ")[1])
        return -1


def get_student_groups_from_file(group_formation_file: Path) -> List[Student]:
    """Parse CSV file for group formation"""
    data = pd.read_csv(group_formation_file, delimiter=",|;")
    students_arr = [
        Student(
            row["First name"],
            row["Surname"],
            row["Email address"],
            row["Choice"],
        )
        for _, row in data.iterrows()
    ]

    return [student for student in students_arr if student.valid_chioce]
