# Skill Usage Policy

This document defines which **Superpowers skill** to invoke at which **OpenSpec phase** in the Skill Forge project. It is the project-level selection policy; the methodology for each skill is in `execution-discipline.md`.

## 1. Decision Rule

The decision rule for invoking a Superpowers skill is:

1. Identify the current OpenSpec phase (see `docs/03-openspec/change-workflow.md`).
2. Identify the most specific Superpowers skill that matches the work being done.
3. Invoke it. If no skill matches, document the gap in `.superpowers/execution-checklist.md` and proceed with the schema's rules as a fallback.

The list below is the canonical mapping. The Agent may skip a skill only when the work is trivial and the schema's rules are sufficient. For non-trivial work, the skill is **required**, not optional.

## 2. Phase-to-Skill Mapping

### 2.1 `brainstorm` — Problem Clarification

- **Phase**: before proposal, when the problem is ambiguous.
- **Required for**: changes that introduce a new lifecycle phase, agent role, governance rule, or schema field. Also required for breaking changes.
- **Optional for**: trivial changes and well-scoped features.
- **Output**: a `brainstorm.md` with at least two candidate approaches, explicit assumptions, and a recommendation.
- **Pitfall**: writing code, templates, or schema files during brainstorm. Output is plain Markdown only.

### 2.2 `writing-plans` (lite) — Proposal, Spec, Design

- **Phase**: when drafting proposal, spec, and design.
- **Usage**: invoke once for the proposal, once for the spec, once for the design. Each invocation produces a single artifact.
- **Output**: a single artifact that is consistent with the prior artifacts in the change folder.
- **Pitfall**: treating the three artifacts as one document. They are three artifacts. The schema enforces this.

### 2.3 `requesting-code-review` — Review

- **Phase**: when forming the review verdict.
- **Required for**: every change that reaches the review step.
- **Output**: a `review.md` with verdict `approve`, `request-changes`, or `block`.
- **Pitfall**: giving verdict `approve` by default. A review is not a rubber stamp; it is a gate.

### 2.4 `executing-plans` — Implementation

- **Phase**: when `tasks.md` is being applied.
- **Required for**: every change that has a `tasks.md`.
- **Output**: completed tasks (marked `- [x]`) and a draft `verification.md`.
- **Pitfall**: skipping a task's verification step. Each task has a verification; the implementer runs it before marking the task done.

### 2.5 `test-driven-development` — Behavior Change

- **Phase**: when the change alters observable behavior.
- **Required for**: any change that adds or modifies a CLI command, a stored artifact schema, a validation result, or an evaluation outcome.
- **Output**: tests written before the implementation. The test must fail for the right reason before the change is made.
- **Pitfall**: changing the test to match a broken implementation. The test encodes the requirement; the implementation satisfies the test.

### 2.6 `systematic-debugging` — Defect Fix

- **Phase**: when a test fails, a verification command exits non-zero, or behavior regresses.
- **Required for**: every defect that surfaces during a change.
- **Output**: a reproducer, a root-cause note, a regression test, and a fix.
- **Pitfall**: changing the implementation to make the test pass without understanding the root cause. The test is a signal, not a target.

### 2.7 `verification-before-completion` — Completion Claim

- **Phase**: before declaring a change done.
- **Required for**: every change.
- **Output**: `verification.md` with executed commands, results, skipped commands, deviations, risks, and verdict.
- **Pitfall**: claiming done before running the final verification commands. "It looks done" is not verification.

### 2.8 `subagent-driven-development` — Large Work

- **Phase**: when the change is large enough that the primary Agent's context is at risk of compression.
- **Required for**: changes that touch more than 5 modules, or that span both runtime code and governance schema.
- **Output**: sub-agent prompts and their summaries, recorded in `.superpowers/execution-checklist.md`.
- **Pitfall**: using subagents to bypass the scope rules in `AGENTS.md` or `CLAUDE.md`. A subagent is scoped to a single question or task; it is not a license to expand scope.

### 2.9 `using-git-worktrees` — Isolation

- **Phase**: when a change needs to be isolated from the main working tree (e.g., parallel experiments, long-running branches).
- **Required for**: changes that the implementer expects to last more than a week, or that involve experiments.
- **Output**: a worktree path, recorded in `.superpowers/execution-checklist.md`.
- **Pitfall**: using a worktree to hide in-progress work from review. Worktrees are for isolation, not concealment.

## 3. Skill Selection by Change Type

The following table maps change types to the required skills. "Always" means the skill is required for every change of that type. "When applicable" means the skill is required only when the condition is met.

| Change type                            | brainstorm | writing-plans | executing-plans | TDD | systematic-debugging | verification-before-completion | subagents | worktrees |
|----------------------------------------|------------|---------------|-----------------|-----|----------------------|--------------------------------|-----------|-----------|
| Trivial doc fix                        | -          | -             | -               | -   | When applicable      | Always                         | -         | -         |
| New CLI command                        | When applicable | Always | Always          | Always | When applicable    | Always                         | When applicable | -         |
| New schema field                        | Always     | Always        | Always          | Always | When applicable    | Always                         | When applicable | -         |
| New governance rule                     | Always     | Always        | Always          | When applicable | When applicable | Always                         | When applicable | -         |
| Refactor (no behavior change)           | When applicable | Always | Always     | -    | When applicable      | Always                         | When applicable | -         |
| Bug fix                                 | When applicable | When applicable | Always | Always | Always          | Always                         | When applicable | -         |
| Cross-cutting change                    | Always     | Always        | Always          | Always | When applicable    | Always                         | Always    | When applicable |

The table is a guide, not a checklist. The Agent must apply judgment. When in doubt, invoke the skill.

## 4. Skill Stacking

Multiple skills can be invoked in a single phase. The order matters:

1. `brainstorm` first (before any artifact).
2. `writing-plans` (lite) for each of proposal, spec, design.
3. `requesting-code-review` for review.
4. `executing-plans` for implementation.
5. `test-driven-development` for each behavior-change task.
6. `systematic-debugging` whenever a verification step fails.
7. `verification-before-completion` at the end.
8. `subagent-driven-development` and `using-git-worktrees` are orthogonal; they can be invoked at any phase.

A skill invocation may pause and report a blocker. The Agent must not skip past a blocker; it must report and wait for the user to redirect.

## 5. Skill Non-Usage

The following are NOT Superpowers skills and should not be invoked as if they were:

- "I'll just clean this up while I'm here." That is opportunistic refactoring. It is forbidden by `AGENTS.md` and is not a Superpowers skill.
- "I'll do a quick sanity check." That is a substitute for verification. Run the actual verification.
- "I'll add a TODO and move on." TODOs are not a substitute for completed tasks. A task is done when its observation is observed.

When the temptation arises, return to the skill mapping and continue only if the action is still justified.

## 6. Cross-References

- Skill methodology: `execution-discipline.md`.
- Subagent and worktree rules: `subagent-policy.md`.
- Project configuration: `.superpowers/skill-usage-policy.md`.
