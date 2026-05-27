from skill_forge.models.quality import build_generation_quality_report, build_repair_suggestions
from skill_forge.models.validation import ValidationIssue, ValidationResult


def test_quality_report_scores_clean_result() -> None:
    report = build_generation_quality_report(ValidationResult(ok=True))

    assert report.ok is True
    assert report.status == "valid"
    assert report.score == 100
    assert report.next_actions == ["Validate when needed", "Install"]


def test_quality_report_scores_warning_result() -> None:
    result = ValidationResult(
        ok=True,
        warnings=[ValidationIssue(level="warning", code="missing_section", message="Missing section")],
    )

    report = build_generation_quality_report(result)

    assert report.ok is True
    assert report.status == "valid_with_warnings"
    assert report.score == 95
    assert report.warnings == result.warnings
    assert report.repair_suggestions[0].code == "missing_section"
    assert "Add the missing recommended section" in report.repair_suggestions[0].suggestion


def test_quality_report_scores_error_result() -> None:
    result = ValidationResult(
        ok=False,
        errors=[ValidationIssue(level="error", code="missing_skill_md", message="Missing SKILL.md")],
        warnings=[ValidationIssue(level="warning", code="missing_section", message="Missing section")],
    )

    report = build_generation_quality_report(result)

    assert report.ok is False
    assert report.status == "invalid"
    assert report.score == 65
    assert report.errors == result.errors
    assert report.warnings == result.warnings
    assert [suggestion.code for suggestion in report.repair_suggestions] == ["missing_skill_md", "missing_section"]


def test_quality_report_omits_suggestions_for_clean_result() -> None:
    report = build_generation_quality_report(ValidationResult(ok=True))

    assert report.repair_suggestions == []


def test_repair_suggestions_deduplicate_issue_codes() -> None:
    result = ValidationResult(
        ok=True,
        warnings=[
            ValidationIssue(level="warning", code="missing_section", message="Missing Purpose"),
            ValidationIssue(level="warning", code="missing_section", message="Missing Workflow"),
        ],
    )

    suggestions = build_repair_suggestions(result)

    assert len(suggestions) == 1
    assert suggestions[0].code == "missing_section"


def test_repair_suggestions_include_fallback_for_unknown_issue_code() -> None:
    result = ValidationResult(
        ok=True,
        warnings=[ValidationIssue(level="warning", code="future_issue", message="Future issue")],
    )

    suggestions = build_repair_suggestions(result)

    assert suggestions[0].code == "future_issue"
    assert "Review the validation issue" in suggestions[0].suggestion
