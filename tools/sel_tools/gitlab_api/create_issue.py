"""Create gitlab issues from tasks."""

import json
from copy import deepcopy
from pathlib import Path

import gitlab
from gitlab.v4.objects.projects import Project
from tqdm import tqdm

from sel_tools.config import GITLAB_SERVER_URL
from sel_tools.gitlab_api.attachments import (
    replace_file_paths_with_urls,
    upload_attachments,
)
from sel_tools.utils.task import Task


def create_issues(tasks: list[Task], student_repos_file: Path, gitlab_token: str) -> None:
    """Create gitlab issues from tasks for all student repos."""
    gitlab_instance = gitlab.Gitlab(GITLAB_SERVER_URL, private_token=gitlab_token)
    student_repos = json.loads(student_repos_file.read_text())
    for student_repo in tqdm(student_repos, desc="Creating homework issues"):
        student_homework_project = gitlab_instance.projects.get(student_repo["id"])
        for task in tasks:
            create_issue(deepcopy(task), student_homework_project)


def create_issue(task: Task, gitlab_project: Project) -> None:
    """Create issue for gitlab project from task."""
    uploaded_files = upload_attachments(task.attachments, gitlab_project)
    task.description = replace_file_paths_with_urls(task.description, uploaded_files, task.attachments)

    gitlab_project.issues.create(get_issue_dict(task))


def get_issue_dict(task: Task) -> dict:
    """Get a dict that contains the fields to create an issue from a task."""
    return {
        "title": task.title,
        "description": task.description + "\n## Documentation\n" + task.documentation,
        "due_date": str(task.due_date) if task.due_date else "",
        "labels": [task.label] if task.label else [],
    }
