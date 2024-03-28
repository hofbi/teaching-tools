"""Comment to gitlab issues."""

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
from sel_tools.utils.comment import Comment


def comment_issues(comment: Comment, student_repos_file: Path, gitlab_token: str) -> None:
    """Comment to all issues from comment to student repos."""
    gitlab_instance = gitlab.Gitlab(GITLAB_SERVER_URL, private_token=gitlab_token)
    student_repos = json.loads(student_repos_file.read_text())
    for student_repo in tqdm(student_repos, desc="Commenting to issues"):
        student_homework_project = gitlab_instance.projects.get(student_repo["id"])
        create_comment(deepcopy(comment), student_homework_project)


def create_comment(comment: Comment, gitlab_project: Project) -> None:
    """Create issue for gitlab project from task."""
    uploaded_files = upload_attachments(comment.attachments, gitlab_project)
    comment.message = replace_file_paths_with_urls(comment.message, uploaded_files, comment.attachments)

    issue = gitlab_project.issues.get(comment.issue_id)
    issue.notes.create({"body": comment.message})
    if comment.state_event is not None:
        issue.state_event = comment.state_event
        issue.save()
