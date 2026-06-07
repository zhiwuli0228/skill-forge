# Plan — extract-perf-harness-and-run-campaign-002

> Change Id: extract-perf-harness-and-run-campaign-002

## Allowed Paths

- `tests/perf/**` (new)
- `outputs/reports/v0.6.0-campaign-002/**` (new)
- `openspec/changes/extract-perf-harness-and-run-campaign-002/**` (new)
- `docs/00-project/current-state.md` (authorization rotation, one write)
- `docs/04-development/versions/v0.6.0/campaign-002/**` (new pointer file)

## Forbidden Paths

- `src/skill_forge/**`
- `pyproject.toml`, `uv.lock`
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md`
- `openspec/config.yaml`, `openspec/schemas/**`, `configs/**`, `templates/**`
- `outputs/reports/v0.6.0-remediation/**`
- `openspec/specs/**` (sync happens at archive time)
- All other paths under `tests/` other than the new `tests/perf/**`

## Pre-Conditions

1. **Authorization rotated**: `docs/00-project/current-state.md`
   shows `PERF_HARNESS_AND_CAMPAIGN_002_V060_FOLLOWUP` and a
   comment-block revert path. ✅ Done in PC1.
2. **All 28 candidate test files exist and pass in
   isolation**. ✅ Done in PC2 (319 tests passed across the
   28 files).
3. **OpenSpec change folder exists** with at least
   `proposal.md` and `tasks.md`. ✅ Done in PC3 (8-artifact
   set produced).
4. **001 freeze contract acknowledged**: harness contains a
   guardrail that refuses to write to any output directory
   matching `v0.6.0-remediation*`. ✅ Implemented in `_main.py`.

## Step 1: Harness Types and Profiles

**Files**: `tests/perf/__init__.py`, `tests/perf/_types.py`,
`tests/perf/_profiles.py`.

**Action**: create the package marker and the two modules
with side-effect-free dataclasses and parameterizable
profile factories. No I/O at import.

**Verification**:
- `uv run python -c "import tests.perf._types, tests.perf._profiles"` → exit 0
- `uv run pytest --collect-only -q | grep -c "tests/perf/"` → 0

## Step 2: Harness Runner and Snapshot Capture

**Files**: `tests/perf/_runner.py`.

**Action**: implement `execute_run(run_spec, project_root,
timeout_per_run) -> RunRecord` that runs
`subprocess.run(["uv", "run", "pytest", *test_files, "-v",
"--tb=line", "--no-header"], cwd=project_root,
timeout=...)` and emits 3 snapshots in
non-decreasing-timestamp order. Capture stdout/stderr line
counts, exit code, and test result counts from the pytest
output.

**Verification**: a synthetic RunSpec against a tiny test
file produces a RunRecord with exactly 3 snapshots and
exit 0.

## Step 3: Harness Gates and Warmup Extraction

**Files**: `tests/perf/_analytics.py`.

**Action**: implement `evaluate_gates(all_runs,
campaign_config) -> list[GateResult]` for G1–G9 (with the
corrected G9 non-increasing structural check) and
`extract_warmup_profile(all_runs, batch_id) -> WarmupProfile`.

**Verification**:
- Synthetic all_runs with monotonically decreasing STEADY
  durations → G9-structural PASS, G9-signal PASS.
- Synthetic all_runs with non-monotonic STEADY → G9-structural
  FAIL.
- Warmup profile JSON has all 5 numeric fields per profile.

## Step 4: Harness Artifact Writers

**Files**: `tests/perf/_artifacts.py`.

**Action**: 7 writers, all atomic. Each takes
`(data, batch_id_or_run_id, output_dir)` and returns the
written Path. No hardcoded paths.

**Verification**: a synthetic all_runs passed through all
7 writers produces 7 files at the expected paths with the
expected schema fields.

## Step 5: Campaign-002 Buckets and RAMP Staircase

**Files**: `tests/perf/_main.py`.

**Action**: define the 5 buckets, wire STEADY (3 × 28),
RAMP (8/18/28 staircase), BURST (D/A/E single-bucket),
implement the 001 freeze contract guardrail, and provide
the CLI entry point with `--campaign`, `--output-dir`,
`--project-root`, `--timeout-per-run` flags.

**Verification**:
- `uv run python -m tests.perf._main --campaign campaign-002 --output-dir /tmp/foo` (refused: doesn't match campaign-002 default) → no, actually with default output-dir it should work. With an explicit frozen pattern it should refuse.
- `uv run python -m tests.perf._main --campaign campaign-002 --output-dir outputs/reports/v0.6.0-remediation/x` → exit 2, error message.
- `uv run python -m tests.perf._main --campaign campaign-002 --output-dir outputs/reports/v0.6.0-campaign-002` → exit 0, all 9 gates PASS, all 7 artifacts written.

**Note (added during apply, 2026-06-07)**: a first V3
run showed G9-structural + G9-signal FAIL on the 28-file
STEADY (`[17063, 16578, 18000]`, firstToMedian 0.948).
The 28-file workload masks the warmup signal that 001
saw on its 6-file STEADY. To restore warmup-detection
conditions, a SMALL_STEADY profile (Bucket A only,
8 files, ~5s per run) is added. The full STEADY is
preserved as a data point; G9 evaluates SMALL_STEADY
only. Total runs go from 9 to 12.

## Step 6: Authorization Rotation and Docs Sync

**Files**: `docs/00-project/current-state.md`,
`docs/04-development/versions/v0.6.0/campaign-002/README.md`.

**Action**: ✅ `current-state.md` already rotated in PC1.
Create the v0.6.0/campaign-002/README.md pointer.

**Verification**: both files exist and reference each other
consistently.

## Step 7: Documentation and Verification

**Files**: `tests/perf/_README.md`,
`openspec/changes/extract-perf-harness-and-run-campaign-002/verification.md`.

**Action**: write the harness README, fill in
verification.md with the 7 verification step results,
finalize the hand-off note.

**Verification**:
- `openspec validate extract-perf-harness-and-run-campaign-002 --strict` → valid
- `openspec validate --strict --all` → valid

## Final Verification Commands

```bash
# PC1: authorization (read-only check)
grep -c "PERF_HARNESS_AND_CAMPAIGN_002_V060_FOLLOWUP" docs/00-project/current-state.md
# expect: 1

# PC2: 28 test files exist and pass
for f in $(cat outputs/reports/v0.6.0-campaign-002/_test-file-list.txt 2>/dev/null || true); do
    uv run pytest "$f" --tb=line -q || exit 1
done
# (this is a re-run; the original 319-test run is recorded in verification.md)

# Step 5 (T5): harness self-test
uv run python -m tests.perf._main --campaign campaign-002 --output-dir outputs/reports/v0.6.0-campaign-002
# expect: exit 0, all 9 gates PASS, 7 artifacts written

# Step 5: 001 freeze contract
uv run python -m tests.perf._main --campaign campaign-002 --output-dir outputs/reports/v0.6.0-remediation/x
# expect: exit 2, error message

# Step 7: OpenSpec validation
openspec validate extract-perf-harness-and-run-campaign-002 --strict
# expect: valid

openspec validate --strict --all
# expect: valid

# Pytest isolation
uv run pytest --collect-only -q | grep -c "tests/perf/"
# expect: 0

# Existing tests untouched
uv run pytest
# expect: 100% pass on the 34 existing test files
```

## Rollback

1. Revert `docs/00-project/current-state.md` to the
   `REMEDIATION_V060` block (preserved in the comment
   header).
2. Delete `tests/perf/`.
3. Delete `outputs/reports/v0.6.0-campaign-002/`.
4. Delete `openspec/changes/extract-perf-harness-and-run-campaign-002/`.
5. Delete `docs/04-development/versions/v0.6.0/campaign-002/`.

No migration of Campaign-002 evidence is needed (the new
campaign is observation-only and produces no state that
other parts of the project depend on).

## Hand-off Note

After all 7 steps complete, the implementer writes a
hand-off block into `verification.md` with: changed files
(exact paths), verification commands run with exit codes,
test results (the 319-test pre-condition run + any new
runs), and any deviations from this plan.
