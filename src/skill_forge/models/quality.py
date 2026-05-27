from pydantic import BaseModel, Field

from skill_forge.models.validation import ValidationIssue, ValidationResult


ERROR_SCORE_PENALTY = 30
WARNING_SCORE_PENALTY = 5


class GenerationQualityReport(BaseModel):
    ok: bool
    score: int
    status: str
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)
    repair_suggestions: list["RepairSuggestion"] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class RepairSuggestion(BaseModel):
    level: str
    code: str
    suggestion: str


REPAIR_SUGGESTIONS_BY_CODE = {
    "missing_directory": "Create the Skill package directory or pass the correct package path.",
    "missing_skill_md": "Add a SKILL.md file at the root of the Skill package.",
    "missing_frontmatter": "Add YAML frontmatter at the top of SKILL.md bounded by --- lines.",
    "missing_name": "Add a non-empty name field to SKILL.md frontmatter.",
    "missing_description": "Add a description field explaining when to use and when not to use the Skill.",
    "empty_description": "Replace the empty description with specific trigger and exclusion guidance.",
    "unsafe_attachment_path": "Use only safe relative attachment paths inside the Skill package.",
    "missing_section": "Add the missing recommended section with task-specific content.",
    "name_not_slug": "Change the frontmatter name to lowercase kebab-case, such as code-review.",
    "package_name_mismatch": "Rename the package directory or frontmatter name so they match.",
    "description_too_short": "Expand the description with a clear task boundary and trigger condition.",
    "description_missing_trigger": "State when to use this Skill in the description.",
    "description_missing_exclusion": "State when not to use this Skill in the description.",
    "empty_section": "Add meaningful content under the empty section heading.",
    "workflow_too_short": "Add at least two actionable workflow steps.",
    "quality_gates_too_few": "Add at least two checkable quality gates.",
}


def build_generation_quality_report(result: ValidationResult) -> GenerationQualityReport:
    score = 100 - (len(result.errors) * ERROR_SCORE_PENALTY) - (len(result.warnings) * WARNING_SCORE_PENALTY)
    score = max(0, min(100, score))

    if result.errors:
        status = "invalid"
        next_actions = [
            "Fix validation errors",
            "Run `skill-forge validate <skill-path>`",
        ]
    elif result.warnings:
        status = "valid_with_warnings"
        next_actions = [
            "Review validation warnings",
            "Run `skill-forge validate <skill-path>`",
            "Install when acceptable",
        ]
    else:
        status = "valid"
        next_actions = [
            "Validate when needed",
            "Install",
        ]

    return GenerationQualityReport(
        ok=result.ok,
        score=score,
        status=status,
        errors=result.errors,
        warnings=result.warnings,
        repair_suggestions=build_repair_suggestions(result),
        next_actions=next_actions,
    )


def build_repair_suggestions(result: ValidationResult) -> list[RepairSuggestion]:
    suggestions: list[RepairSuggestion] = []
    seen: set[tuple[str, str]] = set()
    for issue in [*result.errors, *result.warnings]:
        key = (issue.level, issue.code)
        if key in seen:
            continue
        seen.add(key)
        suggestions.append(
            RepairSuggestion(
                level=issue.level,
                code=issue.code,
                suggestion=REPAIR_SUGGESTIONS_BY_CODE.get(
                    issue.code,
                    "Review the validation issue and update the Skill package accordingly.",
                ),
            )
        )
    return suggestions
