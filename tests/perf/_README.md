# Performance-Campaign Harness

Reusable evidence-collection harness extracted from
[`v0.6.0-remediation-campaign-001`](../../outputs/reports/v0.6.0-remediation/campaign-report-v0.6.0-remediation-campaign-001.md).
Stdlib-only, decoupled from `src/skill_forge/`, and
invokable via `python -m tests.perf._main`.

## Why

The 001 campaign was a 673-line one-off script with
hardcoded paths. This harness:

1. **Reuses** the 001 STEADY/RAMP/BURST profile structure
   and P0 gate logic (G1–G6 verbatim).
2. **Adds** G7–G9 (coverage expansion, bucket coverage,
   warmup extractability) and a `warmup-profile` artifact.
3. **Enforces** the 001 freeze contract: refuses to write
   to any output directory matching `v0.6.0-remediation*`.
4. **Stays** stdlib-only, matching 001's decoupling
   posture.

## Module Layout

```
tests/perf/
├── __init__.py
├── _types.py        # dataclasses: Profile, RunSpec, Snapshot, RunRecord, GateResult, WarmupProfile, CampaignArtifacts
├── _profiles.py     # STEADY / SMALL_STEADY / RAMP / BURST profile factories
├── _runner.py       # subprocess + 3-snapshot capture per run
├── _analytics.py    # G1–G9 gates + warmup-ratio extraction
├── _artifacts.py    # 7 atomic writers
├── _main.py         # CLI entry point
└── _README.md       # this file
```

The `_` prefix prevents pytest's default `test_*.py` /
`*_test.py` collection. Verify with:

```bash
uv run pytest --collect-only -q | grep -c "tests/perf/"
# expect: 0
```

## Invocation

```bash
# Default: campaign-002 → outputs/reports/v0.6.0-campaign-002/
uv run python -m tests.perf._main --campaign campaign-002

# Custom output dir (must NOT match v0.6.0-remediation*)
uv run python -m tests.perf._main --campaign campaign-002 \
    --output-dir /tmp/sf-campaign-002

# Different project root
uv run python -m tests.perf._main --campaign campaign-002 \
    --project-root /path/to/skill-forge

# Longer timeout (default 600s)
uv run python -m tests.perf._main --campaign campaign-002 \
    --timeout-per-run 900
```

## Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--campaign` | `campaign-002` | Campaign identifier (only `campaign-002` is built in) |
| `--output-dir` | `outputs/reports/v0.6.0-campaign-002/` | Where artifacts land |
| `--project-root` | `Path.cwd()` | Project root for `uv run pytest` |
| `--timeout-per-run` | `600.0` | Subprocess timeout in seconds |
| `--batch-id` | `v0.6.0-campaign-002` | Batch ID used in artifact filenames |

## Artifacts Produced

For a successful run, the output dir contains:

1. `run-manifest-<BATCH_ID>.json` — full run records with environment summary
2. `raw-snapshots-<runId>.jsonl` — one per run, 3 lines each
3. `evidence-index-<BATCH_ID>.json` — runId → evidence file mapping
4. `pressure-summary-<BATCH_ID>.json` — per-profile aggregate metrics
5. `readiness-summary-<BATCH_ID>.md` — gate results + verdict
6. `campaign-report-<BATCH_ID>.md` — full human-readable report
7. `warmup-profile-<BATCH_ID>.json` — per-profile warmup metrics

## 001 Freeze Contract

The harness refuses to write to any output directory whose
path matches the substring `v0.6.0-remediation`. Attempting
this returns exit code 2 with a clear stderr message. The
001 artifacts under `outputs/reports/v0.6.0-remediation/`
are frozen historical data and must never be regenerated.

## Cross-Campaign Warmup Comparability

The `warmup-profile` artifact reports three ratios per
profile (`firstToLast`, `firstToMean`, `firstToMedian`),
`convergenceDeltaMs`, and `convergenceRatePct`.

**Ratios are cross-campaign-comparable** (a 1.5x warmup at
2 files and a 1.5x warmup at 28 files mean the same thing).
**Absolute ms are not** (a 28-file workload has larger
absolute numbers than a 2-file workload; this is workload
size, not warmup). Documented in the artifact's `notes`
field.

## Adding a New Campaign

To add Campaign-003 (or any new campaign), write a new
profile factory in `_profiles.py`, add a case to `main()`
in `_main.py`, and add the campaign's bucket layout as a
module-level constant. The gates and writers are
campaign-agnostic; no code changes needed there.
