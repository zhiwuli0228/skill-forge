# Harness Overview

## Purpose

This document defines what "the project-level AI Harness" means in the Skill Forge repository, names the agents and tools that participate in the harness, and states the rules every agent must follow when making a non-trivial change.

## Scope

- Applies to: every AI agent (Codex, Claude Code, opencode, or any other) that writes to the repository.
- Owns: the harness model, the agent split, and the mandatory rules for non-trivial changes.
- Does **not** own: per-agent workflow details (see `agent-workflow.md`), verification mechanics (see `verification-policy.md`), or governance mechanics (see `docs/03-openspec/`).

## Current Rules

### 1. What the Harness Is

The project-level AI Harness is the set of entry points, scopes, and obligations that an AI agent must read and respect when working in the Skill Forge repository. It is the project's contract with every agent, regardless of vendor. The harness is not a tool; it is the boundary between "the agent is acting on the user's behalf" and "the agent is making decisions that belong to the project".

The harness has five components:

- **Agent entry points** — the root-level files `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md`. These are read in order and define roles, prohibitions, and reading order.
- **OpenSpec** — the lifecycle authority for changes. Owns `openspec/changes/`, `openspec/specs/`, and the `skill-forge-governance` schema.
- **Superpowers** — the execution discipline. Owns `docs/04-superpowers/` and the methodology skills (`brainstorm`, `writing-plans`, `executing-plans`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`).
- **Governance check** — `scripts/governance_check.py` (and the underlying `openspec validate` + CLI smoke + pytest) is the executable gate that records the harness's expectations.
- **Project docs** — `docs/01-architecture/`, `docs/05-development/`, `docs/06-domain/`, etc. These are the Skill Forge-specific constraints the methodology layers must respect.

### 2. How the Parts Fit Together

```text
User intent
    |
    v
Agent entry points (AGENTS.md -> CODEX.md / CLAUDE.md / OPENCODE.md -> SUPERPOWERS.md)
    |
    v
OpenSpec change folder (openspec/changes/<change-id>/)        <-- lifecycle
    |
    v
Superpowers phase (brainstorm / writing-plans / TDD / verify) <-- methodology
    |
    v
Implementation in src/, tests/, templates/, configs/         <-- change
    |
    v
Governance check (scripts/governance_check.py)               <-- gate
    |
    v
Commit (when the user explicitly asks)                       <-- hand-off
```

The reading order is mandatory. An agent that skips `AGENTS.md` and reads `CLAUDE.md` directly is operating outside the harness.

### 3. Codex, Claude Code, opencode, OpenSpec, Superpowers, Governance Check

| Component | Role | Authoritative for | Not authoritative for |
|---|---|---|---|
| Codex | Design, planning, OpenSpec change artifacts | `openspec/changes/<id>/proposal.md`, `design.md`, `plan.md`, `tasks.md` | Implementation diffs, commit preparation, pushing |
| Claude Code | Implementation, tests, verification, evidence collection | The actual diff in `src/`, `tests/`, `templates/`, `configs/`; `verification.md` of a change | Design decisions, OpenSpec lifecycle status, pushing |
| opencode | Fallback execution under strict scope | Small, well-scoped diffs explicitly listed in a plan | Anything structural, anything outside the listed paths |
| OpenSpec | Change lifecycle authority | Change artifacts, `openspec/specs/`, `openspec/changes/archive/` | How a change is implemented |
| Superpowers | Execution discipline | Phase-to-skill mapping, TDD, debugging, verification-before-completion | Skill Forge-specific constraints, path scope, schemas |
| Governance check (`scripts/governance_check.py`) | Executable gate | The exit code on the CI-like local run | What the change should be |

A Superpowers skill never overrides `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`, or any `openspec/` decision. A Project Harness rule never relaxes a Superpowers execution rule.

### 4. Mandatory Rules for Non-Trivial Changes

A change is non-trivial when it meets any of the conditions in `AGENTS.md` Section 6: it touches more than one module under `src/skill_forge/`, changes a public CLI surface, changes a stored artifact format (`skill-forge.json`, `eval-report.json`, config schema, blueprint schema), introduces a new lifecycle phase, agent role, or governance rule, or modifies any path the task lists as forbidden.

For a non-trivial change:

1. An OpenSpec change folder must exist under `openspec/changes/<change-id>/` before implementation starts. The folder must contain at least `proposal.md` and `tasks.md`.
2. The change must declare its **allowed paths** and **forbidden paths** explicitly in `plan.md`. The implementation agent must not touch a path outside the allowed set.
3. The implementation agent must run `python scripts/governance_check.py` (full mode, not just `--quick`) before declaring the change done.
4. The implementation agent must record verification evidence in the change's `verification.md`. Chat history is not verification.
5. The user must explicitly ask for a commit. The user must explicitly ask for a push.

### 5. Planning Agent vs. Implementation Agent

The split between planning and implementation is enforced by scope rules, not by prompts.

- The **planning agent** (typically Codex) produces the OpenSpec change artifacts: `proposal.md`, `design.md`, `plan.md`, `tasks.md`, and the per-capability `spec.md`. The planning agent reads `AGENTS.md`, then `CODEX.md`, then `SUPERPOWERS.md`, then the relevant `docs/`. The planning agent does not touch `src/`, `tests/`, `templates/`, `configs/`, or `scripts/` for implementation.
- The **implementation agent** (typically Claude Code) reads the change's `plan.md` and `tasks.md`, follows the plan step by step, runs each step's verification, and records evidence in `verification.md`. The implementation agent reads `AGENTS.md`, then `CLAUDE.md`, then `SUPERPOWERS.md`. The implementation agent may not modify the change's `proposal.md`, `design.md`, or `plan.md` except to mark tasks done in `tasks.md` and to write `verification.md`.

The two agents do not edit each other's work. If the implementation finds a plan that is wrong, the implementation stops and reports. The planning agent revises the plan; the implementation agent re-runs.

### 6. What the Harness Will Not Do

- The harness will not relax a Superpowers execution rule because a project rule says so.
- The harness will not let the implementation agent "fix" a forbidden path because the fix is "obvious".
- The harness will not treat chat history as the source of truth. The repository wins.
- The harness will not let an agent declare a task done without recorded evidence.
- The harness will not push to a remote without explicit user instruction.

## Related Files

- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md` — agent entry points.
- `docs/02-harness/agent-workflow.md` — per-agent workflow rules.
- `docs/02-harness/verification-policy.md` — minimum verification per change type.
- `docs/03-openspec/change-workflow.md` — OpenSpec change lifecycle.
- `docs/04-superpowers/superpowers-overview.md` — Superpowers positioning.
- `scripts/governance_check.py` — the governance check script.

## What Not To Do

- Do not skip the entry-point reading order. `AGENTS.md` is read first; the tool-specific entry point is read second; `SUPERPOWERS.md` is read when execution discipline is relevant.
- Do not let the implementation agent touch `proposal.md`, `design.md`, or `plan.md` mid-flight. If a plan is wrong, stop and ask the planning agent to revise.
- Do not start implementation of a non-trivial change without an OpenSpec change folder.
- Do not run a "while I'm here" refactor across modules.
- Do not declare a change done without recorded verification evidence.
- Do not treat the harness as advisory. The rules are mandatory; the gate is executable.
