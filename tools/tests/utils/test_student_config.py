"""Tests for config functions."""

import json
from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import GIT_MAIN_BRANCH
from sel_tools.utils.student_config import (
    get_branch_from_student_config,
    read_student_repo_info_from_config_file,
    store_student_repo_info_to_config_file,
)


class TestConfig(TestCase):
    """Tests for config functions."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_get_branch_from_student_config_with_branch(self) -> None:
        student_config = {"id": 123, "branch": "feature-branch"}
        branch = get_branch_from_student_config(student_config)
        self.assertEqual(branch, "feature-branch")

    def test_get_branch_from_student_config_without_branch(self) -> None:
        student_config = {"id": 123}
        branch = get_branch_from_student_config(student_config)
        self.assertEqual(branch, GIT_MAIN_BRANCH)

    def test_store_student_repo_info_to_config_file(self) -> None:
        repo_info_dir = Path("config")
        self.fs.create_dir(repo_info_dir)

        config_file = store_student_repo_info_to_config_file(repo_info_dir, "group_name", [{"id": 1}, {"id": 2}])

        self.assertTrue(config_file.is_file())
        config_file_content = json.loads(config_file.read_text())
        self.assertListEqual(config_file_content, [{"id": 1}, {"id": 2}])

    def test_read_student_repo_info_from_config_file(self) -> None:
        config_file = Path("config/group_name.json")
        self.fs.create_file(config_file, contents=json.dumps([{"id": 1}, {"id": 2}]))

        config_file_content = read_student_repo_info_from_config_file(config_file)
        self.assertListEqual(config_file_content, [{"id": 1}, {"id": 2}])
