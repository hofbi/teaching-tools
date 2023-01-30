"""Task module."""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class Task:
    """Student Homework Task."""

    title: str
    description: str
    documentation: str
    due_date: date | None = None
    label: str | None = None
    attachments: list[Path] = field(default_factory=list)

    def add_homework_label(self, label: int) -> None:
        self.label = f"homework::{label}"


def configure_tasks(
    tasks: list[Task], due_date: date | None, homework_number: int
) -> list[Task]:
    """Configure tasks."""
    for task in tasks:
        task.due_date = due_date
        task.add_homework_label(homework_number)
    return tasks
