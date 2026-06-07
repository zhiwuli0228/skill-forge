from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from skill_forge.models.collection import ScoreDimension, ScoreSnapshot


SCORE_VERSION = "v1"

# Default weights for collection_score
DEFAULT_COLLECTION_WEIGHTS: dict[str, float] = {
    "structure": 0.20,
    "quality": 0.25,
    "eval": 0.25,
    "lifecycle": 0.15,
    "provenance": 0.10,
    "reuse": 0.05,
}

# Default weights for promotion_score (emphasize quality and eval)
DEFAULT_PROMOTION_WEIGHTS: dict[str, float] = {
    "structure": 0.10,
    "quality": 0.30,
    "eval": 0.30,
    "lifecycle": 0.15,
    "provenance": 0.10,
    "reuse": 0.05,
}

# Default thresholds
DEFAULT_PROMOTION_THRESHOLD = 0.70
DEFAULT_CURATED_THRESHOLD = 0.50

# Backward-compatible aliases
PROMOTION_THRESHOLD = DEFAULT_PROMOTION_THRESHOLD
CURATED_THRESHOLD = DEFAULT_CURATED_THRESHOLD


@dataclass
class ScoringConfig:
    """Configurable scoring weights and thresholds."""

    collection_weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_COLLECTION_WEIGHTS))
    promotion_weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_PROMOTION_WEIGHTS))
    promotion_threshold: float = DEFAULT_PROMOTION_THRESHOLD
    curated_threshold: float = DEFAULT_CURATED_THRESHOLD


class ScoringInputs:
    """Collects local evidence signals for scoring."""

    def __init__(self) -> None:
        self.has_skill_md: bool = False
        self.has_frontmatter: bool = False
        self.has_required_sections: bool = False
        self.quality_score: float | None = None
        self.quality_status: str | None = None
        self.content_quality_workflow: float | None = None
        self.content_quality_constraint: float | None = None
        self.content_quality_gate: float | None = None
        self.eval_total: int | None = None
        self.eval_passed: int | None = None
        self.eval_failed: int | None = None
        self.lifecycle_state: str | None = None
        self.has_provenance: bool = False
        self.origin_type: str | None = None
        self.has_applied_experience: bool = False
        self.reuse_count: int = 0


def compute_scores(inputs: ScoringInputs, config: ScoringConfig | None = None) -> ScoreSnapshot:
    if config is None:
        config = ScoringConfig()

    structure = _score_structure(inputs)
    quality = _score_quality(inputs)
    eval_score = _score_eval(inputs)
    lifecycle = _score_lifecycle(inputs)
    provenance = _score_provenance(inputs)
    reuse = _score_reuse(inputs)

    dimensions = [
        ScoreDimension(name="structure", score=structure, evidence=_evidence_structure(inputs)),
        ScoreDimension(name="quality", score=quality, evidence=_evidence_quality(inputs)),
        ScoreDimension(name="eval", score=eval_score, evidence=_evidence_eval(inputs)),
        ScoreDimension(name="lifecycle", score=lifecycle, evidence=_evidence_lifecycle(inputs)),
        ScoreDimension(name="provenance", score=provenance, evidence=_evidence_provenance(inputs)),
        ScoreDimension(name="reuse", score=reuse, evidence=_evidence_reuse(inputs)),
    ]

    collection_score = round(
        sum(dim.score * config.collection_weights[dim.name] for dim in dimensions),
        4,
    )
    promotion_score = round(
        sum(dim.score * config.promotion_weights[dim.name] for dim in dimensions),
        4,
    )

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return ScoreSnapshot(
        skill_id="",
        snapshot_at=now,
        structure_score=structure,
        quality_score=quality,
        eval_score=eval_score,
        lifecycle_score=lifecycle,
        provenance_score=provenance,
        reuse_score=reuse,
        final_collection_score=collection_score,
        final_promotion_score=promotion_score,
        score_version=SCORE_VERSION,
        dimensions=dimensions,
    )


def suggested_state(
    collection_score: float,
    promotion_score: float,
    config: ScoringConfig | None = None,
) -> str:
    if config is None:
        config = ScoringConfig()
    if promotion_score >= config.promotion_threshold:
        return "promoted"
    if collection_score >= config.curated_threshold:
        return "curated"
    return "candidate"


def _score_structure(inputs: ScoringInputs) -> float:
    score = 0.0
    if inputs.has_skill_md:
        score += 0.40
    if inputs.has_frontmatter:
        score += 0.30
    if inputs.has_required_sections:
        score += 0.30
    return round(min(score, 1.0), 4)


def _score_quality(inputs: ScoringInputs) -> float:
    if inputs.quality_score is None:
        return 0.0
    normalized = max(0.0, min(1.0, inputs.quality_score / 100.0))
    content_bonus = 0.0
    content_scores = [
        v for v in (
            inputs.content_quality_workflow,
            inputs.content_quality_constraint,
            inputs.content_quality_gate,
        )
        if v is not None
    ]
    if content_scores:
        content_bonus = sum(content_scores) / len(content_scores) * 0.2
    return round(min(normalized + content_bonus, 1.0), 4)


def _score_eval(inputs: ScoringInputs) -> float:
    if inputs.eval_total is None or inputs.eval_total == 0:
        return 0.0
    if inputs.eval_passed is None:
        return 0.0
    pass_rate = inputs.eval_passed / inputs.eval_total
    if inputs.eval_failed is not None and inputs.eval_failed > 0:
        penalty = min(inputs.eval_failed * 0.1, 0.3)
        pass_rate = max(0.0, pass_rate - penalty)
    return round(min(pass_rate, 1.0), 4)


def _score_lifecycle(inputs: ScoringInputs) -> float:
    if inputs.lifecycle_state is None:
        return 0.0
    state_scores = {
        "healthy": 1.0,
        "needs-eval": 0.5,
        "needs-upgrade": 0.4,
        "regressed": 0.1,
        "unknown": 0.0,
    }
    return round(state_scores.get(inputs.lifecycle_state, 0.0), 4)


def _score_provenance(inputs: ScoringInputs) -> float:
    score = 0.0
    if inputs.has_provenance:
        score += 0.50
    if inputs.origin_type is not None:
        if inputs.origin_type == "blueprint-generated":
            score += 0.30
        elif inputs.origin_type == "community-adopted":
            score += 0.20
        else:
            score += 0.10
    if inputs.has_applied_experience:
        score += 0.20
    return round(min(score, 1.0), 4)


def _score_reuse(inputs: ScoringInputs) -> float:
    if inputs.reuse_count <= 0:
        return 0.0
    return round(min(inputs.reuse_count / 5.0, 1.0), 4)


def _evidence_structure(inputs: ScoringInputs) -> str:
    parts = []
    if inputs.has_skill_md:
        parts.append("SKILL.md present")
    else:
        parts.append("SKILL.md missing")
    if inputs.has_frontmatter:
        parts.append("frontmatter present")
    else:
        parts.append("frontmatter missing")
    if inputs.has_required_sections:
        parts.append("required sections present")
    return "; ".join(parts)


def _evidence_quality(inputs: ScoringInputs) -> str:
    if inputs.quality_score is None:
        return "no quality score"
    return f"quality={inputs.quality_score}/100 ({inputs.quality_status or 'unknown'})"


def _evidence_eval(inputs: ScoringInputs) -> str:
    if inputs.eval_total is None:
        return "no eval report"
    return f"{inputs.eval_passed}/{inputs.eval_total} passed, {inputs.eval_failed} failed"


def _evidence_lifecycle(inputs: ScoringInputs) -> str:
    if inputs.lifecycle_state is None:
        return "no lifecycle state"
    return f"lifecycle={inputs.lifecycle_state}"


def _evidence_provenance(inputs: ScoringInputs) -> str:
    parts = []
    if inputs.has_provenance:
        parts.append("provenance present")
    else:
        parts.append("no provenance")
    if inputs.origin_type:
        parts.append(f"origin={inputs.origin_type}")
    if inputs.has_applied_experience:
        parts.append("experience applied")
    return "; ".join(parts)


def _evidence_reuse(inputs: ScoringInputs) -> str:
    if inputs.reuse_count <= 0:
        return "no reuse history"
    return f"reuse_count={inputs.reuse_count}"
