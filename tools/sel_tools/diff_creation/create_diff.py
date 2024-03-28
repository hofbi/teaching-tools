"""Diff creation module."""

from datetime import date
from pathlib import Path

import git
from git.objects.commit import Commit
from tqdm import tqdm

from sel_tools.diff_creation.report import Diff, DiffReport


def create_diff(
    repo_paths: list[Path],
    date_last_homework: date | None,
    evaluation_date: date | None,
) -> list[DiffReport]:
    """Create diff for given repositories since the last homework date."""
    return (
        []
        if date_last_homework is None
        else [
            DiffCreator(repo_path, "build").create(date_last_homework, evaluation_date)
            for repo_path in tqdm(repo_paths, desc=f"Create diff since {date_last_homework}")
        ]
    )


class DiffCreator:
    """Diff creator class."""

    def __init__(self, repo_path: Path, exclude: str | None = None) -> None:
        self.__path = repo_path
        self.__repo = git.Repo(self.__path)
        self.__exclude = exclude

    def create(self, date_last_homework: date, evaluation_date: date | None) -> DiffReport:
        commits_since_last_homework = list(
            self.__repo.iter_commits(since=date_last_homework, before=evaluation_date, no_merges=True)
        )
        diffs = (
            [
                self.__create_overall_diff(commits_since_last_homework[-1]),
                *self.__create_diff_per_commit(commits_since_last_homework),
            ]
            if commits_since_last_homework
            else []
        )
        return DiffReport(self.__path, diffs)

    def __create_overall_diff(self, commit: Commit) -> Diff:
        patch = (
            self.__repo.git.diff(commit.tree)
            if self.__exclude is None
            else self.__repo.git.diff(commit.tree, f":(exclude){self.__exclude}")
        )
        return Diff(
            commit.hexsha,
            "total",
            str(commit.summary),
            patch,
        )

    def __create_diff_per_commit(self, commits: list[Commit]) -> list[Diff]:
        return [
            Diff(
                commit.hexsha,
                str(commit.author),
                str(commit.summary),
                self.__repo.git.diff(commit.parents[0].tree, commit.tree),
            )
            for commit in commits
            if commit.parents
        ]
