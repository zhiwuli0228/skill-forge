from pathlib import Path

from pydantic import BaseModel, Field


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
    generated_at: str
    skill_name: str
    requirement_text: str
    target_platform: str
    language: str
    task_type: str | None = None
    blueprint_id: str | None = None
    blueprint_source: str | None = None
    llm_enabled: bool = False
    project_context_path: str | None = None
    quality_score: int
    quality_status: str
    references: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    scripts: list[str] = Field(default_factory=list)
