# Review: consolidate-lifecycle-recommendation-service

> Status: draft
> Schema: skill-forge-governance
> Reviewer: Skill Forge Phase 5 (lifecycle recommendation service adapter)
> Date: 2026-06-06
>
> The review is the gate between planning and execution. It
> cross-checks proposal, spec, design, plan, and tasks for
> consistency before implementation starts. A change with
> verdict `block` cannot proceed to plan. A change with
> verdict `request-changes` cannot proceed to tasks.

## Change Id

`consolidate-lifecycle-recommendation-service`

## Scope Coverage

| Artifact   | File                                                                 | Verdict | Missing Sections |
|------------|----------------------------------------------------------------------|---------|------------------|
| brainstorm | `brainstorm.md`                                                      | `ok`    | none             |
| proposal   | `proposal.md`                                                        | `ok`    | none             |
| spec       | `specs/lifecycle-recommendation-service-adapter/spec.md`             | `ok`    | none             |
| design     | `design.md`                                                          | `ok`    | none             |

`<verdict>` is one of: `ok`, `minor-issues`, `missing`, `incorrect`.

## Cross-Artifact Consistency

- Capability name in proposal matches the spec file folder:
  **yes** (`lifecycle-recommendation-service-adapter`).
- Data contracts in design match the affected files in plan:
  **yes** (the only data contract is the in-memory
  `LifecycleSummary -> LifecycleRecommendationInput` mapping;
  the plan lists the two source files, the two test files,
  the eight OpenSpec artifact paths, and the verification
  report path as the only files).
- Allowed-path list in plan matches the files in tasks:
  **yes** (both list the same eight OpenSpec artifact paths,
  the two source paths, the two test paths, and the
  verification report path).
- Verification commands in tasks match the commands in plan:
  **yes** (both list `git status --short`,
  `git diff --name-only`,
  `openspec validate consolidate-lifecycle-recommendation-service --strict`,
  `openspec validate --strict --all`,
  `uv run pytest tests/test_lifecycle_recommendation_rules.py`,
  `uv run pytest tests/test_lifecycle_recommendation.py`,
  `uv run pytest`, `uv run skill-forge --help`,
  `python scripts/governance_check.py --quick`, and
  `python scripts/governance_check.py`).

## Allowed Path List

### Allowed

- `openspec/changes/consolidate-lifecycle-recommendation-service/.openspec.yaml`
- `openspec/changes/consolidate-lifecycle-recommendation-service/brainstorm.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/proposal.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/design.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/review.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/plan.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/tasks.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/verification.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/specs/lifecycle-recommendation-service-adapter/spec.md`
- `src/skill_forge/lifecycle/recommendation.py`
- `src/skill_forge/lifecycle/recommendation_rules.py`
- `tests/test_lifecycle_recommendation.py`
- `tests/test_lifecycle_recommendation_rules.py`
- `docs/00-project/lifecycle-service-adapter-verification-report.md`

### Forbidden

- `scripts/governance_check.py`
- `tests/test_governance_check.py`
- `src/skill_forge/cli.py`
- Every other file under `src/skill_forge/**` that is
  not `src/skill_forge/lifecycle/recommendation.py` or
  `src/skill_forge/lifecycle/recommendation_rules.py`.
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`,
  `SUPERPOWERS.md`
- `README.md`, `README.zh-CN.md`
- `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**`
- `openspec/config.yaml`, `openspec/schemas/**`
- `openspec/changes/example-governance-stack-walkthrough/**`
- `openspec/changes/add-skill-lifecycle-recommendation/**`
- `openspec/changes/add-governance-enforcement-hooks/**`
- `templates/**`, `configs/**`
- `pyproject.toml`, `uv.lock`
- Every file under `tests/**` that is not
  `tests/test_lifecycle_recommendation.py` or
  `tests/test_lifecycle_recommendation_rules.py` (and
  `tests/test_governance_check.py` is explicitly
  forbidden).
- Every file under `docs/00-project/**` that is not
  `docs/00-project/lifecycle-service-adapter-verification-report.md`.

### Discrepancies

- None. The allowed list is the minimal set of paths
  needed for the slice. The forbidden list is the
  strict-scope list from the Phase 5 task. No path
  appears in both lists.

## Verification Readiness

| Command                                                                       | Tool / Env | Status     |
|-------------------------------------------------------------------------------|------------|------------|
| `git status --short`                                                          | git        | `ok`       |
| `git diff --name-only`                                                        | git        | `ok`       |
| `openspec validate consolidate-lifecycle-recommendation-service --strict`     | openspec CLI | `ok`     |
| `openspec validate --strict --all`                                            | openspec CLI | `ok`     |
| `uv run pytest tests/test_lifecycle_recommendation_rules.py`                  | uv / pytest | `ok`     |
| `uv run pytest tests/test_lifecycle_recommendation.py`                        | uv / pytest | `ok`     |
| `uv run pytest`                                                               | uv / pytest | `ok`     |
| `uv run skill-forge --help`                                                   | uv / Typer | `ok`       |
| `python scripts/governance_check.py --quick`                                  | python     | `ok`       |
| `python scripts/governance_check.py`                                          | python     | `ok`       |

## Required Changes

None. The artifacts are mutually consistent. The
allowed-path list is explicit and matches the tasks. The
verification commands are runnable in the current
environment.

## Verdict

`approve`
