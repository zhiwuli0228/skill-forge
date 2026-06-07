from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CollectionState(str, Enum):
    CANDIDATE = "candidate"
    CURATED = "curated"
    PROMOTED = "promoted"
    REJECTED = "rejected"


COLLECTION_STATE_VALUES = tuple(state.value for state in CollectionState)

ScoreVersion = Literal["v1"]


class ScoreDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    score: float
    evidence: str | None = None


class ScoreSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_id: str
    snapshot_at: str
    structure_score: float = 0.0
    quality_score: float = 0.0
    eval_score: float = 0.0
    lifecycle_score: float = 0.0
    provenance_score: float = 0.0
    reuse_score: float = 0.0
    final_collection_score: float = 0.0
    final_promotion_score: float = 0.0
    score_version: ScoreVersion = "v1"
    evidence_refs: list[str] = Field(default_factory=list)
    dimensions: list[ScoreDimension] = Field(default_factory=list)


class CollectionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_id: str
    package_name: str
    origin_type: str
    origin_reference: str | None = None
    collection_state: CollectionState = CollectionState.CANDIDATE
    collection_score: float = 0.0
    promotion_score: float = 0.0
    score_version: ScoreVersion = "v1"
    tags: list[str] = Field(default_factory=list)
    rationale: str | None = None
    manual_override: bool = False
    last_verified_at: str | None = None
    created_at: str = ""
    updated_at: str = ""

    @property
    def is_curated_or_better(self) -> bool:
        return self.collection_state in (CollectionState.CURATED, CollectionState.PROMOTED)

    @property
    def is_promoted(self) -> bool:
        return self.collection_state == CollectionState.PROMOTED


def build_collection_record(
    *,
    skill_id: str,
    package_name: str,
    origin_type: str,
    origin_reference: str | None = None,
    collection_state: CollectionState = CollectionState.CANDIDATE,
    rationale: str | None = None,
) -> CollectionRecord:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return CollectionRecord(
        skill_id=skill_id,
        package_name=package_name,
        origin_type=origin_type,
        origin_reference=origin_reference,
        collection_state=collection_state,
        rationale=rationale,
        last_verified_at=now,
        created_at=now,
        updated_at=now,
    )
