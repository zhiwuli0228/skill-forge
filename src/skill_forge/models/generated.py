from pathlib import Path

from pydantic import BaseModel, Field

from skill_forge.models.quality import ContentQualityMetrics


PROVENANCE_METADATA_FILENAME = "skill-forge.json"
PROVENANCE_SCHEMA_VERSION = 1


class GeneratedSkillPackage(BaseModel):
    name: str
    path: Path
    target_platform: str
    skill_md_path: Path
    references: dict[str, str] = Field(default_factory=dict)
    assets: dict[str, str] = Field(default_factory=dict)
    scripts: dict[str, str] = Field(default_factory=dict)


class GenerationProvenanceMetadata(BaseModel):
    schema_version: int = PROVENANCE_SCHEMA_VERSION
    origin_type: str = "generated"
    generated_at: str
    adopted_at: str | None = None
    skill_name: str
    requirement_text: str
    target_platform: str
    language: str
    task_type: str | None = None
    blueprint_id: str | None = None
    blueprint_source: str | None = None
    llm_enabled: bool = False
    llm_mode: str = "unknown"
    llm_selection: str = "unknown"
    llm_fallback_reason: str | None = None
    llm_generated_fields: list[str] = Field(default_factory=list)
    llm_fallback_fields: list[str] = Field(default_factory=list)
    llm_refined_fields: list[str] = Field(default_factory=list)
    retrieval_augmented: bool = False
    retrieval_augmentation_reason: str | None = None
    retrieval_reference_names: list[str] = Field(default_factory=list)
    applied_experience_rule_ids: list[str] = Field(default_factory=list)
    project_context_path: str | None = None
    quality_score: int
    quality_status: str
    content_quality: ContentQualityMetrics | None = None
    source_name: str | None = None
    source_url: str | None = None
    document_url: str | None = None
    document_id: int | None = None
    example_id: int | None = None
    source_platform: str | None = None
    content_hash: str | None = None
    references: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    scripts: list[str] = Field(default_factory=list)
