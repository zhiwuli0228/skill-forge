from __future__ import annotations

from typing import Literal
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


LifecycleState = Literal["healthy", "needs-eval", "needs-upgrade", "regressed", "unknown"]


class LifecycleEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    summary: str
    details: list[str] = Field(default_factory=list)


class LifecycleSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_name: str
    package_path: Path
    state: LifecycleState
    reason: str
    evidence: list[LifecycleEvidence] = Field(default_factory=list)
    missing_facts: list[str] = Field(default_factory=list)
    quality_score: int | None = None
    quality_status: str | None = None
    eval_total: int | None = None
    eval_passed: int | None = None
    eval_failed: int | None = None
    applied_experience_rule_ids: list[str] = Field(default_factory=list)
    resolved_experience_rules: list[str] = Field(default_factory=list)
