from pydantic import BaseModel, Field

from skill_forge.models.requirement import SkillRequirement
from skill_forge.models.validation import ValidationIssue, ValidationResult


ERROR_SCORE_PENALTY = 30
WARNING_SCORE_PENALTY = 5


class GenerationQualityReport(BaseModel):
    ok: bool
    score: int
    status: str
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)
    content_quality: "ContentQualityMetrics | None" = None
    repair_suggestions: list["RepairSuggestion"] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class ContentQualityMetrics(BaseModel):
    workflow_specificity: float
    constraint_verifiability: float
    quality_gate_clarity: float


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


def build_generation_quality_report(
    result: ValidationResult,
    requirement: SkillRequirement | None = None,
) -> GenerationQualityReport:
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
        content_quality=assess_content_quality(requirement) if requirement is not None else None,
        repair_suggestions=build_repair_suggestions(result),
        next_actions=next_actions,
    )


def assess_content_quality(requirement: SkillRequirement) -> ContentQualityMetrics:
    return ContentQualityMetrics(
        workflow_specificity=_score_items(requirement.workflow, _workflow_item_score),
        constraint_verifiability=_score_items(requirement.constraints, _constraint_item_score),
        quality_gate_clarity=_score_items(requirement.quality_gates, _quality_gate_item_score),
    )


def _score_items(items: list[str], item_score) -> float:
    if not items:
        return 0.0
    score = sum(item_score(item) for item in items) / len(items)
    return round(max(0.0, min(1.0, score)), 2)


def _workflow_item_score(item: str) -> float:
    text = item.strip()
    if not text:
        return 0.0
    score = 0.0
    if _contains_action_signal(text):
        score += 0.3
    if _contains_concrete_signal(text):
        score += 0.3
    if _contains_sequence_signal(text):
        score += 0.2
    if not _is_generic_text(text):
        score += 0.2
    return score


def _constraint_item_score(item: str) -> float:
    text = item.strip()
    if not text:
        return 0.0
    score = 0.0
    if _contains_any(text, ["must", "shall", "require", "required", "before", "\u5fc5\u987b", "\u9700\u8981"]):
        score += 0.15
    if _contains_any(text, ["do not", "cannot", "never", "without", "must not", "\u4e0d\u5f97", "\u4e0d\u80fd", "\u4e0d\u8981"]):
        score += 0.25
    if _contains_evidence_signal(text):
        score += 0.3
    if _contains_quantified_signal(text):
        score += 0.2
    if _contains_concrete_signal(text):
        score += 0.1
    return score


def _quality_gate_item_score(item: str) -> float:
    text = item.strip()
    if not text:
        return 0.0
    score = 0.0
    if _contains_any(text, ["pass", "fail", "accept", "reject", "\u901a\u8fc7", "\u5931\u8d25", "\u63a5\u53d7", "\u62d2\u7edd"]):
        score += 0.35
    if _contains_any(text, ["verify", "check", "test", "assert", "evidence", "\u9a8c\u8bc1", "\u68c0\u67e5", "\u6d4b\u8bd5", "\u8bc1\u636e"]):
        score += 0.25
    if _contains_concrete_signal(text):
        score += 0.2
    if _contains_quantified_signal(text):
        score += 0.1
    if _contains_any(text, ["workflow", "output", "artifact", "report", "root cause", "\u6d41\u7a0b", "\u8f93\u51fa", "\u4ea7\u7269", "\u62a5\u544a", "\u6839\u56e0"]):
        score += 0.1
    return score


def _contains_any(text: str, needles: list[str]) -> bool:
    lower = text.lower()
    return any(needle in lower for needle in needles)


def _contains_action_signal(text: str) -> bool:
    return _contains_any(
        text,
        [
            "analyze",
            "check",
            "collect",
            "compare",
            "document",
            "extract",
            "inspect",
            "locate",
            "read",
            "review",
            "run",
            "summarize",
            "trace",
            "verify",
            "\u5206\u6790",
            "\u68c0\u67e5",
            "\u6536\u96c6",
            "\u5bf9\u6bd4",
            "\u8bb0\u5f55",
            "\u63d0\u53d6",
            "\u5b9a\u4f4d",
            "\u9605\u8bfb",
            "\u8fd0\u884c",
            "\u9a8c\u8bc1",
        ],
    )


def _contains_concrete_signal(text: str) -> bool:
    return (
        any(char in text for char in ("`", "/", ".", ":", "-", "_"))
        or any(char.isdigit() for char in text)
        or _contains_any(
            text,
            [
                "api",
                "artifact",
                "code",
                "config",
                "database",
                "diff",
                "evidence",
                "file",
                "log",
                "metric",
                "output",
                "query",
                "report",
                "sql",
                "stack trace",
                "test",
                "trace",
                "yaml",
                "\u4ee3\u7801",
                "\u914d\u7f6e",
                "\u8bc1\u636e",
                "\u6587\u4ef6",
                "\u65e5\u5fd7",
                "\u6307\u6807",
                "\u8f93\u51fa",
                "\u62a5\u544a",
                "\u6d4b\u8bd5",
            ],
        )
    )


def _contains_evidence_signal(text: str) -> bool:
    return _contains_any(
        text,
        [
            "evidence",
            "observable",
            "verified",
            "documented",
            "reproduce",
            "log",
            "test",
            "assert",
            "trace",
            "\u8bc1\u636e",
            "\u53ef\u89c2\u6d4b",
            "\u9a8c\u8bc1",
            "\u8bb0\u5f55",
            "\u590d\u73b0",
            "\u65e5\u5fd7",
            "\u6d4b\u8bd5",
        ],
    )


def _contains_quantified_signal(text: str) -> bool:
    return any(char.isdigit() for char in text) or _contains_any(
        text,
        [
            "at least",
            "at most",
            "less than",
            "more than",
            "within",
            "minimum",
            "maximum",
            "%",
            "\u81f3\u5c11",
            "\u6700\u591a",
            "\u5c0f\u4e8e",
            "\u5927\u4e8e",
            "\u4ee5\u5185",
        ],
    )


def _contains_sequence_signal(text: str) -> bool:
    return _contains_any(text, ["then", "after", "before", "next", "\u7136\u540e", "\u4e4b\u540e", "\u4e4b\u524d", "\u5148"])


def _is_generic_text(text: str) -> bool:
    normalized = text.strip().lower()
    return normalized in {
        "analyze the problem",
        "handle the task",
        "review the output",
        "ensure quality",
        "be careful",
        "do good analysis",
        "\u5206\u6790\u95ee\u9898",
        "\u5904\u7406\u4efb\u52a1",
        "\u786e\u4fdd\u8d28\u91cf",
    }


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
