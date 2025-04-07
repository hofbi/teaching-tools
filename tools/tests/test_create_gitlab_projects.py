"""Tests for CLI argument parser."""

from pathlib import Path

from create_gitlab_projects import parse_arguments
from pyfakefs.fake_filesystem_unittest import TestCase
from sel_tools.config import REPO_DIR


class ArgumentParserTest(TestCase):
    """Tests for CLI argument parser."""

    def setUp(self) -> None:
        self.setUpPyfakefs()

    def test_minimum_parameter_set(self) -> None:
        args = parse_arguments(["foo.py", "my_base_name", "-g", "5421", "-t", "123"])

        self.assertEqual(args.repo_base_name, "my_base_name")
        self.assertEqual(args.group_id, 5421)
        self.assertEqual(args.gitlab_token, "123")

        # Default values
        self.assertEqual(args.number_of_repos, 1)
        expected_source_dir = REPO_DIR / "export" / "homework"
        self.assertEqual(args.source_path, expected_source_dir)
        expected_repo_info_dir = REPO_DIR / "config"
        self.assertEqual(args.repo_info_dir, expected_repo_info_dir)
        self.assertFalse(args.publish_solutions)

    def test_maximum_parameter_set(self) -> None:
        self.fs.create_dir("config_folder")
        self.fs.create_dir("output/homework")
        args = parse_arguments(
            [
                "foo.py",
                "swe",
                "-g",
                "1245",
                "-r",
                "config_folder",
                "-t",
                "456",
                "-n",
                "4",
                "-s",
                "output/homework",
                "--publish-solutions",
            ]
        )

        self.assertEqual(args.repo_base_name, "swe")
        self.assertEqual(args.group_id, 1245)
        self.assertEqual(args.gitlab_token, "456")
        self.assertEqual(args.number_of_repos, 4)
        self.assertEqual(args.source_path, Path("output/homework"))
        self.assertEqual(args.repo_info_dir, Path("config_folder"))
        self.assertTrue(args.publish_solutions)
