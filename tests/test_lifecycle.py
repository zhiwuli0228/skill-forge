from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.experience.service import ExperienceStore
from skill_forge.lifecycle.service import LifecycleService
from skill_forge.models.eval import SkillEvalAssertionResult, SkillEvalCaseResult, SkillEvalReport
from skill_forge.models.experience import ExperienceRule
from skill_forge.models.generated import GenerationProvenanceMetadata
from skill_forge.models.quality import ContentQualityMetrics
from skill_forge.library.manager import SkillLibraryManager


runner = CliRunner()


def _write_skill(
    output_dir: Path,
    name: str,
    *,
    provenance: GenerationProvenanceMetadata | None = None,
    report: SkillEvalReport | None = None,
) -> Path:
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Sample skill.\n---\n\n# {name}\n\nBody.\n",
        encoding="utf-8",
    )
    if provenance is not None:
        (skill_dir / "skill-forge.json").write_text(provenance.model_dump_json(indent=2), encoding="utf-8")
    if report is not None:
        (skill_dir / "eval-report.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return skill_dir


def _build_provenance(
    name: str,
    *,
    quality_score: int = 95,
    quality_status: str = "valid",
    applied_experience_rule_ids: list[str] | None = None,
    content_quality: ContentQualityMetrics | None = None,
) -> GenerationProvenanceMetadata:
    return GenerationProvenanceMetadata(
        generated_at="2026-05-31T00:00:00Z",
        skill_name=name,
        requirement_text="Sample requirement",
        target_platform="opencode",
        language="zh-CN",
        task_type="bug-investigation",
        quality_score=quality_score,
        quality_status=quality_status,
        applied_experience_rule_ids=applied_experience_rule_ids or [],
        content_quality=content_quality,
    )


def _build_eval_report(name: str, *, failed: int = 0) -> SkillEvalReport:
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


def test_lifecycle_service_reports_healthy_state_with_full_facts(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    experience_store = ExperienceStore(home / "experience")
    rule = ExperienceRule(
        id="experience-123",
        task_type="bug-investigation",
        language="zh-CN",
        target_platform="opencode",
        priority=80,
        rule_text="For bug-investigation, confirm logs before code changes.",
        workflow_guidance=["Confirm logs before code changes."],
        constraint_guidance=["Do not change code before logs are reviewed."],
        quality_gate_guidance=["Pass only when logs are linked to the root cause."],
        evidence=[],
        derived_at="2026-05-31T00:00:00Z",
    )
    experience_store.write_rule(rule)
    provenance = _build_provenance(
        "sample",
        applied_experience_rule_ids=[rule.id],
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.95,
            constraint_verifiability=0.9,
            quality_gate_clarity=0.92,
        ),
    )
    _write_skill(output_dir, "sample", provenance=provenance, report=_build_eval_report("sample"))

    summary = LifecycleService(SkillLibraryManager(output_dir), experience_store).show("sample")

    assert summary.state == "healthy"
    assert summary.reason == "Provenance, quality, and eval signals are all healthy."
    assert [item.source for item in summary.evidence] == ["provenance", "content-quality", "eval-report", "experience"]
    assert summary.missing_facts == []
    assert summary.resolved_experience_rules == [rule.rule_text]


def test_lifecycle_service_reports_needs_eval_when_eval_missing(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    provenance = _build_provenance(
        "sample",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.75,
            constraint_verifiability=0.8,
            quality_gate_clarity=0.7,
        ),
    )
    _write_skill(output_dir, "sample", provenance=provenance)

    summary = LifecycleService(SkillLibraryManager(output_dir), ExperienceStore(tmp_path / "experience")).show("sample")

    assert summary.state == "needs-eval"
    assert "No eval report" in summary.reason
    assert "eval-report" in summary.missing_facts


def test_lifecycle_service_reports_regressed_when_eval_fails(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    provenance = _build_provenance("sample")
    _write_skill(output_dir, "sample", provenance=provenance, report=_build_eval_report("sample", failed=1))

    summary = LifecycleService(SkillLibraryManager(output_dir), ExperienceStore(tmp_path / "experience")).show("sample")

    assert summary.state == "regressed"
    assert "failing case" in summary.reason
    assert summary.eval_failed == 1


def test_lifecycle_service_reports_unknown_when_provenance_missing(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    _write_skill(output_dir, "sample")

    summary = LifecycleService(SkillLibraryManager(output_dir), ExperienceStore(tmp_path / "experience")).show("sample")

    assert summary.state == "unknown"
    assert "No provenance metadata" in summary.reason
    assert "provenance" in summary.missing_facts


def test_lifecycle_cli_show_reports_read_only_summary(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    experience_store = ExperienceStore(home / "experience")
    rule = ExperienceRule(
        id="experience-456",
        task_type="bug-investigation",
        language="zh-CN",
        target_platform="opencode",
        priority=80,
        rule_text="For bug-investigation, confirm logs before code changes.",
        workflow_guidance=["Confirm logs before code changes."],
        constraint_guidance=["Do not change code before logs are reviewed."],
        quality_gate_guidance=["Pass only when logs are linked to the root cause."],
        evidence=[],
        derived_at="2026-05-31T00:00:00Z",
    )
    experience_store.write_rule(rule)
    provenance = _build_provenance(
        "sample",
        applied_experience_rule_ids=[rule.id],
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.95,
            constraint_verifiability=0.9,
            quality_gate_clarity=0.92,
        ),
    )
    _write_skill(output_dir, "sample", provenance=provenance, report=_build_eval_report("sample"))
    before = {
        str(path): path.read_text(encoding="utf-8")
        for path in home.rglob("*")
        if path.is_file()
    }

    result = runner.invoke(app, ["lifecycle", "show", "sample", "--home", str(home)])

    after = {
        str(path): path.read_text(encoding="utf-8")
        for path in home.rglob("*")
        if path.is_file()
    }

    assert result.exit_code == 0
    assert "Skill lifecycle: sample" in result.output
    assert "Lifecycle evidence" in result.output
    assert "healthy" in result.output
    assert rule.id in result.output
    assert before == after
