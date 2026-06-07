# performance-campaign-harness Specification

## Purpose
Define the reusable performance-campaign harness under
`tests/perf/`, its data model, profile structure, gate
evaluation, and the 001 freeze contract guardrail.

## ADDED Requirements

### Requirement: Harness module structure
The system SHALL provide a `tests/perf/` package containing
six modules (`__init__.py`, `_types.py`, `_profiles.py`,
`_runner.py`, `_analytics.py`, `_artifacts.py`, `_main.py`),
each side-effect-free at import.

#### Scenario: Importing the harness is side-effect-free
- **WHEN** a user runs `uv run python -c "import tests.perf._types, tests.perf._profiles"`
- **THEN** the command SHALL exit 0 with no I/O performed

#### Scenario: Harness modules are not collected by pytest
- **WHEN** a user runs `uv run pytest --collect-only -q | grep "tests/perf/"`
- **THEN** the command SHALL produce zero matches (the `_` prefix prevents pytest's default `test_*.py` / `*_test.py` collection pattern)

### Requirement: Profile definitions are parameterizable
The system SHALL expose `STEADY`, `SMALL_STEADY`, `RAMP`,
and `BURST` profile factories that take a list of test
files (or a buckets dict) and return a list of `RunSpec`
records (test_files, seed, base_work_units).

#### Scenario: STEADY profile produces 3 runs of the full file list
- **WHEN** a user calls `make_steady_profile(["a.py", "b.py", ...])`
- **THEN** the function SHALL return exactly 3 RunSpec records, each with the same full file list and seeds `42, 43, 44`

#### Scenario: SMALL_STEADY profile produces 3 runs of Bucket A only
- **WHEN** a user calls `make_small_steady_profile({"A": [8 files]})`
- **THEN** the function SHALL return exactly 3 RunSpec records, each running Bucket A's files with seeds `50, 51, 52`
- **AND** this profile SHALL be the warmup probe for G9-warmup-extractable (the full STEADY is preserved as a data point but masks the warmup signal at 28-file scale)

#### Scenario: RAMP profile produces a linear staircase
- **WHEN** a user calls `make_ramp_profile(buckets)` where buckets is `{"A": [8 files], "B": [10 files], "C": [5 files], "D": [4 files], "E": [1 file]}` (totals 28)
- **THEN** the function SHALL return exactly 3 RunSpec records with file counts `[8, 18, 28]` (linear +10/+10 staircase)

#### Scenario: BURST profile produces single-bucket runs
- **WHEN** a user calls `make_burst_profile(buckets)`
- **THEN** the function SHALL return 3 RunSpec records, each running a single bucket's files

### Requirement: Snapshot schema per run
The system SHALL emit exactly 3 snapshots per run with
phases `start`, `execution_complete`, `end` and timestamps
in non-decreasing order.

#### Scenario: A run produces start, execution_complete, and end snapshots
- **WHEN** a RunSpec is executed via `execute_run`
- **THEN** the returned RunRecord SHALL have exactly 3 Snapshot objects
- **AND** the snapshots SHALL have `phase` values `start`, `execution_complete`, `end` in that order
- **AND** their `timestamp` values SHALL be non-decreasing

#### Scenario: Snapshot event-specific fields are present
- **WHEN** a snapshot is inspected
- **THEN** the start snapshot SHALL carry `testFiles` and `testFileCount`
- **AND** the execution_complete snapshot SHALL carry `exitCode`, `durationMs`, `stdoutLineCount`, `stderrLineCount`
- **AND** the end snapshot SHALL carry `testsPassed`, `testsFailed`, `testsError`, `testsSkipped`, `totalTests`, `scenarioDurationMs`

### Requirement: G1–G6 gates are preserved from v0.6.0-remediation-campaign-001
The system SHALL evaluate G1 (profile coverage), G2 (run
count per profile >= 3), G3 (snapshot count per run >= 3),
G4 (timestamp order), G5 (runId consistency), and G6
(metadata completeness) with the same logic as the 001
harness.

#### Scenario: All three profiles are required
- **WHEN** `evaluate_gates` is called with all_runs missing one profile
- **THEN** G1 SHALL fail with evidence `{"profiles": [...]}` showing the missing profile

#### Scenario: Run count of 3 is the minimum
- **WHEN** a profile has only 2 runs
- **THEN** G2-run-count-<profile> SHALL fail with evidence `{"count": 2}`

### Requirement: 001 freeze contract guardrail
The system SHALL refuse to write artifacts to any output
directory matching the pattern `v0.6.0-remediation*`.

#### Scenario: Writing to a frozen directory is refused
- **WHEN** a user runs `python -m tests.perf._main --campaign campaign-002 --output-dir outputs/reports/v0.6.0-remediation/x`
- **THEN** the command SHALL exit with code 2
- **AND** a clear error message SHALL be written to stderr explaining the 001 freeze

#### Scenario: Writing to a fresh directory is allowed
- **WHEN** a user runs `python -m tests.perf._main --campaign campaign-002 --output-dir outputs/reports/v0.6.0-campaign-002/`
- **THEN** the command SHALL proceed with the campaign execution

### Requirement: CLI invocation contract
The system SHALL expose the harness as
`python -m tests.perf._main` with flags `--campaign <id>`,
`--output-dir <path>`, `--project-root <path>` (default
`cwd`), and `--timeout-per-run <seconds>` (default 600).

#### Scenario: Required flags are validated
- **WHEN** `python -m tests.perf._main` is invoked without `--campaign`
- **THEN** the command SHALL exit non-zero with a usage error

#### Scenario: Project root defaults to current working directory
- **WHEN** `python -m tests.perf._main --campaign campaign-002` is invoked without `--project-root`
- **THEN** the runner SHALL use `Path.cwd()` as the project root
