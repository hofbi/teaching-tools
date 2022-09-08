"""Comment module."""

from dataclasses import dataclass, field
from pathlib import Path

from sel_tools.file_parsing.slide_parser import get_attachments


@dataclass
class Comment:
    """Issue Comment."""

    issue_id: int
    message: str
    state_event: str | None = None
    attachments: list[Path] = field(default_factory=lambda: [])

    @staticmethod
    def create(
        issue_id: int, message_or_file_path: str, state_event: str | None
    ) -> "Comment":
        file_path = Path(message_or_file_path)
        message = file_path.read_text() if file_path.is_file() else message_or_file_path
        return Comment(issue_id, message, state_event, get_attachments(message))
