# Review: add-governance-enforcement-hooks

> Status: draft
> Schema: skill-forge-governance
> Reviewer: Skill Forge Phase 4 (governance enforcement hooks)
> Date: 2026-06-06
>
> The review is the gate between planning and execution. It
> cross-checks proposal, spec, design, plan, and tasks for
> consistency before implementation starts. A change with
> verdict `block` cannot proceed to plan. A change with
> verdict `request-changes` cannot proceed to tasks.

## Change Id

`add-governance-enforcement-hooks`

## Scope Coverage

| Artifact   | File                                                   | Verdict | Missing Sections |
|------------|--------------------------------------------------------|---------|------------------|
| brainstorm | `brainstorm.md`                                        | `ok`    | none             |
| proposal   | `proposal.md`                                          | `ok`    | none             |
| spec       | `specs/governance-enforcement-hooks/spec.md`           | `ok`    | none             |
| design     | `design.md`                                            | `ok`    | none             |

`<verdict>` is one of: `ok`, `minor-issues`, `missing`, `incorrect`.

## Cross-Artifact Consistency

- Capability name in proposal matches the spec file folder:
  **yes** (`governance-enforcement-hooks`).
- Data contracts in design match the affected files in plan:
  **yes** (the only data contracts are the in-memory
  `Command` and `Result` dicts; the plan lists the script,
  the test file, the eight OpenSpec artifact paths, and the
  verification report path as the only files).
- Allowed-path list in plan matches the files in tasks:
  **yes** (both list the same eight OpenSpec artifact paths,
  the script path, the test file path, and the verification
  report path).
- Verification commands in tasks match the commands in plan:
  **yes** (both list `git status --short`,
  `git diff --name-only`,
  `openspec validate add-governance-enforcement-hooks --strict`,
  `openspec validate --strict --all`, `uv run pytest`,
  `uv run pytest tests/test_governance_check.py`,
  `uv run skill-forge --help`,
  `python scripts/governance_check.py --quick`, and
  `python scripts/governance_check.py`).

## Allowed Path List

### Allowed

- `openspec/changes/add-governance-enforcement-hooks/.openspec.yaml`
- `openspec/changes/add-governance-enforcement-hooks/brainstorm.md`
- `openspec/changes/add-governance-enforcement-hooks/proposal.md`
- `openspec/changes/add-governance-enforcement-hooks/design.md`
- `openspec/changes/add-governance-enforcement-hooks/review.md`
- `openspec/changes/add-governance-enforcement-hooks/plan.md`
- `openspec/changes/add-governance-enforcement-hooks/tasks.md`
- `openspec/changes/add-governance-enforcement-hooks/verification.md`
- `openspec/changes/add-governance-enforcement-hooks/specs/governance-enforcement-hooks/spec.md`
- `scripts/governance_check.py`
- `tests/test_governance_check.py`
- `docs/00-project/governance-enforcement-verification-report.md`

### Forbidden

- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md`
- `README.md`, `README.zh-CN.md`
- `docs/03-openspec/**`, `docs/04-superpowers/**`, `.superpowers/**`
- `openspec/config.yaml`, `openspec/schemas/**`
- `openspec/changes/example-governance-stack-walkthrough/**`
- `openspec/changes/add-skill-lifecycle-recommendation/**`
- `templates/**`, `configs/**`
- `pyproject.toml`, `uv.lock`
- Every file under `src/**`.
- Every file under `tests/**` that is not
  `tests/test_governance_check.py`.
- Every file under `docs/00-project/**` that is not
  `docs/00-project/governance-enforcement-verification-report.md`.

### Discrepancies

- None. The allowed list is the minimal set of paths needed
  for the slice. The forbidden list is the strict-scope list
  from the Phase 4 task. No path appears in both lists.

## Verification Readiness

| Command                                                       | Tool / Env | Status     |
|---------------------------------------------------------------|------------|------------|
| `git status --short`                                          | git        | `ok`       |
| `git diff --name-only`                                        | git        | `ok`       |
| `openspec validate add-governance-enforcement-hooks --strict` | openspec CLI | `ok`     |
| `openspec validate --strict --all`                            | openspec CLI | `ok`     |
| `uv run pytest`                                               | uv / pytest | `ok`      |
| `uv run pytest tests/test_governance_check.py`                | uv / pytest | `ok`      |
| `uv run skill-forge --help`                                   | uv / Typer | `ok`       |
| `python scripts/governance_check.py --quick`                  | python     | `ok`       |
| `python scripts/governance_check.py`                          | python     | `ok`       |

## Required Changes

None. The artifacts are mutually consistent. The allowed-path
list is explicit and matches the tasks. The verification
commands are runnable in the current environment.

## Verdict

`approve`
