from pydantic import BaseModel, Field

from skill_forge.models.blueprint import BlueprintGeneratedFile


class SkillRequirement(BaseModel):
    name: str
    description: str
    domain: str | None = None
    task_type: str | None = None
    target_platform: str = "opencode"
    language: str = "zh-CN"
    when_to_use: list[str] = Field(default_factory=list)
    when_not_to_use: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    workflow: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    quality_gates: list[str] = Field(default_factory=list)
    references_needed: bool = False
    scripts_needed: bool = False
    assets_needed: bool = False
    references: list[BlueprintGeneratedFile] = Field(default_factory=list)
    assets: list[BlueprintGeneratedFile] = Field(default_factory=list)
    scripts: list[BlueprintGeneratedFile] = Field(default_factory=list)
    applied_blueprint_id: str | None = None
    applied_blueprint_source: str | None = None
