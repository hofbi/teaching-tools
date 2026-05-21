"""Code evaluation report."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sel_tools.utils.comment import ProjectCommentParser
from sel_tools.utils.repo import GitlabProject

MD_EVALUATION_REPORT = """# {report_header}

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

STUDENT_SECTION_TEMPLATE = """### {report_header}

Overall score: {score}/{max_score}

If available, below are a few notes about your code:
Please note that not all of them are errors.

{notes}
"""

COMMENTS_FOR_PROJECT_TEMPLATE = (
    ProjectCommentParser.PROJECT_COMMENT_IDENTIFIER_PREFIX
    + """ {project_id}

{student_section}
---
"""
)


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

    def __init__(self, gitlab_project: GitlabProject, homework_number: int, results: list[EvaluationResult]) -> None:
        self.repo_path = gitlab_project.local_path
        self.project_id = gitlab_project.gitlab_project.id
        self.url = gitlab_project.gitlab_project.web_url
        self.homework_number = homework_number
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

    def print_report_header(self) -> str:
        return f"Homework {self.homework_number} Evaluation Report"

    def to_md(self) -> str:
        return MD_EVALUATION_REPORT.format(
            report_header=self.print_report_header(),
            repo_url=self.url,
            evaluation_json=self.to_json(),
            student_section=self.print_student_section(),
        )

    def print_student_section(self) -> str:
        return STUDENT_SECTION_TEMPLATE.format(
            report_header=self.print_report_header(),
            score=self.score,
            max_score=self.max_score,
            notes="\n".join(f"- {result.comment}" for result in self.results if result.comment),
        )

    def print_project_comments(self) -> str:
        return COMMENTS_FOR_PROJECT_TEMPLATE.format(
            project_id=self.project_id,
            student_section=self.print_student_section(),
        )


def write_evaluation_reports(reports: list[EvaluationReport], report_base_name: str) -> None:
    """Write evaluation reports to disk."""
    for report in reports:
        report_path = report.repo_path / report_base_name
        report_path.with_suffix(".md").write_text(report.to_md())
        report_path.with_suffix(".json").write_text(report.to_json())


def write_evaluation_report_for_student_comments(reports: list[EvaluationReport], workspace: Path) -> None:
    """Write a single evaluation report with comments for the individual student projects."""
    workspace.joinpath("evaluation_report_comments_for_students.md").write_text(
        "\n".join(report.print_project_comments() for report in reports)
    )
