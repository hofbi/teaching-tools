"""Test task module."""

import unittest
from datetime import date
from pathlib import Path

from sel_tools.utils.task import Task, configure_tasks


class TaskModuleTest(unittest.TestCase):
    """Task module test."""

    def test_configure_tasks_empty_list_should_stay_empty(self) -> None:
        tasks = configure_tasks([], date(2000, 12, 31), 3)
        self.assertListEqual([], tasks)

    def test_configure_tasks_should_correctly_configure_date_and_label(self) -> None:
        task = Task("lorem", "ipsum", "dolor")

        tasks = configure_tasks([task], date(2000, 12, 31), 3)

        self.assertEqual(tasks[0].title, "lorem")
        self.assertEqual(tasks[0].description, "ipsum")
        self.assertEqual(tasks[0].documentation, "dolor")
        self.assertEqual(tasks[0].due_date, date(2000, 12, 31))
        self.assertEqual(tasks[0].label, "homework::3")
        self.assertListEqual([], tasks[0].attachments)


class TaskTest(unittest.TestCase):
    """Task test."""

    def test_minimal_constructor(self) -> None:
        unit = Task("lorem", "ipsum", "dolor")
        self.assertEqual(unit.title, "lorem")
        self.assertEqual(unit.description, "ipsum")
        self.assertEqual(unit.documentation, "dolor")
        self.assertIsNone(unit.due_date)
        self.assertIsNone(unit.label)
        self.assertListEqual([], unit.attachments)

    def test_maximal_constructor(self) -> None:
        unit = Task(
            "sit",
            "amet",
            "consectetur",
            date(2000, 12, 31),
            "adipisici",
            [Path("elit"), Path("sed")],
        )

        self.assertEqual(unit.title, "sit")
        self.assertEqual(unit.description, "amet")
        self.assertEqual(unit.documentation, "consectetur")
        self.assertEqual(unit.due_date, date(2000, 12, 31))
        self.assertEqual(unit.label, "adipisici")
        self.assertListEqual(unit.attachments, [Path("elit"), Path("sed")])

    def test_add_homework_label(self) -> None:
        unit = Task("lorem", "ipsum", "dolor")
        unit.add_homework_label(3)
        self.assertEqual(unit.label, "homework::3")
