# Review: triage-dirty-worktree-change-queue

> Status: draft
> Schema: skill-forge-governance
> Reviewer: Skill Forge Phase 6 (dirty worktree triage)
> Date: 2026-06-06
>
> The review is the gate between planning and
> execution. It cross-checks proposal, spec, design,
> plan, and tasks for consistency before
> implementation starts. A change with verdict `block`
> cannot proceed to plan. A change with verdict
> `request-changes` cannot proceed to tasks.

## Change Id

`triage-dirty-worktree-change-queue`

## Scope Coverage

| Artifact   | File                                                                                  | Verdict | Missing Sections |
|------------|---------------------------------------------------------------------------------------|---------|------------------|
| brainstorm | `brainstorm.md`                                                                       | `ok`    | none             |
| proposal   | `proposal.md`                                                                         | `ok`    | none             |
| spec       | `specs/dirty-worktree-change-queue/spec.md`                                           | `ok`    | none             |
| design     | `design.md`                                                                           | `ok`    | none             |

`<verdict>` is one of: `ok`, `minor-issues`, `missing`,
`incorrect`.

## Cross-Artifact Consistency

- Capability name in proposal matches the spec file
  folder: **yes**
  (`dirty-worktree-change-queue`).
- Data contracts in design match the affected files
  in plan: **yes** (the only data contracts are the
  three new doc files; the plan lists them as the
  only writes; the design documents the informal
  schema for each).
- Allowed-path list in plan matches the files in
  tasks: **yes** (both list the OpenSpec change
  folder and the three new doc files as the only
  allowed paths).
- Verification commands in tasks match the commands
  in plan: **yes** (both list
  `openspec validate triage-dirty-worktree-change-queue --strict`,
  `openspec validate --strict --all`, and
  `python scripts/governance_check.py --quick`; the
  plan additionally lists
  `python scripts/governance_check.py`,
  `uv run pytest`, and `uv run skill-forge --help`
  as recommended-but-not-required commands).

## Allowed Path List

### Allowed

- `openspec/changes/triage-dirty-worktree-change-queue/.openspec.yaml`
- `openspec/changes/triage-dirty-worktree-change-queue/brainstorm.md`
- `openspec/changes/triage-dirty-worktree-change-queue/proposal.md`
- `openspec/changes/triage-dirty-worktree-change-queue/design.md`
- `openspec/changes/triage-dirty-worktree-change-queue/review.md`
- `openspec/changes/triage-dirty-worktree-change-queue/plan.md`
- `openspec/changes/triage-dirty-worktree-change-queue/tasks.md`
- `openspec/changes/triage-dirty-worktree-change-queue/verification.md`
- `openspec/changes/triage-dirty-worktree-change-queue/specs/dirty-worktree-change-queue/spec.md`
- `docs/00-project/dirty-worktree-triage-report.md`
- `docs/00-project/wip-disposition-matrix.md`
- `docs/00-project/change-queue.md`

### Forbidden

- `src/**`
- `tests/**`
- `templates/**`
- `configs/**`
- `scripts/**`
- `pyproject.toml`
- `uv.lock`
- `README.md`
- `README.zh-CN.md`
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`,
  `SUPERPOWERS.md`
- `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**`
- `openspec/config.yaml`, `openspec/schemas/**`
- Every pre-existing
  `openspec/changes/<existing-change-id>/` folder
  (active or archived), including but not limited to
  `openspec/changes/add-skill-lifecycle-recommendation/`,
  `openspec/changes/add-governance-enforcement-hooks/`,
  `openspec/changes/consolidate-lifecycle-recommendation-service/`,
  `openspec/changes/example-governance-stack-walkthrough/`,
  and every folder under `openspec/changes/archive/`.

### Discrepancies

- None. The allowed list is the strict-scope list
  from the Phase 6 task plus the standard OpenSpec
  change folder contents. The forbidden list is the
  strict-scope forbidden list from the Phase 6 task
  plus a defense-in-depth restatement of every
  pre-existing OpenSpec change folder. No path
  appears in both lists.

## Verification Readiness

| Command                                                                       | Tool / Env       | Status     |
|-------------------------------------------------------------------------------|------------------|------------|
| `openspec validate triage-dirty-worktree-change-queue --strict`               | openspec CLI     | `ok`       |
| `openspec validate --strict --all`                                            | openspec CLI     | `ok`       |
| `python scripts/governance_check.py --quick`                                  | python           | `ok`       |
| `python scripts/governance_check.py` (recommended)                            | python           | `ok`       |
| `uv run pytest` (recommended)                                                 | uv / pytest      | `ok`       |
| `uv run skill-forge --help` (recommended)                                     | uv / Typer       | `ok`       |

## Required Changes

None. The artifacts are mutually consistent. The
allowed-path list is explicit and matches the
strict-scope list. The verification commands are
runnable in the current environment.

## Verdict

`approve`
