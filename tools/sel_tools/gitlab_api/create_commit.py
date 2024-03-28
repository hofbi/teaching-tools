"""Create Gitlab commit."""

import json
from functools import lru_cache
from pathlib import Path

import git
import gitlab
from gitlab.v4.objects.projects import Project
from tqdm import tqdm

from sel_tools.config import GIT_MAIN_BRANCH, GITLAB_SERVER_URL
from sel_tools.utils.files import FileTree, FileVisitor


def commit_changes(repo_paths: list[Path], message: str) -> None:
    """Commit and push changes to all repos."""
    for repo_path in tqdm(repo_paths, desc="Committing changes"):
        repo = git.Repo(repo_path)
        repo.git.add("--all")
        repo.git.commit("-am", message)
        repo.git.push()


def upload_files(source_folder: Path, student_repos_file: Path, gitlab_token: str) -> None:
    """Upload new files from source folder via commit to the repository.

    For doing more than just adding new files refer to `commit_changes`
    """
    gitlab_instance = gitlab.Gitlab(GITLAB_SERVER_URL, private_token=gitlab_token)
    student_repos = json.loads(student_repos_file.read_text())
    for student_repo in tqdm(student_repos, desc="Uploading files"):
        student_homework_project = gitlab_instance.projects.get(student_repo["id"])
        create_commit(source_folder, f"Add {source_folder.name}", student_homework_project)


def create_commit(source_folder: Path, message: str, gitlab_project: Project) -> None:
    """Create commit in gitlab project from source folder with message."""
    gitlab_project.commits.create(create_gitlab_commit_data_with_all_files_from(source_folder, message))


@lru_cache
def create_gitlab_commit_data_with_all_files_from(folder: Path, message: str) -> dict:
    """Create gitlab commit with all files from folder.

    Folder is assumed to be root of the repo committing to
    """
    file_tree = FileTree(folder)
    initial_file_commit_actions_visitor = InitialFileCommitActionsVisitor(folder)
    file_tree.accept(initial_file_commit_actions_visitor)

    return (
        {
            "branch": GIT_MAIN_BRANCH,
            "commit_message": message,
            "actions": initial_file_commit_actions_visitor.actions,
        }
        if initial_file_commit_actions_visitor.actions
        else {}
    )


class InitialFileCommitActionsVisitor(FileVisitor):
    """Create gitlab commit action for new file."""

    def __init__(self, root_folder: Path) -> None:
        self.actions: list[dict] = []
        self.__root_folder = root_folder

    def visit_file(self, file: Path) -> None:
        path_in_new_repo = file.relative_to(self.__root_folder)
        self.actions.append(
            {
                "action": "create",
                "file_path": str(path_in_new_repo),
                "content": file.read_text(),
            }
        )
