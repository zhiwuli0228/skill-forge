# v0.6.0 Campaign-002

This directory is a pointer to the Campaign-002 evidence
that covers the 28 test files not exercised by
[v0.6.0-remediation-campaign-001](../remediation/README.md).

## Summary

| Field | Value |
|-------|-------|
| Campaign ID | `v0.6.0-campaign-002` |
| OpenSpec change | `extract-perf-harness-and-run-campaign-002` |
| Harness | `tests/perf/` (new project asset, stdlib-only) |
| Profiles | STEADY (3×28), SMALL_STEADY (3×8 Bucket A), RAMP (3× staircase 8/18/28), BURST (3× D/A/E) |
| Total runs | 12 |
| Total snapshots | 36 |
| Test files covered | 28 (was: 6 in 001; total 34) |
| Verdict | **NOT_READY** (G9-warmup-structural FAIL on SMALL_STEADY) |
| Date | 2026-06-07 |

## Artifacts

All artifacts live under:
[`outputs/reports/v0.6.0-campaign-002/`](../../../outputs/reports/v0.6.0-campaign-002/)
(symlink to the 7 writer outputs).

## Key finding

G9-warmup-extractable-structural **failed** for the
SMALL_STEADY (Bucket A, 8-file) workload after a first
V3 pass also failed on the full 28-file STEADY
(durations 17094 / 16406 / 17282 ms, not non-increasing).
The SMALL_STEADY profile was added during apply to
restore 001's warmup-detection conditions at smaller
workload scale; the full STEADY is preserved as a data
point.

In practice, with a hot OS file cache and a recently
compiled `.pyc` tree, neither STEADY (28 files, ~17s)
nor SMALL_STEADY (8 files, ~5s) shows a deterministic
warmup signal. STEADY on a second V3 invocation showed
13.6% warmup (`[20828, 18296, 18000]`, firstToLast
1.157) while SMALL_STEADY remained flat
(`[5750, 6109, 5844]`, firstToLast 0.984). G9's
structural floor of "non-increasing duration series"
is sensitive to this measurement noise; G9 verdict
ends in `NOT_READY` for 002.

Implication: warmup-ratio as a CI gate needs calibration
per workload tier, OR a true cold-start harness (sandbox
or reboot between runs) to detect warmup at scale. This
is a follow-up question, not a defect of Campaign-002 —
the gate evaluated the data honestly and reported the
truth.

## Cross-campaign comparability

Per the warmup-profile spec, ratios are cross-campaign
comparable; absolute ms are not.

- 001 STEADY (6 files, ~6s): firstToMedian = 1.48,
  clear warmup signal.
- 002 STEADY (28 files, ~17s) first V3:
  firstToMedian = 1.01, no warmup.
- 002 STEADY (28 files, ~17s) second V3:
  firstToMedian = 1.15, weak warmup.
- 002 SMALL_STEADY (8 files, ~5s):
  firstToMedian = 0.96, no warmup.

The variability across the 002 STEADY runs is the
empirical evidence that warmup detection at 28-file
scale is not robust to measurement noise.

## Related documents

- OpenSpec change: `openspec/changes/extract-perf-harness-and-run-campaign-002/`
- 001 baseline: `docs/04-development/versions/v0.6.0/remediation/README.md`
- 001 artifacts: `outputs/reports/v0.6.0-remediation/` (frozen)
- 002 artifacts: `outputs/reports/v0.6.0-campaign-002/`
- Authorization rotation: `docs/00-project/current-state.md` (rotated 2026-06-07)
