"""Comment module."""

import re
from copy import deepcopy
from dataclasses import dataclass, field, replace
from pathlib import Path

from sel_tools.file_parsing.slide_parser import get_attachments


@dataclass
class Comment:
    """Issue Comment."""

    issue_id: int
    message: str
    state_event: str | None = None
    attachments: list[Path] = field(default_factory=list)

    @staticmethod
    def create(issue_id: int, message_or_file_path: str, state_event: str | None) -> "Comment":
        file_path = Path(message_or_file_path)
        message = file_path.read_text() if file_path.is_file() else message_or_file_path
        return Comment(issue_id, message, state_event, get_attachments(message))


class ProjectCommentParser:
    """Parse and validate project specific comments from a Comment."""

    PROJECT_COMMENT_IDENTIFIER_PREFIX = "## Comments for Project"
    PROJECT_COMMENT_FOOTER = "---"

    def __init__(self, comment: Comment, student_project_ids: list[int]) -> None:
        self.__is_same_comment_for_all_projects = True
        if self.PROJECT_COMMENT_IDENTIFIER_PREFIX in comment.message:
            has_project_ids = [
                f"{self.PROJECT_COMMENT_IDENTIFIER_PREFIX} {project_id}" in comment.message
                for project_id in student_project_ids
            ]
            prefix_count = comment.message.count(self.PROJECT_COMMENT_IDENTIFIER_PREFIX)
            footer_count = comment.message.count(self.PROJECT_COMMENT_IDENTIFIER_PREFIX)
            if not (all(has_project_ids) and len(has_project_ids) == prefix_count == footer_count):
                msg = "No exact overlap for project IDs in comment text and student project config!"
                raise LookupError(msg)
            self.__is_same_comment_for_all_projects = False
        self.__comment = comment
        self.__student_project_ids = student_project_ids

    @property
    def is_same_comment_for_all_projects(self) -> bool:
        return self.__is_same_comment_for_all_projects

    def get_comment_for_project(self, project_id: int) -> Comment:
        if self.is_same_comment_for_all_projects:
            return deepcopy(self.__comment)

        if project_id not in self.__student_project_ids:
            msg = f"Project ID {project_id} not in list of expect project IDs."
            raise LookupError(msg)

        project_comment_pattern = (
            rf"{self.PROJECT_COMMENT_IDENTIFIER_PREFIX} {project_id}\n(.*?)\n{self.PROJECT_COMMENT_FOOTER}"
        )
        matches = re.findall(project_comment_pattern, self.__comment.message, re.DOTALL)
        if matches:
            return replace(self.__comment, message=matches[0])

        msg = "Invalid project specific comment."
        raise LookupError(msg)
