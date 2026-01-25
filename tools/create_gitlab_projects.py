"""Create GitLab repositories from folder."""

import sys
from argparse import Namespace

from sel_tools.config import REPO_DIR
from sel_tools.file_export.solutions_check import check_code_for_solutions_code
from sel_tools.gitlab_api.create_issue import EVALUATION_DASHBOARD_TASK, create_issues
from sel_tools.gitlab_api.create_repo import create_repos
from sel_tools.gitlab_api.instance import create_gitlab_instance
from sel_tools.utils.args import ArgumentParserFactory
from sel_tools.utils.student_config import (
    read_student_repo_info_from_config_file,
    store_student_repo_info_to_config_file,
)


def parse_arguments(arguments: list[str]) -> Namespace:
    """Parse CLI arguments."""
    factory = ArgumentParserFactory.default_parser(__doc__)
    factory.add_repo_base_name()
    factory.add_group_id()
    factory.add_repo_info_dir()
    factory.add_source_folder(REPO_DIR / "export" / "homework")
    factory.add_number_of_repos()
    factory.add_gitlab_token()
    factory.add_publish_solutions()

    return factory.parser.parse_args(arguments[1:])


def main() -> None:
    """Main."""
    arguments = parse_arguments(sys.argv)
    check_code_for_solutions_code(arguments.source_path, arguments.publish_solutions)
    student_repos, group_name = create_repos(
        arguments.source_path,
        arguments.repo_base_name,
        arguments.group_id,
        arguments.number_of_repos,
        create_gitlab_instance(arguments.gitlab_token),
    )
    config_path = store_student_repo_info_to_config_file(arguments.repo_info_dir, group_name, student_repos)
    create_issues(
        [EVALUATION_DASHBOARD_TASK],
        read_student_repo_info_from_config_file(config_path),
        create_gitlab_instance(arguments.gitlab_token),
    )


if __name__ == "__main__":
    main()
