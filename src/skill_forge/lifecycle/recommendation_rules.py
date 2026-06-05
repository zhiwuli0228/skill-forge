"""Pure, deterministic lifecycle recommendation rules.

This module is deliberately I/O-free. The function
:func:`recommend_lifecycle_action` maps a structured
:class:`LifecycleRecommendationInput` to a
:class:`~skill_forge.lifecycle.recommendation.LifecycleRecommendation`
result. The function performs no file reads, no network calls,
and no side effects. The same input always produces the same
output.

This module is the minimal deterministic slice of the lifecycle
recommendation change. CLI integration, persistence, and
service-level orchestration are intentionally out of scope and
are preserved as pre-existing WIP in
``skill_forge.lifecycle.recommendation.LifecycleRecommendationService``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from skill_forge.lifecycle.models import LifecycleState
from skill_forge.lifecycle.recommendation import LifecycleRecommendation


class LifecycleRecommendationInput(BaseModel):
    """Structured facts used to derive a lifecycle recommendation.

    The model carries facts only. It does not include package
    paths, workspace state, or any field that would force the
    recommender to read from disk. ``extra`` is ``"forbid"`` so
    that unknown fields fail at construction time, and
    ``skill_name`` has a minimum length of one so an empty name
    is rejected by Pydantic rather than silently accepted.
    """

    model_config = ConfigDict(extra="forbid")

    skill_name: str = Field(min_length=1)
    state: LifecycleState
    reason: str = ""
    missing_facts: list[str] = Field(default_factory=list)
    quality_score: int | None = None
    quality_status: str | None = None
    eval_total: int | None = None
    eval_passed: int | None = None
    eval_failed: int | None = None
    applied_experience_rule_ids: list[str] = Field(default_factory=list)


def recommend_lifecycle_action(
    input: LifecycleRecommendationInput,
) -> LifecycleRecommendation:
    """Return a deterministic lifecycle recommendation for the given facts.

    The function is pure: it does not read from disk, perform
    network I/O, mutate the input, or depend on a clock. The
    same ``input`` always produces the same returned
    :class:`LifecycleRecommendation`.

    The mapping is conservative: a Skill with an ``unknown``
    state receives the ``investigate-missing-facts`` action
    rather than a permissive one. The mapping is keyed on
    :class:`~skill_forge.lifecycle.models.LifecycleState`; the
    ``missing_facts`` and other fact fields are preserved on
    the returned recommendation for the caller's downstream
    use but do not change the action.
    """

    action, reason = _recommend_from_facts(input)
    return LifecycleRecommendation(
        skill_name=input.skill_name,
        state=input.state,
        action=action,
        reason=reason,
        missing_facts=list(input.missing_facts),
        signals=_signals(input),
    )


def _recommend_from_facts(
    input: LifecycleRecommendationInput,
) -> tuple[str, str]:
    state = input.state
    if state == "unknown":
        return (
            "investigate-missing-facts",
            (
                "The package lifecycle state is unknown; the missing facts "
                "must be investigated before a stronger recommendation can "
                "be made."
            ),
        )
    if state == "needs-eval":
        return (
            "run-eval",
            (
                "The package should be evaluated before any stronger "
                "lifecycle decision is made."
            ),
        )
    if state == "regressed":
        return (
            "repair-regression",
            (
                "The eval report shows failures, so the package should be "
                "repaired before promotion."
            ),
        )
    if state == "needs-upgrade":
        return (
            "consider-upgrade",
            (
                "The package is usable but does not yet meet the healthy "
                "threshold."
            ),
        )
    return (
        "ready-to-promote",
        "The package is healthy and ready for the next lifecycle step.",
    )


def _signals(input: LifecycleRecommendationInput) -> list[str]:
    signals: list[str] = []
    if input.reason:
        signals.append(input.reason)
    if input.quality_score is not None:
        status = input.quality_status if input.quality_status is not None else "unknown"
        signals.append(f"quality={input.quality_score}/100 ({status})")
    if input.eval_total is not None:
        passed = input.eval_passed if input.eval_passed is not None else 0
        signals.append(f"eval={passed}/{input.eval_total} passed")
    if input.missing_facts:
        signals.append(f"missing={', '.join(input.missing_facts)}")
    if input.applied_experience_rule_ids:
        signals.append(
            f"experience-rules={', '.join(input.applied_experience_rule_ids)}"
        )
    return signals
