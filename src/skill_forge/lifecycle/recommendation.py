from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from skill_forge.lifecycle.models import LifecycleSummary
from skill_forge.lifecycle.service import LifecycleService


LifecycleRecommendationAction = Literal[
    "investigate-missing-facts",
    "run-eval",
    "repair-regression",
    "consider-upgrade",
    "ready-to-promote",
]


class LifecycleRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_name: str
    state: str
    action: LifecycleRecommendationAction
    reason: str
    missing_facts: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)


class LifecycleComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    left_skill_name: str
    right_skill_name: str
    preferred_skill_name: str
    reason: str
    tie_breaker: str
    left_summary: LifecycleSummary
    right_summary: LifecycleSummary


class LifecycleRecommendationService:
    def __init__(self, lifecycle_service: LifecycleService) -> None:
        self._lifecycle_service = lifecycle_service

    @property
    def lifecycle_service(self) -> LifecycleService:
        return self._lifecycle_service

    def recommend(self, skill_name: str) -> LifecycleRecommendation:
        summary = self._lifecycle_service.show(skill_name)
        return _recommend_via_rules(summary)

    def compare(self, left_skill_name: str, right_skill_name: str) -> LifecycleComparison:
        left = self._lifecycle_service.show(left_skill_name)
        right = self._lifecycle_service.show(right_skill_name)
        left_key = _comparison_key(left)
        right_key = _comparison_key(right)
        if left_key > right_key:
            preferred = left
            tie_breaker = _tie_breaker_reason(left, right, preferred_side="left")
        elif right_key > left_key:
            preferred = right
            tie_breaker = _tie_breaker_reason(left, right, preferred_side="right")
        else:
            preferred = left if left.skill_name.casefold() <= right.skill_name.casefold() else right
            tie_breaker = f"States and signals were equivalent, so skill name order selected {preferred.skill_name}."
        return LifecycleComparison(
            left_skill_name=left.skill_name,
            right_skill_name=right.skill_name,
            preferred_skill_name=preferred.skill_name,
            reason=_compare_reason(left, right, preferred.skill_name),
            tie_breaker=tie_breaker,
            left_summary=left,
            right_summary=right,
        )


_STATE_ORDER: dict[str, int] = {
    "healthy": 4,
    "needs-upgrade": 3,
    "needs-eval": 2,
    "regressed": 1,
    "unknown": 0,
}


def _summary_to_input(summary: LifecycleSummary):
    """Map a ``LifecycleSummary`` to a ``LifecycleRecommendationInput``.

    The pure module ``skill_forge.lifecycle.recommendation_rules``
    imports ``LifecycleRecommendation`` from this module at module
    load time, which creates a circular dependency. The pure input
    model is therefore imported lazily inside this function body
    so the cycle is resolved at call time, after both modules are
    fully loaded.
    """

    from skill_forge.lifecycle.recommendation_rules import (
        LifecycleRecommendationInput,
    )

    return LifecycleRecommendationInput(
        skill_name=summary.skill_name,
        state=summary.state,
        reason=summary.reason,
        missing_facts=list(summary.missing_facts),
        quality_score=summary.quality_score,
        quality_status=summary.quality_status,
        eval_total=summary.eval_total,
        eval_passed=summary.eval_passed,
        eval_failed=summary.eval_failed,
        applied_experience_rule_ids=list(summary.applied_experience_rule_ids),
    )


def _recommend_via_rules(summary: LifecycleSummary) -> LifecycleRecommendation:
    """Delegate to the pure ``recommend_lifecycle_action`` function.

    The pure module owns the deterministic state-based rule. This
    service-level helper exists to bridge the service-layer data
    carrier (``LifecycleSummary``) to the pure function's input
    model. The pure function and its input model are imported
    lazily to break the circular dependency between this module and
    ``skill_forge.lifecycle.recommendation_rules``.
    """

    from skill_forge.lifecycle.recommendation_rules import (
        recommend_lifecycle_action,
    )

    return recommend_lifecycle_action(_summary_to_input(summary))


def _comparison_key(summary: LifecycleSummary) -> tuple[int, int, int, int, int]:
    quality_score = summary.quality_score if summary.quality_score is not None else -1
    eval_passed = summary.eval_passed if summary.eval_passed is not None else -1
    eval_failed = summary.eval_failed if summary.eval_failed is not None else 0
    return (
        _STATE_ORDER.get(summary.state, 0),
        quality_score,
        eval_passed,
        -eval_failed,
        -len(summary.missing_facts),
    )


def _compare_reason(left: LifecycleSummary, right: LifecycleSummary, preferred_skill_name: str) -> str:
    left_key = _comparison_key(left)
    right_key = _comparison_key(right)
    if left_key == right_key:
        return (
            f"Both packages have equivalent lifecycle ordering inputs; {preferred_skill_name} was selected "
            "by deterministic name order."
        )
    better = left if left.skill_name == preferred_skill_name else right
    worse = right if better is left else left
    return (
        f"{preferred_skill_name} ranked higher than {worse.skill_name} based on state, quality, eval, "
        f"and missing-fact ordering."
    )


def _tie_breaker_reason(left: LifecycleSummary, right: LifecycleSummary, *, preferred_side: str) -> str:
    if preferred_side == "left":
        return (
            f"{left.skill_name} outranked {right.skill_name} on the deterministic comparison key "
            "(state, quality, eval, missing facts, then name)."
        )
    return (
        f"{right.skill_name} outranked {left.skill_name} on the deterministic comparison key "
        "(state, quality, eval, missing facts, then name)."
    )
