# Proposal: example-governance-stack-walkthrough

> Status: example
> Schema: skill-forge-governance
> Author: Skill Forge Phase 2 (governance example)
> Date: 2026-06-05
>
> **EXAMPLE ONLY.** This proposal does not propose a real change. It is
> part of the example change `example-governance-stack-walkthrough`, which
> exists to demonstrate the full eight-artifact governance flow.
> The "What Changes" section below is meta: it describes the example
> itself, not a real feature. See `brainstorm.md` for the rationale.

## Why

The Skill Forge governance stack (`AGENTS.md` + schema + `docs/03-openspec/` + `docs/04-superpowers/`) defines a complete eight-artifact change flow, but there is no worked example showing all eight artifacts in one place. New drafters have to read the schema, then the templates, then reverse-engineer the flow. Adding a self-referential example lowers the on-ramp cost.

## What Changes

- **NEW**: a new example change folder under `openspec/changes/example-governance-stack-walkthrough/` containing all eight artifacts (`brainstorm.md`, `proposal.md`, `spec.md`, `design.md`, `review.md`, `plan.md`, `tasks.md`, `verification.md`).
- **NEW**: the example is self-referential. It does not modify any external file.
- **NEW**: every artifact is marked at the top with `> Status: example` and a `> **EXAMPLE ONLY.**` notice.

## Capabilities

### New Capabilities

- `governance-example-walkthrough`: an example OpenSpec change that exercises the full eight-artifact flow under the `skill-forge-governance` schema, marked as Example Only.

### Modified Capabilities

- None. The change does not modify any existing capability.

### Removed Capabilities

- None.

## Impact

- **Code**: none. The example does not modify any runtime code.
- **CLI**: none. The example does not modify any CLI surface.
- **Schemas**: none. The example does not modify any stored artifact schema.
- **Workspaces**: none. The example does not modify any user workspace.
- **OpenSpec tree**: a new folder is added under `openspec/changes/`. The folder is not archived; it is left in place as a permanent example.
- **Validation**: the example must pass `openspec validate --strict --all` so that it is a valid, runnable demonstration of the pipeline.

## Non-Goals

- The example does not propose a real feature or fix.
- The example does not modify any file outside the example change folder.
- The example is not a template that gets `cp -r`'d into a real change. The schema's templates are the templates.
- The example does not add a new schema field, a new lifecycle phase, a new agent role, or a new governance rule.

## Risks

- A future drafter mistakes the example for a real change and tries to archive it -> Mitigation: every artifact is marked `> Status: example` and `> **EXAMPLE ONLY.**`; `verification.md` records the verdict as `done-as-example` to make the example status explicit.
- The example becomes stale as the schema evolves -> Mitigation: a follow-up change should re-validate the example whenever the schema is bumped.
- The example becomes a copy-paste template, defeating the purpose of having a schema -> Mitigation: the example is intentionally not a "fill in the blanks" template; it is a worked instance of a self-referential change.

## Rollback

1. Delete the folder `openspec/changes/example-governance-stack-walkthrough/`.
2. No other file is touched, so no other rollback is needed.
3. The schema, templates, and docs are unchanged. The example is self-contained.

## Consistency With Brainstorm

- Brainstorm file: `brainstorm.md` (in this folder).
- Recommended option: Option A (this option). The proposal implements Option A.
- Deviations and reasons: none. The proposal is consistent with the brainstorm.
