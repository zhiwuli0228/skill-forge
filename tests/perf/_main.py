"""Entry point for the performance-campaign harness.

Invocation::

    python -m tests.perf._main --campaign campaign-002 \
        --output-dir outputs/reports/v0.6.0-campaign-002

The default output dir is ``outputs/reports/v0.6.0-campaign-002``
under the project root. The 001 freeze contract refuses to
write to any directory matching ``v0.6.0-remediation*``.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from ._analytics import evaluate_gates, extract_warmup_profile
from ._artifacts import write_all
from ._profiles import (
    make_burst_profile,
    make_ramp_profile,
    make_small_steady_profile,
    make_steady_profile,
    specs_from_profile,
)
from ._runner import run_profile


BUCKETS: dict[str, list[str]] = {
    "A": [
        "tests/test_lifecycle.py",
        "tests/test_lifecycle_recommendation.py",
        "tests/test_lifecycle_recommendation_rules.py",
        "tests/test_collection_cli.py",
        "tests/test_collection_reuse.py",
        "tests/test_collection_scoring.py",
        "tests/test_collection_search.py",
        "tests/test_collection_store.py",
    ],
    "B": [
        "tests/test_search_retrieval.py",
        "tests/test_semantic_retrieval.py",
        "tests/test_research_update.py",
    ],
    "C": [
        "tests/test_skill_adoption.py",
        "tests/test_experience.py",
        "tests/test_promotion.py",
        "tests/test_community_skill_discovery.py",
        "tests/test_sqlite_store.py",
    ],
    "D": [
        "tests/test_skill_generator.py",
        "tests/test_skill_library.py",
        "tests/test_skill_upgrade.py",
        "tests/test_skill_evals.py",
    ],
    "E": [
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


FROZEN_DIR_PATTERN = re.compile(r"v0\.6\.0-remediation")
DEFAULT_BATCH_ID = "v0.6.0-campaign-002"
DEFAULT_VERSION = "v0.6.0"
DEFAULT_OUTPUT_DIR = Path("outputs") / "reports" / "v0.6.0-campaign-002"


def assert_not_frozen(output_dir: Path) -> None:
    """001's artifacts are frozen historical data. Refuse to overwrite."""
    if FROZEN_DIR_PATTERN.search(str(output_dir)):
        sys.stderr.write(
            f"REFUSED: output dir '{output_dir}' matches the 001 frozen pattern "
            f"'v0.6.0-remediation*'. Use a different --output-dir "
            f"(e.g., outputs/reports/v0.6.0-campaign-002/).\n"
        )
        sys.exit(2)


def run_campaign_002(
    output_dir: Path,
    project_root: Path,
    timeout_per_run: float = 600.0,
    batch_id: str = DEFAULT_BATCH_ID,
) -> int:
    """Execute the Campaign-002 plan and write all artifacts.

    Returns the process exit code (0 on all-gates-pass, 2 on
    gate failure, 3 on subprocess failure).
    """
    assert_not_frozen(output_dir)

    all_union: list[str] = []
    for fs in BUCKETS.values():
        all_union.extend(fs)
    all_union = sorted(set(all_union))

    steady = make_steady_profile(all_union)
    small_steady = make_small_steady_profile(BUCKETS)
    ramp = make_ramp_profile(BUCKETS)
    burst = make_burst_profile(BUCKETS)

    all_runs = []
    for profile in (steady, small_steady, ramp, burst):
        specs = specs_from_profile(profile)
        records = run_profile(
            profile_name=profile.name,
            specs=specs,
            project_root=project_root,
            timeout_per_run=timeout_per_run,
        )
        all_runs.extend(records)

    campaign_config = {
        "buckets": BUCKETS,
        "expected_min_coverage": 28,
    }
    gates = evaluate_gates(all_runs, campaign_config)
    warmup = extract_warmup_profile(all_runs, batch_id)
    write_all(
        all_runs=all_runs,
        gate_results=gates,
        warmup=warmup,
        batch_id=batch_id,
        version_name=DEFAULT_VERSION,
        output_dir=output_dir,
    )

    all_passed = all(g.passed for g in gates)
    return 0 if all_passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tests.perf._main",
        description="Performance-campaign harness for skill-forge.",
    )
    parser.add_argument(
        "--campaign",
        default="campaign-002",
        help="Campaign identifier (default: campaign-002)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root for pytest invocations (default: cwd)",
    )
    parser.add_argument(
        "--timeout-per-run",
        type=float,
        default=600.0,
        help="Per-run subprocess timeout in seconds (default: 600)",
    )
    parser.add_argument(
        "--batch-id",
        default=DEFAULT_BATCH_ID,
        help=f"Batch identifier used in artifact filenames (default: {DEFAULT_BATCH_ID})",
    )
    args = parser.parse_args(argv)

    if args.campaign != "campaign-002":
        sys.stderr.write(
            f"unknown campaign {args.campaign!r}; this build only supports 'campaign-002'\n"
        )
        return 2

    return run_campaign_002(
        output_dir=args.output_dir,
        project_root=args.project_root,
        timeout_per_run=args.timeout_per_run,
        batch_id=args.batch_id,
    )


if __name__ == "__main__":
    sys.exit(main())
