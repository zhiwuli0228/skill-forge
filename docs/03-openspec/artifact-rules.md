# Artifact Rules

This document lists the rules each artifact must satisfy under the `skill-forge-governance` schema. The rules are also encoded in `openspec/config.yaml` under `rules:` and in `openspec/schemas/skill-forge-governance/schema.yaml` under each artifact's `instruction`. This document is the human-readable reference; the schema is the machine-checkable reference.

## 1. Artifact Order

The artifacts are produced in a fixed order:

```text
brainstorm  ->  proposal  ->  spec  ->  design  ->  review  ->  plan  ->  tasks  ->  verification
```

`brainstorm` is optional for trivial changes. The other seven are required for any non-trivial change.

The `requires:` field in `schema.yaml` enforces a partial order at the OpenSpec level. The full order is enforced by the review step: a `review.md` with verdict `approve` confirms that the prior artifacts are consistent.

## 2. Brainstorm

Required when the change introduces:

- A new lifecycle phase.
- A new agent role.
- A new governance rule.
- A new schema field.
- A breaking change to an existing schema.

For other changes, brainstorm is optional but recommended when the problem is ambiguous.

Required sections:

- `## Problem` — the actual user problem in 2-3 sentences.
- `## Context` — current state, constraints, stakeholders. Cite files by path.
- `## Options` — at least two candidate approaches.
- `## Assumptions` — with verified / unverified tags.
- `## Open Questions` — blocking / non-blocking.
- `## Recommendation` — the recommended option and the reason.

Output is plain Markdown. No code, no templates, no schema edits.

## 3. Proposal

Always required for a non-trivial change.

Required sections, in this order:

- `## Why` — 1-2 sentences.
- `## What Changes` — bullet list; mark breaking changes with `**BREAKING**`.
- `## Capabilities` — three subsections: `### New Capabilities`, `### Modified Capabilities`, `### Removed Capabilities`.
- `## Impact` — code, CLI, schemas, workspaces.
- `## Non-Goals` — what is explicitly NOT being done.
- `## Risks` — top 3 with one-line mitigations.
- `## Rollback` — exact steps to revert.
- `## Consistency With Brainstorm` — required if brainstorm.md exists.

Length: under two pages of body text. Implementation details belong in `design.md`.

## 4. Spec

Required. One file per capability under `specs/<capability>/spec.md`.

Required sections:

- `# <Capability Name> Specification` — heading.
- `## Purpose` — 1-2 sentences.
- Delta sections, in this order if multiple are present:
  - `## ADDED Requirements`
  - `## MODIFIED Requirements`
  - `## REMOVED Requirements`
  - `## RENAMED Requirements`
- Each requirement: `### Requirement: <name>` followed by SHALL/MUST description.
- Each scenario: `#### Scenario: <name>` (exactly four hashtags) with `**WHEN**` / `**THEN**`.

Rules:

- Every requirement must have at least one scenario.
- `MODIFIED Requirements` must include the FULL updated content, not a partial diff.
- `REMOVED Requirements` must include `**Reason**` and `**Migration**`.
- `RENAMED Requirements` must use `**FROM**` / `**TO**` format.
- Do not encode implementation details as requirements unless they are externally observable.

## 5. Design

Required for cross-cutting changes. Optional but recommended for single-file changes.

Required sections (in this order):

- `## Context`
- `## Goals / Non-Goals`
- `## Decisions` — one or more decisions, each with `**Decision**` / `**Rationale**` / `**Alternatives considered**`.
- `## Data Contracts` — required if any of the following change: config, blueprint, validation result, package metadata, provenance schemas.
- `## Module Boundaries` — Added / Modified / Untouched.
- `## Compatibility Impact` — Claude Code, Codex, opencode, generated Skill packages.
- `## Offline and Deterministic Mode` — behavior under network-down and LLM-disabled.
- `## Security and Filesystem` — reads, writes, env vars.
- `## Risks / Trade-offs` — `[Risk] -> [mitigation]` format.
- `## Migration Plan` — Deploy / Rollback.
- `## Open Questions` — blocking / non-blocking.

Skip the document only when the change is single-file, single-module, and does not change any data contract.

## 6. Review

Required. The review is the gate between planning and execution.

Required sections:

- `## Change Id`
- `## Reviewer`
- `## Scope Coverage` — table: artifact, file, verdict, missing sections.
- `## Cross-Artifact Consistency` — capability names, data contracts, allowed paths, verification commands.
- `## Allowed Path List` — Allowed / Forbidden / Discrepancies.
- `## Verification Readiness` — table: command, tool, status.
- `## Required Changes` — required for verdict `request-changes`.
- `## Verdict` — `approve`, `request-changes`, or `block`.

A change with verdict `block` cannot proceed to plan. A change with verdict `request-changes` cannot proceed to tasks until the listed changes are applied.

## 7. Plan

Required for any change that has an implementation phase. Required artifact for `applying`.

Required sections:

- `## Change Id`
- `## Allowed Paths`
- `## Forbidden Paths`
- `## Pre-Conditions` — checklist.
- `## Steps` — numbered. Each step has Files / Action / Verification (command, expected exit code, expected observation) / Escalation.
- `## Final Verification` — exact commands.
- `## Rollback` — exact steps.
- `## Hand-off Note` — single most important rule for this change.

The plan must be runnable by an agent that has only read `AGENTS.md`, `CODEX.md`/`CLAUDE.md`, the change folder, and the files in `Allowed Paths`.

## 8. Tasks

Required. The apply phase parses checkboxes to track progress.

Required structure:

- Numbered group headings `## 1. <Group Name>`, `## 2. <Group Name>`, etc.
- Each task is a checkbox `- [ ] N.M <description>`. Files and observation are part of the description.
- A final `## N. Final Verification` group with: run final commands, write `verification.md`, run `openspec validate <change-id> --strict`.

Rules:

- Separate docs, tests, config, schema, and code tasks. Do not mix them.
- Each task must have an observable completion condition.
- Tasks must respect the allowed-path list from plan.md. A task that would touch a forbidden path must escalate.

## 9. Verification

Required. Written at the END of the change, after tasks are complete.

Required sections:

- `## Change Id`
- `## Executed Commands` — one subsection per command: working directory, exit code, output summary.
- `## Test Results` — pytest summary line.
- `## OpenSpec Validation` — output of `openspec validate <change-id> --strict`.
- `## Skipped Commands` — table: command, reason, impact.
- `## Deviations from Plan` — empty when none.
- `## Remaining Risks` — `[Risk] -> [mitigation or follow-up]` format.
- `## Follow-up Changes` — list of new changes, or "None".
- `## Verdict` — `done`, `done-with-risks`, or `not-done`.

A change without a verification record is not done.

## 10. Cross-Artifact Rules

The following cross-artifact rules are not enforceable by `schema.yaml` directly. They are enforced by the review step and the planning agent's discipline.

- The capability names in `proposal.md` must match the spec file names.
- The data contracts in `design.md` must match the files in `plan.md`.
- The allowed-path list in `plan.md` must match the file list in `tasks.md`.
- The verification commands in `tasks.md` must match the commands in `plan.md` `## Final Verification`.
- The follow-up changes in `verification.md` must be consistent with the proposal's `## Non-Goals`.

The review step is the place where these are checked. A change with verdict `request-changes` is one where one or more of these rules is violated.
