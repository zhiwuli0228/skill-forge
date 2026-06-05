# Project Skill Usage Policy

This file is the **project-local skill usage policy** for Superpowers in the Skill Forge repository. It is a quick-reference for the Agent. The canonical policy is in `../docs/04-superpowers/skill-usage-policy.md`. This file mirrors the canonical and adds project-specific quick rules.

## 1. Quick Decision Tree

When the Agent is about to do work, walk this tree:

1. Is the work trivial (typo, single-line edit, doc wording)?
   - Yes: skip Superpowers; use the schema's rules and verify.
   - No: continue.
2. Is the work non-trivial and the problem ambiguous?
   - Yes: invoke `brainstorm`. Write `brainstorm.md` before any other artifact.
   - No: continue.
3. Is the work an OpenSpec change?
   - Yes: invoke `writing-plans` (lite) for each of proposal, spec, design. Then `requesting-code-review` for the review.
   - No: continue.
4. Is the work an implementation?
   - Yes: invoke `executing-plans`. For each behavior-change task, invoke `test-driven-development`.
   - No: continue.
5. Did a verification step fail?
   - Yes: invoke `systematic-debugging`. Do not modify the test or the implementation until the root cause is found.
   - No: continue.
6. Are you about to claim the change is done?
   - Yes: invoke `verification-before-completion`. Write `verification.md` with the required evidence.
   - No: continue.
7. Is the change large (more than 5 modules) or context-heavy?
   - Yes: invoke `subagent-driven-development` for parallelizable research, and `using-git-worktrees` for isolation.
   - No: continue.
8. Is there no matching skill for the work?
   - Yes: document the gap in `.superpowers/execution-checklist.md` and proceed with the schema's rules.

## 2. Skill Triggers (Cheat Sheet)

| Trigger                                                | Skill                       |
|--------------------------------------------------------|-----------------------------|
| "I am about to write a new artifact for a non-trivial change." | `brainstorm` (if ambiguous) then `writing-plans` (lite) |
| "I am about to give a review verdict."                 | `requesting-code-review`    |
| "I am starting to apply tasks.md."                     | `executing-plans`           |
| "This change alters CLI output, an artifact, or a behavior." | `test-driven-development`   |
| "A test is failing or a verification command exited non-zero." | `systematic-debugging`      |
| "I am about to claim the change is done."              | `verification-before-completion` |
| "The change is large and I am worried about context."  | `subagent-driven-development`, `using-git-worktrees` |
| "I am tempted to clean up an unrelated file."          | STOP. Surface as a follow-up. |

## 3. Project-Specific Rules

The following rules are project-specific and override the generic Superpowers defaults:

- **Always run `openspec validate --strict` before claiming done.** This is in addition to pytest. The two together are the contract.
- **Never touch `src/**`, `tests/**`, `templates/**`, `configs/**` without an in-flight OpenSpec change that names them.** The change's `plan.md` `## Allowed Paths` is the authority.
- **Read `AGENTS.md` first, then `CLAUDE.md` (or `CODEX.md` / `OPENCODE.md`), then `.superpowers/project-profile.md`.** This is the project-specific reading order.
- **Use the templates under `openspec/schemas/skill-forge-governance/templates/`.** Do not invent your own structure.
- **Mark every `verification.md` with the change's verdict and a date.** A `verification.md` without a verdict is incomplete.

## 4. Skill Stacking Order

When multiple skills apply in a single phase, the order is:

1. `brainstorm` (if applicable)
2. `writing-plans` (lite) for each artifact
3. `requesting-code-review` (review step)
4. `executing-plans` (implementation)
5. `test-driven-development` (per behavior-change task)
6. `systematic-debugging` (per failure)
7. `verification-before-completion` (at the end)
8. `subagent-driven-development` and `using-git-worktrees` (orthogonal; can be invoked at any phase)

## 5. Cross-References

- Canonical policy: `../docs/04-superpowers/skill-usage-policy.md`
- Execution discipline: `../docs/04-superpowers/execution-discipline.md`
- Subagent policy: `../docs/04-superpowers/subagent-policy.md`
- Project profile: `./project-profile.md`
- Execution checklist: `./execution-checklist.md`
