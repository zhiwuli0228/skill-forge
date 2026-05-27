from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field

from skill_forge.models.generated import GeneratedSkillPackage
from skill_forge.models.requirement import SkillRequirement


class DraftStatus(StrEnum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    READY_TO_GENERATE = "ready_to_generate"
    GENERATED = "generated"
    INSTALLED = "installed"


class SkillDraftState(BaseModel):
    draft_id: str
    requirement: SkillRequirement
    current_step: str = "name"
    status: DraftStatus = DraftStatus.DRAFT
    project_path: str | None = None
    project_context_summary: str | None = None
    selected_examples: list[str] = Field(default_factory=list)
    generated_package: GeneratedSkillPackage | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
