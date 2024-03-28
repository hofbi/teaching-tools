"""Tests for attachment uploading."""

from pathlib import Path
from unittest.mock import MagicMock

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import REPO_DIR
from sel_tools.gitlab_api.attachments import (
    replace_file_paths_with_urls,
    upload_attachments,
)


class AttachmentsTest(TestCase):
    """Attachments test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_replace_file_paths_with_urls(self) -> None:
        description = """Some text with [a file](/path/to/file.txt) and some
[other file](/path/to/different/file.cpp) with links relative to the repository"""
        uploaded_files = [{"url": "gitlab.com/file1"}, {"url": "gitlab.com/file2"}]
        txt_file = REPO_DIR / "path/to/file.txt"
        cpp_file = REPO_DIR / "path/to/different/file.cpp"
        attachments = [txt_file, cpp_file]
        self.fs.create_dir(REPO_DIR)
        self.fs.create_file(txt_file)
        self.fs.create_file(cpp_file)

        revised_description = replace_file_paths_with_urls(description, uploaded_files, attachments)
        self.assertEqual(
            revised_description,
            """Some text with [a file](gitlab.com/file1) and some
[other file](gitlab.com/file2) with links relative to the repository""",
        )

    def test_upload_attachments_no_attachment_no_uploaded_files(self) -> None:
        attachments: list[Path] = []
        gitlab_project = MagicMock()

        results = upload_attachments(attachments, gitlab_project)

        self.assertListEqual([], results)

    def test_upload_attachments_one_attachment_one_uploaded_file_path(self) -> None:
        attachments = [Path("/path/to/file.txt")]
        gitlab_project = MagicMock()
        gitlab_project.upload = MagicMock(return_value={"url": "/uploads/hash/file.txt"})

        results = upload_attachments(attachments, gitlab_project)

        self.assertEqual("/uploads/hash/file.txt", results[0]["url"])
