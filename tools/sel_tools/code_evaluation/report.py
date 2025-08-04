"""Code evaluation report."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sel_tools.utils.repo import GitlabProject

MD_EVALUATION_REPORT = """# Homework Evaluation Report

[Repo]({repo_url})

Overall:

## Auto Evaluation

```json
{evaluation_json}
```

## Manual Evaluation

Use this section for notes when evaluating the code manually.

## Student Section

The content of this section and below of this sentence can be shared with the students:

{student_section}

"""

STUDENT_SECTION_TEMPLATE = """Overall score: {score}/{max_score}

If available, below are a few notes about your code:
Please note that not all of them are errors.

{notes}
"""


@dataclass(frozen=True)
class EvaluationResult:
    """Evaluation result."""

    name: str
    score: int
    max_score: int
    comment: str = ""


@dataclass
class EvaluationReport:
    """Evaluation report."""

    def __init__(self, gitlab_project: GitlabProject, results: list[EvaluationResult]) -> None:
        self.repo_path = gitlab_project.local_path
        self.url = gitlab_project.gitlab_project.web_url
        self.score = sum(result.score for result in set(results))
        self.max_score = sum(result.max_score for result in set(results))
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
        return MD_EVALUATION_REPORT.format(
            repo_url=self.url, evaluation_json=self.to_json(), student_section=self.print_student_section()
        )

    def print_student_section(self) -> str:
        return STUDENT_SECTION_TEMPLATE.format(
            score=self.score,
            max_score=self.max_score,
            notes="\n".join(f"- {result.comment}" for result in self.results if result.comment),
        )


def write_evaluation_reports(reports: list[EvaluationReport], report_base_name: str) -> None:
    """Write evaluation reports to disk."""
    for report in reports:
        report_path = report.repo_path / report_base_name
        report_path.with_suffix(".md").write_text(report.to_md())
        report_path.with_name(f"{report_base_name}_students.md").write_text(report.print_student_section())
        report_path.with_suffix(".json").write_text(report.to_json())
