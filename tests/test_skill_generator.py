from pathlib import Path

import pytest

from skill_forge.blueprints.enricher import BlueprintRequirementEnricher
from skill_forge.generator.skill_generator import SkillGenerator, SkillPackageExistsError, UnsafeGeneratedFilePathError
from skill_forge.models.blueprint import BlueprintGeneratedFile
from skill_forge.requirement.analyzer import RequirementAnalyzer


def test_generator_writes_skill_package(tmp_path: Path) -> None:
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")

    package = SkillGenerator().generate(requirement, tmp_path)

    assert package.name == "java-bug-investigation"
    assert package.path == tmp_path / "java-bug-investigation"
    assert package.skill_md_path == package.path / "SKILL.md"
    assert package.skill_md_path.is_file()
    assert "## Quality gates" in package.skill_md_path.read_text(encoding="utf-8")


def test_generator_writes_declared_references_and_metadata(tmp_path: Path) -> None:
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")
    requirement = BlueprintRequirementEnricher().enrich(requirement)

    package = SkillGenerator().generate(requirement, tmp_path)

    reference = package.path / "references" / "diagnosis-checklist.md"
    assert reference.is_file()
    assert package.references == {"references/diagnosis-checklist.md": str(reference.resolve())}
    assert "Diagnosis Checklist" in reference.read_text(encoding="utf-8")


def test_generator_rejects_generated_file_path_escape(tmp_path: Path) -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    requirement.references.append(BlueprintGeneratedFile.model_construct(path="../escape.md", content="bad"))

    with pytest.raises(UnsafeGeneratedFilePathError):
        SkillGenerator().generate(requirement, tmp_path)


def test_generator_does_not_overwrite_existing_package(tmp_path: Path) -> None:
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")
    SkillGenerator().generate(requirement, tmp_path)

    with pytest.raises(SkillPackageExistsError):
        SkillGenerator().generate(requirement, tmp_path)
