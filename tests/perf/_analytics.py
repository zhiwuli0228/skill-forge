"""Gate evaluation (G1–G9) and warmup-profile extraction.

G1–G6 are preserved verbatim from the 001 harness
(``outputs/reports/v0.6.0-remediation/_run_experiments.py``).
G7–G9 are new for Campaign-002.

G9-warmup-extractable is two-tier:
  - Structural: SMALL_STEADY duration series is **non-increasing**
    (must pass for any verdict). SMALL_STEADY is the 3 ×
    Bucket A run profile; the full STEADY (28 files) masks
    the warmup signal that 001's 6-file STEADY detected.
  - Signal: ``warmupRatio.firstToMedian >= 1.1``
    (must pass for ``READY``; otherwise ``READY_WITH_RISK``)
"""

from __future__ import annotations

from statistics import median

from ._types import GateResult, RunRecord, WarmupProfile


REQUIRED_METADATA_FIELDS: tuple[str, ...] = (
    "run_id",
    "scenario_profile",
    "seed",
    "step_count",
    "base_work_units",
    "baseline_policy_id",
    "core_pool_size",
    "maximum_pool_size",
    "queue_capacity",
    "command_line",
    "start_time",
    "end_time",
    "exit_code",
)


def evaluate_gates(
    all_runs: list[RunRecord],
    campaign_config: dict,
) -> list[GateResult]:
    """Evaluate G1–G9 against a list of RunRecords.

    ``campaign_config`` carries the bucket layout
    (``{"buckets": {"A": [...], "B": [...], ...}}``) and the
    expected coverage count.
    """
    results: list[GateResult] = []

    required_profiles = {"STEADY", "SMALL_STEADY", "RAMP", "BURST"}
    profiles_present = {r.scenario_profile for r in all_runs}
    results.append(
        GateResult(
            gate_id="G1-profile-coverage",
            description="All four profiles (STEADY, SMALL_STEADY, RAMP, BURST) present",
            passed=required_profiles.issubset(profiles_present),
            evidence={
                "present": sorted(profiles_present),
                "required": sorted(required_profiles),
            },
        )
    )

    for profile in ("STEADY", "SMALL_STEADY", "RAMP", "BURST"):
        n = sum(1 for r in all_runs if r.scenario_profile == profile)
        results.append(
            GateResult(
                gate_id=f"G2-run-count-{profile}",
                description=f"At least 3 runs for {profile}",
                passed=n >= 3,
                evidence={"count": n},
            )
        )

    for r in all_runs:
        n_snapshots = len(r.snapshots)
        results.append(
            GateResult(
                gate_id=f"G3-snapshot-count-{r.run_id}",
                description=f"Run {r.run_id} has >= 3 snapshots",
                passed=n_snapshots >= 3,
                evidence={"snapshotCount": n_snapshots},
            )
        )
        timestamps = [s.timestamp for s in r.snapshots]
        non_decreasing = all(
            timestamps[i] <= timestamps[i + 1] for i in range(len(timestamps) - 1)
        )
        results.append(
            GateResult(
                gate_id=f"G4-timestamp-order-{r.run_id}",
                description=f"Run {r.run_id} timestamps are non-decreasing",
                passed=non_decreasing,
                evidence={"timestamps": timestamps},
            )
        )
        run_ids = {s.run_id for s in r.snapshots}
        results.append(
            GateResult(
                gate_id=f"G5-runid-consistency-{r.run_id}",
                description=f"Run {r.run_id} snapshots share runId",
                passed=len(run_ids) == 1,
                evidence={"uniqueRunIds": sorted(run_ids)},
            )
        )
        missing = [f for f in REQUIRED_METADATA_FIELDS if getattr(r, f, None) is None]
        results.append(
            GateResult(
                gate_id=f"G6-metadata-{r.run_id}",
                description=f"Run {r.run_id} has complete metadata",
                passed=len(missing) == 0,
                evidence={"missing": missing},
            )
        )

    covered = {f for r in all_runs for f in r.test_files}
    expected_min = campaign_config.get("expected_min_coverage", 28)
    results.append(
        GateResult(
            gate_id="G7-coverage-expansion",
            description=f"At least {expected_min} unique test files covered",
            passed=len(covered) >= expected_min,
            evidence={"coveredCount": len(covered), "expectedMin": expected_min},
        )
    )

    buckets = campaign_config.get("buckets", {})
    seen_buckets: set[str] = set()
    for bucket_name, fs in buckets.items():
        if any(f in covered for f in fs):
            seen_buckets.add(bucket_name)
    results.append(
        GateResult(
            gate_id="G8-bucket-coverage",
            description="All buckets appear in at least one run",
            passed=seen_buckets == set(buckets.keys()),
            evidence={
                "seenBuckets": sorted(seen_buckets),
                "expectedBuckets": sorted(buckets.keys()),
            },
        )
    )

    steady_runs = sorted(
        [r for r in all_runs if r.scenario_profile == "SMALL_STEADY"],
        key=lambda r: r.start_time,
    )
    durations = [r.duration_ms for r in steady_runs]
    if len(durations) >= 3:
        non_increasing = all(
            durations[i] >= durations[i + 1] for i in range(len(durations) - 1)
        )
        results.append(
            GateResult(
                gate_id="G9-warmup-extractable-structural",
                description="SMALL_STEADY duration series is non-increasing",
                passed=non_increasing,
                evidence={"durations": durations},
            )
        )
        d0 = durations[0]
        rest = durations[1:]
        d_median_rest = float(median(rest)) if rest else 0.0
        ratio = (d0 / d_median_rest) if d_median_rest > 0 else 0.0
        results.append(
            GateResult(
                gate_id="G9-warmup-extractable-signal",
                description="firstToMedian ratio >= 1.1 (>=10% warmup)",
                passed=ratio >= 1.1,
                evidence={
                    "ratio": ratio,
                    "d0": d0,
                    "medianRest": d_median_rest,
                },
            )
        )
    else:
        results.append(
            GateResult(
                gate_id="G9-warmup-extractable-structural",
                description="SMALL_STEADY has >= 3 runs (required for warmup analysis)",
                passed=False,
                evidence={"durations": durations},
            )
        )
        results.append(
            GateResult(
                gate_id="G9-warmup-extractable-signal",
                description="firstToMedian ratio (skipped: structural failed)",
                passed=False,
                evidence={"reason": "structural check failed; signal not evaluated"},
            )
        )

    return results


def derive_verdict(gate_results: list[GateResult]) -> tuple[str, str]:
    """Map G1–G9 outcomes to a verdict label.

    - All G1–G9 PASS → READY
    - All G1–G8 PASS, G9-signal FAIL → READY_WITH_RISK
    - Any G1–G8 FAIL → NOT_READY
    """
    by_id = {g.gate_id: g for g in gate_results}

    g1_g8_failed = [
        gid
        for gid in (
            "G1-profile-coverage",
            "G7-coverage-expansion",
            "G8-bucket-coverage",
        )
        if by_id.get(gid) is not None and not by_id[gid].passed
    ]
    for g in gate_results:
        if g.gate_id.startswith(("G2-", "G3-", "G4-", "G5-", "G6-")) and not g.passed:
            g1_g8_failed.append(g.gate_id)

    if g1_g8_failed:
        return "NOT_READY", f"failing G1-G8 gates: {g1_g8_failed}"

    structural = by_id.get("G9-warmup-extractable-structural")
    signal = by_id.get("G9-warmup-extractable-signal")

    if structural is not None and not structural.passed:
        return "NOT_READY", "G9 structural check failed"

    if signal is not None and not signal.passed:
        return "READY_WITH_RISK", "warmup not detectable in 3 runs"

    return "READY", "all G1-G9 passed"


def extract_warmup_profile(
    all_runs: list[RunRecord],
    batch_id: str,
) -> WarmupProfile:
    """Compute per-profile warmup metrics.

    For each profile with >= 3 runs, reports:
      - warmupRatio.{firstToLast, firstToMean, firstToMedian}
      - convergenceDeltaMs
      - convergenceRatePct
      - runs (one entry per run with runId, durationMs, exitCode)

    Profiles with < 3 runs are omitted. The median-of-rest is
    the most outlier-robust ratio with n=3, so it drives the
    G9 verdict.
    """
    per_profile: dict[str, dict] = {}
    for profile_name in ("STEADY", "SMALL_STEADY", "RAMP", "BURST"):
        profile_runs = sorted(
            [r for r in all_runs if r.scenario_profile == profile_name],
            key=lambda r: r.start_time,
        )
        if len(profile_runs) < 3:
            continue
        d0 = profile_runs[0].duration_ms
        d_last = profile_runs[-1].duration_ms
        rest = [r.duration_ms for r in profile_runs[1:]]
        d_mean_rest = sum(rest) / len(rest) if rest else 0.0
        d_median_rest = float(median(rest)) if rest else 0.0
        per_profile[profile_name] = {
            "warmupRatio": {
                "firstToLast": (d0 / d_last) if d_last > 0 else 0.0,
                "firstToMean": (d0 / d_mean_rest) if d_mean_rest > 0 else 0.0,
                "firstToMedian": (d0 / d_median_rest) if d_median_rest > 0 else 0.0,
            },
            "convergenceDeltaMs": d0 - d_last,
            "convergenceRatePct": ((d0 - d_last) / d0) * 100 if d0 > 0 else 0.0,
            "runs": [
                {
                    "runId": r.run_id,
                    "durationMs": r.duration_ms,
                    "exitCode": r.exit_code,
                }
                for r in profile_runs
            ],
        }
    return WarmupProfile(batch_id=batch_id, per_profile=per_profile)
