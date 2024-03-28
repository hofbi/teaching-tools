"""Test slide parser module."""

from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import REPO_DIR
from sel_tools.file_parsing.slide_parser import get_attachments, get_tasks_from_slides
from sel_tools.utils.task import Task

FILE_WITHOUT_TASK = "# Header\n\nsome content\n\n---"
TASK_1_DESCRIPTION = "\nDo something clever\n\n```shell\n# Comment\n$ make\n```\n\n"
ATTACHMENT = "Material for this task: [Text of the attachment](/path/to/local/file)\n"
FILE_WITH_TASK_WITHOUT_FOOTER = FILE_WITHOUT_TASK + "\n\n## Task 1 - Do stuff\n" + TASK_1_DESCRIPTION
FILE_WITH_ONE_TASK = FILE_WITH_TASK_WITHOUT_FOOTER + "---\n\n## Other content\n\nText\n\n---"

TASK_2_DESCRIPTION = "\n Don't stop working!\nKeep it up\n\n"
FILE_WITH_TWO_TASKS = FILE_WITH_ONE_TASK + "\n\n## Task 2 - Do more\n" + TASK_2_DESCRIPTION + "---\n"
DOCUMENTATION = "\n[First ref](www.google.de)\n[Second ref](gitlab.com)\n"
FILE_WITH_TWO_TASKS_AND_DOCUMENTATION = FILE_WITH_TWO_TASKS + "\n## Documentation\n" + DOCUMENTATION
FILE_WITH_TASK_AND_ATTACHMENT = FILE_WITH_TASK_WITHOUT_FOOTER + ATTACHMENT + "---\n"

TASK_WITH_SPECIAL_CHARACTERS_IN_TITLE = """## Task 1 - `~!@#$%^&*()_+|;'"<>.,-:ab12
bla-bla
do stuff
---"""


class ParserTest(TestCase):
    """Parser test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def _check_task(self, task: Task, expected_task: Task) -> None:
        self.assertEqual(task.title, expected_task.title)
        self.assertEqual(task.description, expected_task.description)
        self.assertEqual(task.documentation, expected_task.documentation)
        self.assertListEqual(task.attachments, expected_task.attachments)

    def test_no_tasks_in_slides(self) -> None:
        self.fs.create_file("slide.md", contents=FILE_WITHOUT_TASK)
        self.assertRaises(LookupError, get_tasks_from_slides, Path("slide.md"))

    def test_incomplete_task_in_slides(self) -> None:
        self.fs.create_file("slide.md", contents=FILE_WITH_TASK_WITHOUT_FOOTER)
        self.assertRaises(LookupError, get_tasks_from_slides, Path("slide.md"))

    def test_get_only_task_from_slides(self) -> None:
        self.fs.create_file("slide.md", contents=FILE_WITH_ONE_TASK)
        tasks = get_tasks_from_slides(Path("slide.md"))
        self.assertEqual(len(tasks), 1)
        self._check_task(tasks[0], Task("Task 1 - Do stuff", TASK_1_DESCRIPTION, ""))

    def test_get_tasks_from_slides(self) -> None:
        self.fs.create_file("slide.md", contents=FILE_WITH_TWO_TASKS)
        tasks = get_tasks_from_slides(Path("slide.md"))
        self.assertEqual(len(tasks), 2)
        self._check_task(tasks[0], Task("Task 1 - Do stuff", TASK_1_DESCRIPTION, ""))
        self._check_task(tasks[1], Task("Task 2 - Do more", TASK_2_DESCRIPTION, ""))

    def test_get_tasks_from_slides_with_documentation(self) -> None:
        self.fs.create_file("slide.md", contents=FILE_WITH_TWO_TASKS_AND_DOCUMENTATION)
        tasks = get_tasks_from_slides(Path("slide.md"))
        self.assertEqual(len(tasks), 2)
        self._check_task(tasks[0], Task("Task 1 - Do stuff", TASK_1_DESCRIPTION, DOCUMENTATION))
        self._check_task(tasks[1], Task("Task 2 - Do more", TASK_2_DESCRIPTION, DOCUMENTATION))

    def test_get_task_with_attachment_from_slide(self) -> None:
        self.fs.create_file("slide.md", contents=FILE_WITH_TASK_AND_ATTACHMENT)
        tasks = get_tasks_from_slides(Path("slide.md"))
        self.assertEqual(len(tasks), 1)
        self._check_task(
            tasks[0],
            Task(
                "Task 1 - Do stuff",
                TASK_1_DESCRIPTION + ATTACHMENT,
                "",
                attachments=[REPO_DIR / "path/to/local/file"],
            ),
        )

    def test_task_title_with_dash(self) -> None:
        self.fs.create_file("slide.md", contents=TASK_WITH_SPECIAL_CHARACTERS_IN_TITLE)
        tasks = get_tasks_from_slides(Path("slide.md"))
        self.assertEqual(len(tasks), 1)
        self._check_task(
            tasks[0],
            Task("Task 1 - `~!@#$%^&*()_+|;'\"<>.,-:ab12", "bla-bla\ndo stuff\n", ""),
        )

    def test_get_attachments_on_different_lines_from_description(self) -> None:
        attachments = get_attachments(
            """Some text, then [myfile](/path/to), other attachment: [otherfile](/path/to/other).
And here's a [link](http://www.google.com), and a local file again [cmake lists](/cmake/catch2.cmake)"""
        )
        self.assertEqual(len(attachments), 3)
        self.assertListEqual(
            attachments,
            [
                REPO_DIR / "path/to",
                REPO_DIR / "path/to/other",
                REPO_DIR / "cmake/catch2.cmake",
            ],
        )

    def test_get_no_attachments_from_description_if_link_is_not_starting_with_slash(
        self,
    ) -> None:
        attachments = get_attachments("Some text, then [myfile](path/to/file)")
        self.assertListEqual([], attachments)
