# Proposal — extract-perf-harness-and-run-campaign-002

> Status: proposed
> Schema: skill-forge-governance
> Author: implementation (Claude Code)
> Date: 2026-06-07

## Why

`v0.6.0-remediation-campaign-001` produced real performance
data for 6 of 34 test files using a one-off harness script.
The remaining 28 files (lifecycle, collection governance,
retrieval/semantic, adoption/experience/promotion, generation/
library/upgrade/evals, CLI/interaction/project-context) are
uncovered. A clear warmup signal was observed in STEADY but
recorded only as a side observation, not a structured
artifact. The 001 harness is monolithic, hardcoded to one
output directory, and not reusable.

This change introduces a project-level performance-campaign
harness under `tests/perf/` and uses it to run
`v0.6.0-campaign-002`, a follow-up campaign that covers the
28 uncovered files and emits a `warmup-profile-002.json`
artifact that quantifies warmup as a comparable, structured
signal.

## What Changes

- **New** capability `performance-campaign-harness`: the
  reusable harness under `tests/perf/`. Invoked via
  `python -m tests.perf._main --campaign <id> --output-dir <path>`.
  Produces run-manifest, raw-snapshots-*.jsonl,
  evidence-index, pressure-summary, readiness-summary,
  campaign-report artifacts. Includes a 001 freeze contract
  guardrail that refuses to write to any output directory
  matching `v0.6.0-remediation*`.
- **New** capability `performance-campaign-warmup-profile`:
  the structured warmup signal. Emits
  `warmup-profile-<BATCH_ID>.json` with three ratios
  (`firstToLast`, `firstToMean`, `firstToMedian`),
  `convergenceDeltaMs`, and `convergenceRatePct`, per
  profile. Median-of-rest is the G9 verdict ratio; ratios
  are cross-campaign-comparable while absolute ms are not.
- **New** P0 gates G7–G9 on top of the G1–G6 inherited from
  001: G7-coverage-expansion, G8-bucket-coverage,
  G9-warmup-extractable (two-tier: structural must pass,
  signal required for `READY`).
- **New** Campaign-002 evidence under
  `outputs/reports/v0.6.0-campaign-002/`, parallel to and
  independently comparable with the 001 artifacts under
  `outputs/reports/v0.6.0-remediation/`.

## Capabilities

### New

- `performance-campaign-harness`
- `performance-campaign-warmup-profile`

### Modified

None. The new change does not modify any existing capability
spec in `openspec/specs/**`; sync happens at archive time.

### Removed

None.

## Impact

- **Affected specs**: 2 new capability specs under
  `openspec/changes/extract-perf-harness-and-run-campaign-002/specs/`.
  At archive time, these merge into
  `openspec/specs/performance-campaign-harness/spec.md` and
  `openspec/specs/performance-campaign-warmup-profile/spec.md`.
- **Affected surfaces**: `tests/perf/` (new asset dir);
  `outputs/reports/v0.6.0-campaign-002/` (new campaign output);
  `docs/00-project/current-state.md` (one-time authorization
  rotation).
- **Affected tests**: none of the existing 34 test files
  are modified. The new harness exercises them but does not
  touch their contents. No new test files are added.
- **Affected dependencies**: none. The harness is stdlib-only
  (matching 001's posture); no `pyproject.toml` / `uv.lock`
  changes.

## Non-Goals

- Production ThreadPoolExecutor integration. Out of scope.
- Queue resizing. Out of scope.
- Modifying the 001 frozen artifacts. Out of scope.
- Auto-promoting warmup-ratio into a CI gate. Belongs to a
  follow-up change.
- Web UI for harness results. Out of scope.
- New tests under `tests/test_*.py`. Out of scope (harness is
  not a test suite; the `_` prefix prevents pytest collection).

## Risks

- **[R1] G9 sign error** → the gate definition must use
  `non-increasing` (not `non-decreasing`) for STEADY duration
  series; with `warmupRatio > 1.0` durations decrease over
  runs. Mitigated: G9's structural check is `non-increasing`
  in the harness; corrected during planning.
- **[R2] Pytest auto-collection** → the harness lives under
  `tests/` which pytest auto-discovers. Mitigated: all
  harness modules use `_`-prefix; verification step asserts
  `pytest --collect-only -q | grep -c "tests/perf/"` = 0.
- **[R3] 28-file STEADY run duration** → may exceed 001's
  120s subprocess timeout. Mitigated: harness supports
  `--timeout-per-run <seconds>` (default 600s).
- **[R4] Bucket-C `test_sqlite_store` disk I/O** → may
  dominate RAMP/BURST timings and confound the warmup
  signal. Mitigated: flagged in `design.md` as a known
  confounding factor; no in-change mitigation (would
  require isolation which is a future change).
- **[R5] Authorization rotation** → only governance file
  this change writes. Mitigated: rotation is reversible
  (old block kept as a comment header in
  `current-state.md`); 001 freeze contract enforced by
  harness guardrail.

## Rollback

1. Revert `docs/00-project/current-state.md` to its
   pre-rotation `REMEDIATION_V060` block (preserved in the
   comment header).
2. Delete `tests/perf/` and `outputs/reports/v0.6.0-campaign-002/`.
3. Delete the OpenSpec change folder
   `openspec/changes/extract-perf-harness-and-run-campaign-002/`.
4. No migration of Campaign-002 evidence is needed
   (Campaign-002 is observation-only and produces no
   state that other parts of the project depend on).

## Consistency With Brainstorm

This proposal is consistent with `brainstorm.md` alternative
C (chosen) and explicitly rejects alternatives A, B, and D.
The deferred decomposition alternative (D) is preserved as a
future-change candidate in `brainstorm.md`.
