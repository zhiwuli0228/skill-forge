# Agent Workflow

## Purpose

This document defines the per-agent workflow for Codex, Claude Code, and opencode in the Skill Forge repository, the conditions under which an agent must stop and ask, the file scope rules, the dirty worktree handling rules, and the commit rules.

## Scope

- Applies to: every agent run against the Skill Forge repository.
- Owns: the per-agent workflow, scope discipline, and dirty worktree handling.
- Does **not** own: per-flow verification mechanics (see `verification-policy.md`) or governance mechanics (see `docs/03-openspec/`).

## Current Rules

### 1. Codex Workflow

Codex is the **design and planning agent**.

1. Read `AGENTS.md`, then `CODEX.md`, then `SUPERPOWERS.md`.
2. Re-read the relevant repository state: `openspec/specs/`, recent `openspec/changes/`, the relevant `docs/`, the modules that will be affected, and any existing `skill-forge.json` provenance.
3. When the user's request is ambiguous, invoke the `brainstorm` skill from `SUPERPOWERS.md`. Produce 2+ candidate approaches, their tradeoffs, and a recommendation. A single-approach response to an ambiguous request is a stop.
4. For a non-trivial change, draft the OpenSpec change: `proposal.md` first, then `specs/<capability>/spec.md`, then `design.md`, then `review.md` (with verdict `approve` before plan and tasks are drafted).
5. Draft `plan.md` with explicit **allowed paths** and **forbidden paths**, sequenced steps, and per-step verification.
6. Draft `tasks.md` with checkbox-tracked steps and observable completion conditions.
7. Hand off to the implementation agent with the change id, the plan, and the verification command list.
8. After implementation, review the evidence in `verification.md` and update the change status.

Codex must not, in the default flow, perform implementation in `src/`, `tests/`, `templates/`, `configs/`, or `scripts/`. Codex must not commit or push.

### 2. Claude Code Workflow

Claude Code is the **implementation and verification agent**.

1. Read `AGENTS.md`, then `CLAUDE.md`, then `SUPERPOWERS.md`.
2. Read the change's `plan.md` and `tasks.md`. Record the allowed paths and the forbidden paths before touching any file.
3. Confirm the OpenSpec change is on disk. If it is not, stop and report.
4. Execute the plan step by step. After each step, run the step's verification before moving on. If a step fails, invoke `systematic-debugging` from `SUPERPOWERS.md` and only then change code.
5. When the change alters observable behavior (CLI output, stored artifact, evaluator result, public function contract), follow `test-driven-development` from `SUPERPOWERS.md`. Write the test first, see it fail for the right reason, make it pass with the minimum change.
6. Mark completed tasks in `tasks.md` with `- [x]`. Do not edit `proposal.md`, `design.md`, or `plan.md` mid-flight.
7. Run the full governance check: `python scripts/governance_check.py`. If any check fails, stop and report.
8. Write `verification.md` with the exact commands run, exit statuses, and observed outputs.
9. Prepare a commit when the user explicitly asks. Do not push without a separate explicit instruction.

### 3. opencode Fallback Workflow

opencode is the **fallback execution agent** under strict scope.

1. Read `AGENTS.md`, then `OPENCODE.md`, then `SUPERPOWERS.md`.
2. Confirm the change is fully specified by a `plan.md` / `tasks.md` produced by Codex, **or** the user gave a single, narrow, file-scoped instruction.
3. Produce and record the pre-edit checklist: expected files to be modified, expected verification commands, expected exit criteria, known risks. If any of these is not producible, stop and report.
4. Touch only the paths in the checklist. Refuse to "fix" a file not on the list, refuse to create new files outside the list, refuse to read a forbidden path unless the read is required to understand a current file (and record the read).
5. Do not perform full-repository rewrites, broad refactors, opportunistic cleanup, dependency changes, schema changes, or new governance rules. Each of these is a hard stop.
6. Prefer the smallest possible diff. One file is better than two. A line addition is better than a helper.
7. After editing, report in order: actual files modified, diff between expected and actual, verification commands run with exit codes, verification result, any forbidden path touched (which is a failure, not a warning).
8. If "actual files modified" is not a subset of "expected files to be modified", revert the change and report.

### 4. When to Stop and Ask

Every agent must stop and report (not improvise) when any of the following is true:

- Required context is missing (no OpenSpec change for a non-trivial task).
- The expected file list and the actual file list disagree in a way that affects the diff.
- A forbidden path would have to be modified to complete the plan.
- A verification command fails for a reason that is not clearly environmental.
- The user asks for a change that contradicts an OpenSpec decision already on `main`.
- A re-read of the repository contradicts a previously written plan.
- The task spans both design and implementation and the user has not authorized the cross-role work.

Report format on stop: **what was attempted, what was blocked, what is needed to unblock**. Do not silently reduce scope to keep going.

### 5. File Scope Rules

- The current task must name the allowed paths.
- If no path list is provided, an agent must stop and ask before writing anything.
- A scoped change must never expand silently:
  - Do not "fix" adjacent files.
  - Do not reformat unrelated code.
  - Do not rename variables or modules to match personal preference.
  - Do not add "while I'm here" refactors.
  - Do not modify dependencies (`pyproject.toml`, `uv.lock`) without explicit authorization.
  - Do not modify pre-existing OpenSpec change folders or pre-existing docs files outside the allowed list.
- The forbidden-path rule is absolute. If the task says "do not modify `src/**`", then `src/**` is out of scope for the entire task, including for "small" or "obvious" fixes.
- A new file path is as much a scope decision as a modification. Adding a new file outside the allowed list is the same kind of violation as editing a forbidden file.

### 6. Dirty Worktree Handling Rules

The dirty worktree rule applies to every change.

- Run `git status --short` and `git diff --name-only` before staging. The output is the ground truth for what is about to be committed.
- Use explicit `git add <path>` for every file in the allowed set. **Never** use `git add .` or `git add -A`.
- After staging, run `git diff --cached --stat` and `git diff --cached --name-only` to verify the staged set is exactly the allowed set.
- Do not reset, restore, clean, or delete user WIP. A dirty entry that is not in the allowed set stays in the working tree untracked (or with its original modification) and is not part of the commit.
- Do not commit user WIP into the current change's commit. A future change is the right place for a WIP entry that has not been authorized.
- If the staged set is wrong, use `git restore --staged <path>` to unstage the offending path, re-stage the allowed paths, and re-verify. Do not proceed with a wrong staged set.
- For deletions of tracked files, use `git rm <path>` (not `git add <path>`). `git add` on a deleted tracked file does not stage the deletion.

### 7. Commit Rules

- Do not commit without explicit user permission. Commit preparation is allowed when the user asks; committing is allowed only when the user asks.
- Do not push without a separate explicit instruction. Pushing is never implicit.
- Commit messages follow the repository's convention: a short imperative subject line (e.g., `docs: ...`, `feat: ...`, `fix: ...`, `refactor: ...`) and, when useful, a multi-line body that explains the why and lists the absorbed or deferred items.
- Each commit is the smallest coherent unit of work. Do not bundle unrelated changes into one commit.
- A commit must reference the change id (e.g., `feat(<change-id>): ...` or a body line) when the change is governed by an OpenSpec change folder.

## Related Files

- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md` — agent entry points.
- `docs/02-harness/harness-overview.md` — harness model.
- `docs/02-harness/verification-policy.md` — minimum verification.
- `docs/03-openspec/change-workflow.md` — OpenSpec change lifecycle.
- `docs/04-superpowers/execution-discipline.md` — TDD, debugging, verification.

## What Not To Do

- Do not let Codex implement. Codex plans; Claude Code implements; opencode executes under strict scope.
- Do not let Claude Code redesign. If the plan is wrong, stop and ask Codex to revise.
- Do not let opencode expand scope. Strict scope is the fallback's safety net.
- Do not use `git add .` or `git add -A`. Always use explicit `git add <path>`.
- Do not commit user WIP into a change's commit. The change's commit is the change's commit.
- Do not push without explicit user instruction.
- Do not skip the stop conditions. Stopping is a feature, not a failure.
- Do not invent a new agent role or governance rule without an OpenSpec change.
