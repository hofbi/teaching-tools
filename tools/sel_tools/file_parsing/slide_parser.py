"""Parse homework slides for tasks and documentation."""

import re
from pathlib import Path

from sel_tools.config import REPO_DIR
from sel_tools.file_parsing.config import (
    DOCUMENTATION_PATTERN,
    TASK_FOOTER_PATTERN,
    TASK_HEADER_PATTERN,
)
from sel_tools.utils.task import Task


def get_tasks_from_slides(slides_markdown_file: Path) -> list[Task]:
    """Parse slides for tasks."""
    text = slides_markdown_file.read_text()
    minimal_length_between_markers_pattern = TASK_HEADER_PATTERN + "(.*?)" + TASK_FOOTER_PATTERN

    matches = re.findall(minimal_length_between_markers_pattern, text, re.DOTALL)
    if not matches:
        msg = f"Couldn't find any task in {slides_markdown_file}!"
        raise LookupError(msg)

    documentation_match = re.search(DOCUMENTATION_PATTERN, text, re.DOTALL)
    documentation = documentation_match.group(1) if documentation_match else ""

    tasks: list[Task] = [Task(title, description, documentation) for (title, description) in matches]
    fill_attachments(tasks)

    return tasks


def fill_attachments(tasks: list[Task]) -> None:
    """Fill attachments fields in tasks."""
    for task in tasks:
        task.attachments = get_attachments(task.description)


def get_attachments(description: str) -> list[Path]:
    """Get attachments from task description."""
    markdown_local_file_link_pattern = r".*?\[[^\[]*?\]\(/(.*?)\).*?"
    matches = re.findall(markdown_local_file_link_pattern, description, re.DOTALL)
    if not matches:
        return []

    return [REPO_DIR / file_path for file_path in matches]
