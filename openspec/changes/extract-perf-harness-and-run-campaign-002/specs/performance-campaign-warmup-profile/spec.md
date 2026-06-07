# performance-campaign-warmup-profile Specification

## Purpose
Define the structured `warmup-profile-<BATCH_ID>.json`
artifact and the G9-warmup-extractable gate that quantifies
warmup as a comparable, structured signal.

## ADDED Requirements

### Requirement: Warmup profile artifact schema
The system SHALL emit
`warmup-profile-<BATCH_ID>.json` containing per-profile
warmup metrics with three ratio variants, a delta, and a
rate.

#### Scenario: Each profile in perProfile has all five numeric fields
- **WHEN** `extract_warmup_profile(all_runs, batch_id)` is called with at least 3 runs per profile
- **THEN** the returned WarmupProfile SHALL have a `perProfile` dict
- **AND** each profile entry SHALL have `warmupRatio.firstToLast`, `warmupRatio.firstToMean`, `warmupRatio.firstToMedian`, `convergenceDeltaMs`, `convergenceRatePct`
- **AND** each profile entry SHALL have a `runs` list with one entry per run carrying `runId`, `durationMs`, `exitCode`

#### Scenario: Profiles with fewer than 3 runs are omitted
- **WHEN** a profile has fewer than 3 runs in all_runs
- **THEN** that profile SHALL be omitted from `perProfile`
- **AND** the JSON SHALL NOT contain a partial entry for that profile

### Requirement: Cross-campaign ratio comparability
The system SHALL document that warmup ratios are
cross-campaign-comparable while absolute ms are not
(workload size scales the absolute values).

#### Scenario: The warmup-profile JSON contains a comparability note
- **WHEN** the JSON is read
- **THEN** it SHALL contain a top-level `notes` field with text describing the cross-campaign ratio comparability

### Requirement: G9-warmup-extractable two-tier gate
The system SHALL evaluate G9 as two checks: a structural
check (non-increasing SMALL_STEADY duration series) and a
signal check (firstToMedian ratio >= 1.1). SMALL_STEADY is
the 3 × Bucket A run profile (~5s per run) added because
the full STEADY workload (28 files, ~17s per run) masks
the warmup signal that 001's 6-file STEADY detected.

#### Scenario: Monotonic decreasing SMALL_STEADY passes the structural check
- **WHEN** SMALL_STEADY durations are `[8453, 6047, 5344]`
- **THEN** G9-warmup-extractable-structural SHALL pass
- **AND** G9-warmup-extractable-signal SHALL pass because `firstToMedian = 8453 / 6047 = 1.40 >= 1.1`
- **AND** the overall verdict SHALL be `READY`

#### Scenario: Non-monotonic SMALL_STEADY fails the structural check
- **WHEN** SMALL_STEADY durations are `[5000, 7000, 4000]`
- **THEN** G9-warmup-extractable-structural SHALL fail because the series is not non-increasing
- **AND** the overall verdict SHALL be `NOT_READY`

#### Scenario: Monotonic but small warmup gives READY_WITH_RISK
- **WHEN** SMALL_STEADY durations are `[5000, 4950, 4900]` (1% improvement)
- **THEN** G9-warmup-extractable-structural SHALL pass
- **AND** G9-warmup-extractable-signal SHALL fail because `firstToMedian = 5000 / 4950 = 1.01 < 1.1`
- **AND** the overall verdict SHALL be `READY_WITH_RISK` with reason "warmup not detectable in 3 runs"

#### Scenario: Full STEADY durations are emitted but not used for G9
- **WHEN** the campaign runs both full STEADY and SMALL_STEADY
- **THEN** the warmup-profile JSON SHALL include both `STEADY` and `SMALL_STEADY` entries in `perProfile`
- **AND** G9 SHALL evaluate SMALL_STEADY only

### Requirement: G9 verdict controls the readiness label
The system SHALL set the readiness label based on G1–G9
outcomes:
- All G1–G9 PASS → `READY`
- All G1–G8 PASS, G9-signal FAIL → `READY_WITH_RISK`
- Any G1–G8 FAIL → `NOT_READY`

#### Scenario: All gates passing yields READY
- **WHEN** G1–G9 all pass
- **THEN** the readiness label SHALL be `READY`

#### Scenario: G9-signal failure yields READY_WITH_RISK
- **WHEN** G1–G8 pass and G9-signal fails
- **THEN** the readiness label SHALL be `READY_WITH_RISK`

#### Scenario: Any G1–G8 failure yields NOT_READY
- **WHEN** any of G1–G8 fails
- **THEN** the readiness label SHALL be `NOT_READY` regardless of G9
