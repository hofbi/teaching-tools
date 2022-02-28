"""Task module"""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import List, Optional


@dataclass
class Task:
    """Student Homework Task"""

    title: str
    description: str
    documentation: str
    due_date: Optional[date] = None
    label: Optional[str] = None
    attachments: List[Path] = field(default_factory=lambda: [])

    def add_homework_label(self, label: int) -> None:
        self.label = f"homework::{label}"


def configure_tasks(
    tasks: List[Task], due_date: Optional[date], homework_number: int
) -> List[Task]:
    """Configure tasks"""
    for task in tasks:
        task.due_date = due_date
        task.add_homework_label(homework_number)
    return tasks
