"""Upload attachments to gitlab."""

from pathlib import Path

from gitlab.v4.objects.projects import Project
from sel_tools.config import REPO_DIR


def upload_attachments(attachments: list[Path], gitlab_project: Project) -> list:
    """Upload attachments to gitlab and return the URL."""
    return [
        gitlab_project.upload(attachment.name, filepath=attachment)
        for attachment in attachments
    ]


def replace_file_paths_with_urls(
    description: str, uploaded_files: list, attachments: list[Path]
) -> str:
    """Replace local file paths in description with gitlab URLs."""
    for uploaded_file, attachment in zip(uploaded_files, attachments):
        file_path_in_description = f"/{attachment.relative_to(REPO_DIR)}"
        description = description.replace(
            file_path_in_description, uploaded_file["url"]
        )
    return description
