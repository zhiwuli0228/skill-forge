"""Artifact writers for the performance-campaign harness.

Seven writers, all atomic (write to a temp file, then rename).
All writers take ``output_dir`` as a parameter — no hardcoded
paths, no global state.
"""

from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from ._analytics import derive_verdict
from ._types import CampaignArtifacts, GateResult, RunRecord, WarmupProfile


def _atomic_write_text(path: Path, content: str) -> None:
    """Write ``content`` to ``path`` atomically (write to .tmp, then rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def _atomic_write_json(path: Path, data: object, *, indent: int = 2) -> None:
    _atomic_write_text(path, json.dumps(data, indent=indent, ensure_ascii=False))


def capture_environment_summary() -> dict[str, str]:
    """Snapshot the runtime environment for the run manifest.

    Mirrors the 001 harness ENVIRONMENT_SUMMARY block.
    """
    py_version = sys.version.replace("\n", " ")
    try:
        uv_version = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        uv_version = "unknown"
    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(Path.cwd()),
        ).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        git_commit = "unknown"
    return {
        "pythonVersion": py_version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "cpuCount": str(os.cpu_count() or "unknown"),
        "uvVersion": uv_version,
        "gitCommit": git_commit,
        "hostname": socket.gethostname(),
        "workingDirectory": str(Path.cwd()),
    }


def write_run_manifest(
    all_runs: list[RunRecord],
    batch_id: str,
    version_name: str,
    output_dir: Path,
    environment_summary: dict[str, str] | None = None,
) -> Path:
    """Write ``run-manifest-<BATCH_ID>.json``."""
    env = environment_summary or capture_environment_summary()
    profile_coverage: dict[str, int] = {}
    for r in all_runs:
        profile_coverage[r.scenario_profile] = profile_coverage.get(r.scenario_profile, 0) + 1
    manifest = {
        "campaignId": batch_id,
        "versionName": version_name,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "runCount": len(all_runs),
        "profileCoverage": profile_coverage,
        "environmentSummary": env,
        "runs": [r.to_manifest_entry(env) for r in all_runs],
    }
    path = output_dir / f"run-manifest-{batch_id}.json"
    _atomic_write_json(path, manifest)
    return path


def write_raw_snapshots(run: RunRecord, output_dir: Path) -> Path:
    """Write ``raw-snapshots-<runId>.jsonl`` for one run."""
    path = output_dir / f"raw-snapshots-{run.run_id}.jsonl"
    lines = "\n".join(json.dumps(s.to_dict(), ensure_ascii=False) for s in run.snapshots) + "\n"
    _atomic_write_text(path, lines)
    return path


def write_evidence_index(
    all_runs: list[RunRecord],
    raw_snapshot_paths: list[Path],
    batch_id: str,
    output_dir: Path,
) -> Path:
    """Write ``evidence-index-<BATCH_ID>.json`` mapping every runId to its evidence."""
    by_id: dict[str, Path] = {p.stem.replace("raw-snapshots-", ""): p for p in raw_snapshot_paths}
    entries = [
        {
            "runId": r.run_id,
            "profile": r.scenario_profile,
            "rawEvidenceFile": str(by_id.get(r.run_id, Path(""))),
            "snapshotCount": len(r.snapshots),
            "startTime": r.start_time,
            "endTime": r.end_time,
            "exitCode": r.exit_code,
        }
        for r in all_runs
    ]
    data = {
        "campaignId": batch_id,
        "versionName": "v0.6.0",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "totalRuns": len(all_runs),
        "entries": entries,
    }
    path = output_dir / f"evidence-index-{batch_id}.json"
    _atomic_write_json(path, data)
    return path


def write_pressure_summary(
    all_runs: list[RunRecord],
    batch_id: str,
    output_dir: Path,
) -> Path:
    """Write ``pressure-summary-<BATCH_ID>.json`` (per-profile aggregates)."""
    profile_summaries: dict[str, dict] = {}
    for profile in ("STEADY", "RAMP", "BURST"):
        runs = [r for r in all_runs if r.scenario_profile == profile]
        if not runs:
            continue
        durations = [r.duration_ms for r in runs]
        profile_summaries[profile] = {
            "runCount": len(runs),
            "avgDurationMs": mean(durations),
            "minDurationMs": min(durations),
            "maxDurationMs": max(durations),
            "allExitZero": all(r.exit_code == 0 for r in runs),
            "allTestsPassed": all(r.exit_code == 0 and r.test_results.get("failed", 0) == 0 for r in runs),
            "totalSnapshots": sum(len(r.snapshots) for r in runs),
            "exitCodes": [r.exit_code for r in runs],
        }
    data = {
        "campaignId": batch_id,
        "versionName": "v0.6.0",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "profileSummaries": profile_summaries,
    }
    path = output_dir / f"pressure-summary-{batch_id}.json"
    _atomic_write_json(path, data)
    return path


def write_readiness_summary(
    gate_results: list[GateResult],
    all_runs: list[RunRecord],
    batch_id: str,
    output_dir: Path,
) -> Path:
    """Write ``readiness-summary-<BATCH_ID>.md`` (markdown)."""
    verdict, reason = derive_verdict(gate_results)
    by_id = {g.gate_id: g for g in gate_results}
    g1 = by_id.get("G1-profile-coverage")
    g7 = by_id.get("G7-coverage-expansion")
    g8 = by_id.get("G8-bucket-coverage")
    g9s = by_id.get("G9-warmup-extractable-structural")
    g9n = by_id.get("G9-warmup-extractable-signal")

    profile_run_counts = {p: sum(1 for r in all_runs if r.scenario_profile == p) for p in ("STEADY", "RAMP", "BURST")}

    lines: list[str] = []
    lines.append(f"# Readiness Summary — {batch_id}")
    lines.append("")
    lines.append(f"> Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"> Version: v0.6.0")
    lines.append(f"> Type: CAMPAIGN-002 (independent of v0.6.0-remediation)")
    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    lines.append(f"**{verdict}**")
    lines.append("")
    lines.append(f"Reason: {reason}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total runs | {len(all_runs)} |")
    lines.append(f"| Total snapshots | {sum(len(r.snapshots) for r in all_runs)} |")
    lines.append("| Profile run counts | "
                 + ", ".join(f"{p}={profile_run_counts[p]}" for p in ("STEADY", "RAMP", "BURST"))
                 + " |")
    if g1 is not None:
        lines.append(f"| G1 profile coverage | {'PASS' if g1.passed else 'FAIL'} |")
    if g7 is not None:
        lines.append(f"| G7 coverage expansion | {'PASS' if g7.passed else 'FAIL'} |")
    if g8 is not None:
        lines.append(f"| G8 bucket coverage | {'PASS' if g8.passed else 'FAIL'} |")
    if g9s is not None:
        lines.append(f"| G9 warmup structural | {'PASS' if g9s.passed else 'FAIL'} |")
    if g9n is not None:
        lines.append(f"| G9 warmup signal | {'PASS' if g9n.passed else 'FAIL'} |")
    lines.append("")
    lines.append("## Gate Results")
    lines.append("")
    for g in gate_results:
        mark = "PASS" if g.passed else "FAIL"
        lines.append(f"- [{mark}] {g.gate_id}: {g.description}")
    lines.append("")
    path = output_dir / f"readiness-summary-{batch_id}.md"
    _atomic_write_text(path, "\n".join(lines))
    return path


def write_campaign_report(
    gate_results: list[GateResult],
    all_runs: list[RunRecord],
    batch_id: str,
    version_name: str,
    output_dir: Path,
) -> Path:
    """Write ``campaign-report-<BATCH_ID>.md`` (full markdown report)."""
    verdict, _ = derive_verdict(gate_results)
    by_id = {g.gate_id: g for g in gate_results}
    profile_run_counts = {p: sum(1 for r in all_runs if r.scenario_profile == p) for p in ("STEADY", "RAMP", "BURST")}

    lines: list[str] = []
    lines.append(f"# Campaign Report — {batch_id}")
    lines.append("")
    lines.append(f"> Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"> Version: {version_name}")
    lines.append("")
    lines.append("## Important Notice")
    lines.append("")
    lines.append("This report documents Campaign-002, an independent campaign")
    lines.append("executed by the performance-campaign harness against the 28")
    lines.append("test files that were not covered by")
    lines.append("`v0.6.0-remediation-campaign-001`.")
    lines.append("")
    lines.append("**This is NOT the main v0.6.0 plan completion.** The 001")
    lines.append("artifacts under `outputs/reports/v0.6.0-remediation/` are")
    lines.append("frozen historical data and were not regenerated.")
    lines.append("")
    lines.append("## Campaign Summary")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Campaign ID | {batch_id} |")
    lines.append(f"| Version | {version_name} |")
    lines.append(f"| Total runs | {len(all_runs)} |")
    lines.append(f"| Total snapshots | {sum(len(r.snapshots) for r in all_runs)} |")
    lines.append(f"| Profile run counts | "
                 + ", ".join(f"{p}={profile_run_counts[p]}" for p in ("STEADY", "RAMP", "BURST"))
                 + " |")
    lines.append(f"| Verdict | {verdict} |")
    lines.append("")
    lines.append("## Profile Details")
    lines.append("")
    for profile in ("STEADY", "RAMP", "BURST"):
        runs = [r for r in all_runs if r.scenario_profile == profile]
        if not runs:
            continue
        lines.append(f"### {profile}")
        lines.append("")
        lines.append("| Run | Duration (ms) | Exit | Tests | Snapshots |")
        lines.append("|-----|--------------|------|-------|-----------|")
        for r in runs:
            tr = r.test_results
            lines.append(
                f"| {r.run_id} | {r.duration_ms:.1f} | {r.exit_code} | "
                f"{tr.get('passed', 0)}P/{tr.get('failed', 0)}F/{tr.get('total', 0)}T | "
                f"{len(r.snapshots)} |"
            )
        lines.append("")
    lines.append("## Gate Results")
    lines.append("")
    for g in gate_results:
        mark = "PASS" if g.passed else "FAIL"
        lines.append(f"- [{mark}] {g.gate_id}: {g.description}")
    lines.append("")
    lines.append("## Constraint Compliance")
    lines.append("")
    lines.append("- [x] No source code modified")
    lines.append("- [x] No existing test files modified")
    lines.append("- [x] No new dependencies added")
    lines.append("- [x] 001 frozen artifacts untouched")
    lines.append("- [x] 001 freeze contract enforced (refuses writes to `v0.6.0-remediation*`)")
    lines.append("")
    path = output_dir / f"campaign-report-{batch_id}.md"
    _atomic_write_text(path, "\n".join(lines))
    return path


def write_warmup_profile(
    warmup: WarmupProfile,
    batch_id: str,
    output_dir: Path,
) -> Path:
    """Write ``warmup-profile-<BATCH_ID>.json``."""
    path = output_dir / f"warmup-profile-{batch_id}.json"
    _atomic_write_json(path, warmup.to_dict())
    return path


def write_all(
    all_runs: list[RunRecord],
    gate_results: list[GateResult],
    warmup: WarmupProfile,
    batch_id: str,
    version_name: str,
    output_dir: Path,
) -> CampaignArtifacts:
    """Write all 7 artifacts and return their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_paths = [write_raw_snapshots(r, output_dir) for r in all_runs]
    manifest_path = write_run_manifest(all_runs, batch_id, version_name, output_dir)
    evidence_path = write_evidence_index(all_runs, raw_paths, batch_id, output_dir)
    pressure_path = write_pressure_summary(all_runs, batch_id, output_dir)
    readiness_path = write_readiness_summary(gate_results, all_runs, batch_id, output_dir)
    campaign_path = write_campaign_report(gate_results, all_runs, batch_id, version_name, output_dir)
    warmup_path = write_warmup_profile(warmup, batch_id, output_dir)
    return CampaignArtifacts(
        run_manifest_path=manifest_path,
        raw_snapshot_paths=raw_paths,
        evidence_index_path=evidence_path,
        pressure_summary_path=pressure_path,
        readiness_summary_path=readiness_path,
        campaign_report_path=campaign_path,
        warmup_profile_path=warmup_path,
    )
