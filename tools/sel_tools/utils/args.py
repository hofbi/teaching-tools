"""Argparse helper module."""

import copy
from argparse import Action, ArgumentDefaultsHelpFormatter, ArgumentParser, FileType
from datetime import date
from pathlib import Path
from typing import Any

from sel_tools.config import REPO_DIR


def dir_path(path_string: str) -> Path:
    """Argparse type check if path is a directory."""
    if Path(path_string).is_dir():
        return Path(path_string)
    raise NotADirectoryError(path_string)


def file_path(path_string: str) -> Path:
    """Argparse type check if path is a file."""
    if Path(path_string).is_file():
        return Path(path_string)
    raise FileNotFoundError(path_string)


class DateAction(Action):
    """Parse dates from CLI arguments into datetime.date."""

    def __call__(self, arg_parser, args, values, option_string=None):  # type: ignore[no-untyped-def]
        due_date = date.fromisoformat(f"{values[0]:04}-{values[1]:02}-{values[2]:02}")
        setattr(args, self.dest, due_date)


class ArgumentParserFactory:  # pylint: disable=too-many-public-methods
    """Argument Parser Factory to setup commonly used arguments."""

    def __init__(self, parser: ArgumentParser) -> None:
        self.__parser = parser

    @staticmethod
    def default_parser(description: str) -> "ArgumentParserFactory":
        return ArgumentParserFactory(
            ArgumentParser(
                description=description,
                formatter_class=ArgumentDefaultsHelpFormatter,
            )
        )

    @staticmethod
    def parent_parser() -> "ArgumentParserFactory":
        return ArgumentParserFactory(ArgumentParser(add_help=False))

    @staticmethod
    def create_default_date_arg() -> dict:
        return {
            "metavar": ("YEAR", "MONTH", "DAY"),
            "type": int,
            "nargs": 3,
            "action": DateAction,
            "default": None,
        }

    @staticmethod
    def default_or_required_if_none(default: Any) -> dict:
        return {"required": True} if default is None else {"default": default}

    @property
    def parser(self) -> ArgumentParser:
        return self.__parser

    def copy(self) -> "ArgumentParserFactory":
        return copy.deepcopy(self)

    def add_gitlab_token(self) -> None:
        self.__parser.add_argument(
            "-t",
            "--gitlab-token",
            type=str,
            required=True,
            help="Private gitlab token",
        )

    def add_student_repo_info_file(self) -> None:
        self.__parser.add_argument(
            "student_repo_info_file",
            type=FileType("r"),
            help="File which contains the student repositories info (name, id)",
        )

    def add_homework_number(self) -> None:
        self.__parser.add_argument(
            "-n",
            "--homework-number",
            type=int,
            required=True,
            help="Homework number as integer",
        )

    def add_workspace(self) -> None:
        self.__parser.add_argument(
            "-w",
            "--workspace",
            type=dir_path,
            default=REPO_DIR / "workspace",
            help="Path to the workspace where all repositories will be cloned/pulled",
        )

    def add_issue_md_slide(self) -> None:
        self.__parser.add_argument(
            "-i",
            "--issue-md-slides",
            type=FileType("r"),
            required=True,
            help="Path to the markdown slides used for creating the issues",
        )

    def add_due_date(self) -> None:
        self.__parser.add_argument(
            "-d",
            "--due-date",
            **ArgumentParserFactory.create_default_date_arg(),
            help="Due date for the homework's task(s)",
        )

    def add_date_sine_last_homework(self) -> None:
        self.__parser.add_argument(
            "-d",
            "--date-last-homework",
            **ArgumentParserFactory.create_default_date_arg(),
            help="Date of the last homework used to generate a diff. If no date is provided, no diff will be generated",
        )

    def add_message(self, help_text: str) -> None:
        self.__parser.add_argument(
            "-m",
            "--message",
            type=str,
            required=True,
            help=help_text,
        )

    def add_issue_number(self) -> None:
        self.__parser.add_argument(
            "-i",
            "--issue-number",
            type=int,
            required=True,
            help="Issue number the comment should be added",
        )

    def add_state_event(self) -> None:
        self.__parser.add_argument(
            "-s",
            "--state-event",
            type=str,
            choices=["close", "reopen"],
            default=None,
            help="Changes the state of the issue to",
        )

    def add_source_folder(self, default: Path | None) -> None:
        self.__parser.add_argument(
            "-s",
            "--source-path",
            type=dir_path,
            **ArgumentParserFactory.default_or_required_if_none(default),
            help="Path to the source files",
        )

    def add_number_of_repos(self) -> None:
        self.__parser.add_argument(
            "-n",
            "--number-of-repos",
            type=int,
            default=1,
            help="Number of repos to create",
        )

    def add_repo_info_dir(self) -> None:
        self.__parser.add_argument(
            "-r",
            "--repo-info-dir",
            type=dir_path,
            default=REPO_DIR / "config",
            help="Folder into which the config file containing the repositories info (name, id) will be saved",
        )

    def add_group_id(self) -> None:
        self.__parser.add_argument(
            "-g",
            "--group-id",
            type=int,
            required=True,
            help="ID of an existing GitLab group",
        )

    def add_repo_base_name(self) -> None:
        self.__parser.add_argument(
            "repo_base_name",
            type=str,
            help="Base name of the to-be-created repo(s)",
        )

    def add_output_path(self) -> None:
        self.__parser.add_argument(
            "-o",
            "--output-dir",
            default=REPO_DIR / "export",
            type=Path,
            help="Path to export location",
        )

    def add_keep_solutions(self) -> None:
        self.__parser.add_argument(
            "-k",
            "--keep-solutions",
            action="store_true",
            help="Keep solution blocks from exported files",
        )

    def add_evaluation_date(self) -> None:
        self.__parser.add_argument(
            "-e",
            "--evaluation-date",
            **ArgumentParserFactory.create_default_date_arg(),
            help="Date of the evaluation deadline",
        )

    def add_job_factory_path(self) -> None:
        self.__parser.add_argument(
            "-j",
            "--job-factory",
            type=file_path,
            default=REPO_DIR
            / "tools"
            / "sel_tools"
            / "code_evaluation"
            / "jobs"
            / "sel.py",
            help="Path to the python module containing the evaluation job factory",
        )

    def add_student_group_info_file(self) -> None:
        self.__parser.add_argument(
            "student_group_info_file",
            type=FileType("r"),
            help="File which contains the student groups info",
        )
