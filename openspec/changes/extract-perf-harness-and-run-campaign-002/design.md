# Design — extract-perf-harness-and-run-campaign-002

## Module Structure (6 modules)

```
tests/perf/
├── __init__.py
├── _types.py        # dataclasses: Profile, RunRecord, Snapshot, GateResult, CampaignArtifacts, WarmupProfile
├── _profiles.py     # STEADY / RAMP / BURST profile definitions (parameterizable)
├── _runner.py       # subprocess + 3-snapshot capture per run
├── _analytics.py    # G1–G9 gates + warmup-ratio extraction (one place for "compute from all_runs")
├── _artifacts.py    # writers: run-manifest, raw-snapshots, evidence-index, pressure-summary, readiness-summary, campaign-report, warmup-profile
└── _main.py         # entry point: `python -m tests.perf._main --campaign <id> --output-dir <path>`
```

The `_` prefix prevents pytest auto-collection. All modules
are side-effect-free at import. Verified by
`uv run pytest --collect-only -q | grep -c "tests/perf/"` = 0.

## Data Model (dataclasses in `_types.py`)

```python
@dataclass(frozen=True)
class Profile:
    name: str           # "STEADY" | "RAMP" | "BURST"
    run_count: int
    file_lists: list[list[str]]   # one list per run

@dataclass
class Snapshot:
    run_id: str
    snapshot_index: int
    phase: str          # "start" | "execution_complete" | "end"
    timestamp: str      # ISO 8601 with timezone
    event: str          # "scenario_started" | "test_execution_finished" | "results_parsed"
    fields: dict        # event-specific fields

@dataclass
class RunRecord:
    run_id: str
    scenario_profile: str
    seed: int
    step_count: int
    base_work_units: int
    baseline_policy_id: str       # "default-pytest"
    core_pool_size: int           # placeholder, 1 (matches 001)
    maximum_pool_size: int        # placeholder, 1 (matches 001)
    queue_capacity: int           # = step_count
    command_line: str
    start_time: str
    end_time: str
    duration_ms: float
    exit_code: int
    test_files: list[str]
    test_results: dict            # {passed, failed, errors, skipped, total}
    snapshots: list[Snapshot]

@dataclass
class GateResult:
    gate_id: str
    description: str
    passed: bool
    evidence: dict | str

@dataclass
class WarmupProfile:
    batch_id: str
    per_profile: dict[str, dict]  # {STEADY: {firstToLast, firstToMean, firstToMedian, convergenceDeltaMs, convergenceRatePct, runs}, ...}

@dataclass
class CampaignArtifacts:
    run_manifest_path: Path
    raw_snapshot_paths: list[Path]
    evidence_index_path: Path
    pressure_summary_path: Path
    readiness_summary_path: Path
    campaign_report_path: Path
    warmup_profile_path: Path
```

## Profile Definitions (in `_profiles.py`)

Four factory functions, each returning a list of `RunSpec`
records. RunSpec = `(test_files, seed, base_work_units)`.

```python
def make_steady_profile(all_files: list[str]) -> list[RunSpec]:
    return [(all_files, 42 + i, len(all_files)) for i in range(3)]

def make_small_steady_profile(buckets: dict[str, list[str]]) -> list[RunSpec]:
    """SMALL_STEADY: 3 runs of Bucket A only (~5s each).

    This profile is the warmup probe for G9. The full STEADY
    (28 files, ~17s per run) masks the warmup signal because
    process-startup and IO-warmup costs are dominated by test
    execution. SMALL_STEADY reproduces 001's warmup-detection
    conditions (small workload, dominated by startup costs).
    """
    a = buckets["A"]
    return [(a, 50 + i, len(a)) for i in range(3)]

def make_ramp_profile(buckets: dict[str, list[str]]) -> list[RunSpec]:
    a = buckets["A"]
    ab = a + buckets["B"]
    full = a + buckets["B"] + buckets["C"] + buckets["D"] + buckets["E"]
    return [(a, 100, len(a)), (ab, 101, len(ab)), (full, 102, len(full))]

def make_burst_profile(buckets: dict[str, list[str]]) -> list[RunSpec]:
    return [
        (buckets["D"], 200, len(buckets["D"])),
        (buckets["A"], 201, len(buckets["A"])),
        (buckets["E"], 202, len(buckets["E"])),
    ]
```

RAMP staircase is **8 → 18 → 28** files (linear +10/+10),
matching 001's linear-scaling property (001 was 2 → 4 → 6,
+2/+2).

G9-warmup-extractable evaluates **SMALL_STEADY** (Bucket A,
3 × 8 files), not the full STEADY. The full STEADY is
preserved as a data point and its durations still appear in
`warmup-profile-002.json` and the campaign report, but the
warmup-extractable gate is computed on SMALL_STEADY.

## Bucket Design (in `_main.py`)

```python
BUCKETS = {
    "A": [  # collection + lifecycle, 8 files
        "tests/test_lifecycle.py",
        "tests/test_lifecycle_recommendation.py",
        "tests/test_lifecycle_recommendation_rules.py",
        "tests/test_collection_cli.py",
        "tests/test_collection_reuse.py",
        "tests/test_collection_scoring.py",
        "tests/test_collection_search.py",
        "tests/test_collection_store.py",
    ],
    "B": [  # retrieval + semantic + search, 3 files
        "tests/test_search_retrieval.py",
        "tests/test_semantic_retrieval.py",
        "tests/test_research_update.py",
    ],
    "C": [  # adoption + experience + promotion + community, 5 files
        "tests/test_skill_adoption.py",
        "tests/test_experience.py",
        "tests/test_promotion.py",
        "tests/test_community_skill_discovery.py",
        "tests/test_sqlite_store.py",
    ],
    "D": [  # generation + library + upgrade + evals, 4 files
        "tests/test_skill_generator.py",
        "tests/test_skill_library.py",
        "tests/test_skill_upgrade.py",
        "tests/test_skill_evals.py",
    ],
    "E": [  # cli + drafts + wizard + project_context + governance + installer + llm + quality, 8 files
        "tests/test_cli.py",
        "tests/test_drafts.py",
        "tests/test_wizard.py",
        "tests/test_project_context.py",
        "tests/test_governance_check.py",
        "tests/test_installer.py",
        "tests/test_llm_refiner.py",
        "tests/test_generation_quality_report.py",
    ],
}
```

## Warmup Metric (in `_analytics.py`)

For each profile with `>= 3` runs in duration order:

```python
def extract_warmup_profile(runs: list[RunRecord], batch_id: str) -> WarmupProfile:
    per_profile = {}
    for profile_name in ("STEADY", "RAMP", "BURST"):
        profile_runs = [r for r in runs if r.scenario_profile == profile_name]
        if len(profile_runs) < 3:
            continue
        profile_runs.sort(key=lambda r: r.start_time)
        d0 = profile_runs[0].duration_ms
        d_last = profile_runs[-1].duration_ms
        rest = [r.duration_ms for r in profile_runs[1:]]
        d_mean_rest = sum(rest) / len(rest)
        d_median_rest = sorted(rest)[len(rest) // 2]  # with 2 elements, the upper middle
        per_profile[profile_name] = {
            "warmupRatio": {
                "firstToLast": d0 / d_last if d_last > 0 else 0.0,
                "firstToMean": d0 / d_mean_rest if d_mean_rest > 0 else 0.0,
                "firstToMedian": d0 / d_median_rest if d_median_rest > 0 else 0.0,
            },
            "convergenceDeltaMs": d0 - d_last,
            "convergenceRatePct": ((d0 - d_last) / d0) * 100 if d0 > 0 else 0.0,
            "runs": [
                {"runId": r.run_id, "durationMs": r.duration_ms, "exitCode": r.exit_code}
                for r in profile_runs
            ],
        }
    return WarmupProfile(batch_id=batch_id, per_profile=per_profile)
```

**Cross-campaign comparability**: ratios are
cross-campaign-comparable; absolute ms are not (002's
larger workload produces larger absolute numbers than 001's).
Documented in the warmup-profile JSON via a `notes` field
and in the schema description in the spec.

## Gate Logic (in `_analytics.py`)

```python
def evaluate_gates(all_runs, campaign_config) -> list[GateResult]:
    results = []

    # G1: profile coverage
    profiles_present = {r.scenario_profile for r in all_runs}
    results.append(GateResult(
        "G1-profile-coverage",
        "All three profiles (STEADY, RAMP, BURST) present",
        profiles_present == {"STEADY", "RAMP", "BURST"},
        {"profiles": sorted(profiles_present)},
    ))

    # G2: run count per profile (>= 3)
    for profile in ("STEADY", "RAMP", "BURST"):
        n = sum(1 for r in all_runs if r.scenario_profile == profile)
        results.append(GateResult(
            f"G2-run-count-{profile}",
            f"At least 3 runs for {profile}",
            n >= 3,
            {"count": n},
        ))

    # G3-G6: per-run checks
    for r in all_runs:
        n_snapshots = len(r.snapshots)
        results.append(GateResult(
            f"G3-snapshot-count-{r.run_id}",
            f"Run {r.run_id} has >= 3 snapshots",
            n_snapshots >= 3,
            {"snapshotCount": n_snapshots},
        ))
        timestamps = [s.timestamp for s in r.snapshots]
        non_decreasing = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
        results.append(GateResult(
            f"G4-timestamp-order-{r.run_id}",
            f"Run {r.run_id} timestamps are non-decreasing",
            non_decreasing,
            {"timestamps": timestamps},
        ))
        run_ids = {s.run_id for s in r.snapshots}
        results.append(GateResult(
            f"G5-runid-consistency-{r.run_id}",
            f"Run {r.run_id} snapshots share runId",
            len(run_ids) == 1,
            {"uniqueRunIds": sorted(run_ids)},
        ))
        required = ["runId", "scenarioProfile", "seed", "stepCount",
                    "baseWorkUnits", "baselinePolicyId", "corePoolSize",
                    "maximumPoolSize", "queueCapacity", "commandLine",
                    "environmentSummary"]
        # metadata completeness check (project_root etc. injected from
        # CampaignConfig at runtime; here we check the run record fields)
        missing = [f for f in ("runId", "scenarioProfile", "seed",
                                "stepCount", "baseWorkUnits", "commandLine",
                                "startTime", "endTime", "exitCode")
                   if getattr(r, _to_snake(f), None) is None]
        results.append(GateResult(
            f"G6-metadata-{r.run_id}",
            f"Run {r.run_id} has complete metadata",
            len(missing) == 0,
            {"missing": missing},
        ))

    # G7: coverage expansion
    covered = {f for r in all_runs for f in r.test_files}
    results.append(GateResult(
        "G7-coverage-expansion",
        f"At least 28 unique test files covered",
        len(covered) >= 28,
        {"coveredCount": len(covered), "expectedMin": 28},
    ))

    # G8: bucket coverage
    bucket_files = {f for fs in campaign_config["buckets"].values() for f in fs}
    seen_buckets = set()
    for bucket_name, fs in campaign_config["buckets"].items():
        if any(f in covered for f in fs):
            seen_buckets.add(bucket_name)
    results.append(GateResult(
        "G8-bucket-coverage",
        "All 5 buckets (A, B, C, D, E) appear in at least one run",
        seen_buckets == {"A", "B", "C", "D", "E"},
        {"seenBuckets": sorted(seen_buckets)},
    ))

    # G9: warmup extractable (two-tier)
    steady_runs = sorted(
        [r for r in all_runs if r.scenario_profile == "STEADY"],
        key=lambda r: r.start_time,
    )
    durations = [r.duration_ms for r in steady_runs]
    if len(durations) >= 3:
        # Structural: non-increasing
        non_increasing = all(durations[i] >= durations[i+1] for i in range(len(durations)-1))
        results.append(GateResult(
            "G9-warmup-extractable-structural",
            "STEADY duration series is non-increasing",
            non_increasing,
            {"durations": durations},
        ))
        # Signal: firstToMedian ratio >= 1.1
        d0 = durations[0]
        rest = durations[1:]
        d_median_rest = sorted(rest)[len(rest) // 2]
        ratio = d0 / d_median_rest if d_median_rest > 0 else 0.0
        results.append(GateResult(
            "G9-warmup-extractable-signal",
            f"firstToMedian ratio >= 1.1 (>=10% warmup)",
            ratio >= 1.1,
            {"ratio": ratio, "d0": d0, "medianRest": d_median_rest},
        ))
    else:
        results.append(GateResult(
            "G9-warmup-extractable-structural",
            "STEADY has >= 3 runs (required for warmup analysis)",
            False,
            {"durations": durations},
        ))

    return results
```

## 001 Freeze Contract (in `_main.py`)

```python
import re
import sys

FROZEN_DIR_PATTERN = re.compile(r"v0\.6\.0-remediation")

def assert_not_frozen(output_dir: Path) -> None:
    """001's artifacts are frozen historical data. Refuse to overwrite."""
    if FROZEN_DIR_PATTERN.search(str(output_dir)):
        sys.stderr.write(
            f"REFUSED: output dir '{output_dir}' matches the 001 "
            f"frozen pattern 'v0.6.0-remediation*'. "
            f"Use a different --output-dir (e.g., "
            f"outputs/reports/v0.6.0-campaign-002/).\n"
        )
        sys.exit(2)
```

The pattern matches the substring `v0.6.0-remediation` in
any output dir path, so `--output-dir
outputs/reports/v0.6.0-remediation/anything` is rejected
with exit 2.

## Confounding Factors (flagged, not mitigated)

- **Bucket-C `test_sqlite_store`** is disk I/O-heavy and may
  dominate RAMP/BURST timings. The warmup ratio is robust
  to this (ratios normalize absolute differences), but the
  absolute ms in `warmup-profile-002.json` will reflect
  Bucket-C's contribution.
- **28-file STEADY run** is ~7x larger than 001's 2-file
  STEADY. Absolute convergence ms will be larger, ratios
  should be comparable.
- **`test_cli`** is an end-to-end smoke test that spawns
  subprocesses; its duration is sensitive to system state
  (network, IO, lock contention). Flagged in
  `pressure-summary-002.json` per-run exit codes.

## Test Collection Isolation

Pytest's default collection pattern is `test_*.py` and
`*_test.py`. The harness uses `_`-prefixed module names,
which match neither pattern, so pytest will not collect
them. Verification: `uv run pytest --collect-only -q | grep
-c "tests/perf/"` returns 0.

This is the simplest isolation strategy and avoids the
alternative of writing `tests/perf/conftest.py` with
`collect_ignore_glob` (which would itself be a test file
and would have to be guarded against collection).

## Artifacts Path Convention

All artifacts for Campaign-002 land under the user-supplied
`--output-dir`. Default if not supplied:
`outputs/reports/v0.6.0-campaign-002/`.

Naming:
- `run-manifest-<BATCH_ID>.json`
- `raw-snapshots-<runId>.jsonl` (one per run)
- `evidence-index-<BATCH_ID>.json`
- `pressure-summary-<BATCH_ID>.json`
- `readiness-summary-<BATCH_ID>.md`
- `campaign-report-<BATCH_ID>.md`
- `warmup-profile-<BATCH_ID>.json`

`BATCH_ID` defaults to `v0.6.0-campaign-002`.
