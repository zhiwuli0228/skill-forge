"""Tests for the pure lifecycle recommendation function.

These tests cover the deterministic mapping from
:class:`LifecycleRecommendationInput` to
:class:`~skill_forge.lifecycle.recommendation.LifecycleRecommendation`.
The function under test is pure: no file I/O, no network, no
clock, no global state. The tests do not need ``tmp_path``,
fixtures, or monkey-patching.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from skill_forge.lifecycle.recommendation import LifecycleRecommendation
from skill_forge.lifecycle.recommendation_rules import (
    LifecycleRecommendationInput,
    recommend_lifecycle_action,
)


# --- happy-path state mapping -----------------------------------------------


def test_unknown_state_recommends_investigate_missing_facts() -> None:
    """A new or unknown Skill state maps to the conservative action."""
    result = recommend_lifecycle_action(
        LifecycleRecommendationInput(
            skill_name="new-skill",
            state="unknown",
            reason="Provenance is missing.",
            missing_facts=["provenance", "eval-report", "quality metrics"],
        )
    )

    assert isinstance(result, LifecycleRecommendation)
    assert result.skill_name == "new-skill"
    assert result.state == "unknown"
    assert result.action == "investigate-missing-facts"
    assert "unknown" in result.reason.casefold()
    assert "provenance" in result.missing_facts


def test_unknown_state_without_explicit_missing_facts_is_still_conservative() -> None:
    """Unknown state with no listed missing facts still gets the conservative action."""
    result = recommend_lifecycle_action(
        LifecycleRecommendationInput(skill_name="ambiguous-skill", state="unknown")
    )

    assert result.action == "investigate-missing-facts"
    assert result.state == "unknown"
    assert result.missing_facts == []


def test_outdated_provenance_recommends_investigate_missing_facts() -> None:
    """Outdated provenance is treated as a missing fact and triggers the conservative action."""
    result = recommend_lifecycle_action(
        LifecycleRecommendationInput(
            skill_name="outdated-skill",
            state="unknown",
            reason="Provenance schema version is outdated.",
            missing_facts=["provenance"],
        )
    )

    assert result.action == "investigate-missing-facts"
    assert result.state == "unknown"
    assert result.missing_facts == ["provenance"]


def test_current_valid_metadata_recommends_ready_to_promote() -> None:
    """A healthy Skill with full metadata is recommended for promotion."""
    result = recommend_lifecycle_action(
        LifecycleRecommendationInput(
            skill_name="healthy-skill",
            state="healthy",
            reason="Provenance, quality, and eval signals are all healthy.",
            quality_score=95,
            quality_status="valid",
            eval_total=10,
            eval_passed=10,
            eval_failed=0,
        )
    )

    assert result.action == "ready-to-promote"
    assert result.state == "healthy"
    assert "ready" in result.reason.casefold()
    assert "healthy" in result.reason.casefold()
    assert result.missing_facts == []


def test_needs_eval_state_recommends_run_eval() -> None:
    result = recommend_lifecycle_action(
        LifecycleRecommendationInput(
            skill_name="needs-eval-skill",
            state="needs-eval",
            missing_facts=["eval-report"],
        )
    )

    assert result.action == "run-eval"
    assert result.state == "needs-eval"


def test_regressed_state_recommends_repair_regression() -> None:
    result = recommend_lifecycle_action(
        LifecycleRecommendationInput(
            skill_name="regressed-skill",
            state="regressed",
            eval_total=3,
            eval_passed=2,
            eval_failed=1,
        )
    )

    assert result.action == "repair-regression"
    assert result.state == "regressed"


def test_needs_upgrade_state_recommends_consider_upgrade() -> None:
    result = recommend_lifecycle_action(
        LifecycleRecommendationInput(
            skill_name="needs-upgrade-skill",
            state="needs-upgrade",
            quality_score=85,
            quality_status="valid",
        )
    )

    assert result.action == "consider-upgrade"
    assert result.state == "needs-upgrade"


# --- invalid or incomplete input -------------------------------------------


def test_invalid_state_raises_validation_error() -> None:
    """A state outside the LifecycleState literal fails Pydantic validation."""
    with pytest.raises(ValidationError):
        LifecycleRecommendationInput(skill_name="x", state="not-a-valid-state")


def test_empty_skill_name_raises_validation_error() -> None:
    """An empty skill name fails the min_length=1 constraint."""
    with pytest.raises(ValidationError):
        LifecycleRecommendationInput(skill_name="", state="healthy")


def test_missing_required_state_raises_validation_error() -> None:
    """A model without the required state field fails Pydantic validation."""
    with pytest.raises(ValidationError):
        LifecycleRecommendationInput(skill_name="x")  # type: ignore[call-arg]


def test_extra_field_raises_validation_error() -> None:
    """An unknown field is rejected by the extra='forbid' model config."""
    with pytest.raises(ValidationError):
        LifecycleRecommendationInput(
            skill_name="x",
            state="healthy",
            not_a_real_field=1,  # type: ignore[call-arg]
        )


# --- determinism -----------------------------------------------------------


def test_function_is_deterministic_on_repeated_calls() -> None:
    """The same input produces the same recommendation on repeated calls."""
    input = LifecycleRecommendationInput(
        skill_name="det-skill",
        state="needs-eval",
        reason="No eval report is available for this Skill package.",
        missing_facts=["eval-report"],
    )

    first = recommend_lifecycle_action(input)
    second = recommend_lifecycle_action(input)
    third = recommend_lifecycle_action(input)

    assert first.model_dump() == second.model_dump()
    assert second.model_dump() == third.model_dump()


def test_function_does_not_mutate_input() -> None:
    """The function must not mutate the input model."""
    input = LifecycleRecommendationInput(
        skill_name="pure-skill",
        state="healthy",
        reason="All signals healthy.",
        missing_facts=["eval-report"],
    )
    snapshot = input.model_dump()

    recommend_lifecycle_action(input)
    recommend_lifecycle_action(input)
    recommend_lifecycle_action(input)

    assert input.model_dump() == snapshot


def test_signals_are_produced_in_a_stable_order() -> None:
    """The signals list is built in a stable, deterministic order."""
    input = LifecycleRecommendationInput(
        skill_name="signals-skill",
        state="needs-upgrade",
        reason="Quality score 80/100 is below the healthy threshold.",
        quality_score=80,
        quality_status="valid",
        eval_total=5,
        eval_passed=4,
        eval_failed=1,
        applied_experience_rule_ids=["rule-a", "rule-b"],
    )

    first = recommend_lifecycle_action(input)
    second = recommend_lifecycle_action(input)
    third = recommend_lifecycle_action(input)

    assert first.signals == second.signals == third.signals
    assert first.signals[0] == "Quality score 80/100 is below the healthy threshold."
    assert first.signals[1] == "quality=80/100 (valid)"
    assert first.signals[2] == "eval=4/5 passed"
    assert first.signals[3] == "experience-rules=rule-a, rule-b"


# --- module-level purity guard ---------------------------------------------


def test_module_does_not_depend_on_disk_or_clock() -> None:
    """The function must be callable with no I/O setup at all.

    This test is a guard against a future refactor that
    accidentally introduces a side-effecting dependency
    (e.g., a logger that writes to a file). The test constructs
    the input and calls the function in a single statement,
    without any fixture or context manager.
    """

    result = recommend_lifecycle_action(
        LifecycleRecommendationInput(skill_name="isolated-skill", state="healthy")
    )
    assert result.action == "ready-to-promote"
