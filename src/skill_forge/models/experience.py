from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


EXPERIENCE_SCHEMA_VERSION = 1
EXPERIENCE_RULE_FILENAME_SUFFIX = ".json"


class ExperienceRuleEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_package: str
    source_kind: Literal["eval-failure", "quality-dimension"]
    task_type: str | None = None
    language: str | None = None
    target_platform: str | None = None
    case_id: str | None = None
    assertion: str | None = None
    message: str | None = None
    quality_dimension: str | None = None
    score: float | None = None

    @field_validator("source_package", "source_kind")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Value cannot be empty.")
        return normalized


class ExperienceRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = EXPERIENCE_SCHEMA_VERSION
    id: str
    task_type: str
    language: str | None = None
    target_platform: str | None = None
    priority: int = 0
    rule_text: str
    workflow_guidance: list[str] = Field(default_factory=list)
    constraint_guidance: list[str] = Field(default_factory=list)
    quality_gate_guidance: list[str] = Field(default_factory=list)
    evidence: list[ExperienceRuleEvidence] = Field(default_factory=list)
    derived_at: str

    @field_validator("id", "task_type", "rule_text", "derived_at")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Value cannot be empty.")
        return normalized

    @field_validator("priority")
    @classmethod
    def require_non_negative_priority(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Priority cannot be negative.")
        return value

    @field_validator("workflow_guidance", "constraint_guidance", "quality_gate_guidance")
    @classmethod
    def trim_guidance_items(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ExperienceDerivationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules: list[ExperienceRule] = Field(default_factory=list)
    scanned_packages: int = 0
    skipped_packages: list[str] = Field(default_factory=list)
    evidence_count: int = 0


class AppliedExperienceRuleContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    used: bool = False
    task_type: str | None = None
    language: str | None = None
    target_platform: str | None = None
    rule_ids: list[str] = Field(default_factory=list)
    rule_summaries: list[str] = Field(default_factory=list)

