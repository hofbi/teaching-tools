"""Test Comment Module."""

from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import REPO_DIR
from sel_tools.utils.comment import Comment

MD_TEXT = """This is a comment

## Attachments

Find one attachment [here](/path/to/attachment.txt)
"""


class CommentTest(TestCase):
    """Comment test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_minimal_constructor(self) -> None:
        unit = Comment(42, "message text")
        self.assertEqual(unit.issue_id, 42)
        self.assertEqual(unit.message, "message text")
        self.assertIsNone(unit.state_event)
        self.assertListEqual([], unit.attachments)

    def test_maximal_constructor(self) -> None:
        unit = Comment(
            42,
            "message text",
            "close",
            [Path("one"), Path("two")],
        )
        self.assertEqual(unit.issue_id, 42)
        self.assertEqual(unit.message, "message text")
        self.assertEqual(unit.state_event, "close")
        self.assertListEqual(unit.attachments, [Path("one"), Path("two")])

    def test_create_from_message_should_contain_message_and_no_attachments(
        self,
    ) -> None:
        result = Comment.create(42, "message text", None)

        self.assertEqual(42, result.issue_id)
        self.assertEqual(result.message, "message text")
        self.assertIsNone(result.state_event)
        self.assertListEqual([], result.attachments)

    def test_create_from_message_with_attachment_should_contain_message_and_one_attachment(
        self,
    ) -> None:
        result = Comment.create(42, "message with [attachment](/path/to/attachment.txt)", None)

        self.assertEqual(42, result.issue_id)
        self.assertIn("message with ", result.message)
        self.assertIsNone(result.state_event)
        self.assertListEqual([REPO_DIR / "path/to/attachment.txt"], result.attachments)

    def test_create_from_message_and_close_should_contain_message_and_close_and_no_attachments(
        self,
    ) -> None:
        result = Comment.create(42, "message text", "close")

        self.assertEqual(42, result.issue_id)
        self.assertEqual(result.message, "message text")
        self.assertEqual(result.state_event, "close")
        self.assertListEqual([], result.attachments)

    def test_create_from_file_should_contain_message_and_no_attachments(self) -> None:
        self.fs.create_file("simple.md", contents="A simple text from file")

        result = Comment.create(42, "simple.md", None)

        self.assertEqual(42, result.issue_id)
        self.assertEqual(result.message, "A simple text from file")
        self.assertIsNone(result.state_event)
        self.assertListEqual([], result.attachments)

    def test_create_from_file_with_attachments_should_contain_message_and_attachments(
        self,
    ) -> None:
        self.fs.create_file("markdown.md", contents=MD_TEXT)

        result = Comment.create(42, "markdown.md", None)

        self.assertEqual(42, result.issue_id)
        self.assertIn("This is a comment", result.message)
        self.assertIn("## Attachments", result.message)
        self.assertIsNone(result.state_event)
        self.assertListEqual([REPO_DIR / "path/to/attachment.txt"], result.attachments)
