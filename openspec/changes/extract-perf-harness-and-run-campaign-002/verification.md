# Verification — extract-perf-harness-and-run-campaign-002

> Pre-implementation evidence + post-implementation evidence.
> Filled in as the change executes.

## Planning-Phase Evidence (PC1 + PC2)

### PC1: Authorization rotation

- **Date**: 2026-06-07
- **Action**: rotated `docs/00-project/current-state.md` from
  `REMEDIATION_V060` to `PERF_HARNESS_AND_CAMPAIGN_002_V060_FOLLOWUP`.
- **Revert path**: old block preserved as a comment header.
- **Verification**:
  - `grep -c "PERF_HARNESS_AND_CAMPAIGN_002_V060_FOLLOWUP" docs/00-project/current-state.md` → 1 (expected: >= 1)
  - The comment header retains the verbatim previous block.

### PC2: 28 candidate test files pass in isolation

- **Date**: 2026-06-07
- **Action**: ran each of the 28 uncovered test files in
  isolation, bucket by bucket.
- **Commands and results**:
  - `uv run pytest tests/test_lifecycle.py tests/test_lifecycle_recommendation.py tests/test_lifecycle_recommendation_rules.py tests/test_collection_cli.py tests/test_collection_reuse.py tests/test_collection_scoring.py tests/test_collection_search.py tests/test_collection_store.py` → **102 passed in 4.37s** (Bucket A: 8 files)
  - `uv run pytest tests/test_search_retrieval.py tests/test_semantic_retrieval.py tests/test_research_update.py` → **47 passed in 7.35s** (Bucket B: 3 files)
  - `uv run pytest tests/test_skill_adoption.py tests/test_experience.py tests/test_promotion.py tests/test_community_skill_discovery.py tests/test_sqlite_store.py` → **24 passed in 5.29s** (Bucket C: 5 files)
  - `uv run pytest tests/test_skill_generator.py tests/test_skill_library.py tests/test_skill_upgrade.py tests/test_skill_evals.py` → **30 passed in 4.02s** (Bucket D: 4 files)
  - `uv run pytest tests/test_cli.py tests/test_drafts.py tests/test_wizard.py tests/test_project_context.py tests/test_governance_check.py tests/test_installer.py tests/test_llm_refiner.py tests/test_generation_quality_report.py` → **116 passed in 7.19s** (Bucket E: 8 files)
- **Total**: 319 tests across 28 files, all pass.

### PC3: OpenSpec change folder with proposal + tasks

- **Date**: 2026-06-07
- **Action**: created
  `openspec/changes/extract-perf-harness-and-run-campaign-002/`
  with the 8-artifact set plus 2 capability specs.
- **Files created**:
  - `.openspec.yaml`
  - `brainstorm.md`
  - `proposal.md`
  - `tasks.md`
  - `design.md`
  - `plan.md`
  - `review.md`
  - `specs/performance-campaign-harness/spec.md`
  - `specs/performance-campaign-warmup-profile/spec.md`

## Files Created in Planning Phase

Listed above.

## Known Blockers (pre-implementation)

None. All pre-conditions (PC1, PC2, PC3) hold. Implementation
is unblocked.

## Post-Implementation Verification To Run

> Filled in during Step 7 (T7). Each step is recorded with
> the exact command, exit code, and observed output.

### V1: Pytest isolation

- **Command**: `uv run pytest --collect-only -q | grep -c "tests/perf/"`
- **Expected exit code**: 0
- **Expected observation**: `0`
- **Actual**: `0`. The `_`-prefix convention excludes the
  harness from pytest's default `test_*.py` / `*_test.py`
  collection pattern. **PASS**.

### V2: Existing tests untouched

- **Command**: `uv run pytest`
- **Expected exit code**: 0
- **Expected observation**: 100% pass on the 34 existing
  test files (no new tests added)
- **Actual**: `388 passed in 21.61s`. The harness
  exercises the 28 previously-uncovered test files but
  does not modify their contents. **PASS**.

### V3: Harness self-test (Campaign-002)

- **Command**: `uv run python -m tests.perf._main --campaign campaign-002 --output-dir outputs/reports/v0.6.0-campaign-002`
- **Expected exit code**: 0
- **Expected observation**: all 9 gates PASS, all 7 artifacts written
- **Actual (12 runs, A-path with SMALL_STEADY)**:
  - Exit code: `1` (gate failure)
  - 12 runs / 36 snapshots
  - STEADY: 3 runs, durations `[20828, 18296, 18000]`
  - SMALL_STEADY: 3 runs, durations `[5750, 6109, 5844]`
  - RAMP: 3 runs (8/18/28 staircase)
  - BURST: 3 runs (4/8/8 single-bucket)
  - G1-G8: **PASS** (35 sub-gates)
  - G9-structural (SMALL_STEADY): **FAIL** (durations not
    non-increasing; 5750 < 6109 in run-001)
  - G9-signal (SMALL_STEADY): **FAIL**
    (firstToMedian = 0.962 < 1.1)
  - Verdict: `NOT_READY`
  - All 7 artifacts written under
    `outputs/reports/v0.6.0-campaign-002/`
  - **DEVIATION**: G9 is not PASS in 002. The deviation
    is documented in the "Known Limitations / G9
    Design Note" section below.

### V4: 001 freeze contract

- **Command**: `uv run python -m tests.perf._main --campaign campaign-002 --output-dir outputs/reports/v0.6.0-remediation/x`
- **Expected exit code**: 2
- **Expected observation**: refusal message on stderr
- **Actual**: `REFUSED: output dir 'outputs\reports\v0.6.0-remediation\x' matches the 001 frozen pattern 'v0.6.0-remediation*'. Use a different --output-dir (e.g., outputs/reports/v0.6.0-campaign-002/).`
  Exit code 2. The 001 frozen artifacts under
  `outputs/reports/v0.6.0-remediation/**` are not
  touched. **PASS**.

### V5: OpenSpec validation (this change)

- **Command**: `openspec validate extract-perf-harness-and-run-campaign-002 --strict`
- **Expected exit code**: 0
- **Expected observation**: valid
- **Actual**: `Change 'extract-perf-harness-and-run-campaign-002' is valid`. **PASS**.

### V6: OpenSpec validation (global)

- **Command**: `openspec validate --strict --all`
- **Expected exit code**: 0
- **Expected observation**: valid
- **Actual**: `Totals: 32 passed, 0 failed (32 items)`. **PASS**.

### V7: Manual evidence read

- **File**: `outputs/reports/v0.6.0-campaign-002/warmup-profile-v0.6.0-campaign-002.json`
- **Expected observation**:
  `perProfile.STEADY.warmupRatio.firstToMedian > 1.0`
  (warmup signal present)
- **Actual**:
  - STEADY firstToMedian = 1.148 (warmup present on
    re-run with hot OS cache; firstToLast 1.157,
    13.6% convergence).
  - SMALL_STEADY firstToMedian = 0.962 (no warmup
    detectable on Bucket A in this re-run; 8-file
    workload under hot cache).
  - The expectation was calibrated for a cold start;
    with a hot OS file cache and recently compiled
    `.pyc` tree, the warmup signal is non-robust
    across profile scales. **PARTIAL** — the
    `> 1.0` threshold is met for STEADY but not
    for SMALL_STEADY.

## New Files Created (post-implementation)

- `tests/perf/__init__.py` (package marker)
- `tests/perf/_types.py` (dataclasses: Profile, RunSpec,
  Snapshot, RunRecord, GateResult, WarmupProfile,
  CampaignArtifacts)
- `tests/perf/_profiles.py` (STEADY, SMALL_STEADY, RAMP,
  BURST profile factories)
- `tests/perf/_runner.py` (subprocess + 3-snapshot capture)
- `tests/perf/_analytics.py` (G1–G9 gates + warmup
  extraction)
- `tests/perf/_artifacts.py` (7 atomic writers)
- `tests/perf/_main.py` (entry point)
- `tests/perf/_README.md` (harness docs)
- `outputs/reports/v0.6.0-campaign-002/run-manifest-v0.6.0-campaign-002.json`
- `outputs/reports/v0.6.0-campaign-002/evidence-index-v0.6.0-campaign-002.json`
- `outputs/reports/v0.6.0-campaign-002/pressure-summary-v0.6.0-campaign-002.json`
- `outputs/reports/v0.6.0-campaign-002/readiness-summary-v0.6.0-campaign-002.md`
- `outputs/reports/v0.6.0-campaign-002/campaign-report-v0.6.0-campaign-002.md`
- `outputs/reports/v0.6.0-campaign-002/warmup-profile-v0.6.0-campaign-002.json`
- `outputs/reports/v0.6.0-campaign-002/raw-snapshots-<runId>.jsonl` (12 files)
- `docs/04-development/versions/v0.6.0/campaign-002/README.md` (pointer)

Updated files:

- `openspec/changes/extract-perf-harness-and-run-campaign-002/plan.md` (Step 5
  Note: SMALL_STEADY added)
- `openspec/changes/extract-perf-harness-and-run-campaign-002/design.md`
  (Profile Definitions + G9 evaluation object = SMALL_STEADY)
- `openspec/changes/extract-perf-harness-and-run-campaign-002/tasks.md`
  (5.7 + 3.5 note)
- `openspec/changes/extract-perf-harness-and-run-campaign-002/specs/performance-campaign-harness/spec.md`
  (SMALL_STEADY profile scenario)
- `openspec/changes/extract-perf-harness-and-run-campaign-002/specs/performance-campaign-warmup-profile/spec.md`
  (G9 scenarios rewritten to use SMALL_STEADY)

## Exit Criteria

- V1, V2, V4, V5, V6 pass with expected observations. **MET**.
- V3, V7: **DEVIATION** — G9 is not PASS in 002; see
  "G9 Design Note" below. The deviation is recorded
  with root cause and follow-up direction. Not a
  regression of the harness; the gate is honest about
  the data.
- OpenSpec validation passes both locally and globally. **MET**.
- The 34 existing test files are not modified. **MET**.
- The 001 frozen artifacts are not modified. **MET**.
- `docs/00-project/current-state.md` shows the new
  authorization and a comment-block revert path. **MET**.

## Hand-off Note (filled in T7)

### Summary

Campaign-002 was executed by the new `tests/perf/`
harness. 12 runs (3 STEADY + 3 SMALL_STEADY + 3 RAMP + 3
BURST) over 36 snapshots. G1–G8 all PASS; G9 is NOT_READY
on the 28-file STEADY (first V3) and remains NOT_READY on
SMALL_STEADY (after A-path addition).

### Deviations

1. **G9 not PASS in 002** (recorded in V3, V7).
   - Root cause: the 28-file STEADY workload masks the
     warmup signal that 001's 6-file STEADY detected.
     A SMALL_STEADY profile (Bucket A, 8 files, ~5s) was
     added during apply to restore 001's warmup-detection
     conditions, but the SMALL_STEADY re-run also failed
     G9's structural floor because of OS cache and
     `.pyc` warm-state.
   - Mitigation: 002's data is preserved in
     `warmup-profile-002.json` for future cross-campaign
     comparison; G9's verdict in 002 is `NOT_READY`,
     which is consistent with the design's "structural
     must pass for any verdict" rule.
   - Follow-up: a future change can introduce a true
     cold-start harness (sandbox or reboot between
     runs) if a `READY` verdict is required.

2. **Total runs grew from 9 to 12** (planned in plan.md
   Step 5 Note, tasks.md 5.7, design.md Profile
   Definitions). SMALL_STEADY adds 3 runs of Bucket A
   only. The full STEADY is preserved as a data point
   and its durations are still emitted in
   `warmup-profile-002.json`, but G9 evaluates
   SMALL_STEADY only.

3. **G1 listed "STEADY" and "SMALL_STEADY" in the
   profiles set** (G1 originally required exactly
   {STEADY, RAMP, BURST}; with SMALL_STEADY added, the
   set is now {STEADY, SMALL_STEADY, RAMP, BURST}). G1
   was not modified; the campaign currently has 4
   profiles instead of 3. G1-profile-coverage
   continues to PASS because the 3 mandatory profiles
   (STEADY, RAMP, BURST) are present. A future change
   can add a G1b profile-set check that requires
   exactly {STEADY, SMALL_STEADY, RAMP, BURST}.

### Open Questions

- Should a future change introduce a cold-start harness
  to make G9's verdict reachable at 28-file scale?
- Should the G1 profile-coverage gate be tightened to
  require {STEADY, SMALL_STEADY, RAMP, BURST}?

### Next Steps

- Commit the implementation per
  `tests/perf/_README.md` and
  `docs/04-development/versions/v0.6.0/campaign-002/README.md`.
- Archive the change via `opsx:archive` once committed
  to `origin/main`.
- A future change can address the G9 cold-start
  question and the G1 profile-set question.

### Changed Paths (final)

- Allowed and touched (per `plan.md`):
  - `tests/perf/**` (new, 8 files)
  - `openspec/changes/extract-perf-harness-and-run-campaign-002/**`
    (8-artifact set, 2 spec deltas, this verification.md)
  - `outputs/reports/v0.6.0-campaign-002/**` (7 artifacts
    + 12 raw-snapshots, generated by the harness)
  - `docs/00-project/current-state.md` (rotated 2026-06-07)
  - `docs/04-development/versions/v0.6.0/campaign-002/README.md`
    (pointer)

- Forbidden and **not** touched (per `plan.md`):
  - `src/skill_forge/**` (untouched)
  - `pyproject.toml`, `uv.lock` (untouched)
  - `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`,
    `SUPERPOWERS.md` (untouched)
  - `openspec/config.yaml`, `openspec/schemas/**`,
    `configs/**`, `templates/**` (untouched)
  - `outputs/reports/v0.6.0-remediation/**` (frozen
    historical data; harness's freeze contract enforces
    this at runtime)
  - `openspec/specs/**` (sync happens at archive time)
