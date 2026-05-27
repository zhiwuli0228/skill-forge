from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


EVAL_REPORT_FILENAME = "eval-report.json"


class SkillEvalAssertions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required_sections: list[str] = Field(default_factory=list)
    required_constraints: list[str] = Field(default_factory=list)
    forbidden_phrases: list[str] = Field(default_factory=list)

    @field_validator("required_sections", "required_constraints", "forbidden_phrases")
    @classmethod
    def trim_items(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class SkillEvalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: str | None = None


class SkillEvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    skill: str
    input: SkillEvalInput = Field(default_factory=SkillEvalInput)
    assertions: SkillEvalAssertions
    path: Path | None = None

    @field_validator("id", "skill")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Value cannot be empty.")
        return normalized


class SkillEvalAssertionResult(BaseModel):
    passed: bool
    assertion: str
    message: str


class SkillEvalCaseResult(BaseModel):
    case_id: str
    case_path: str | None = None
    passed: bool
    assertions: list[SkillEvalAssertionResult] = Field(default_factory=list)


class SkillEvalReport(BaseModel):
    skill_name: str
    total: int
    passed: int
    failed: int
    results: list[SkillEvalCaseResult] = Field(default_factory=list)
