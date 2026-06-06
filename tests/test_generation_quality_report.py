from skill_forge.models.quality import assess_content_quality, build_generation_quality_report, build_repair_suggestions
from skill_forge.models.requirement import SkillRequirement
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


def test_quality_report_includes_content_quality_without_changing_status() -> None:
    requirement = SkillRequirement(
        name="release-readiness",
        description="Use this skill for release readiness checks. Do not use it for unrelated work.",
        workflow=["Check `release.yaml` first, then verify rollout owner"],
        constraints=["Rollback evidence must be documented before release"],
        quality_gates=["Pass when `release.yaml` and rollback evidence are verified"],
    )

    report = build_generation_quality_report(ValidationResult(ok=True), requirement=requirement)

    assert report.status == "valid"
    assert report.score == 100
    assert report.content_quality is not None
    assert report.content_quality.workflow_specificity > 0
    assert report.content_quality.constraint_verifiability > 0
    assert report.content_quality.quality_gate_clarity > 0


def test_content_quality_metrics_are_deterministic() -> None:
    requirement = SkillRequirement(
        name="release-readiness",
        description="Use this skill for release readiness checks.",
        workflow=["Check `release.yaml` first, then verify rollout owner"],
        constraints=["Do not release without rollback evidence"],
        quality_gates=["Pass when release evidence is verified"],
    )

    first = assess_content_quality(requirement)
    second = assess_content_quality(requirement)

    assert first == second


def test_workflow_specificity_rewards_concrete_steps() -> None:
    specific = SkillRequirement(
        name="sql-diagnosis",
        description="Use this skill for SQL diagnosis.",
        workflow=["Collect slow-query.log first, then inspect `EXPLAIN` output for missing indexes"],
    )
    generic = SkillRequirement(
        name="generic-analysis",
        description="Use this skill for generic analysis.",
        workflow=["Analyze the problem"],
    )

    assert assess_content_quality(specific).workflow_specificity > assess_content_quality(generic).workflow_specificity


def test_constraint_verifiability_rewards_checkable_conditions() -> None:
    checkable = SkillRequirement(
        name="release-readiness",
        description="Use this skill for release readiness checks.",
        constraints=["Do not release without rollback evidence documented in `release.yaml` within 24 hours"],
    )
    vague = SkillRequirement(
        name="generic-analysis",
        description="Use this skill for generic analysis.",
        constraints=["Be careful"],
    )

    assert assess_content_quality(checkable).constraint_verifiability > assess_content_quality(vague).constraint_verifiability


def test_quality_gate_clarity_rewards_pass_criteria() -> None:
    clear = SkillRequirement(
        name="bug-investigation",
        description="Use this skill for bug investigation.",
        quality_gates=["Pass when `pytest` succeeds and the report includes root cause evidence"],
    )
    vague = SkillRequirement(
        name="generic-review",
        description="Use this skill for generic review.",
        quality_gates=["Review the output"],
    )

    assert assess_content_quality(clear).quality_gate_clarity > assess_content_quality(vague).quality_gate_clarity


def test_empty_content_quality_sections_score_zero() -> None:
    requirement = SkillRequirement(
        name="empty-content",
        description="Use this skill for empty content checks.",
        workflow=[],
        constraints=[],
        quality_gates=[],
    )

    metrics = assess_content_quality(requirement)

    assert metrics.workflow_specificity == 0.0
    assert metrics.constraint_verifiability == 0.0
    assert metrics.quality_gate_clarity == 0.0


def test_content_quality_scores_are_normalized() -> None:
    requirement = SkillRequirement(
        name="strong-content",
        description="Use this skill for strong content checks.",
        workflow=["Collect api.log first, then verify `/health` traces before summarizing the report"],
        constraints=["Do not proceed without 2 reproducible test failures and documented trace evidence"],
        quality_gates=["Pass when 2 tests pass, evidence is verified, and output report names the root cause"],
    )

    metrics = assess_content_quality(requirement)

    assert 0.0 <= metrics.workflow_specificity <= 1.0
    assert 0.0 <= metrics.constraint_verifiability <= 1.0
    assert 0.0 <= metrics.quality_gate_clarity <= 1.0
