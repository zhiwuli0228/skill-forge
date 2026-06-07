"""Dataclasses for the performance-campaign harness.

Side-effect-free at import. No I/O, no logging configuration,
no global state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Profile:
    """A named profile (STEADY, SMALL_STEADY, RAMP, or BURST).

    Attributes:
        name: One of "STEADY", "SMALL_STEADY", "RAMP", "BURST".
        run_count: Number of runs the profile produces.
        file_lists: One test-file list per run.
    """

    name: str
    run_count: int
    file_lists: list[tuple[str, ...]]

    def __post_init__(self) -> None:
        if self.name not in {"STEADY", "SMALL_STEADY", "RAMP", "BURST"}:
            raise ValueError(
                f"Profile name must be STEADY/SMALL_STEADY/RAMP/BURST, got {self.name!r}"
            )
        if self.run_count != len(self.file_lists):
            raise ValueError(
                f"run_count ({self.run_count}) != len(file_lists) ({len(self.file_lists)})"
            )


@dataclass(frozen=True)
class RunSpec:
    """A single run specification: which files, which seed, how many work units."""

    test_files: tuple[str, ...]
    seed: int
    base_work_units: int


@dataclass
class Snapshot:
    """One of the three per-run snapshots.

    Attributes:
        run_id: Stable identifier for the run this snapshot belongs to.
        snapshot_index: 0, 1, or 2 (start, execution_complete, end).
        phase: "start" | "execution_complete" | "end".
        timestamp: ISO-8601 with timezone.
        event: "scenario_started" | "test_execution_finished" | "results_parsed".
        fields: Event-specific fields (testFiles, exitCode, testsPassed, etc.).
    """

    run_id: str
    snapshot_index: int
    phase: str
    timestamp: str
    event: str
    fields: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "snapshotIndex": self.snapshot_index,
            "phase": self.phase,
            "timestamp": self.timestamp,
            "event": self.event,
            **self.fields,
        }


@dataclass
class RunRecord:
    """A complete record of one campaign run.

    Mirrors the 001 harness's per-run dict schema. The
    ``corePoolSize`` / ``maximumPoolSize`` / ``queueCapacity``
    fields are placeholders (1 / 1 / step_count) because the
    001 v0.6.0 design surface is not exercised by this
    campaign. A future change will validate that surface.
    """

    run_id: str
    scenario_profile: str
    seed: int
    step_count: int
    base_work_units: int
    baseline_policy_id: str
    core_pool_size: int
    maximum_pool_size: int
    queue_capacity: int
    command_line: str
    start_time: str
    end_time: str
    duration_ms: float
    exit_code: int
    test_files: list[str]
    test_results: dict[str, int]
    snapshots: list[Snapshot]

    def to_manifest_entry(self, environment_summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "scenarioProfile": self.scenario_profile,
            "seed": self.seed,
            "stepCount": self.step_count,
            "baseWorkUnits": self.base_work_units,
            "baselinePolicyId": self.baseline_policy_id,
            "corePoolSize": self.core_pool_size,
            "maximumPoolSize": self.maximum_pool_size,
            "queueCapacity": self.queue_capacity,
            "commandLine": self.command_line,
            "environmentSummary": environment_summary,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "durationMs": self.duration_ms,
            "exitCode": self.exit_code,
            "testResults": self.test_results,
            "snapshotCount": len(self.snapshots),
        }


@dataclass
class GateResult:
    """Outcome of one P0 gate evaluation."""

    gate_id: str
    description: str
    passed: bool
    evidence: dict[str, Any] | str

    def to_dict(self) -> dict[str, Any]:
        return {
            "gateId": self.gate_id,
            "description": self.description,
            "passed": self.passed,
            "evidence": self.evidence,
        }


@dataclass
class WarmupProfile:
    """Per-profile warmup metrics.

    Three ratio variants are reported for transparency; only
    ``warmupRatio.firstToMedian`` drives the G9 verdict.
    Ratios are cross-campaign-comparable; absolute ms are not.
    """

    batch_id: str
    per_profile: dict[str, dict[str, Any]]
    notes: str = (
        "Ratios (warmupRatio.firstToLast, .firstToMean, .firstToMedian) are "
        "cross-campaign-comparable. Absolute ms (convergenceDeltaMs) and "
        "convergenceRatePct scale with workload size, so they are comparable "
        "across campaigns only when the workload is matched."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "batchId": self.batch_id,
            "notes": self.notes,
            "perProfile": self.per_profile,
        }


@dataclass
class CampaignArtifacts:
    """Paths to all artifacts written by one campaign run."""

    run_manifest_path: Path
    raw_snapshot_paths: list[Path]
    evidence_index_path: Path
    pressure_summary_path: Path
    readiness_summary_path: Path
    campaign_report_path: Path
    warmup_profile_path: Path

    def all_paths(self) -> list[Path]:
        return [
            self.run_manifest_path,
            *self.raw_snapshot_paths,
            self.evidence_index_path,
            self.pressure_summary_path,
            self.readiness_summary_path,
            self.campaign_report_path,
            self.warmup_profile_path,
        ]
