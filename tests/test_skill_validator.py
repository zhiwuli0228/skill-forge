from pathlib import Path

from skill_forge.generator.skill_generator import SkillGenerator
from skill_forge.requirement.analyzer import RequirementAnalyzer
from skill_forge.validator.skill_validator import SkillValidator


def _generated_package(tmp_path: Path) -> Path:
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")
    return SkillGenerator().generate(requirement, tmp_path).path


def test_validator_accepts_generated_package(tmp_path: Path) -> None:
    result = SkillValidator().validate(_generated_package(tmp_path))

    assert result.ok is True
    assert result.errors == []


def test_validator_accepts_safe_attachment_metadata(tmp_path: Path) -> None:
    result = SkillValidator().validate(
        _generated_package(tmp_path),
        attachment_paths=["references/diagnosis-checklist.md"],
    )

    assert result.ok is True
    assert result.errors == []


def test_validator_rejects_unsafe_attachment_metadata(tmp_path: Path) -> None:
    result = SkillValidator().validate(
        _generated_package(tmp_path),
        attachment_paths=["../escape.md"],
    )

    assert result.ok is False
    assert any(issue.code == "unsafe_attachment_path" for issue in result.errors)


def test_validator_reports_missing_directory(tmp_path: Path) -> None:
    result = SkillValidator().validate(tmp_path / "missing")

    assert result.ok is False
    assert result.errors[0].code == "missing_directory"


def test_validator_reports_missing_skill_md(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()

    result = SkillValidator().validate(skill_dir)

    assert result.ok is False
    assert result.errors[0].code == "missing_skill_md"


def test_validator_reports_missing_frontmatter_and_metadata(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Skill\n\n## Purpose\n\nText\n", encoding="utf-8")

    result = SkillValidator().validate(skill_dir)
    codes = {issue.code for issue in result.errors}

    assert result.ok is False
    assert "missing_frontmatter" in codes
    assert "missing_name" in codes
    assert "missing_description" in codes


def test_validator_reports_empty_description(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: sample\ndescription: ''\n---\n", encoding="utf-8")

    result = SkillValidator().validate(skill_dir)

    assert result.ok is False
    assert any(issue.code == "empty_description" for issue in result.errors)


def test_validator_warns_for_missing_recommended_sections(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: sample\ndescription: Valid.\n---\n", encoding="utf-8")

    result = SkillValidator().validate(skill_dir)

    assert result.ok is True
    assert any(issue.code == "missing_section" for issue in result.warnings)


def test_validator_warns_for_non_slug_name_and_package_mismatch(tmp_path: Path) -> None:
    skill_dir = tmp_path / "sample-package"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: Sample Package
description: Use this skill when reviewing package metadata. Do not use it for unrelated tasks.
---

## Purpose
Text

## When to use
- Reviewing package metadata.

## When not to use
- Unrelated tasks.

## Workflow
1. Inspect metadata.
2. Report mismatch.

## Output format
- Findings

## Quality gates
- Name is checked.
- Package is checked.
""",
        encoding="utf-8",
    )

    result = SkillValidator().validate(skill_dir)
    codes = {issue.code for issue in result.warnings}

    assert result.ok is True
    assert "name_not_slug" in codes
    assert "package_name_mismatch" in codes


def test_validator_warns_for_weak_description(tmp_path: Path) -> None:
    skill_dir = tmp_path / "sample"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: sample
description: Helpful.
---

## Purpose
Text

## When to use
- Useful tasks.

## When not to use
- Other tasks.

## Workflow
1. Inspect.
2. Report.

## Output format
- Result

## Quality gates
- Checked.
- Verified.
""",
        encoding="utf-8",
    )

    result = SkillValidator().validate(skill_dir)
    codes = {issue.code for issue in result.warnings}

    assert result.ok is True
    assert "description_too_short" in codes
    assert "description_missing_trigger" in codes
    assert "description_missing_exclusion" in codes


def test_validator_warns_for_empty_section_and_thin_lists(tmp_path: Path) -> None:
    skill_dir = tmp_path / "sample"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: sample
description: Use this skill when reviewing a Skill package. Do not use it for unrelated implementation.
---

## Purpose

## When to use
- Reviewing packages.

## When not to use
- Building features.

## Workflow
1. Inspect.

## Output format
- Result

## Quality gates
- Checked.
""",
        encoding="utf-8",
    )

    result = SkillValidator().validate(skill_dir)
    codes = {issue.code for issue in result.warnings}

    assert result.ok is True
    assert "empty_section" in codes
    assert "workflow_too_short" in codes
    assert "quality_gates_too_few" in codes
