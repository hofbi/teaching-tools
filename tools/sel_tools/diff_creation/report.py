"""Git diff report"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers.diff import DiffLexer


@dataclass
class Diff:
    """Git diff model"""

    hexsha: str
    author: str
    message: str
    patch: str


@dataclass
class DiffReport:
    """Git diff model"""

    def __init__(self, repo_path: Path, diffs: List[Diff]):
        self.repo_path = repo_path
        self.diffs = diffs

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
            base_path.with_suffix(".patch").write_text(diff.patch)
            base_path.with_suffix(".html").write_text(self.highlight_diff(diff.patch))

    @staticmethod
    def highlight_diff(patch: str) -> str:
        return str(
            highlight(patch, DiffLexer(), HtmlFormatter(full=True, style="manni"))
        )


def write_diff_reports(reports: List[DiffReport], report_base_name: str) -> None:
    """Write diff reports to disk"""
    for report in reports:
        report.generate_overview_table().to_csv(
            report.repo_path.joinpath(report_base_name).with_suffix(".csv")
        )
        report.write_diff_patches()
