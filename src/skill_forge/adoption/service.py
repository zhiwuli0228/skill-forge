from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
from pydantic import BaseModel

from skill_forge.models.generated import GeneratedSkillPackage, GenerationProvenanceMetadata, PROVENANCE_METADATA_FILENAME
from skill_forge.models.quality import GenerationQualityReport, build_generation_quality_report
from skill_forge.models.search import CorpusDocument
from skill_forge.storage.corpus_reader import CorpusReader
from skill_forge.validator.skill_validator import SkillValidator


class AdoptionError(RuntimeError):
    """Base error for adoption failures."""


class CorpusDocumentNotFoundError(AdoptionError):
    def __init__(self, document_id: int) -> None:
        super().__init__(f"Cached corpus document not found: {document_id}")
        self.document_id = document_id


class EmptyCorpusDocumentError(AdoptionError):
    def __init__(self, document_id: int) -> None:
        super().__init__(f"Cached corpus document has no adoptable Skill content: {document_id}")
        self.document_id = document_id


class AdoptedSkillExistsError(AdoptionError):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Adopted Skill package already exists: {path}")
        self.path = path


class SkillAdoptionResult(BaseModel):
    package: GeneratedSkillPackage
    source_document: CorpusDocument
    quality_report: GenerationQualityReport


class SkillAdoptionService:
    def __init__(
        self,
        *,
        output_dir: Path,
        corpus_reader: CorpusReader,
        validator: SkillValidator | None = None,
    ) -> None:
        self._output_dir = output_dir.expanduser()
        self._corpus_reader = corpus_reader
        self._validator = validator or SkillValidator()

    def adopt(self, *, document_id: int, name: str | None = None) -> SkillAdoptionResult:
        document = self._corpus_reader.load_document(document_id)
        if document is None:
            raise CorpusDocumentNotFoundError(document_id)
        if not document.content.strip():
            raise EmptyCorpusDocumentError(document_id)

        package_name = _safe_package_name(name or _frontmatter_name(document.content) or document.title)
        package_path = self._output_dir / package_name
        if package_path.exists():
            raise AdoptedSkillExistsError(package_path)

        package_path.mkdir(parents=True)
        skill_md_path = package_path / "SKILL.md"
        skill_md_path.write_text(document.content, encoding="utf-8")

        validation_result = self._validator.validate(package_path)
        quality_report = build_generation_quality_report(validation_result)
        package = GeneratedSkillPackage(
            name=package_name,
            path=package_path,
            target_platform=document.platform or "unknown",
            skill_md_path=skill_md_path,
        )
        _write_adoption_provenance(package=package, document=document, quality_report=quality_report)
        return SkillAdoptionResult(package=package, source_document=document, quality_report=quality_report)


def _frontmatter_name(content: str) -> str | None:
    post = frontmatter.loads(content)
    value = post.metadata.get("name")
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_package_name(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "adopted-skill"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_adoption_provenance(
    *,
    package: GeneratedSkillPackage,
    document: CorpusDocument,
    quality_report: GenerationQualityReport,
) -> None:
    now = _utcnow()
    metadata = GenerationProvenanceMetadata(
        origin_type="community-adopted",
        generated_at=now,
        adopted_at=now,
        skill_name=package.name,
        requirement_text="",
        target_platform=package.target_platform,
        language="unknown",
        quality_score=quality_report.score,
        quality_status=quality_report.status,
        source_name=document.source_name,
        source_url=document.source_url,
        document_url=document.document_url,
        document_id=document.document_id,
        example_id=document.example_id,
        source_platform=document.platform,
        content_hash=document.content_hash,
    )
    (package.path / PROVENANCE_METADATA_FILENAME).write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
