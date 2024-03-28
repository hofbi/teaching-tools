"""Create gitlab repos with contents of source folder."""

import json
from pathlib import Path

import gitlab
from gitlab.v4.objects.projects import Project
from tqdm import tqdm

from sel_tools.config import AVATAR_PATH, GIT_MAIN_BRANCH, GITLAB_SERVER_URL, RUNNER_ID
from sel_tools.gitlab_api.create_commit import create_commit


def create_repos(
    source_folder: Path,
    repo_base_name: str,
    group_id: int,
    number_of_repos: int,
    gitlab_token: str,
) -> tuple[list[dict], str]:
    """Create gitlab repos with contents of source folder."""
    gitlab_instance = gitlab.Gitlab(GITLAB_SERVER_URL, private_token=gitlab_token)

    student_repos = []
    for repo_number in tqdm(range(1, number_of_repos + 1), desc="Creating Student Repos"):
        project = gitlab_instance.projects.create(get_repo_settings(group_id, repo_base_name, repo_number))
        configure_project(project)
        configure_main_branch(project)
        create_commit(source_folder, "Initial commit", project)
        student_repos.append({"name": project.name, "id": project.id})

    group = gitlab_instance.groups.get(group_id)
    return student_repos, group.path


def configure_project(gitlab_project: Project) -> None:
    """Configure gitlab project."""
    gitlab_project.runners.create({"runner_id": RUNNER_ID})
    gitlab_project.avatar = AVATAR_PATH.read_bytes()
    gitlab_project.save()


def configure_main_branch(gitlab_project: Project) -> None:
    """Configure main branch."""
    gitlab_project.protectedbranches.create(
        {
            "name": GIT_MAIN_BRANCH,
            "merge_access_level": gitlab.const.DEVELOPER_ACCESS,
            "push_access_level": gitlab.const.MAINTAINER_ACCESS,
        }
    )


def get_repo_settings(group_id: int, repo_base_name: str, repo_number: int) -> dict:
    """Get gitlab repo settings dictionary."""
    return {
        "name": f"{repo_base_name}_{repo_number}",
        "description": f"Software Engineering Lab Homework Group {repo_number}",
        "namespace_id": group_id,
        "jobs_enabled": True,
        "approvals_before_merge": 1,
    }


def store_student_repo_info_to_config_file(
    repo_info_dir: Path, group_name: str, student_repo_infos: list[dict]
) -> None:
    """Store repo infos into config file created from repo info dir and repo_base_name.

    Existing config files will be overwritten.
    """
    student_repos_file = repo_info_dir.joinpath(group_name).with_suffix(".json")
    student_repos_file.write_text(json.dumps(student_repo_infos, sort_keys=True, indent=2))
