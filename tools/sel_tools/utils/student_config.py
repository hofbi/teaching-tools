"""Student config utilities."""

import json
from pathlib import Path

from sel_tools.config import GIT_MAIN_BRANCH


def get_branch_from_student_config(student_config: dict) -> str:
    """Get branch from student config."""
    return str(student_config.get("branch", GIT_MAIN_BRANCH))


def store_student_repo_info_to_config_file(
    repo_info_dir: Path, group_name: str, student_repo_infos: list[dict]
) -> Path:
    """Store repo infos into config file created from repo info dir and repo_base_name.

    Existing config files will be overwritten.
    """
    student_repos_file = repo_info_dir.joinpath(group_name).with_suffix(".json")
    student_repos_file.write_text(json.dumps(student_repo_infos, sort_keys=True, indent=2))
    return student_repos_file


def read_student_repo_info_from_config_file(config_file: Path | str) -> list[dict]:
    """Read student repo info from config file."""
    return json.loads(Path(config_file).read_text())  # type: ignore[no-any-return]
