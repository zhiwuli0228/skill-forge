from pathlib import Path

from skill_forge.experience.service import ExperienceService, ExperienceStore
from skill_forge.models.eval import SkillEvalAssertionResult, SkillEvalCaseResult, SkillEvalReport
from skill_forge.models.experience import ExperienceRule
from skill_forge.models.generated import GenerationProvenanceMetadata
from skill_forge.models.quality import ContentQualityMetrics
from skill_forge.requirement.analyzer import RequirementAnalyzer


def _write_package(
    output_dir: Path,
    name: str,
    *,
    generated_at: str,
    case_id: str = "case-1",
    assertion_message: str = "Missing required section: Findings",
    workflow_specificity: float = 0.2,
    constraint_verifiability: float = 0.8,
    quality_gate_clarity: float = 0.9,
) -> Path:
    package_dir = output_dir / name
    package_dir.mkdir(parents=True)
    (package_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Sample skill.\n---\n\n# {name}\n\n## Findings\n\nDetails.\n",
        encoding="utf-8",
    )
    provenance = GenerationProvenanceMetadata(
        generated_at=generated_at,
        skill_name=name,
        requirement_text="Java bug investigation skill",
        target_platform="opencode",
        language="zh-CN",
        task_type="bug-investigation",
        quality_score=70,
        quality_status="valid_with_warnings",
        content_quality=ContentQualityMetrics(
            workflow_specificity=workflow_specificity,
            constraint_verifiability=constraint_verifiability,
            quality_gate_clarity=quality_gate_clarity,
        ),
    )
    (package_dir / "skill-forge.json").write_text(provenance.model_dump_json(indent=2), encoding="utf-8")
    report = SkillEvalReport(
        skill_name=name,
        total=1,
        passed=0,
        failed=1,
        results=[
            SkillEvalCaseResult(
                case_id=case_id,
                passed=False,
                assertions=[
                    SkillEvalAssertionResult(
                        passed=False,
                        assertion="required_sections",
                        message=assertion_message,
                    )
                ],
            )
        ],
    )
    (package_dir / "eval-report.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return package_dir


def test_experience_store_round_trips_rules_and_handles_missing_directory(tmp_path: Path) -> None:
    store = ExperienceStore(tmp_path / "experience")
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

    assert store.list_rules() == []
    store.write_rule(rule)
    assert store.read_rule(rule.id) == rule
    assert store.list_rules() == [rule]

    store.clear()
    assert store.list_rules() == []


def test_experience_service_derives_stable_rules_from_repeated_evidence(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    store = ExperienceStore(tmp_path / "experience")
    service = ExperienceService(store)

    _write_package(output_dir, "pkg-a", generated_at="2026-05-31T00:00:00Z")
    _write_package(output_dir, "pkg-b", generated_at="2026-05-31T01:00:00Z")
    _write_package(output_dir, "pkg-c", generated_at="2026-05-31T02:00:00Z")

    first = service.derive_from_output_dir(output_dir, rebuild=True)
    first_ids = [rule.id for rule in first.rules]
    first_texts = [rule.rule_text for rule in first.rules]

    assert first.scanned_packages == 3
    assert len(first.rules) == 2
    assert first_ids == [rule.id for rule in store.list_rules()]
    assert first_texts == [rule.rule_text for rule in store.list_rules()]

    second = service.derive_from_output_dir(output_dir, rebuild=True)
    assert [rule.id for rule in second.rules] == first_ids
    assert [rule.rule_text for rule in second.rules] == first_texts

    requirement = RequirementAnalyzer().analyze("Java bug investigation skill")
    updated, context = service.apply_to_requirement(requirement)

    assert context.used is True
    assert context.rule_ids == first_ids
    assert any("confirm" in item.casefold() or "findings" in item.casefold() for item in updated.workflow)
    assert any("log" in item.casefold() or "observable" in item.casefold() for item in updated.constraints)
    assert any("pass only" in item.casefold() for item in updated.quality_gates)


def test_experience_service_skips_missing_and_malformed_packages(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    broken = output_dir / "broken"
    broken.mkdir()
    (broken / "SKILL.md").write_text("content", encoding="utf-8")
    (broken / "skill-forge.json").write_text("{not-json", encoding="utf-8")

    service = ExperienceService(ExperienceStore(tmp_path / "experience"))
    result = service.derive_from_output_dir(output_dir)

    assert result.scanned_packages == 1
    assert result.rules == []
    assert result.skipped_packages == ["broken"]


def test_experience_service_selects_matching_rules_deterministically() -> None:
    service = ExperienceService(ExperienceStore(Path("unused")))
    requirement = RequirementAnalyzer().analyze("Java bug investigation skill")
    rules = [
        ExperienceRule(
            id="experience-generic",
            task_type="bug-investigation",
            priority=20,
            rule_text="Generic bug-investigation guidance.",
            workflow_guidance=["Generic workflow."],
            constraint_guidance=[],
            quality_gate_guidance=[],
            evidence=[],
            derived_at="2026-05-31T00:00:00Z",
        ),
        ExperienceRule(
            id="experience-specific",
            task_type="bug-investigation",
            language="zh-CN",
            target_platform="opencode",
            priority=10,
            rule_text="Specific bug-investigation guidance.",
            workflow_guidance=["Specific workflow."],
            constraint_guidance=[],
            quality_gate_guidance=[],
            evidence=[],
            derived_at="2026-05-31T00:00:00Z",
        ),
        ExperienceRule(
            id="experience-nonmatching",
            task_type="bug-investigation",
            language="en-US",
            priority=90,
            rule_text="Nonmatching guidance.",
            workflow_guidance=["Nonmatching workflow."],
            constraint_guidance=[],
            quality_gate_guidance=[],
            evidence=[],
            derived_at="2026-05-31T00:00:00Z",
        ),
    ]

    selected = service.select_applicable_rules(requirement, rules)

    assert [rule.id for rule in selected] == ["experience-specific", "experience-generic"]
