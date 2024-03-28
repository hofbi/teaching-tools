"""Code evaluation report."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sel_tools.utils.repo import GitlabProject

MD_EVALUATION_REPORT = """# Homework Evaluation Report

[Repo](%s)

Overall:

## Auto Evaluation

```json
%s
```

## Manual Evaluation
"""


@dataclass(frozen=True)
class EvaluationResult:
    """Evaluation result."""

    name: str
    score: int
    comment: str = ""


@dataclass
class EvaluationReport:
    """Evaluation report."""

    def __init__(self, gitlab_project: GitlabProject, results: list[EvaluationResult]) -> None:
        self.repo_path = gitlab_project.local_path
        self.url = gitlab_project.gitlab_project.web_url
        self.score = sum(result.score for result in set(results))
        self.results = results

    def to_json(self) -> str:
        class JsonEncoder(json.JSONEncoder):
            """Evaluation report json encoder."""

            def default(self, o: Any) -> str | Any:
                if isinstance(o, Path):
                    return str(o)
                return o.__dict__

        return json.dumps(self, cls=JsonEncoder, indent=4)

    def to_md(self) -> str:
        return MD_EVALUATION_REPORT % (self.url, self.to_json())


def write_evaluation_reports(reports: list[EvaluationReport], report_base_name: str) -> None:
    """Write evaluation reports to disk."""
    for report in reports:
        report_path = report.repo_path / report_base_name
        report_path.with_suffix(".md").write_text(report.to_md())
        report_path.with_suffix(".json").write_text(report.to_json())
