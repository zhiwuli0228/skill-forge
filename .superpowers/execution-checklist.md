# Superpowers Execution Checklist

This file is the **execution checklist** for Superpowers in the Skill Forge repository. It is the audit trail for skill invocations, subagent usage, and worktree lifecycle. The Agent updates this file as work progresses.

## 1. How to Use This File

The Agent appends a new section to this file at each skill invocation. The section follows a fixed template. Reviewers can read this file to reconstruct what skills were used, when, and on what.

The file is append-only for entries. Old entries are not deleted; they are marked as `superseded` if a follow-up supersedes them.

## 2. Entry Templates

### 2.1 Skill Invocation

```markdown
### <YYYY-MM-DD HH:MM> — <skill name> — <change-id or task>

- **Phase**: <phase name>
- **Trigger**: <what triggered the invocation>
- **Output**: <artifact path or short result>
- **Outcome**: <success / partial / blocked>
- **Notes**: <free-form notes, including any gaps or escalations>
```

### 2.2 Subagent Usage

```markdown
### <YYYY-MM-DD HH:MM> — subagent — <change-id or task>

- **Subagent task**: <one-line task>
- **Allowed files**: <paths or "read-only">
- **Returned**: <shape of the returned summary>
- **Decision**: <what the primary Agent did with the result>
- **Status**: <consumed / discarded / partial>
```

### 2.3 Worktree Usage

```markdown
### <YYYY-MM-DD HH:MM> — worktree — <change-id or task>

- **Branch**: <branch name>
- **Base ref**: <base ref>
- **Path**: <worktree path>
- **Expected lifetime**: <duration or "until <date>">
- **Status**: <open / in-progress / ready-to-merge / stale>
```

### 2.4 Verification

```markdown
### <YYYY-MM-DD HH:MM> — verification — <change-id>

- **Commands run**: <list of commands>
- **Results**: <exit codes, pass/fail counts>
- **Verdict**: <done / done-with-risks / not-done>
- **Risks**: <list of remaining risks, if any>
```

## 3. Pre-Execution Checklist

Before starting work, the Agent confirms:

- [ ] `AGENTS.md` has been read.
- [ ] The tool-specific entry point has been read (`CODEX.md` / `CLAUDE.md` / `OPENCODE.md`).
- [ ] `SUPERPOWERS.md` and `.superpowers/project-profile.md` have been read.
- [ ] The relevant `openspec/changes/<id>/` folder has been read end-to-end (for an existing change) or the schema and templates have been read (for a new change).
- [ ] The forbidden-path map (in `.superpowers/project-profile.md`) has been reviewed against the planned work.
- [ ] The skill to be invoked has been identified from `.superpowers/skill-usage-policy.md`.
- [ ] The entry below has been started with the date, skill name, and change-id.

## 4. Post-Execution Checklist

After completing work, the Agent confirms:

- [ ] The artifact produced is in the expected location.
- [ ] The artifact satisfies the schema's content rules (for OpenSpec changes).
- [ ] The verification commands have been run and the results recorded.
- [ ] The verdict in `verification.md` is `done` or `done-with-risks`.
- [ ] `openspec validate <change-id> --strict` returns `valid`.
- [ ] The post-execution entry below has been appended.

## 5. Entries

> Append new entries below this line. Do not edit or remove past entries; if a past entry is wrong, append a correction entry with a "Correction" suffix in the title.

<!-- Add entries below. -->

### 2026-06-05 23:30 — verification — phase-2-integration

- **Commands run**:
  - `git status --short`
  - `openspec validate --strict --all`
  - `uv run skill-forge --help`
  - `uv run pytest`
- **Results**:
  - `git status --short`: exit 0. Phase 2 files isolated; pre-existing drift untouched.
  - `openspec validate --strict --all`: exit 0. 23 items passed (1 change + 22 specs); the new example change is also valid.
  - `uv run skill-forge --help`: exit 0. CLI help rendered without regression.
  - `uv run pytest`: exit 0. 265 tests passed.
- **Verdict**: `done`
- **Risks**: Pre-existing dirty worktree (src/, tests/, openspec/specs/, openspec/changes/) is out of scope and remains uncommitted. See `docs/00-project/superpowers-integration-verification-report.md` Section 7.
