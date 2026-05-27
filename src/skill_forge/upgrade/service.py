from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ValidationError

from skill_forge.blueprints.enricher import BlueprintRequirementEnricher
from skill_forge.blueprints.loader import BlueprintError, BlueprintLoader, BlueprintNotFoundError
from skill_forge.generator.skill_generator import SkillGenerator, SkillPackageExistsError
from skill_forge.models.generated import GeneratedSkillPackage, GenerationProvenanceMetadata, PROVENANCE_METADATA_FILENAME
from skill_forge.models.quality import GenerationQualityReport, build_generation_quality_report
from skill_forge.requirement.analyzer import RequirementAnalyzer
from skill_forge.validator.skill_validator import SkillValidator


_PACKAGE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class MissingUpgradeProvenanceError(RuntimeError):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Missing provenance metadata: {path}")
        self.path = path


class InvalidUpgradeProvenanceError(RuntimeError):
    def __init__(self, path: Path, message: str) -> None:
        super().__init__(f"Invalid provenance metadata: {path}: {message}")
        self.path = path
        self.message = message


class MissingUpgradeBlueprintError(RuntimeError):
    def __init__(self, blueprint_id: str) -> None:
        super().__init__(f"Upgrade blueprint not found: {blueprint_id}")
        self.blueprint_id = blueprint_id


class CandidateExistsError(RuntimeError):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Upgrade candidate already exists: {path}")
        self.path = path


class InvalidCandidateNameError(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Candidate name must be lowercase kebab-case: {name}")
        self.name = name


class InvalidUpgradeCandidateError(RuntimeError):
    def __init__(self, package: GeneratedSkillPackage, quality_report: GenerationQualityReport) -> None:
        super().__init__(f"Upgrade candidate is invalid: {package.path}")
        self.package = package
        self.quality_report = quality_report


class SkillUpgradeResult(BaseModel):
    source_name: str
    candidate_name: str
    source_path: Path
    candidate_package: GeneratedSkillPackage
    previous_quality_score: int
    previous_quality_status: str
    candidate_quality_report: GenerationQualityReport
    blueprint_id: str | None = None
    blueprint_source: str | None = None


class SkillUpgradeService:
    def __init__(
        self,
        *,
        output_dir: Path,
        blueprint_loader: BlueprintLoader | None = None,
        analyzer: RequirementAnalyzer | None = None,
        generator: SkillGenerator | None = None,
        validator: SkillValidator | None = None,
    ) -> None:
        self._output_dir = output_dir.expanduser()
        self._blueprint_loader = blueprint_loader or BlueprintLoader()
        self._analyzer = analyzer or RequirementAnalyzer()
        self._generator = generator or SkillGenerator()
        self._validator = validator or SkillValidator()

    def upgrade(self, source_path: Path, *, candidate_name: str | None = None, force: bool = False) -> SkillUpgradeResult:
        provenance = _read_required_provenance(source_path)
        resolved_candidate_name = candidate_name or f"{source_path.name}-upgraded"
        _validate_candidate_name(resolved_candidate_name)
        candidate_path = self._output_dir / resolved_candidate_name
        _ensure_candidate_path(self._output_dir, candidate_path, source_path)
        if candidate_path.exists():
            if not force:
                raise CandidateExistsError(candidate_path)
            shutil.rmtree(candidate_path)

        requirement = self._analyzer.analyze(
            provenance.requirement_text,
            target_platform=provenance.target_platform,
            language=provenance.language,
        )
        requirement.name = resolved_candidate_name
        if provenance.blueprint_id:
            try:
                requirement = BlueprintRequirementEnricher(self._blueprint_loader).enrich(
                    requirement,
                    blueprint_id=provenance.blueprint_id,
                )
            except BlueprintNotFoundError as exc:
                raise MissingUpgradeBlueprintError(exc.blueprint_id) from exc
            except BlueprintError:
                raise
        else:
            requirement = BlueprintRequirementEnricher(self._blueprint_loader).enrich(requirement)

        package = self._generator.generate(requirement, self._output_dir)
        attachment_paths = [*package.references, *package.assets, *package.scripts]
        validation_result = self._validator.validate(package.path, attachment_paths=attachment_paths)
        quality_report = build_generation_quality_report(validation_result)
        if not quality_report.ok:
            raise InvalidUpgradeCandidateError(package, quality_report)

        _write_candidate_provenance(
            package=package,
            requirement=requirement,
            source_provenance=provenance,
            quality_report=quality_report,
        )
        return SkillUpgradeResult(
            source_name=source_path.name,
            candidate_name=resolved_candidate_name,
            source_path=source_path,
            candidate_package=package,
            previous_quality_score=provenance.quality_score,
            previous_quality_status=provenance.quality_status,
            candidate_quality_report=quality_report,
            blueprint_id=requirement.applied_blueprint_id,
            blueprint_source=requirement.applied_blueprint_source,
        )


def _read_required_provenance(skill_path: Path) -> GenerationProvenanceMetadata:
    metadata_path = skill_path / PROVENANCE_METADATA_FILENAME
    if not metadata_path.is_file():
        raise MissingUpgradeProvenanceError(metadata_path)
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        return GenerationProvenanceMetadata.model_validate(data)
    except json.JSONDecodeError as exc:
        raise InvalidUpgradeProvenanceError(metadata_path, str(exc)) from exc
    except OSError as exc:
        raise InvalidUpgradeProvenanceError(metadata_path, str(exc)) from exc
    except ValidationError as exc:
        raise InvalidUpgradeProvenanceError(metadata_path, _format_validation_error(exc)) from exc


def _validate_candidate_name(name: str) -> None:
    if not _PACKAGE_NAME_PATTERN.fullmatch(name):
        raise InvalidCandidateNameError(name)


def _ensure_candidate_path(output_dir: Path, candidate_path: Path, source_path: Path) -> None:
    output_root = output_dir.expanduser().resolve()
    resolved_candidate = candidate_path.resolve()
    resolved_source = source_path.resolve()
    if not resolved_candidate.is_relative_to(output_root):
        raise InvalidCandidateNameError(candidate_path.name)
    if resolved_candidate == resolved_source:
        raise CandidateExistsError(candidate_path)


def _write_candidate_provenance(
    *,
    package: GeneratedSkillPackage,
    requirement,
    source_provenance: GenerationProvenanceMetadata,
    quality_report: GenerationQualityReport,
) -> None:
    metadata = GenerationProvenanceMetadata(
        generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        skill_name=package.name,
        requirement_text=source_provenance.requirement_text,
        target_platform=package.target_platform,
        language=requirement.language,
        task_type=requirement.task_type,
        blueprint_id=requirement.applied_blueprint_id,
        blueprint_source=requirement.applied_blueprint_source,
        llm_enabled=False,
        project_context_path=source_provenance.project_context_path,
        quality_score=quality_report.score,
        quality_status=quality_report.status,
        references=sorted(package.references),
        assets=sorted(package.assets),
        scripts=sorted(package.scripts),
    )
    (package.path / PROVENANCE_METADATA_FILENAME).write_text(metadata.model_dump_json(indent=2), encoding="utf-8")


def _format_validation_error(error: ValidationError) -> str:
    issues: list[str] = []
    for issue in error.errors():
        location = ".".join(str(part) for part in issue["loc"])
        issues.append(f"{location}: {issue['msg']}")
    return "; ".join(issues)
