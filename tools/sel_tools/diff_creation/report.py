"""Git diff report."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers.diff import DiffLexer

MD_WARNING_REPORT = """# Inactive Student Repositories

The following student repositories have not been updated since the last homework evaluation:

%s

Please check if the students are still active.
If not, remove them from the course and the repo config for the current semester.
The latter to make sure they are not evaluated again next time.
"""


@dataclass
class Diff:
    """Git diff model."""

    hexsha: str
    author: str
    message: str
    patch: str


@dataclass
class DiffReport:
    """Git diff model."""

    def __init__(self, repo_path: Path, diffs: list[Diff]) -> None:
        self.repo_path = repo_path
        self.diffs = diffs

    @property
    def has_diffs(self) -> bool:
        return bool(self.diffs)

    def generate_overview_table(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "hexsha": diff.hexsha,
                    "author": diff.author,
                    "message": diff.message,
                }
                for diff in self.diffs
            ]
        )

    def write_diff_patches(self) -> None:
        for index, diff in enumerate(self.diffs):
            base_path = self.repo_path / f"{index}-{diff.hexsha}"
            try:
                base_path.with_suffix(".patch").write_text(diff.patch, encoding="utf-8", errors="replace")
                base_path.with_suffix(".html").write_text(
                    self.highlight_diff(diff.patch), encoding="utf-8", errors="replace"
                )
            except UnicodeError:
                print("UnicodeError: Fallback: clean the patch text by encoding/decoding to remove surrogates")
                clean_patch = diff.patch.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
                base_path.with_suffix(".patch").write_text(clean_patch)
                base_path.with_suffix(".html").write_text(self.highlight_diff(clean_patch))

    @staticmethod
    def highlight_diff(patch: str) -> str:
        return str(highlight(patch, DiffLexer(), HtmlFormatter(full=True, style="manni")))


def write_diff_reports(reports: list[DiffReport], report_base_name: str) -> None:
    """Write diff reports to disk."""
    for report in reports:
        print(f"Writing diff report for {report.repo_path.name}")
        report.generate_overview_table().to_csv(report.repo_path.joinpath(report_base_name).with_suffix(".csv"))
        report.write_diff_patches()


def write_report_for_inactive_student_repos(reports: list[DiffReport], workspace: Path) -> None:
    """Check for repos that don't have any diffs since the last homework and write them to a file."""
    inactive_repos = [f"- {report.repo_path.name}" for report in reports if not report.has_diffs]
    print(f"Found {len(inactive_repos)} inactive student repositories.")
    if inactive_repos:
        workspace.joinpath("inactive_student_repos.md").write_text(MD_WARNING_REPORT % "\n".join(inactive_repos))
