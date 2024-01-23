"""Test student group parser module."""

from pathlib import Path

from pandas import DataFrame
from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.file_parsing.student_group_parser import (
    Student,
    get_student_groups_from_file,
)

from tests.helper import STUDENT1, STUDENT2

STUDENT_NOT_ANSWERED = {
    "Last name": "def",
    "First name": "abc",
    "matriculation-id": "01234567",
    "Email address": "abc.def@tum.de",
    "Group": "Standardgruppe 123456",
    "Choice": "Not answered yet",
}


class ParserTest(TestCase):
    """Parser test."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_from_dict(self) -> None:
        self.assertEqual(
            Student.from_dict(STUDENT1),
            Student(
                STUDENT1["First name"],
                STUDENT1["Last name"],
                STUDENT1["Email address"],
                STUDENT1["Choice"],
            ),
        )

    def test_no_csv_file(self) -> None:
        self.fs.create_file("group_formation.txt", contents="")
        self.assertRaises(
            ValueError, get_student_groups_from_file, Path("group_formation.txt")
        )

    def test_get_students_from_file(self) -> None:
        content = DataFrame([STUDENT1, STUDENT2])
        content.to_csv("group_formation.csv")
        expected_student_arr = [
            Student.from_dict(STUDENT1),
            Student.from_dict(STUDENT2),
        ]
        self.assertEqual(
            get_student_groups_from_file(Path("group_formation.csv")),
            expected_student_arr,
        )

    def test_semicolon_separated(self) -> None:
        content = DataFrame([STUDENT1, STUDENT2])
        content.to_csv("group_formation.csv", sep=";")
        expected_student_arr = [
            Student.from_dict(STUDENT1),
            Student.from_dict(STUDENT2),
        ]
        self.assertEqual(
            get_student_groups_from_file(Path("group_formation.csv")),
            expected_student_arr,
        )

    def test_not_answered_yet(self) -> None:
        content = DataFrame([STUDENT1, STUDENT_NOT_ANSWERED])
        content.to_csv("group_formation.csv")
        expected_student_arr = [Student.from_dict(STUDENT1)]
        self.assertEqual(
            get_student_groups_from_file(Path("group_formation.csv")),
            expected_student_arr,
        )

    def test_file_in_german(self) -> None:
        content = DataFrame([STUDENT1, STUDENT2])
        headers_german = [
            "Nachname",
            "Vorname",
            "Matrikelnummer",
            "E-Mail-Adresse",
            "Gruppe",
            "Abstimmung",
        ]
        content.to_csv("group_formation.csv", header=headers_german)
        self.assertRaises(
            KeyError, get_student_groups_from_file, Path("group_formation.csv")
        )

    def test_vowel_mutation(self) -> None:
        content = DataFrame([STUDENT1, STUDENT2])
        content.to_csv("group_formation.csv")
        expected_student_arr = [
            Student.from_dict(STUDENT1),
            Student.from_dict(STUDENT2),
        ]
        self.assertEqual(
            get_student_groups_from_file(Path("group_formation.csv")),
            expected_student_arr,
        )

    def test_not_utf8_encoded(self) -> None:
        content = DataFrame([STUDENT1, STUDENT2])
        content.to_csv("group_formation.csv", encoding="latin_1")
        self.assertRaises(
            UnicodeError, get_student_groups_from_file, Path("group_formation.csv")
        )
