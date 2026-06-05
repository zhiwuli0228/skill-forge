# Review: add-skill-lifecycle-recommendation

> Status: draft
> Schema: skill-forge-governance
> Reviewer: Skill Forge Phase 3 (first governed change slice)
> Date: 2026-06-06
>
> The review is the gate between planning and execution. It
> cross-checks proposal, spec, design, plan, and tasks for
> consistency before implementation starts. A change with
> verdict `block` cannot proceed to plan. A change with
> verdict `request-changes` cannot proceed to tasks.

## Change Id

`add-skill-lifecycle-recommendation`

## Scope Coverage

| Artifact     | File                                              | Verdict  | Missing Sections      |
|--------------|---------------------------------------------------|----------|-----------------------|
| brainstorm   | `brainstorm.md`                                   | `ok`     | none                  |
| proposal     | `proposal.md`                                     | `ok`     | none                  |
| spec         | `specs/skill-lifecycle-recommendation/spec.md`    | `ok`     | none                  |
| design       | `design.md`                                       | `ok`     | none                  |

`<verdict>` is one of: `ok`, `minor-issues`, `missing`, `incorrect`.

## Cross-Artifact Consistency

- Capability name in proposal matches the spec file folder:
  **yes** (`skill-lifecycle-recommendation`).
- Data contracts in design match the affected files in plan:
  **yes** (the only data contract is the in-memory
  `LifecycleRecommendationInput`; the plan lists
  `src/skill_forge/lifecycle/recommendation_rules.py` and the
  test file as the only code files).
- Allowed-path list in plan matches the files in tasks:
  **yes** (both list the same eight OpenSpec artifact paths,
  the two new code paths, and the verification report path).
- Verification commands in tasks match the commands in plan:
  **yes** (both list `git status --short`, `openspec validate
  add-skill-lifecycle-recommendation --strict`,
  `openspec validate --strict --all`, `uv run pytest`,
  `uv run pytest tests/test_lifecycle_recommendation_rules.py`,
  and `uv run skill-forge --help`).

## Allowed Path List

### Allowed

- `openspec/changes/add-skill-lifecycle-recommendation/.openspec.yaml`
- `openspec/changes/add-skill-lifecycle-recommendation/brainstorm.md`
- `openspec/changes/add-skill-lifecycle-recommendation/proposal.md`
- `openspec/changes/add-skill-lifecycle-recommendation/design.md`
- `openspec/changes/add-skill-lifecycle-recommendation/review.md`
- `openspec/changes/add-skill-lifecycle-recommendation/plan.md`
- `openspec/changes/add-skill-lifecycle-recommendation/tasks.md`
- `openspec/changes/add-skill-lifecycle-recommendation/verification.md`
- `openspec/changes/add-skill-lifecycle-recommendation/specs/skill-lifecycle-recommendation/spec.md`
- `src/skill_forge/lifecycle/recommendation_rules.py`
- `tests/test_lifecycle_recommendation_rules.py`
- `docs/00-project/first-governed-change-verification-report.md`

### Forbidden

- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md`
- `README.md`, `README.zh-CN.md`
- `docs/03-openspec/**`, `docs/04-superpowers/**`, `.superpowers/**`
- `openspec/config.yaml`, `openspec/schemas/**`
- `openspec/changes/example-governance-stack-walkthrough/**`
- `templates/**`, `configs/**`
- `pyproject.toml`, `uv.lock`
- Every other file under `src/skill_forge/lifecycle/` that is
  not `recommendation_rules.py` (i.e., the existing
  `__init__.py`, `models.py`, `service.py`,
  `recommendation.py`, and `promotion.py` are preserved).
- Every other file under `tests/` that is not
  `test_lifecycle_recommendation_rules.py`.
- Every other file under `docs/00-project/` that is not
  `first-governed-change-verification-report.md`.

### Discrepancies

- None. The allowed list is the minimal set of paths needed
  for the slice. The forbidden list is the strict-scope list
  from the Phase 3 task. No path appears in both lists.

## Verification Readiness

| Command                                          | Tool / Env           | Status     |
|--------------------------------------------------|----------------------|------------|
| `git status --short`                             | git                  | `ok`       |
| `git diff --name-only`                           | git                  | `ok`       |
| `openspec validate add-skill-lifecycle-recommendation --strict` | openspec CLI | `ok`       |
| `openspec validate --strict --all`               | openspec CLI         | `ok`       |
| `uv run pytest`                                  | uv / pytest          | `ok`       |
| `uv run pytest tests/test_lifecycle_recommendation_rules.py` | uv / pytest | `ok`       |
| `uv run skill-forge --help`                      | uv / Typer           | `ok`       |

## Required Changes

None. The artifacts are mutually consistent. The allowed-path
list is explicit and matches the tasks. The verification
commands are runnable in the current environment.

## Verdict

`approve`
