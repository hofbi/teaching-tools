"""Create GitLab repositories from folder."""

import sys
from argparse import Namespace

from sel_tools.config import REPO_DIR
from sel_tools.gitlab_api.create_repo import (
    create_repos,
    store_student_repo_info_to_config_file,
)
from sel_tools.utils.args import ArgumentParserFactory


def parse_arguments(arguments: list[str]) -> Namespace:
    """Parse CLI arguments."""
    factory = ArgumentParserFactory.default_parser(__doc__)
    factory.add_repo_base_name()
    factory.add_group_id()
    factory.add_repo_info_dir()
    factory.add_source_folder(REPO_DIR / "export" / "homework")
    factory.add_number_of_repos()
    factory.add_gitlab_token()

    return factory.parser.parse_args(arguments[1:])


def main() -> None:
    """main."""
    arguments = parse_arguments(sys.argv)
    student_repos, group_name = create_repos(
        arguments.source_path,
        arguments.repo_base_name,
        arguments.group_id,
        arguments.number_of_repos,
        arguments.gitlab_token,
    )
    store_student_repo_info_to_config_file(
        arguments.repo_info_dir, group_name, student_repos
    )


if __name__ == "__main__":
    main()
