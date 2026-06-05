# Brainstorm: example-governance-stack-walkthrough

> Status: example
> Schema: skill-forge-governance
> Author: Skill Forge Phase 2 (governance example)
> Date: 2026-06-05
>
> **EXAMPLE ONLY.** This brainstorm does not propose a real change. It is
> part of the example change `example-governance-stack-walkthrough`, which
> exists to demonstrate the full eight-artifact governance flow. The
> "problem" below is a teaching device, not a real bug or feature.
> See `proposal.md` for the meta-purpose of this example.

## Problem

A new Agent entering the Skill Forge repository has a hard time seeing the governance flow end-to-end. The schema, templates, and docs exist, but there is no worked example showing all eight artifacts in one place. New drafters have to read the schema, then the templates, then reverse-engineer the flow.

How do we make the flow obvious?

## Context

- The repository has the `skill-forge-governance` schema, eight templates, and a `docs/03-openspec/` set of guidelines.
- There is no worked example.
- `openspec/changes/add-skill-lifecycle-recommendation/` exists as a partial example (proposal, design, tasks) but it predates the new schema and does not include `review.md`, `plan.md`, or `verification.md`.
- A new example would lower the on-ramp cost for future drafters.

## Options

### Option A: A self-referential example change (this option)

- **Changes**: creates a new example change folder under `openspec/changes/example-governance-stack-walkthrough/` with all eight artifacts.
- **Does not change**: any external file. The example is self-contained.
- **Top risk**: a future drafter mistakes the example for a real change and tries to archive it.
- **Effort**: small (one phase, all in the example folder).

### Option B: A real-feeling example change that actually adds a docs section

- **Changes**: adds a "Cross-Reference Footer" to `docs/04-superpowers/superpowers-overview.md` and demonstrates the governance flow by walking the change.
- **Does not change**: any runtime code.
- **Top risk**: the change must be performed AND demonstrated, doubling the work. A reader might be confused about whether the example is a real change or not.
- **Effort**: medium (one phase + the actual doc edit).

### Option C: A worked example that lives outside `openspec/changes/`, in `docs/03-openspec/examples/`

- **Changes**: creates a new docs file under `docs/03-openspec/examples/walkthrough.md` and references the eight artifacts as inline code blocks.
- **Does not change**: the `openspec/changes/` tree.
- **Top risk**: the example is not a real OpenSpec change, so it does not exercise `openspec validate --strict`. A reader cannot run the example through the same pipeline as a real change.
- **Effort**: small (one phase, all in the docs folder).

## Assumptions

- [verified] The `skill-forge-governance` schema is in place (Phase 1 completed).
- [verified] The eight templates exist under `openspec/schemas/skill-forge-governance/templates/`.
- [verified] The Phase 2 strict scope allows creating files under `openspec/changes/example-governance-stack-walkthrough/`.
- [unverified] No future drafter will accidentally archive the example.
- [unverified] The example is small enough that it can be reviewed in a single read.

## Open Questions

- [non-blocking] Should the example change folder be excluded from `openspec validate --strict` automatically? (Answer for a future phase: it should be valid, not excluded. Validity is the point.)
- [non-blocking] Should the example be tagged with a special `status: example` field that the OpenSpec CLI recognizes? (Answer: not yet. The OpenSpec schema does not have such a field. Use the `> Status: example` line in each artifact for now.)

## Recommendation

- Recommended: **Option A** (this option).
- Reason: it exercises the full pipeline (`openspec validate --strict`) without modifying any external file, and it is clearly marked as an example in every artifact.
