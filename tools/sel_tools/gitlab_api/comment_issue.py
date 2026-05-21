"""Comment to gitlab issues."""

import gitlab
from gitlab.v4.objects import Project
from tqdm import tqdm

from sel_tools.gitlab_api.attachments import (
    replace_file_paths_with_urls,
    upload_attachments,
)
from sel_tools.utils.comment import Comment, ProjectCommentParser


def comment_issues(comment: Comment, student_repos: list[dict], gitlab_instance: gitlab.Gitlab) -> None:
    """Comment to all issues from comment to student repos."""
    project_comment_parser = ProjectCommentParser(comment, [student_repo["id"] for student_repo in student_repos])
    for student_repo in tqdm(
        student_repos,
        desc="Commenting same message to all issues"
        if project_comment_parser.is_same_comment_for_all_projects
        else "Commenting specific message to individual projects",
    ):
        student_homework_project = gitlab_instance.projects.get(student_repo["id"])
        create_comment(project_comment_parser.get_comment_for_project(student_repo["id"]), student_homework_project)


def create_comment(comment: Comment, gitlab_project: Project) -> None:
    """Create issue for gitlab project from task."""
    uploaded_files = upload_attachments(comment.attachments, gitlab_project)
    comment.message = replace_file_paths_with_urls(comment.message, uploaded_files, comment.attachments)

    issue = gitlab_project.issues.get(comment.issue_id)
    issue.notes.create({"body": comment.message})
    if comment.state_event is not None:
        issue.state_event = comment.state_event
        issue.save()
