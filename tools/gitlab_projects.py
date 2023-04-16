"""Perform actions on gitlab projects."""

import sys
from argparse import ArgumentDefaultsHelpFormatter, Namespace
from pathlib import Path

from sel_tools.code_evaluation.evaluate_code import evaluate_code
from sel_tools.code_evaluation.jobs.factory import EvaluationJobFactory
from sel_tools.code_evaluation.report import write_evaluation_reports
from sel_tools.diff_creation.create_diff import create_diff
from sel_tools.diff_creation.report import write_diff_reports
from sel_tools.file_export.export_item import export_items
from sel_tools.file_parsing.slide_parser import get_tasks_from_slides
from sel_tools.gitlab_api.add_user import add_users
from sel_tools.gitlab_api.comment_issue import comment_issues
from sel_tools.gitlab_api.create_commit import commit_changes, upload_files
from sel_tools.gitlab_api.create_issue import create_issues
from sel_tools.gitlab_api.fetch_repo import fetch_repos
from sel_tools.utils.args import ArgumentParserFactory
from sel_tools.utils.comment import Comment
from sel_tools.utils.task import configure_tasks


def edit_create_issues(args: Namespace) -> None:
    """Default action for create_issues subcommand."""
    tasks = get_tasks_from_slides(Path(args.issue_md_slides.name))
    tasks = configure_tasks(tasks, args.due_date, args.homework_number)
    create_issues(tasks, Path(args.student_repo_info_file.name), args.gitlab_token)


def edit_comment_issue(args: Namespace) -> None:
    """Default action for comment_issue subcommand."""
    comment = Comment.create(args.issue_number, args.message, args.state_event)
    comment_issues(comment, Path(args.student_repo_info_file.name), args.gitlab_token)


def edit_fetch_code(args: Namespace) -> None:
    """Default action for fetch_code subcommand."""
    fetch_repos(
        args.workspace, Path(args.student_repo_info_file.name), args.gitlab_token
    )


def edit_evaluate_code(args: Namespace) -> None:
    """Default action for evaluate_code subcommand."""
    gitlab_projects = fetch_repos(
        args.workspace, Path(args.student_repo_info_file.name), args.gitlab_token
    )
    factory = EvaluationJobFactory.load_factory_from_file(args.job_factory)
    evaluation_reports = evaluate_code(
        factory, gitlab_projects, args.homework_number, args.evaluation_date
    )
    write_evaluation_reports(
        evaluation_reports, f"homework-{args.homework_number}-report"
    )
    diff_reports = create_diff(
        [project.local_path for project in gitlab_projects],
        args.date_last_homework,
        args.evaluation_date,
    )
    write_diff_reports(diff_reports, f"homework-{args.homework_number}-diff")


def edit_upload_files(args: Namespace) -> None:
    """Default action for upload_files subcommand."""
    upload_files(
        args.source_path, Path(args.student_repo_info_file.name), args.gitlab_token
    )


def edit_commit_changes(args: Namespace) -> None:
    """Default action for commit_changes subcommand."""
    gitlab_projects = fetch_repos(
        args.workspace, Path(args.student_repo_info_file.name), args.gitlab_token
    )
    student_repos = [project.local_path for project in gitlab_projects]
    export_items(args.source_path, student_repos, args.keep_solutions)
    commit_changes(student_repos, args.message)


def edit_add_users(args: Namespace) -> None:
    """Default action for add_users subcommand."""
    add_users(
        Path(args.student_repo_info_file.name),
        Path(args.student_group_info_file.name),
        args.gitlab_token,
    )


def parse_arguments(arguments: list[str]) -> Namespace:
    """Parse CLI arguments."""
    # pylint: disable=too-many-locals

    parser = ArgumentParserFactory.default_parser(__doc__).parser
    subparsers = parser.add_subparsers(
        title="actions", dest="actions", help="sub-command help", required=True
    )

    # Common arguments
    factory = ArgumentParserFactory.parent_parser()
    factory.add_student_repo_info_file()
    factory.add_gitlab_token()

    # Create issues parser
    create_issue_factory = factory.copy()
    create_issue_factory.add_issue_md_slide()
    create_issue_factory.add_homework_number()
    create_issue_factory.add_due_date()
    parser_issues = subparsers.add_parser(
        "create_issues",
        parents=[create_issue_factory.parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Create Gitlab issues from homework slides",
        help="Create Gitlab issues from homework slides",
    )
    parser_issues.set_defaults(func=edit_create_issues)

    # Comment issues parser
    comment_issue_factory = factory.copy()
    comment_issue_factory.add_issue_number()
    comment_issue_factory.add_message("Message or path to a .md file")
    comment_issue_factory.add_state_event()
    parser_comment = subparsers.add_parser(
        "comment_issue",
        parents=[comment_issue_factory.parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Comment to Gitlab issues via message or markdown slides",
        help="Comment to Gitlab issues via message or markdown slides",
    )
    parser_comment.set_defaults(func=edit_comment_issue)

    # Fetch code parser
    fetch_code_factory = factory.copy()
    fetch_code_factory.add_workspace()
    parser_fetch = subparsers.add_parser(
        "fetch_code",
        parents=[fetch_code_factory.parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Fetch (clone or pull) Gitlab repositories",
        help="Fetch (clone or pull) Gitlab repositories",
    )
    parser_fetch.set_defaults(func=edit_fetch_code)

    # Evaluate code parser
    evaluate_code_factory = factory.copy()
    evaluate_code_factory.add_homework_number()
    evaluate_code_factory.add_job_factory_path()
    evaluate_code_factory.add_workspace()
    evaluate_code_factory.add_date_sine_last_homework()
    evaluate_code_factory.add_evaluation_date()
    parser_evaluate = subparsers.add_parser(
        "evaluate_code",
        parents=[evaluate_code_factory.parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Fetch (clone or pull) Gitlab repositories and evaluate code",
        help="Fetch (clone or pull) Gitlab repositories and evaluate code",
    )
    parser_evaluate.set_defaults(func=edit_evaluate_code)

    # Upload files parser
    upload_files_factory = factory.copy()
    upload_files_factory.add_source_folder(None)
    parser_upload_files = subparsers.add_parser(
        "upload_files",
        parents=[upload_files_factory.parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Upload files via commit to Gitlab from source folder",
        help="Upload files via commit to Gitlab from source folder",
    )
    parser_upload_files.set_defaults(func=edit_upload_files)

    # Commit changes parser
    commit_changes_factory = factory.copy()
    commit_changes_factory.add_source_folder(None)
    commit_changes_factory.add_message("Commit message used for all repos")
    commit_changes_factory.add_workspace()
    commit_changes_factory.add_keep_solutions()
    parser_commit_changes = subparsers.add_parser(
        "commit_changes",
        parents=[commit_changes_factory.parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Copy source folder to workspace and commit the changes",
        help="Copy source folder to workspace and commit the changes",
    )
    parser_commit_changes.set_defaults(func=edit_commit_changes)

    # Add users parser
    add_users_factory = factory.copy()
    add_users_factory.add_student_group_info_file()
    parser_add_users = subparsers.add_parser(
        "add_users",
        parents=[add_users_factory.parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Add all users to their respective repositories",
        help="Add all users to their respective repositories",
    )
    parser_add_users.set_defaults(func=edit_add_users)

    return parser.parse_args(arguments[1:])


def main() -> None:
    """main."""
    args = parse_arguments(sys.argv)
    args.func(args)


if __name__ == "__main__":
    main()
