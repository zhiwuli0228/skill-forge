import re
from pathlib import PurePosixPath, PureWindowsPath

from pydantic import BaseModel, ConfigDict, Field, field_validator


_BLUEPRINT_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class BlueprintGeneratedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    content: str

    @field_validator("path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        normalized = value.strip().replace("\\", "/")
        path = PurePosixPath(normalized)
        if not normalized or path.is_absolute() or PureWindowsPath(normalized).is_absolute() or ".." in path.parts:
            raise ValueError("Generated file path must be a safe relative path.")
        return normalized

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value:
            raise ValueError("Generated file content cannot be empty.")
        return value


class SkillBlueprint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    task_type: str
    when_to_use: list[str] = Field(default_factory=list)
    when_not_to_use: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    workflow: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    quality_gates: list[str] = Field(default_factory=list)
    references: list[BlueprintGeneratedFile] = Field(default_factory=list)
    assets: list[BlueprintGeneratedFile] = Field(default_factory=list)
    scripts: list[BlueprintGeneratedFile] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not _BLUEPRINT_ID_PATTERN.fullmatch(value):
            raise ValueError("Blueprint id must be a lowercase kebab-case slug.")
        return value

    @field_validator("name", "description", "task_type")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Value cannot be empty.")
        return normalized

    @field_validator(
        "when_to_use",
        "when_not_to_use",
        "required_inputs",
        "workflow",
        "constraints",
        "expected_outputs",
        "quality_gates",
    )
    @classmethod
    def validate_non_empty_items(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]
