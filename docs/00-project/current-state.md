# Current State

> Status: active
> Last updated: 2026-06-07
> Rotated: 2026-06-07 → `PERF_HARNESS_AND_CAMPAIGN_002_V060_FOLLOWUP`

<!--
================================================================================
PREVIOUS AUTHORIZATION (kept for reversibility, rotated-out 2026-06-07)
================================================================================

## Current Authorized Work Type

`REMEDIATION_V060`

## Authorization Scope

The user has granted explicit authorization to execute the
v0.6.0 real-experiment-data remediation campaign. This
authorization covers:

- Collecting real performance data from existing CLI and
  test-suite executions.
- Producing independent remediation artifacts under
  `outputs/reports/v0.6.0-remediation/`.
- No code changes, no test changes, no new dependencies,
  no new OpenSpec changes, no queue resizing, no production
  ThreadPoolExecutor integration.

## Constraints

- This is a remediation path only, not the main v0.6.0
  design implementation.
- Results must not be represented as "main plan completed."
- Raw evidence is not version-controlled by default.

================================================================================
END PREVIOUS AUTHORIZATION
-->

## Capability Baseline

`CAPABILITY_BASELINE_DELIVERED_AND_MAIN_SYNCED`

## Current Authorized Work Type

`PERF_HARNESS_AND_CAMPAIGN_002_V060_FOLLOWUP`

## Authorization Scope

The user has granted explicit authorization to execute the
v0.6.0 perf-harness extraction and Campaign-002 follow-up.
This authorization covers:

- Creating a reusable performance-campaign harness under
  `tests/perf/**` (a new project asset; the directory is
  not pytest-collected via `_`-prefix convention and
  contains no `test_*` or `*_test.py` files).
- Creating a new OpenSpec change under
  `openspec/changes/extract-perf-harness-and-run-campaign-002/`
  with its 8-artifact set (`.openspec.yaml`, `brainstorm.md`,
  `proposal.md`, `design.md`, `review.md`, `plan.md`,
  `tasks.md`, `verification.md`) and two new capability
  specs under `specs/performance-campaign-harness/` and
  `specs/performance-campaign-warmup-profile/`.
- Producing Campaign-002 evidence under
  `outputs/reports/v0.6.0-campaign-002/` (parallel to,
  and independently comparable with, the 001 artifacts
  under `outputs/reports/v0.6.0-remediation/`).
- Writing this `current-state.md` rotation (one-time,
  governed by reversibility via the comment block above).

## Constraints

- This is a perf-harness extraction + Campaign-002 follow-up
  path, not the main v0.6.0 design implementation.
- Results must not be represented as "main plan completed."
- The frozen 001 artifacts under
  `outputs/reports/v0.6.0-remediation/**` MUST NOT be
  regenerated, modified, or deleted; the new harness
  contains a guardrail that refuses to write to any output
  directory matching `v0.6.0-remediation*`.
- `src/skill_forge/**`, `pyproject.toml`, `uv.lock`,
  `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`,
  `SUPERPOWERS.md`, `openspec/config.yaml`,
  `openspec/schemas/**`, `configs/**`, `templates/**`,
  and `openspec/specs/**` (other than the two new
  capability specs in this change) are all out of scope
  for this rotation. No new production dependencies.
- Existing 34 test files under `tests/test_*.py` are not
  modified; the harness exercises them but does not touch
  their contents.
- Cross-campaign warmup comparability: ratios are
  cross-campaign-comparable; absolute ms are not
  (002's larger workload will produce larger absolute
  numbers than 001's).

## Reversal

To revert this rotation, restore the previous block
from the comment header above and remove the new
`Current Authorized Work Type` / `Authorization Scope` /
`Constraints` sections. The pre-rotation
`REMEDIATION_V060` authorization is preserved verbatim
in the comment block for this purpose.
