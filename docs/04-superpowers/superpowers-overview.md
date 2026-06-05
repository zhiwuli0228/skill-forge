# Superpowers Overview

This document explains what **Superpowers** is in the Skill Forge governance stack, what it owns, what it does not own, and how it relates to OpenSpec and the Project Harness.

## 1. Positioning

Superpowers is the **execution discipline** layer of the governance stack. It does not produce design decisions, lifecycle rules, or path-scope lists. It produces **better behavior** at each phase of work.

The four-layer governance stack:

```text
OpenSpec                          — owns lifecycle (proposal -> design -> tasks -> verify -> archive)
SuperSpec-style schema            — owns structured change artifacts
Superpowers                       — owns execution discipline (TDD, debugging, verification)
Project Harness (Skill Forge)     — owns Skill Forge-specific constraints
```

A change that satisfies Superpowers but violates the Project Harness is still wrong. A change that satisfies the schema but skips verification is still not done.

## 2. What Superpowers Owns

Superpowers owns:

- The **methodology** used at each phase of an OpenSpec change.
- The **phase-to-skill mapping** that tells an Agent which skill to invoke when.
- The **execution discipline** required for behavior changes (TDD), defect fixes (systematic debugging), and completion claims (verification before completion).
- The **escalation vocabulary** (BLOCKED, request-changes, blocked-by-tooling) that the Project Harness and OpenSpec use to communicate risk.
- The **subagent and worktree policy** for large work.

Superpowers does not own:

- The **structure** of a change artifact. That is the schema's job (`openspec/schemas/skill-forge-governance/`).
- The **Skill Forge-specific constraints**. Those are in `openspec/config.yaml` under `context:` and `rules:`.
- The **runtime code** under `src/`, `tests/`, `templates/`, `configs/`. Superpowers influences how the code is written, not what the code is.

## 3. What This Folder Is

This folder (`docs/04-superpowers/`) is the human-readable reference for how Skill Forge uses Superpowers. The companion folder `.superpowers/` is the project-local configuration that an Agent reads first when it enters the project.

The four docs in this folder:

- `superpowers-overview.md` — this file.
- `skill-usage-policy.md` — which Superpowers skill to invoke at which phase.
- `execution-discipline.md` — TDD, debugging, verification, and how they apply to Skill Forge work.
- `subagent-policy.md` — when to use subagents and worktrees, and the rules for both.

The three project config files in `.superpowers/`:

- `project-profile.md` — the project context Superpowers needs to know about.
- `skill-usage-policy.md` — the project-level skill selection rules.
- `execution-checklist.md` — the pre-/post-execution checklist.

## 4. The Phase-to-Skill Mapping

The phases an OpenSpec change goes through, and the Superpowers skill that anchors each:

| OpenSpec phase                  | Superpowers skill           | When to invoke                                  |
|---------------------------------|-----------------------------|-------------------------------------------------|
| Problem clarification            | `brainstorm`                | Before any artifact is written                  |
| Writing the proposal             | `writing-plans` (lite)      | When drafting the proposal and the plan         |
| Writing the spec                | `writing-plans` (lite)      | When drafting the spec scenarios                |
| Writing the design              | `writing-plans` (lite)      | When drafting the design decisions              |
| Review                          | `requesting-code-review`    | When the review verdict is being formed        |
| Implementation                  | `executing-plans`           | When `tasks.md` is being applied                |
| Behavior change                  | `test-driven-development`   | When the change alters observable behavior      |
| Defect fix                       | `systematic-debugging`      | When a test fails or behavior regresses         |
| Completion claim                 | `verification-before-completion` | Before declaring a change done              |
| Large work                       | `subagent-driven-development`, `using-git-worktrees` | When context is at risk or isolation is needed |

The full mapping with rationale is in `skill-usage-policy.md`. The execution discipline for each skill is in `execution-discipline.md`.

## 5. Boundary with the Project Harness

The Project Harness (`AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`, `SUPERPOWERS.md`) defines the rules Agents must follow. Superpowers provides the methodology to follow them well. When the two are in tension:

- The Project Harness is authoritative for Skill Forge-specific constraints (scope, paths, schemas).
- Superpowers is authoritative for methodology (how to think, how to debug, how to verify).

If a Superpowers skill and a Project Harness rule conflict, the **Project Harness wins**. Superpowers never overrides `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`, or any `openspec/` decision.

## 6. Boundary with OpenSpec

OpenSpec owns the lifecycle: which artifact exists when, which status a change is in, when a change is archived. Superpowers does not own any of this. Superpowers is consulted WITHIN each phase of the lifecycle. It does not replace the lifecycle.

A change under OpenSpec is not done until:
- All eight artifacts exist and pass `openspec validate --strict`.
- `verification.md` is written and its verdict is `done` or `done-with-risks`.

A change under Superpowers is not done until:
- The implementation phase followed `executing-plans`.
- Behavior changes followed TDD.
- Defects were fixed with `systematic-debugging`.
- The completion claim was preceded by `verification-before-completion`.

The two definitions of "done" must both be satisfied. Superpowers does not relax OpenSpec; OpenSpec does not relax Superpowers.

## 7. Where to Read Next

- Project entry points: `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`, `SUPERPOWERS.md`.
- Schema and artifact rules: `docs/03-openspec/`.
- Superpowers skill selection: `docs/04-superpowers/skill-usage-policy.md`.
- Execution discipline: `docs/04-superpowers/execution-discipline.md`.
- Subagent and worktree policy: `docs/04-superpowers/subagent-policy.md`.
- Project configuration for Superpowers: `.superpowers/project-profile.md`.
