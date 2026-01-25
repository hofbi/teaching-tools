"""Clone or pull repos into a local workspace."""

import os
from pathlib import Path

import gitlab
from gitlab.v4.objects import Project
from tqdm import tqdm

from sel_tools.utils.repo import GitlabProject, GitRepo
from sel_tools.utils.student_config import get_branch_from_student_config


def fetch_repos(workspace: Path, student_repos: list[dict], gitlab_instance: gitlab.Gitlab) -> list[GitlabProject]:
    """Fetch the student repositories into the workspace."""
    workspace.mkdir(parents=True, exist_ok=True)
    return [
        fetch_repo(
            GitRepo(workspace / student_repo["name"], get_branch_from_student_config(student_repo)),
            gitlab_instance.projects.get(student_repo["id"]),
        )
        for student_repo in tqdm(student_repos, desc="Fetching Repos")
    ]


def fetch_repo(repo: GitRepo, gitlab_project: Project) -> GitlabProject:
    """Clone or pull student repo."""
    if os.environ.get("CI"):  # This variable is set by the CI pipeline
        repo.fetch_from(gitlab_project.http_url_to_repo)
    elif repo.is_repo():
        repo.pull()
    else:
        repo.clone(gitlab_project.ssh_url_to_repo)
    return GitlabProject(repo.path, gitlab_project)
