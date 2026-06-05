from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.experience.service import ExperienceStore
from skill_forge.library.manager import SkillLibraryManager
from skill_forge.lifecycle.recommendation import LifecycleRecommendationService
from skill_forge.lifecycle.recommendation_rules import (
    LifecycleRecommendationInput,
    recommend_lifecycle_action,
)
from skill_forge.lifecycle.service import LifecycleService
from skill_forge.models.eval import SkillEvalAssertionResult, SkillEvalCaseResult, SkillEvalReport
from skill_forge.models.generated import GenerationProvenanceMetadata
from skill_forge.models.quality import ContentQualityMetrics


runner = CliRunner()


def _write_skill(
    output_dir: Path,
    name: str,
    *,
    quality_score: int = 95,
    quality_status: str = "valid",
    content_quality: ContentQualityMetrics | None = None,
    report: SkillEvalReport | None = None,
    apply_rule_id: str | None = None,
) -> Path:
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Sample skill.\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    provenance = GenerationProvenanceMetadata(
        generated_at="2026-05-31T00:00:00Z",
        skill_name=name,
        requirement_text="Sample requirement",
        target_platform="opencode",
        language="zh-CN",
        task_type="bug-investigation",
        quality_score=quality_score,
        quality_status=quality_status,
        content_quality=content_quality,
        applied_experience_rule_ids=[apply_rule_id] if apply_rule_id is not None else [],
    )
    (skill_dir / "skill-forge.json").write_text(provenance.model_dump_json(indent=2), encoding="utf-8")
    if report is not None:
        (skill_dir / "eval-report.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return skill_dir


def _make_report(name: str, *, failed: int = 0) -> SkillEvalReport:
    return SkillEvalReport(
        skill_name=name,
        total=1,
        passed=0 if failed else 1,
        failed=failed,
        results=[
            SkillEvalCaseResult(
                case_id="case-1",
                passed=failed == 0,
                assertions=[
                    SkillEvalAssertionResult(
                        passed=failed == 0,
                        assertion="required_sections",
                        message="Missing required section: Findings" if failed else "Section present",
                    )
                ],
            )
        ],
    )


def _service(home: Path) -> LifecycleRecommendationService:
    return LifecycleRecommendationService(
        LifecycleService(SkillLibraryManager(home / "output"), ExperienceStore(home / "experience"))
    )


def test_recommendation_maps_healthy_skill_to_ready_to_promote(tmp_path: Path) -> None:
    home = tmp_path / "home"
    _write_skill(
        home / "output",
        "healthy-skill",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.95,
            constraint_verifiability=0.9,
            quality_gate_clarity=0.92,
        ),
        report=_make_report("healthy-skill"),
    )

    recommendation = _service(home).recommend("healthy-skill")

    assert recommendation.action == "ready-to-promote"
    assert recommendation.state == "healthy"
    assert "ready" in recommendation.reason.casefold()


def test_recommendation_maps_missing_eval_to_run_eval(tmp_path: Path) -> None:
    home = tmp_path / "home"
    _write_skill(
        home / "output",
        "needs-eval",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.75,
            constraint_verifiability=0.8,
            quality_gate_clarity=0.7,
        ),
    )

    recommendation = _service(home).recommend("needs-eval")

    assert recommendation.action == "run-eval"
    assert recommendation.state == "needs-eval"
    assert "eval-report" in recommendation.missing_facts


def test_recommendation_maps_regressed_skill_to_repair_regression(tmp_path: Path) -> None:
    home = tmp_path / "home"
    _write_skill(
        home / "output",
        "regressed-skill",
        report=_make_report("regressed-skill", failed=1),
    )

    recommendation = _service(home).recommend("regressed-skill")

    assert recommendation.action == "repair-regression"
    assert recommendation.state == "regressed"
    assert "failure" in recommendation.reason.casefold()


def test_recommendation_maps_missing_provenance_to_investigate_missing_facts(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    skill_dir = output_dir / "missing-provenance"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: missing-provenance\n---\n", encoding="utf-8")

    recommendation = _service(home).recommend("missing-provenance")

    assert recommendation.action == "investigate-missing-facts"
    assert recommendation.state == "unknown"


def test_compare_prefers_healthier_skill_and_uses_state_order(tmp_path: Path) -> None:
    home = tmp_path / "home"
    _write_skill(
        home / "output",
        "healthy-skill",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.95,
            constraint_verifiability=0.9,
            quality_gate_clarity=0.92,
        ),
        report=_make_report("healthy-skill"),
    )
    _write_skill(
        home / "output",
        "regressed-skill",
        report=_make_report("regressed-skill", failed=1),
    )

    comparison = _service(home).compare("healthy-skill", "regressed-skill")

    assert comparison.preferred_skill_name == "healthy-skill"
    assert "ranked higher" in comparison.reason.casefold()
    assert "deterministic comparison key" in comparison.tie_breaker.casefold()


def test_compare_uses_name_order_when_lifecycle_signals_are_equal(tmp_path: Path) -> None:
    home = tmp_path / "home"
    _write_skill(
        home / "output",
        "alpha-skill",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.95,
            constraint_verifiability=0.9,
            quality_gate_clarity=0.92,
        ),
        report=_make_report("alpha-skill"),
    )
    _write_skill(
        home / "output",
        "beta-skill",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.95,
            constraint_verifiability=0.9,
            quality_gate_clarity=0.92,
        ),
        report=_make_report("beta-skill"),
    )

    comparison = _service(home).compare("alpha-skill", "beta-skill")

    assert comparison.preferred_skill_name == "alpha-skill"
    assert "name order" in comparison.tie_breaker.casefold()


def test_recommend_and_compare_cli_are_read_only(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    _write_skill(
        output_dir,
        "alpha-skill",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.95,
            constraint_verifiability=0.9,
            quality_gate_clarity=0.92,
        ),
        report=_make_report("alpha-skill"),
    )
    _write_skill(
        output_dir,
        "beta-skill",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.75,
            constraint_verifiability=0.8,
            quality_gate_clarity=0.7,
        ),
        report=_make_report("beta-skill"),
    )
    before = {
        str(path): path.read_text(encoding="utf-8")
        for path in home.rglob("*")
        if path.is_file()
    }

    recommend_result = runner.invoke(app, ["lifecycle", "recommend", "alpha-skill", "--home", str(home)])
    compare_result = runner.invoke(app, ["lifecycle", "compare", "alpha-skill", "beta-skill", "--home", str(home)])

    after = {
        str(path): path.read_text(encoding="utf-8")
        for path in home.rglob("*")
        if path.is_file()
    }

    assert recommend_result.exit_code == 0
    assert "Lifecycle recommendation" in recommend_result.output
    assert "ready-to-promote" in recommend_result.output
    assert compare_result.exit_code == 0
    assert "Lifecycle comparison" in compare_result.output
    assert "Preferred" in compare_result.output
    assert before == after


def test_recommend_cli_fails_for_missing_generated_skill(tmp_path: Path) -> None:
    result = runner.invoke(app, ["lifecycle", "recommend", "missing", "--home", str(tmp_path / "home")])

    assert result.exit_code == 1
    assert "Generated Skill package not found" in result.output


def test_compare_cli_fails_for_missing_generated_skill(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["lifecycle", "compare", "left", "right", "--home", str(tmp_path / "home")],
    )

    assert result.exit_code == 1
    assert "Generated Skill package not found" in result.output


# --- parity tests: service delegates to the pure function --------------------


def test_service_outdated_provenance_matches_pure_function(tmp_path: Path) -> None:
    """A Skill with missing provenance (state=unknown) matches the pure path."""

    home = tmp_path / "home"
    output_dir = home / "output"
    skill_dir = output_dir / "outdated-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: outdated-skill\ndescription: Outdated.\n---\n",
        encoding="utf-8",
    )

    service = _service(home)
    service_recommendation = service.recommend("outdated-skill")

    summary = service.lifecycle_service.show("outdated-skill")
    pure_input = LifecycleRecommendationInput(
        skill_name=summary.skill_name,
        state=summary.state,
        reason=summary.reason,
        missing_facts=list(summary.missing_facts),
        quality_score=summary.quality_score,
        quality_status=summary.quality_status,
        eval_total=summary.eval_total,
        eval_passed=summary.eval_passed,
        eval_failed=summary.eval_failed,
        applied_experience_rule_ids=list(summary.applied_experience_rule_ids),
    )
    pure_recommendation = recommend_lifecycle_action(pure_input)

    assert service_recommendation.state == pure_recommendation.state
    assert service_recommendation.action == pure_recommendation.action
    assert service_recommendation.reason == pure_recommendation.reason
    assert service_recommendation.missing_facts == pure_recommendation.missing_facts
    assert service_recommendation.signals == pure_recommendation.signals


def test_service_current_metadata_matches_pure_function(tmp_path: Path) -> None:
    """A Skill with current valid metadata (state=healthy) matches the pure path."""

    home = tmp_path / "home"
    _write_skill(
        home / "output",
        "current-skill",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.95,
            constraint_verifiability=0.9,
            quality_gate_clarity=0.92,
        ),
        report=_make_report("current-skill"),
    )

    service = _service(home)
    service_recommendation = service.recommend("current-skill")

    summary = service.lifecycle_service.show("current-skill")
    pure_input = LifecycleRecommendationInput(
        skill_name=summary.skill_name,
        state=summary.state,
        reason=summary.reason,
        missing_facts=list(summary.missing_facts),
        quality_score=summary.quality_score,
        quality_status=summary.quality_status,
        eval_total=summary.eval_total,
        eval_passed=summary.eval_passed,
        eval_failed=summary.eval_failed,
        applied_experience_rule_ids=list(summary.applied_experience_rule_ids),
    )
    pure_recommendation = recommend_lifecycle_action(pure_input)

    assert service_recommendation.state == "healthy"
    assert pure_recommendation.state == "healthy"
    assert service_recommendation.action == pure_recommendation.action
    assert service_recommendation.action == "ready-to-promote"
    assert service_recommendation.reason == pure_recommendation.reason
    assert service_recommendation.missing_facts == pure_recommendation.missing_facts
    assert service_recommendation.signals == pure_recommendation.signals


def test_service_unknown_new_skill_matches_pure_function(tmp_path: Path) -> None:
    """A new Skill with no provenance at all (state=unknown) matches the pure path."""

    home = tmp_path / "home"
    output_dir = home / "output"
    skill_dir = output_dir / "new-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: new-skill\ndescription: Brand new.\n---\n",
        encoding="utf-8",
    )

    service = _service(home)
    service_recommendation = service.recommend("new-skill")

    summary = service.lifecycle_service.show("new-skill")
    pure_input = LifecycleRecommendationInput(
        skill_name=summary.skill_name,
        state=summary.state,
        reason=summary.reason,
        missing_facts=list(summary.missing_facts),
        quality_score=summary.quality_score,
        quality_status=summary.quality_status,
        eval_total=summary.eval_total,
        eval_passed=summary.eval_passed,
        eval_failed=summary.eval_failed,
        applied_experience_rule_ids=list(summary.applied_experience_rule_ids),
    )
    pure_recommendation = recommend_lifecycle_action(pure_input)

    assert service_recommendation.state == "unknown"
    assert pure_recommendation.state == "unknown"
    assert service_recommendation.action == pure_recommendation.action
    assert service_recommendation.action == "investigate-missing-facts"
    assert service_recommendation.reason == pure_recommendation.reason
    assert service_recommendation.missing_facts == pure_recommendation.missing_facts
    assert service_recommendation.signals == pure_recommendation.signals


def test_service_recommend_uses_pure_function_for_known_state(tmp_path: Path) -> None:
    """For a Skill whose state is known, the service delegates to the pure function.

    This test directly checks that the recommendation returned by
    the service is byte-for-byte equal to the recommendation
    produced by the pure function for an input constructed from
    the same summary. The test exercises a Skill with the
    ``needs-eval`` state to cover a state that is neither
    ``unknown`` nor ``healthy``.
    """

    home = tmp_path / "home"
    _write_skill(
        home / "output",
        "needs-eval-skill",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.75,
            constraint_verifiability=0.8,
            quality_gate_clarity=0.7,
        ),
    )

    service = _service(home)
    service_recommendation = service.recommend("needs-eval-skill")

    summary = service.lifecycle_service.show("needs-eval-skill")
    pure_input = LifecycleRecommendationInput(
        skill_name=summary.skill_name,
        state=summary.state,
        reason=summary.reason,
        missing_facts=list(summary.missing_facts),
        quality_score=summary.quality_score,
        quality_status=summary.quality_status,
        eval_total=summary.eval_total,
        eval_passed=summary.eval_passed,
        eval_failed=summary.eval_failed,
        applied_experience_rule_ids=list(summary.applied_experience_rule_ids),
    )
    pure_recommendation = recommend_lifecycle_action(pure_input)

    assert service_recommendation.state == "needs-eval"
    assert service_recommendation.action == "run-eval"
    assert service_recommendation.model_dump() == pure_recommendation.model_dump()


def test_service_recommend_no_longer_uses_removed_private_helpers(tmp_path: Path) -> None:
    """The service module no longer defines the pre-Phase-5 private rule helpers.

    The two private helpers ``_recommend_from_summary`` and
    ``_summary_signals`` were removed by the Phase 5 adapter
    slice. The service's ``recommend`` method now delegates to
    the pure function via the private ``_recommend_via_rules``
    helper. This test guards against an accidental re-introduction
    of the duplicated rule.
    """

    from skill_forge.lifecycle import recommendation

    assert not hasattr(recommendation, "_recommend_from_summary"), (
        "The pre-Phase-5 _recommend_from_summary helper must remain removed."
    )
    assert not hasattr(recommendation, "_summary_signals"), (
        "The pre-Phase-5 _summary_signals helper must remain removed."
    )
    assert hasattr(recommendation, "_recommend_via_rules"), (
        "The new _recommend_via_rules adapter helper must be present."
    )
    assert hasattr(recommendation, "_summary_to_input"), (
        "The new _summary_to_input adapter helper must be present."
    )


def test_cli_help_is_unchanged() -> None:
    """The CLI help text is unchanged after the refactor."""

    help_result = runner.invoke(app, ["lifecycle", "--help"])
    assert help_result.exit_code == 0
    assert "recommend" in help_result.output.casefold()
    assert "compare" in help_result.output.casefold()
