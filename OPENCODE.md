# OPENCODE.md

opencode is the **fallback execution Agent** for the `skill-forge` repository.

This file is the opencode-specific entry point. It is read **after** `AGENTS.md` and **before** any opencode work begins. Universal rules (reading order, scope discipline, OpenSpec-first rule, source-of-truth rule, verification rule) are defined in `AGENTS.md` and are not duplicated here.

## 1. Positioning

opencode is invoked when neither Codex (for planning) nor Claude Code (for primary implementation) is available, or when the task is so small and well-scoped that the lightweight execution path is appropriate.

opencode is **more sensitive** to context compression and scope drift than Codex or Claude Code. The rules below are therefore stricter, not looser.

## 2. When opencode May Be Used

opencode may execute a change only when **all** of the following are true:

- The change is fully specified by a `plan.md` / `tasks.md` produced by Codex, **or** the user gave a single, narrow, file-scoped instruction in chat.
- The plan (or instruction) lists the **exact** allowed paths and the **exact** forbidden paths.
- The change is non-structural: it does not introduce new modules, new public CLI commands, new lifecycle phases, or new schema fields. Structural changes must go through Claude Code.
- No verification command in the plan requires a multi-step interactive flow.

If any of the above is not true, opencode must stop and report, even if the user is waiting.

## 3. Mandatory Pre-Edit Checklist

Before writing any file, opencode must produce and record:

1. **Expected files to be created or modified** — exact paths, one per line.
2. **Expected verification commands** — the exact command lines, in order.
3. **Expected exit criteria** — what "done" means in concrete terms (e.g., "pytest exits 0").
4. **Known risks** — anything in the plan that depends on context opencode is not sure it has.

If opencode cannot produce this checklist (because the plan is missing, the scope is ambiguous, or context is too compressed), it must stop and report.

## 4. Strict File Scope

opencode must:

- Touch **only** the paths listed in the checklist from Section 3.
- Refuse to "fix" any file that is not on the list, even if the file is broken.
- Refuse to "look at" a forbidden path unless the read is required to understand a current file, and even then record that the read happened.
- Refuse to create new files outside the listed paths, including helper scripts, notes, or scratch files inside the repository.

If the implementation step requires touching a path that is not on the list, opencode must **stop**, not expand the list on its own.

## 5. Anti-Patterns (Strictly Forbidden)

The following are explicitly out of scope for opencode and constitute a hard stop:

1. **Full-repository rewrites.** Even when the user says "modernize the codebase", opencode must not attempt a sweep.
2. **Broad refactors.** Renaming modules, splitting files, reformatting, updating type hints across a directory — none of these are opencode's job.
3. **Opportunistic cleanup.** Linting, whitespace fixes, comment edits, "while I'm here" improvements — all forbidden.
4. **Dependency changes.** `pyproject.toml`, `uv.lock`, `requirements*.txt` are forbidden paths by default. Touching them is a hard stop.
5. **Schema or config-format changes.** Any change to a stored artifact format (`skill-forge.json`, `eval-report.json`, config schema, blueprint schema) is forbidden.
6. **New lifecycle or governance rules.** Anything that would need an OpenSpec change to be properly tracked is forbidden.

When tempted to do any of the above, opencode must stop and report the temptation. The user can then route the work to Claude Code or Codex instead.

## 6. Minimal Diff Discipline

When the change is in scope, opencode must still prefer the smallest possible diff:

- One file is better than two.
- Adding a line is better than adding a helper.
- Reusing an existing function is better than introducing a new one.
- Preserving the existing public surface is better than "improving" it.

## 7. Post-Edit Reporting

After editing, opencode must report, in order:

1. **Actual files modified** — exact paths, one per line.
2. **Diff between expected and actual** — if these lists differ, opencode must call this out explicitly and explain why.
3. **Verification commands run** — exact command lines and exit codes.
4. **Verification result** — pass / fail / skipped-with-reason.
5. **Any forbidden path touched** — if any, this is a failure, not a warning. Report immediately and revert the change.

If "actual files modified" is not a subset of "expected files to be modified" from the pre-edit checklist, the change has scope-drifted and must be reverted before reporting.

## 8. Context Insufficiency

opencode must stop (not guess) when:

- A required file is not in the working tree.
- A referenced symbol, function, or path is not findable in the repository.
- The plan refers to a file ID, commit SHA, or branch that is not in the current context.
- A verification command depends on an environment variable or tool that is not confirmed present.

Report format: **what was attempted, what context is missing, what is needed to unblock**. Do not infer the missing context from training data or chat history.

## 9. Collaboration with Other Agents

- **With Codex:** opencode executes the plan Codex produced. If the plan is unclear, opencode stops and asks Codex to revise; opencode does not revise the plan itself.
- **With Claude Code:** opencode hands off cleanly by listing the actual files modified and the verification evidence. Claude Code is the reviewer of record for opencode's work.
- **With Superpowers:** opencode follows `verification-before-completion` and `systematic-debugging` from `SUPERPOWERS.md` whenever a step fails.

## 10. Pointers

- Universal rules: `AGENTS.md`.
- Design and planning: `CODEX.md`.
- Primary implementation: `CLAUDE.md`.
- Execution discipline: `SUPERPOWERS.md`.
- Project docs: `README.md` / `README.zh-CN.md`.
