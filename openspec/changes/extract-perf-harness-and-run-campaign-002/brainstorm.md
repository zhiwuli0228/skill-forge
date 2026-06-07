# Brainstorm — extract-perf-harness-and-run-campaign-002

## Trigger

v0.6.0-remediation-campaign-001 produced 9 real test runs
across STEADY/RAMP/BURST, all exit 0, all P0 gates pass —
but covered only 6 of 34 test files. A real warmup signal
is visible in STEADY (8453 → 6047 → 5344 ms, ratio ~1.58).
The 001 harness is a 673-line, hardcoded, monolithic
script at `outputs/reports/v0.6.0-remediation/_run_experiments.py`
that is not reusable.

## Why now

1. **Coverage gap**: 28 of 34 test files were not exercised
   in 001. These include the high-value modules that made
   v0.6.0 actually shippable (lifecycle, collection
   governance, retrieval/semantic, adoption/experience,
   promotion, generation/library/upgrade/evals, CLI,
   drafts/wizard, project context, governance check,
   installer, llm, quality report).
2. **Reusability deficit**: 001's harness cannot be invoked
   for v0.6.x follow-ups without copy-paste. A v0.7.0
   campaign would need to redo the same work from scratch.
3. **Methodology risk**: the warmup signal is currently a
   side observation, not a structured artifact. Future
   campaigns cannot easily compare their warmup behavior
   against 001.

## Alternatives considered

- **A. Drop the follow-up**. Status quo: 001 artifacts
  remain the only evidence. **Rejected** — coverage gap
  and methodology risk persist.
- **B. Re-run 001 as a single expanded campaign** (no
  harness extraction). Add the 28 files to 001's RAMP and
  re-run. **Rejected** — loses the 001↔002 cross-campaign
  comparability that the warmup signal needs.
- **C. Extract the harness AND run Campaign-002** (chosen).
  Two artifacts: a reusable project asset (the harness)
  and a new campaign (002) that exercises it on the
  missing 28 files. **Accepted** — addresses coverage,
  reusability, and methodology in one change.
- **D. Extract the harness as a separate change; run
  Campaign-002 as a follow-up change**. **Considered and
  deferred** — would create an additional OpenSpec change
  for what's logically one project decision. Keep D as a
  candidate for a future decomposition if the change
  scope proves too large.

## Strategic outcomes

- **Reusability**: `tests/perf/` is the v0.6.x and beyond
  project-level evidence collection asset.
- **Coverage**: 28 additional test files exercised with
  full P0 gate verification.
- **Methodology**: a `warmup-profile-<BATCH_ID>.json`
  artifact becomes a structured, comparable signal across
  campaigns.

## Out of scope (this change)

- Production ThreadPoolExecutor integration. The 001 design
  surface (corePoolSize, maximumPoolSize, queueCapacity) is
  still placeholder; this change does not touch it.
- Queue resizing. Same reason.
- Modifying the 001 frozen artifacts. They are historical
  evidence; 002 is a separate campaign with its own output
  directory.
- Auto-promoting warmup-ratio into a CI gate. That decision
  belongs to a follow-up change that consumes 002's data.
- The lifecycle / collection / retrieval modules'
  *implementation* (only their test coverage is exercised
  by 002).
