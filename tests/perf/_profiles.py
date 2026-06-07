"""Profile factories for STEADY, RAMP, and BURST workloads.

Each factory takes a list of test files (or a buckets dict)
and returns a list of ``RunSpec`` records. RAMP uses the
linear +10/+10 staircase (8 / 18 / 28 files for the
Campaign-002 bucket layout).
"""

from __future__ import annotations

from ._types import Profile, RunSpec


def make_steady_profile(all_files: list[str]) -> Profile:
    """STEADY: 3 runs of the full file list, fixed rate.

    Seeds 42/43/44 match the 001 harness convention. The
    full file list is used as a data point in
    warmup-profile, but the G9 warmup-extractable gate
    evaluates SMALL_STEADY (which uses Bucket A only),
    because the full STEADY masks the warmup signal at
    28-file scale.
    """
    if not all_files:
        raise ValueError("make_steady_profile requires at least one test file")
    file_lists: list[tuple[str, ...]] = [tuple(all_files) for _ in range(3)]
    return Profile(name="STEADY", run_count=3, file_lists=file_lists)


def make_small_steady_profile(buckets: dict[str, list[str]]) -> Profile:
    """SMALL_STEADY: 3 runs of Bucket A only (~5s each).

    This profile is the warmup probe for G9. The full
    STEADY (28 files, ~17s per run) masks the warmup
    signal because process-startup and IO-warmup costs
    are dominated by test execution. SMALL_STEADY
    reproduces 001's warmup-detection conditions (small
    workload, dominated by startup costs).

    Seeds 50/51/52 are distinct from STEADY's 42/43/44
    so the run IDs are also distinct.
    """
    a = buckets.get("A", [])
    if not a:
        raise ValueError("make_small_steady_profile requires bucket A")
    file_lists: list[tuple[str, ...]] = [tuple(a) for _ in range(3)]
    return Profile(name="SMALL_STEADY", run_count=3, file_lists=file_lists)


def make_ramp_profile(buckets: dict[str, list[str]]) -> Profile:
    """RAMP: 3 runs with a linear staircase.

    For the Campaign-002 layout (8/10/5/4/1 buckets totalling
    28), the staircase is ``[8, 18, 28]`` — linear +10/+10
    steps. This matches 001's linear-scaling property
    (001 was 2/4/6, +2/+2).
    """
    a = buckets.get("A", [])
    b = buckets.get("B", [])
    c = buckets.get("C", [])
    d = buckets.get("D", [])
    e = buckets.get("E", [])
    if not (a and b):
        raise ValueError("make_ramp_profile requires at least buckets A and B")
    if not (a and e):
        raise ValueError("make_ramp_profile requires the full bucket set A..E")
    r0 = list(a)
    r1 = list(a) + list(b)
    r2 = list(a) + list(b) + list(c) + list(d) + list(e)
    file_lists: list[tuple[str, ...]] = [tuple(r0), tuple(r1), tuple(r2)]
    return Profile(name="RAMP", run_count=3, file_lists=file_lists)


def make_burst_profile(buckets: dict[str, list[str]]) -> Profile:
    """BURST: 3 single-bucket runs, varying weight.

    For the Campaign-002 layout the order is D / A / E
    (4 / 8 / 8 files) — three different bucket weights to
    test burst behavior across module sizes.
    """
    d = buckets.get("D", [])
    a = buckets.get("A", [])
    e = buckets.get("E", [])
    if not (d and a and e):
        raise ValueError("make_burst_profile requires buckets A, D, and E")
    file_lists: list[tuple[str, ...]] = [tuple(d), tuple(a), tuple(e)]
    return Profile(name="BURST", run_count=3, file_lists=file_lists)


def specs_from_profile(profile: Profile) -> list[RunSpec]:
    """Convert a Profile into the RunSpec list the runner consumes.

    Seeds are deterministic per (profile, run_index):
        STEADY: 42, 43, 44 (matches 001)
        RAMP:   100, 101, 102 (matches 001)
        BURST:  200, 201, 202 (matches 001)
    base_work_units equals the number of test files in the
    run for STEADY/RAMP; for BURST it equals the run's file
    count too (matching 001's behavior — see design notes
    about baseWorkUnits in Campaign-001).
    """
    seed_base = {
        "STEADY": 42,
        "SMALL_STEADY": 50,
        "RAMP": 100,
        "BURST": 200,
    }[profile.name]
    return [
        RunSpec(test_files=files, seed=seed_base + i, base_work_units=len(files))
        for i, files in enumerate(profile.file_lists)
    ]
