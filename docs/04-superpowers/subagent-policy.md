# Subagent and Worktree Policy

This document defines the policy for using **subagents** and **git worktrees** in the Skill Forge project. The two mechanisms are related: both are about isolating work. They are not interchangeable, and they are not free.

## 1. When Subagents Apply

A subagent is a secondary Agent invocation that runs in its own context, with its own prompt, and returns a summary. Subagents are used when:

- The primary Agent's context is at risk of compression (a large diff, a long-running task).
- The work is parallelizable (e.g., reading many files, comparing many options).
- A specific question can be answered in isolation (e.g., "what files in `src/skill_forge/` import `pydantic`?").

Subagents are NOT used when:

- The work is small enough to fit in the primary Agent's context.
- The work requires back-and-forth (e.g., clarifying questions). Subagents do not have a channel for back-and-forth.
- The work is the actual implementation. The primary Agent applies the change; the subagent supports the primary.

## 2. Subagent Scope Rules

A subagent is **scoped to a single question or task**. The scope must be explicit in the subagent's prompt:

- What the subagent is asked to do.
- What files the subagent is allowed to read.
- What files the subagent is allowed to write (almost always: nothing).
- What the subagent must return (a specific shape, not a free-form summary).
- What the subagent must not do (e.g., "do not modify any files", "do not run commands that modify state").

A subagent that exceeds its scope is a scope violation. The primary Agent must discard the subagent's output and re-invoke with a tighter scope, or do the work itself.

## 3. Subagent Output Rules

A subagent returns a summary, not a diff. The primary Agent consumes the summary and decides what to do.

A subagent output is acceptable when:

- It is in the requested shape (e.g., a list of file paths, a comparison table).
- It cites the files it read by path.
- It does not contain commands the primary Agent did not ask for.
- It does not contain scope-expanding suggestions ("while I was there, I noticed X — you should also do Y").

A subagent output that violates these rules is rejected. The primary Agent must re-invoke with a tighter scope, or do the work itself.

## 4. Subagent Logging

Every subagent invocation is logged in `.superpowers/execution-checklist.md` under "Subagent Usage". The log entry includes:

- The date and time.
- The subagent's task (one line).
- The subagent's allowed files (or "read-only").
- The subagent's output (or a link to it if it is long).
- The primary Agent's decision based on the output.

The log is the audit trail. A subagent invocation without a log entry is treated as if it did not happen.

## 5. When Worktrees Apply

A worktree is a separate working tree of the same git repository, on a different branch. Worktrees are used when:

- A change is expected to last more than a week.
- A change involves experiments (e.g., trying multiple approaches).
- Two changes need to be in flight in parallel (e.g., a feature and a hotfix).
- A change touches a file that another in-flight change also touches, and the conflict must be resolved in isolation.

Worktrees are NOT used when:

- The change is small and quick. A worktree is overhead.
- The change does not need to be isolated. A worktree without a reason is ceremony.
- The change is the only thing in flight. A worktree without parallel work is unnecessary.

## 6. Worktree Scope Rules

A worktree is scoped to a single change or experiment. The scope must be explicit:

- The branch name. Format: `change/<change-id>` or `experiment/<purpose>`.
- The base ref. Format: `main` (or another explicit ref).
- The expected lifetime. Format: `<N> days` or `until <date>`.
- The exit criterion. Format: "merge to main" or "discard after <date>".

A worktree that exceeds its scope (e.g., lives for a month without progress) is a stale worktree. The implementer cleans it up or escalates.

## 7. Worktree Logging

Every worktree creation is logged in `.superpowers/execution-checklist.md` under "Worktree Usage". The log entry includes:

- The date the worktree was created.
- The branch name and base ref.
- The expected lifetime.
- The current status (open, in-progress, ready-to-merge, stale).

The log is the audit trail. A worktree without a log entry is untracked.

## 8. Boundary with the Project Harness

Subagents and worktrees are subject to the same rules as the primary Agent:

- A subagent may not exceed the scope of the change it supports.
- A worktree may not contain changes that are not in the corresponding OpenSpec change.
- Both must respect the allowed-path list from `plan.md`.
- Both must follow the schema's artifact rules.

The Project Harness rules in `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, and `OPENCODE.md` apply to subagents and worktrees as if they were the primary Agent. There is no "subagent bypass".

## 9. Anti-Patterns

The following are explicitly forbidden:

- **Subagent for implementation.** The primary Agent applies the change. The subagent supports.
- **Worktree to hide in-progress work.** Worktrees are for isolation, not concealment. In-progress work is in the OpenSpec change folder, visible to reviewers.
- **Subagent to bypass scope.** A subagent prompt that says "feel free to clean up X" is a scope violation. The subagent does not have authority to clean up.
- **Worktree without a base ref.** A worktree that does not state its base ref is a scope violation.
- **Subagent output that is not in the requested shape.** A subagent that returns a free-form essay when asked for a list is a scope violation.

When tempted, return to the rules above and continue only if the action is still justified.

## 10. Cross-References

- Skill selection: `skill-usage-policy.md`.
- Execution discipline: `execution-discipline.md`.
- Project configuration: `.superpowers/execution-checklist.md`.
