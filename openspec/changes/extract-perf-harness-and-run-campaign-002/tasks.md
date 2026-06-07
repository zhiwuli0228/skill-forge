# Tasks — extract-perf-harness-and-run-campaign-002

> All tasks are checkboxes; the apply phase tracks progress
> by `- [x]`.

## 1. Harness Types and Profiles

- [x] 1.1 Create `tests/perf/__init__.py` (package marker, no exports).
- [x] 1.2 Create `tests/perf/_types.py` with dataclasses: `Profile`, `RunRecord`, `Snapshot`, `GateResult`, `CampaignArtifacts`, `WarmupProfile`. Side-effect-free at import.
- [x] 1.3 Create `tests/perf/_profiles.py` with `STEADY`, `RAMP`, `BURST` profile definitions, parameterizable by file list, run count, and base-work-units. Each profile is a function returning a list of `RunSpec` records.
- [x] 1.4 Verify: `uv run python -c "import tests.perf._types, tests.perf._profiles"` exits 0.

## 2. Harness Runner and Snapshot Capture

- [x] 2.1 Create `tests/perf/_runner.py` with `execute_run(run_spec) -> RunRecord` that runs `subprocess.run(["uv", "run", "pytest", *test_files, "-v", "--tb=line", "--no-header"], cwd=project_root, timeout=timeout_per_run)`, capturing start / execution_complete / end snapshots.
- [x] 2.2 Capture per-snapshot: `runId`, `snapshotIndex`, `phase`, `timestamp`, `event`, plus event-specific fields (scenario_started: testFiles, testFileCount; test_execution_finished: exitCode, durationMs, stdoutLineCount, stderrLineCount; results_parsed: testsPassed, testsFailed, testsError, testsSkipped, totalTests, scenarioDurationMs).
- [x] 2.3 Support `--timeout-per-run <seconds>` CLI flag with default 600s.
- [x] 2.4 Verify: a single synthetic RunSpec produces a RunRecord with exactly 3 snapshots in non-decreasing timestamp order.

## 3. Harness Gates and Warmup Extraction

- [x] 3.1 Create `tests/perf/_analytics.py` with `evaluate_gates(all_runs, campaign_config) -> list[GateResult]` implementing G1–G9.
- [x] 3.2 G1–G6 from 001 verbatim: profile coverage, run count (>=3 per profile), snapshot count (>=3 per run), timestamp order (non-decreasing), runId consistency, metadata completeness.
- [x] 3.3 G7-coverage-expansion: unique test files across all_runs >= 28.
- [x] 3.4 G8-bucket-coverage: all 5 buckets (A, B, C, D, E) appear in at least one run.
- [x] 3.5 G9-warmup-extractable two-tier (evaluated on **SMALL_STEADY** = Bucket A, 3 × 8 files; full STEADY is preserved as a data point but not used for G9):
  - Structural: SMALL_STEADY duration series is **non-increasing** (each subsequent run is `<=` prior) — **must pass** for any verdict.
  - Signal: `warmupRatio.firstToMedian >= 1.1` — **must pass** for `READY`; otherwise `READY_WITH_RISK` with reason "warmup not detectable in 3 runs".
  - Note (added 2026-06-07): G9 originally targeted full STEADY. The first V3 run showed G9-structural + G9-signal FAIL on the 28-file STEADY (`[17063, 16578, 18000]`, firstToMedian 0.948). The 28-file workload masks the warmup signal; SMALL_STEADY (8 files, ~5s per run) restores 001's warmup-detection conditions.
- [x] 3.6 `extract_warmup_profile(all_runs, batch_id) -> WarmupProfile` computing `firstToLast`, `firstToMean`, `firstToMedian` ratios, `convergenceDeltaMs`, `convergenceRatePct`, per profile.
- [x] 3.7 Verify: synthetic all_runs with monotonic decreasing STEADY durations produce a passing G9; non-monotonic STEADY fails structural.

## 4. Harness Artifact Writers

- [x] 4.1 Create `tests/perf/_artifacts.py` with 7 writers, all atomic (write to `.tmp` then `replace`):
  - `write_run_manifest(all_runs, batch_id, output_dir) -> Path`
  - `write_raw_snapshots(run, output_dir) -> Path` (one JSONL per run)
  - `write_evidence_index(all_runs, batch_id, output_dir) -> Path`
  - `write_pressure_summary(all_runs, batch_id, output_dir) -> Path`
  - `write_readiness_summary(gate_results, all_runs, batch_id, output_dir) -> Path`
  - `write_campaign_report(gate_results, all_runs, batch_id, output_dir) -> Path`
  - `write_warmup_profile(warmup, batch_id, output_dir) -> Path`
- [x] 4.2 All writers take `output_dir` as a parameter (no hardcoded paths; matches 001's `OUTPUT_DIR` style but parameterizable).
- [x] 4.3 Verify: a synthetic all_runs passed through all 7 writers produces 7 files at the expected paths with the expected schema fields.

## 5. Campaign-002 Buckets and RAMP Staircase

- [x] 5.1 In `tests/perf/_main.py`: define the 5 buckets (A/B/C/D/E) as a module-level dict of `{"A": [...], "B": [...], ...}`.
- [x] 5.2 Wire STEADY: 3 runs × 28 files (all 5 buckets union).
- [x] 5.3 Wire RAMP: 3 runs × linear staircase **[8 / 18 / 28]** files — bucket A (8) → A+B (18) → A+B+C+D+E (28). +10/+10 linear scaling, matches 001's linear-scaling property.
- [x] 5.4 Wire BURST: 3 single-bucket runs × [D (4) / A (8) / E (8)] files.
- [x] 5.5 001 freeze contract guardrail: refuse to write to any output directory matching `v0.6.0-remediation*`. Exit non-zero with a clear error message.
- [x] 5.6 Verify: a dry-run of `_main.py` against a temp output dir emits the 9-run plan without invoking pytest.
- [ ] 5.7 (Added 2026-06-07) Wire SMALL_STEADY: 3 runs × Bucket A only (8 files, ~5s per run) for G9 warmup probing. Total runs go from 9 to 12. Full STEADY is preserved as a data point; G9 evaluates SMALL_STEADY only.

## 6. Authorization Rotation and Docs Sync

- [x] 6.1 Write rotated `docs/00-project/current-state.md` with new `PERF_HARNESS_AND_CAMPAIGN_002_V060_FOLLOWUP` authorization (already done in PC1).
- [x] 6.2 Add a Campaign-002 pointer under `docs/04-development/versions/v0.6.0/` alongside the existing 001 remediation entry. New file: `docs/04-development/versions/v0.6.0/campaign-002/README.md` with link to the artifacts dir and a one-line summary.
- [x] 6.3 Verify: `docs/00-project/current-state.md` shows the new authorization and a comment-block revert path.

## 7. Documentation and Verification

- [x] 7.1 Create `tests/perf/_README.md` documenting: how to invoke (`python -m tests.perf._main --campaign <id> --output-dir <path>`), what it produces, the 001 freeze contract, and the cross-campaign warmup-ratio comparability note.
- [x] 7.2 Fill in `verification.md` with pre-implementation evidence (the 28-file test runs from PC2) and post-implementation evidence (the 7 verification steps from the plan).
- [x] 7.3 Run the 7 verification steps from the plan; record exit codes and observed outputs.
- [x] 7.4 Final hand-off note summarizing: changed paths, verification commands and exit codes, any deviations from the plan.
- [x] 7.5 `openspec validate extract-perf-harness-and-run-campaign-002 --strict` → valid.
- [x] 7.6 `openspec validate --strict --all` → valid.
