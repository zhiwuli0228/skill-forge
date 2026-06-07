# Campaign Report — v0.6.0-campaign-002

> Generated: 2026-06-07T09:24:01.765139+00:00
> Version: v0.6.0

## Important Notice

This report documents Campaign-002, an independent campaign
executed by the performance-campaign harness against the 28
test files that were not covered by
`v0.6.0-remediation-campaign-001`.

**This is NOT the main v0.6.0 plan completion.** The 001
artifacts under `outputs/reports/v0.6.0-remediation/` are
frozen historical data and were not regenerated.

## Campaign Summary

| Field | Value |
|-------|-------|
| Campaign ID | v0.6.0-campaign-002 |
| Version | v0.6.0 |
| Total runs | 12 |
| Total snapshots | 36 |
| Profile run counts | STEADY=3, RAMP=3, BURST=3 |
| Verdict | NOT_READY |

## Profile Details

### STEADY

| Run | Duration (ms) | Exit | Tests | Snapshots |
|-----|--------------|------|-------|-----------|
| steady-run-000-a162a7e5 | 16390.0 | 0 | 319P/0F/319T | 3 |
| steady-run-001-a162e7ec | 15766.0 | 0 | 319P/0F/319T | 3 |
| steady-run-002-a1632585 | 16422.0 | 0 | 319P/0F/319T | 3 |

### RAMP

| Run | Duration (ms) | Exit | Tests | Snapshots |
|-----|--------------|------|-------|-----------|
| ramp-run-000-a164019b | 30562.0 | 0 | 102P/0F/102T | 3 |
| ramp-run-001-a1647907 | 23640.0 | 0 | 149P/0F/149T | 3 |
| ramp-run-002-a164d56c | 20110.0 | 0 | 319P/0F/319T | 3 |

### BURST

| Run | Duration (ms) | Exit | Tests | Snapshots |
|-----|--------------|------|-------|-----------|
| burst-run-000-a16523fb | 5297.0 | 0 | 30P/0F/30T | 3 |
| burst-run-001-a16538a1 | 6812.0 | 0 | 102P/0F/102T | 3 |
| burst-run-002-a1655340 | 8859.0 | 0 | 116P/0F/116T | 3 |

## Gate Results

- [PASS] G1-profile-coverage: All four profiles (STEADY, SMALL_STEADY, RAMP, BURST) present
- [PASS] G2-run-count-STEADY: At least 3 runs for STEADY
- [PASS] G2-run-count-SMALL_STEADY: At least 3 runs for SMALL_STEADY
- [PASS] G2-run-count-RAMP: At least 3 runs for RAMP
- [PASS] G2-run-count-BURST: At least 3 runs for BURST
- [PASS] G3-snapshot-count-steady-run-000-a162a7e5: Run steady-run-000-a162a7e5 has >= 3 snapshots
- [PASS] G4-timestamp-order-steady-run-000-a162a7e5: Run steady-run-000-a162a7e5 timestamps are non-decreasing
- [PASS] G5-runid-consistency-steady-run-000-a162a7e5: Run steady-run-000-a162a7e5 snapshots share runId
- [PASS] G6-metadata-steady-run-000-a162a7e5: Run steady-run-000-a162a7e5 has complete metadata
- [PASS] G3-snapshot-count-steady-run-001-a162e7ec: Run steady-run-001-a162e7ec has >= 3 snapshots
- [PASS] G4-timestamp-order-steady-run-001-a162e7ec: Run steady-run-001-a162e7ec timestamps are non-decreasing
- [PASS] G5-runid-consistency-steady-run-001-a162e7ec: Run steady-run-001-a162e7ec snapshots share runId
- [PASS] G6-metadata-steady-run-001-a162e7ec: Run steady-run-001-a162e7ec has complete metadata
- [PASS] G3-snapshot-count-steady-run-002-a1632585: Run steady-run-002-a1632585 has >= 3 snapshots
- [PASS] G4-timestamp-order-steady-run-002-a1632585: Run steady-run-002-a1632585 timestamps are non-decreasing
- [PASS] G5-runid-consistency-steady-run-002-a1632585: Run steady-run-002-a1632585 snapshots share runId
- [PASS] G6-metadata-steady-run-002-a1632585: Run steady-run-002-a1632585 has complete metadata
- [PASS] G3-snapshot-count-small_steady-run-000-a16365a2: Run small_steady-run-000-a16365a2 has >= 3 snapshots
- [PASS] G4-timestamp-order-small_steady-run-000-a16365a2: Run small_steady-run-000-a16365a2 timestamps are non-decreasing
- [PASS] G5-runid-consistency-small_steady-run-000-a16365a2: Run small_steady-run-000-a16365a2 snapshots share runId
- [PASS] G6-metadata-small_steady-run-000-a16365a2: Run small_steady-run-000-a16365a2 has complete metadata
- [PASS] G3-snapshot-count-small_steady-run-001-a16387f3: Run small_steady-run-001-a16387f3 has >= 3 snapshots
- [PASS] G4-timestamp-order-small_steady-run-001-a16387f3: Run small_steady-run-001-a16387f3 timestamps are non-decreasing
- [PASS] G5-runid-consistency-small_steady-run-001-a16387f3: Run small_steady-run-001-a16387f3 snapshots share runId
- [PASS] G6-metadata-small_steady-run-001-a16387f3: Run small_steady-run-001-a16387f3 has complete metadata
- [PASS] G3-snapshot-count-small_steady-run-002-a163a5ca: Run small_steady-run-002-a163a5ca has >= 3 snapshots
- [PASS] G4-timestamp-order-small_steady-run-002-a163a5ca: Run small_steady-run-002-a163a5ca timestamps are non-decreasing
- [PASS] G5-runid-consistency-small_steady-run-002-a163a5ca: Run small_steady-run-002-a163a5ca snapshots share runId
- [PASS] G6-metadata-small_steady-run-002-a163a5ca: Run small_steady-run-002-a163a5ca has complete metadata
- [PASS] G3-snapshot-count-ramp-run-000-a164019b: Run ramp-run-000-a164019b has >= 3 snapshots
- [PASS] G4-timestamp-order-ramp-run-000-a164019b: Run ramp-run-000-a164019b timestamps are non-decreasing
- [PASS] G5-runid-consistency-ramp-run-000-a164019b: Run ramp-run-000-a164019b snapshots share runId
- [PASS] G6-metadata-ramp-run-000-a164019b: Run ramp-run-000-a164019b has complete metadata
- [PASS] G3-snapshot-count-ramp-run-001-a1647907: Run ramp-run-001-a1647907 has >= 3 snapshots
- [PASS] G4-timestamp-order-ramp-run-001-a1647907: Run ramp-run-001-a1647907 timestamps are non-decreasing
- [PASS] G5-runid-consistency-ramp-run-001-a1647907: Run ramp-run-001-a1647907 snapshots share runId
- [PASS] G6-metadata-ramp-run-001-a1647907: Run ramp-run-001-a1647907 has complete metadata
- [PASS] G3-snapshot-count-ramp-run-002-a164d56c: Run ramp-run-002-a164d56c has >= 3 snapshots
- [PASS] G4-timestamp-order-ramp-run-002-a164d56c: Run ramp-run-002-a164d56c timestamps are non-decreasing
- [PASS] G5-runid-consistency-ramp-run-002-a164d56c: Run ramp-run-002-a164d56c snapshots share runId
- [PASS] G6-metadata-ramp-run-002-a164d56c: Run ramp-run-002-a164d56c has complete metadata
- [PASS] G3-snapshot-count-burst-run-000-a16523fb: Run burst-run-000-a16523fb has >= 3 snapshots
- [PASS] G4-timestamp-order-burst-run-000-a16523fb: Run burst-run-000-a16523fb timestamps are non-decreasing
- [PASS] G5-runid-consistency-burst-run-000-a16523fb: Run burst-run-000-a16523fb snapshots share runId
- [PASS] G6-metadata-burst-run-000-a16523fb: Run burst-run-000-a16523fb has complete metadata
- [PASS] G3-snapshot-count-burst-run-001-a16538a1: Run burst-run-001-a16538a1 has >= 3 snapshots
- [PASS] G4-timestamp-order-burst-run-001-a16538a1: Run burst-run-001-a16538a1 timestamps are non-decreasing
- [PASS] G5-runid-consistency-burst-run-001-a16538a1: Run burst-run-001-a16538a1 snapshots share runId
- [PASS] G6-metadata-burst-run-001-a16538a1: Run burst-run-001-a16538a1 has complete metadata
- [PASS] G3-snapshot-count-burst-run-002-a1655340: Run burst-run-002-a1655340 has >= 3 snapshots
- [PASS] G4-timestamp-order-burst-run-002-a1655340: Run burst-run-002-a1655340 timestamps are non-decreasing
- [PASS] G5-runid-consistency-burst-run-002-a1655340: Run burst-run-002-a1655340 snapshots share runId
- [PASS] G6-metadata-burst-run-002-a1655340: Run burst-run-002-a1655340 has complete metadata
- [PASS] G7-coverage-expansion: At least 28 unique test files covered
- [PASS] G8-bucket-coverage: All buckets appear in at least one run
- [FAIL] G9-warmup-extractable-structural: SMALL_STEADY duration series is non-increasing
- [FAIL] G9-warmup-extractable-signal: firstToMedian ratio >= 1.1 (>=10% warmup)

## Constraint Compliance

- [x] No source code modified
- [x] No existing test files modified
- [x] No new dependencies added
- [x] 001 frozen artifacts untouched
- [x] 001 freeze contract enforced (refuses writes to `v0.6.0-remediation*`)
