# Proposal Guidelines

A `proposal.md` explains WHY a change exists. It is the smallest possible artifact that still lets a reader decide whether the change is in scope. Implementation details belong in `design.md`; observable behavior belongs in `spec.md`; the executable plan belongs in `plan.md`.

This document collects the writing rules for proposals. The structural rules are in `artifact-rules.md`; the schema-enforced rules are in `openspec/schemas/skill-forge-governance/schema.yaml` and `openspec/schemas/skill-forge-governance/templates/proposal.md`.

## 1. Voice

Write the proposal in plain language. The reader is a human reviewer or a future agent re-reading the change. Avoid jargon, marketing language, and "we will revolutionize" rhetoric. State the problem as it is.

## 2. Length

A proposal is at most two pages of body text. If you cannot fit it in two pages, you are mixing in implementation detail. Move the detail to `design.md` and reference it.

## 3. The `## Why` Section

`## Why` is 1-2 sentences. It states the problem or opportunity, and why the change is happening now. It does not describe the solution.

Bad:

> We will introduce a new lifecycle phase for Skill Forge skills, with phases A, B, C, and D, using a state machine implemented in `src/skill_forge/lifecycle/`.

Good:

> Generated Skill packages currently have no lifecycle state, which makes it hard to know whether a package is fresh, stale, or ready for promotion. Adding a lifecycle state would let users decide when to upgrade.

The first version describes the solution. The second version describes the problem and the opportunity. The solution is decided later, in the spec and design.

## 4. The `## What Changes` Section

This is a bullet list. Each bullet is a single, concrete change. Mark breaking changes with `**BREAKING**` at the start of the bullet.

Rules:

- One bullet per change. If a bullet contains "and", it is two bullets.
- The bullet describes the change, not the rationale. Rationale goes in `## Risks` or `## Rollback`.
- A bullet that says "we will improve X" is not a change. State what specifically improves.

## 5. The `## Capabilities` Section

Capabilities are the bridge between proposal and spec. Each capability listed here becomes a spec file. If you list a capability, you must be willing to write a spec for it. If you cannot, the capability is not yet scoped enough; either tighten it or remove it.

### New Capabilities

- Use kebab-case names. `user-auth`, `data-export`, `api-rate-limiting`.
- The name becomes the spec folder name and the file `specs/<name>/spec.md`.
- The description is one line. It is restated in the spec's `## Purpose` section.

### Modified Capabilities

- Use the existing spec folder name from `openspec/specs/`.
- Each modified capability needs a `## MODIFIED Requirements` section in the new spec file.
- Only list a capability here if its REQUIREMENTS are changing. Implementation-only changes (refactors, internal cleanup) do not belong here.

### Removed Capabilities

- Use the existing spec folder name from `openspec/specs/`.
- Each removed capability needs a `## REMOVED Requirements` section in the new spec file, with `**Reason**` and `**Migration**`.

## 6. The `## Impact` Section

`## Impact` lists what the change touches. Use bullet sub-headings:

- Code: which modules
- CLI: which commands or surfaces
- Schemas: which stored artifacts change shape
- Workspaces: backward-compatibility note for existing user data

A proposal that does not list schemas is incomplete. If a stored artifact shape changes, the proposal must say so.

## 7. The `## Non-Goals` Section

`## Non-Goals` is a bullet list of what the change is explicitly NOT doing. It is the most important section for scope control. A reviewer will check this section against the spec to confirm the change did not expand.

Non-goals are not "future work". They are explicit boundaries. If a future change should do X, list X in `## Follow-up Changes` of the verification report, not in `## Non-Goals`.

## 8. The `## Risks` Section

Top 3 risks, each with a one-line mitigation. Format: `[Risk] -> [mitigation]`.

A proposal with more than 5 risks is a sign that the change is too broad. Either tighten the scope or split into multiple changes.

## 9. The `## Rollback` Section

The exact steps to revert the change if it lands broken. For a doc-only change, this is "revert the commit". For a schema change, it is "revert the schema files and bump the version back". For a runtime change, it is "revert the affected modules, archive the change as a no-op".

A proposal that does not describe a rollback is not safe to merge.

## 10. The `## Consistency With Brainstorm` Section

Required when `brainstorm.md` exists in the change folder. It states:

- The path to the brainstorm file (`brainstorm.md`).
- The recommended option in the brainstorm.
- Any deviations and the reason.

A proposal that contradicts the brainstorm without explanation will be sent back to the brainstorm step.

## 11. Common Mistakes

- **The proposal is a design doc.** Move detail to `design.md`.
- **The proposal lists capabilities that do not need a spec.** If the change is config-only or doc-only, you may have zero capabilities. List nothing under `### New Capabilities`.
- **The proposal hides the impact.** Schema changes, CLI changes, and workspace-impacting changes must be visible in `## Impact`.
- **The proposal promises performance numbers.** Performance numbers belong in the verification report of the implementing change, after the change is done. A proposal that promises "50% faster" is making an unverified claim.
- **The proposal references chat history.** "As we discussed" is not a source of truth. Cite files by path.

## 12. Reviewer Checklist

A reviewer should be able to answer "yes" to all of the following:

- Does the `## Why` state a problem, not a solution?
- Is the change scope clear from `## What Changes`?
- Are all listed capabilities realistically spec-able?
- Is the schema impact explicit in `## Impact`?
- Are the non-goals specific enough to block scope expansion?
- Are the top 3 risks named, with mitigations?
- Is the rollback path concrete?

If any answer is "no", the proposal needs another draft.
