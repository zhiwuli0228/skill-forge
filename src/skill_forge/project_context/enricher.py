from pathlib import Path

from skill_forge.models.project_context import ProjectContextSummary
from skill_forge.models.requirement import SkillRequirement
from skill_forge.project_context.reader import ProjectContextReader
from skill_forge.project_context.summarizer import ProjectContextSummarizer


class ProjectContextEnricher:
    def __init__(
        self,
        reader: ProjectContextReader | None = None,
        summarizer: ProjectContextSummarizer | None = None,
    ) -> None:
        self.reader = reader or ProjectContextReader()
        self.summarizer = summarizer or ProjectContextSummarizer()

    def enrich(self, requirement: SkillRequirement, project_path: Path) -> ProjectContextSummary:
        summary = self.summarizer.summarize(self.reader.read(project_path))
        requirement.constraints = merge_constraints(requirement.constraints, summary.derived_constraints)
        return summary


def merge_constraints(existing: list[str], project_constraints: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for constraint in [*existing, *project_constraints]:
        key = constraint.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(constraint)
    return merged
