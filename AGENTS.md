# AGENTS.md

Universal entry point for every AI Agent that touches the `skill-forge` repository.

This file is **read first** by Codex, Claude Code, opencode, and any other Agent before they do anything else. It defines what the project is, what an Agent is allowed to do, and the order in which Agent-specific instructions must be read.

## 1. Project Positioning

`skill-forge` is **not** a generic Python CLI project. It is a local-first Skill generation and AI Harness governance tool:

- It generates, validates, updates, searches, and installs AI agent `SKILL.md` packages.
- It is the host project for an evolving **OpenSpec + SuperSpec + Superpowers + Project Harness** governance stack.
- Future evolution (lifecycle, schema, policy, multi-agent workflow) is governed by the artifacts in `openspec/`, `docs/`, and the Agent entry points in this directory.

Treat the project as a governed workspace, not a free-form codebase. The CLI is one product surface, not the project itself.

## 2. Required Reading Order

Every Agent must read files in the following order before acting:

1. `AGENTS.md` (this file) — universal rules.
2. The tool-specific entry point:
   - Codex → `CODEX.md`
   - Claude Code → `CLAUDE.md`
   - opencode → `OPENCODE.md`
3. When the work involves execution discipline, methodology, or skill phases, read `SUPERPOWERS.md`.
4. When the work involves project context, product, or architecture, read `README.md` (or `README.zh-CN.md`) and the relevant `docs/` files.

Reading order is mandatory. Skipping ahead is a scope violation.

## 3. Agent Role Split

| Agent       | Primary role                                          | May also do (only when explicitly authorized) |
|-------------|-------------------------------------------------------|-------------------------------------------------|
| Codex       | Design, planning, brainstorming, OpenSpec/SuperSpec change artifacts | Review of implementation evidence; advisory review of plans |
| Claude Code | Implementation, tests, verification, evidence collection | Commit preparation when the user explicitly asks |
| opencode    | Fallback execution under strict scope                 | Nothing beyond the granted scope                |
| Superpowers | Execution discipline — methodology, not authority      | Not applicable — Superpowers is not an Agent that produces diffs |
| Project Harness (`AGENTS.md` + `CLAUDE.md` + `docs/`) | Source of Skill Forge-specific constraints | Not applicable |

The split is enforced by scope rules (Section 5), not by prompts.

## 4. Governance Stack

The project's governance is layered. Each layer owns a specific concern:

```text
OpenSpec                          — owns lifecycle (proposal → design → tasks → verify → archive)
SuperSpec-style artifacts         — own structured change assets (spec deltas, design, tasks)
Superpowers                       — owns execution discipline (TDD, debugging, verification)
Project Harness (AGENTS + CLAUDE) — owns Skill Forge-specific constraints
```

OpenSpec is the lifecycle authority. Superpowers is the methodology authority. Neither is a project-authority for Skill Forge semantics — those come from this file, `CLAUDE.md`, and the docs.

## 5. Strict Modification Boundary

An Agent may only touch files that are explicitly in scope for the current task. Specifically:

- The current task must name the allowed paths.
- If no path list is provided, an Agent must **stop and ask** before writing anything.
- A scoped change must never expand silently:
  - Do not "fix" adjacent files.
  - Do not reformat unrelated code.
  - Do not rename variables or modules to match personal preference.
  - Do not add "while I'm here" refactors.
  - Do not modify dependencies (`pyproject.toml`, `uv.lock`) without explicit authorization.

The forbidden-path rule is absolute. If the task says "do not modify `src/**`", then `src/**` is out of scope for the entire task, including for "small" or "obvious" fixes.

## 6. OpenSpec-First Rule for Non-Trivial Changes

A change is **non-trivial** when it meets **any** of the following:

- Touches more than one module under `src/skill_forge/`.
- Changes a public CLI command surface.
- Changes a stored artifact format (`skill-forge.json`, `eval-report.json`, config schema, blueprint schema).
- Introduces a new lifecycle phase, agent role, or governance rule.
- Modifies any path listed in the task's "forbidden" set.

For any non-trivial change:

1. Read the existing `openspec/specs/` and `openspec/changes/` to see if a related change already exists.
2. If not, create or update an OpenSpec change (`openspec/changes/<change-id>/`).
3. Do not start implementation until the change has at least `proposal.md` and `tasks.md` (or the equivalent SuperSpec artifacts for the current phase).

Trivial direct edits (typos, doc fixes, single-line corrections) do not need an OpenSpec change, but the Agent must still announce the edit before making it.

## 7. Source-of-Truth Rule

Chat history is **not** the only source of truth. Specifically:

- File contents in the repository override anything said in chat.
- `openspec/specs/` overrides ad-hoc design claims.
- `docs/` architecture docs override verbal summaries.
- The latest committed version of a file overrides older copies of the same file.

If chat history and a file disagree, the file wins, and the Agent must call out the disagreement explicitly.

## 8. Verification Before Completion

No Agent may declare a task complete without verification evidence. Evidence must include:

- The exact verification commands run.
- The exit status of each command.
- For diff-producing commands, the list of changed files.
- For test commands, the pass/fail count or a clear "skipped" reason.

If a verification command cannot run, the Agent must record:

- The command as written.
- The reason it could not run (environment, missing tool, blocked dependency).
- Whether the failure is blocking for the current phase.

"Looks good" is not verification. "It compiled" is not verification for tasks that require tests.

## 9. Stop Conditions

An Agent must stop and report (not improvise) when:

- Required context is missing (no OpenSpec change for a non-trivial task).
- The expected file list and the actual file list disagree.
- A forbidden path would have to be modified to complete the task.
- A verification command fails for a reason that is not clearly environmental.
- The user asks for a change that contradicts an OpenSpec decision already on `main`.

Report format on stop: **what was attempted, what was blocked, what is needed to unblock**. Do not silently reduce scope to keep going.

## 10. Minimal Diff Discipline

When in doubt, prefer the smaller diff:

- Edit the smallest set of files that satisfies the task.
- Do not introduce new abstractions for a single occurrence.
- Do not pre-build features "for the next phase".
- Keep the existing public surface stable unless the task explicitly changes it.

## 11. Anti-Patterns

The following are explicitly forbidden and will cause a task to be rejected:

- "I'll just clean this up while I'm here."
- "OpenSpec is overkill for this — I'll just do it."
- "The README said X, but the user probably meant Y."
- "Tests were failing before my change too, so it's not my problem."
- "I'll add this because it might be useful later."
- "I'll commit this since it's done."

When tempted, stop, re-read Sections 5–8, and continue only if the action is still justified.

## 12. Pointers

- Codex entry: see `CODEX.md`.
- Claude Code entry: see `CLAUDE.md`.
- opencode entry: see `OPENCODE.md`.
- Execution discipline: see `SUPERPOWERS.md`.
- Project user docs: see `README.md` / `README.zh-CN.md`.
