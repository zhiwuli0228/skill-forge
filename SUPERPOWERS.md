# SUPERPOWERS.md

This file defines how the `skill-forge` project uses the **Superpowers** methodology.

Superpowers is **execution discipline**, not project authority. It is a set of phase-based skills that guide how an Agent should think and act at each step. It does not define what `skill-forge` is, what its lifecycle is, or which paths are in scope — those are owned by other layers (see Section 2).

## 1. Positioning

Superpowers is the methodology layer. It does not produce design decisions, lifecycle rules, or path-scope lists. It produces **better behavior** at each phase of work:

- Better problem framing at the start.
- Better plans before implementation.
- Better execution discipline during implementation.
- Better debugging when things fail.
- Better evidence before declaring success.

If a Superpowers skill and a project rule conflict, the **project rule wins**. Superpowers never overrides `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`, or any `openspec/` decision.

## 2. Layered Ownership

The project's governance is split across four layers. Each layer owns one concern and is authoritative **only** for that concern.

```text
OpenSpec                          — owns lifecycle (proposal → design → tasks → verify → archive)
SuperSpec-style artifacts         — own structured change assets (spec deltas, design docs, tasks)
Superpowers                       — owns execution discipline (TDD, debugging, verification, review)
Project Harness (this repo)       — owns Skill Forge-specific constraints (scope, paths, semantics)
```

What this means in practice:

- **OpenSpec** decides *whether* a change exists, *what* its scope is, and *when* it is done. It does not decide how the implementation is executed.
- **SuperSpec-style artifacts** carry the structured content of a change (spec deltas, design, tasks, plans). They are the inputs to implementation, not the execution.
- **Superpowers** decides *how* the implementation is executed: what skill to invoke at each phase, what to do when a test fails, what to do before declaring success.
- **Project Harness** (`AGENTS.md`, `CLAUDE.md`, `docs/`, this file) decides *what the project allows*: which paths are in scope, which schemas are stable, which commands are valid, which product semantics are non-negotiable.

A change is correctly governed only if all four layers are aligned. A change that satisfies Superpowers but violates the Project Harness is still wrong.

## 3. Phase Mapping

The phases below are the canonical execution phases. Each phase names a Superpowers skill, the Agent that typically owns it, and the project-layer artifact that anchors it.

| Phase                          | Superpowers skill                  | Typical owner | Anchoring artifact                       |
|--------------------------------|------------------------------------|---------------|------------------------------------------|
| Clarify the problem            | `brainstorm`                       | Codex         | `openspec/changes/<id>/proposal.md`      |
| Plan before implementation     | `writing-plans`                    | Codex         | `openspec/changes/<id>/tasks.md` + `plan.md` |
| Execute the plan               | `executing-plans`                  | Claude Code   | The actual diff                          |
| Behavior changes               | `test-driven-development`          | Claude Code   | Tests written before the implementation  |
| Defect fix                     | `systematic-debugging`             | Claude Code   | Root-cause note + repro test             |
| Review (pre-merge)             | `requesting-code-review` / `receiving-code-review` | Claude Code / Codex | Review comments against the plan |
| Verification before completion | `verification-before-completion`   | All Agents    | Verification log + recorded evidence     |
| Large work isolation           | `subagent-driven-development` / `using-git-worktrees` | Codex / Claude Code | Worktree path or sub-agent prompt log |

Phase ordering is a guideline, not a ritual. A trivial typo fix does not need a brainstorm; a behavior change should not skip TDD just because the diff is small.

## 4. Phase Guidance (Short)

The notes below expand the table for the phases that most often get shortcut.

### 4.1 Brainstorm

Use when:

- The request is ambiguous ("make it better", "add some validation").
- There are multiple reasonable approaches and the choice has long-term cost.
- A new lifecycle phase, governance rule, or schema field is being proposed.

Output:

- 2+ candidate approaches, with explicit tradeoffs.
- A recommendation with reasons.
- A clear "do not do" list.

### 4.2 Writing Plans

Use when:

- The change touches more than one file.
- The change has any non-obvious sequencing (e.g., schema before consumer, migration before deploy).
- The change will be handed to a different Agent for implementation.

Output (`plan.md`):

- Problem statement.
- Allowed paths.
- Forbidden paths.
- Sequenced steps, each with a verification step.
- Acceptance criteria.

### 4.3 Executing Plans

Use when:

- Implementation is in progress.

Behavior:

- Follow the plan step order. Do not reorder steps without reason.
- After each step, run the step's verification before moving on.
- If a step fails, do not silently skip it. Either fix it (with debugging) or stop and report.

### 4.4 Test-Driven Development

Use when:

- The change alters observable behavior (CLI output, stored artifact, evaluator result, public function contract).
- The change is a bug fix with a known repro.

Behavior:

- Write or extend the test first.
- See the test fail for the right reason.
- Make the test pass with the minimum change.
- Do not change the test to match an implementation that does not satisfy the original requirement.

### 4.5 Systematic Debugging

Use when:

- A test fails.
- A verification command exits non-zero.
- The runtime behavior does not match the design.

Behavior:

- Reproduce the failure first.
- Locate the root cause; do not "fix" the symptom.
- Add a regression test that would have caught the bug.
- Only then change the implementation.

### 4.6 Verification Before Completion

Use when:

- About to declare a task done.

Required evidence:

- Exact commands run.
- Exit statuses.
- Pass/fail counts (for tests).
- List of changed files.
- For each "skipped" command, the reason.

If any required verification step is missing, the task is not done.

### 4.7 Subagents and Worktrees

Use when:

- A change is large enough that the primary Agent's context is at risk of compression.
- A change needs isolation from the main working tree (e.g., parallel experiments).

Behavior:

- Subagents are scoped to a single question or task. They are not used to bypass the scope rules in `AGENTS.md`.
- Worktrees are used to isolate large changes. They are not used to hide in-progress work from review.
- Both are subject to the same OpenSpec-first rule: a subagent or worktree may not start work that the main change has not authorized.

## 5. Skill Selection (Cheat Sheet)

```text
brainstorm:                  clarifying the problem and options
writing-plans:               before implementation
executing-plans:             during implementation
test-driven-development:     when behavior changes
systematic-debugging:        for defects
verification-before-completion: always required
requesting-code-review:      before merge
receiving-code-review:       during review
subagent-driven-development: only for large work
using-git-worktrees:         only for isolated large changes
```

## 6. Pointers

- Universal rules: `AGENTS.md`.
- Design and planning: `CODEX.md`.
- Primary implementation: `CLAUDE.md`.
- Fallback execution: `OPENCODE.md`.
- Project docs: `README.md` / `README.zh-CN.md`.
