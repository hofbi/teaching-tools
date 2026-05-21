"""Test Comment Module."""

import unittest
from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import REPO_DIR
from sel_tools.utils.comment import Comment, ProjectCommentParser

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


MULTI_PROJECT_COMMENT = f"""{ProjectCommentParser.PROJECT_COMMENT_IDENTIFIER_PREFIX} 123

### Results Group 123

Good job project 123

{ProjectCommentParser.PROJECT_COMMENT_FOOTER}

{ProjectCommentParser.PROJECT_COMMENT_IDENTIFIER_PREFIX} 456

### Results Group 456

Sorry 456

{ProjectCommentParser.PROJECT_COMMENT_FOOTER}
"""

INVALID_MULTI_PROJECT_COMMENT = f"""{ProjectCommentParser.PROJECT_COMMENT_IDENTIFIER_PREFIX} 123
{ProjectCommentParser.PROJECT_COMMENT_FOOTER}
"""


class ProjectCommentParserTest(unittest.TestCase):
    """Project Comment Parser Test."""

    def test_get_comment_for_project_with_no_project_specific_markers_should_return_full_copy(self) -> None:
        original_comment = Comment(42, "message")

        unit = ProjectCommentParser(original_comment, [1])
        result_comment = unit.get_comment_for_project(1)

        self.assertTrue(unit.is_same_comment_for_all_projects)
        self.assertEqual(result_comment, original_comment)
        original_comment.message = "foo"
        self.assertNotEqual(result_comment, original_comment)

    def test_get_comment_for_project_with_project_specific_markers_should_return_project_comment(self) -> None:
        original_comment = Comment(42, MULTI_PROJECT_COMMENT)

        unit = ProjectCommentParser(original_comment, [123, 456])
        result_comment = unit.get_comment_for_project(123)

        self.assertFalse(unit.is_same_comment_for_all_projects)
        self.assertNotEqual(result_comment, original_comment)
        self.assertEqual(result_comment.issue_id, 42)
        self.assertIn("Good job project 123", result_comment.message)
        self.assertIn("### Results Group 123", result_comment.message)
        self.assertNotIn("456", result_comment.message)

    def test_get_comment_for_project_with_project_specific_markers_but_different_id_should_raise(self) -> None:
        original_comment = Comment(42, MULTI_PROJECT_COMMENT)

        unit = ProjectCommentParser(original_comment, [123, 456])

        self.assertFalse(unit.is_same_comment_for_all_projects)
        with self.assertRaisesRegex(LookupError, r"not in list of expect project IDs"):
            unit.get_comment_for_project(789)

    def test_constructor_with_project_specific_markers_but_less_ids_in_list_should_raise(self) -> None:
        original_comment = Comment(42, MULTI_PROJECT_COMMENT)

        with self.assertRaisesRegex(LookupError, r"No exact overlap for project IDs"):
            ProjectCommentParser(original_comment, [123])

    def test_constructor_with_project_specific_markers_but_more_ids_in_list_should_raise(self) -> None:
        original_comment = Comment(42, MULTI_PROJECT_COMMENT)

        with self.assertRaisesRegex(LookupError, r"No exact overlap for project IDs"):
            ProjectCommentParser(original_comment, [123, 456, 789])

    def test_constructor_with_project_specific_markers_but_different_ids_in_list_should_raise(self) -> None:
        original_comment = Comment(42, MULTI_PROJECT_COMMENT)

        with self.assertRaisesRegex(LookupError, r"No exact overlap for project IDs"):
            ProjectCommentParser(original_comment, [123, 789])

    def test_get_comment_with_project_specific_markers_but_invalid_comment_should_raise(self) -> None:
        original_comment = Comment(42, INVALID_MULTI_PROJECT_COMMENT)

        unit = ProjectCommentParser(original_comment, [123])

        self.assertFalse(unit.is_same_comment_for_all_projects)
        with self.assertRaisesRegex(LookupError, r"Invalid project specific comment"):
            unit.get_comment_for_project(123)
