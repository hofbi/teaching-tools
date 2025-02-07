"""Tests for config functions."""

import unittest

from sel_tools.config import GIT_MAIN_BRANCH, get_branch_from_student_config


class TestConfig(unittest.TestCase):
    """Tests for config functions."""

    def test_get_branch_from_student_config_with_branch(self) -> None:
        student_config = {"id": 123, "branch": "feature-branch"}
        branch = get_branch_from_student_config(student_config)
        self.assertEqual(branch, "feature-branch")

    def test_get_branch_from_student_config_without_branch(self) -> None:
        student_config = {"id": 123}
        branch = get_branch_from_student_config(student_config)
        self.assertEqual(branch, GIT_MAIN_BRANCH)
