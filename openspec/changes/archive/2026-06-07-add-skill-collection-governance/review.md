# Review: add-skill-collection-governance

> Status: draft
> Schema: skill-forge-governance
> Reviewer: Codex
> Date: 2026-06-07
>
> The review is the gate between planning and execution. It checks that
> the change artifacts define a coherent implementation scope before any
> source files are modified.

## Change Id

`add-skill-collection-governance`

## Scope Coverage

| Artifact   | File                                         | Verdict | Missing Sections |
|------------|----------------------------------------------|---------|------------------|
| brainstorm | `brainstorm.md`                              | `ok`    | none             |
| proposal   | `proposal.md`                                | `ok`    | none             |
| design     | `design.md`                                  | `ok`    | none             |
| specs      | `specs/**/spec.md`                           | `ok`    | none             |
| plan       | `plan.md`                                    | `ok`    | none             |
| tasks      | `tasks.md`                                   | `ok`    | none             |

## Cross-Artifact Consistency

- Capability additions in proposal match the spec folders:
  **yes** (`skill-collection-management`,
  `skill-collection-scoring`, `semantic-skill-retrieval`).
- Modified capability claims in proposal match the spec deltas:
  **yes** (`search-retrieval`, `skill-library-management`,
  `experience-accumulation`, `llm-assisted-generation`).
- Design phasing matches task sequencing: **yes**.
- Plan allowed paths cover the implementation surfaces named in design:
  **yes**.
- Verification strategy in plan matches task verification milestones:
  **yes**.

## Allowed Path List

### Allowed

- `openspec/changes/add-skill-collection-governance/**`
- `src/skill_forge/cli.py`
- `src/skill_forge/retrieval/**`
- `src/skill_forge/storage/**`
- `src/skill_forge/adoption/**`
- `src/skill_forge/generator/**`
- `src/skill_forge/lifecycle/**`
- `src/skill_forge/models/**`
- `src/skill_forge/library/**`
- `tests/**`
- `README.md`
- `README.zh-CN.md`

### Forbidden

- `AGENTS.md`
- `CODEX.md`
- `CLAUDE.md`
- `OPENCODE.md`
- `SUPERPOWERS.md`
- `openspec/config.yaml`
- `openspec/schemas/**`
- `configs/**`
- `templates/**`
- `pyproject.toml`
- `uv.lock`
- Any new remote-service dependency or hosted vector database config

## Discrepancies

- `openspec validate` may be blocked by an unrelated YAML parse error in
  `openspec/config.yaml`. This is a repository-level issue, not part of
  the new change's scope. The verification artifact must record that
  blocker explicitly if it persists at implementation time.

## Verification Readiness

| Command | Tool / Env | Status |
|---------|------------|--------|
| `git status --short` | git | `ok` |
| `git diff --name-only` | git | `ok` |
| `openspec validate add-skill-collection-governance --strict` | openspec CLI | `blocked-by-repo-config` |
| `openspec validate --strict --all` | openspec CLI | `blocked-by-repo-config` |
| `uv run pytest` | uv / pytest | `ok` |
| `uv run pytest <focused-files>` | uv / pytest | `ok` |
| `uv run skill-forge search "<query>"` | uv / CLI | `ok` |

## Required Changes

None before planning. The artifacts are coherent enough to hand off to
an implementation agent, with the repo-level OpenSpec validation blocker
already documented.

## Verdict

`approve`
