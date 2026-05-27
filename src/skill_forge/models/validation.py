from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    level: str
    code: str
    message: str


class ValidationResult(BaseModel):
    ok: bool
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)
