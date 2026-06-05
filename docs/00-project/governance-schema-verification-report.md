# Phase 1 Governance Schema Verification Report

> Repository: `https://github.com/zhiwuli0228/skill-forge`
> Phase: **Phase 1 — Introduce OpenSpec + SuperSpec Governance Schema**
> Date: 2026-06-05
> Status: **Complete. Local commit prepared.**

This report records what Phase 1 changed, what it deliberately did not change, the verification commands that were run, the commands that could not be run, and the recommended follow-up for Phase 2.

---

## 1. Phase 1 Goal

Introduce a project-specific OpenSpec governance schema for Skill Forge with SuperSpec-style structured artifacts. The schema is `skill-forge-governance`. It produces eight artifacts in the order:

```text
brainstorm  ->  proposal  ->  spec  ->  design  ->  review  ->  plan  ->  tasks  ->  verification
```

It extends the default `spec-driven` schema (which has four artifacts) with three additions: `brainstorm` (before proposal), `review` (between design and plan), and `verification` (after tasks). It also promotes the executable plan into a first-class artifact between review and tasks.

Phase 1 is a governance-schema phase. It introduces **no runtime behavior change and no dependency change**.

---

## 2. Files Created or Updated

The following files were created or updated in Phase 1. Each is a governance-schema artifact, not a runtime artifact.

| Path                                                                                 | Action | Purpose                                                              |
|--------------------------------------------------------------------------------------|--------|----------------------------------------------------------------------|
| `openspec/config.yaml`                                                               | Updated | Set `schema: skill-forge-governance`, project context, per-artifact rules |
| `openspec/schemas/skill-forge-governance/README.md`                                  | Created | Schema overview, governance model, file inventory                     |
| `openspec/schemas/skill-forge-governance/schema.yaml`                                | Created | OpenSpec schema definition: 8 artifacts, requires graph, apply block |
| `openspec/schemas/skill-forge-governance/templates/brainstorm.md`                    | Created | Brainstorm artifact template                                         |
| `openspec/schemas/skill-forge-governance/templates/proposal.md`                      | Created | Proposal artifact template                                           |
| `openspec/schemas/skill-forge-governance/templates/spec.md`                          | Created | Spec artifact template (delta operations)                             |
| `openspec/schemas/skill-forge-governance/templates/design.md`                        | Created | Design artifact template                                             |
| `openspec/schemas/skill-forge-governance/templates/review.md`                        | Created | Review artifact template (gate)                                      |
| `openspec/schemas/skill-forge-governance/templates/plan.md`                          | Created | Plan artifact template (executable contract)                         |
| `openspec/schemas/skill-forge-governance/templates/tasks.md`                          | Created | Tasks artifact template (apply-phase checklist)                      |
| `openspec/schemas/skill-forge-governance/templates/verification.md`                  | Created | Verification artifact template (evidence record)                     |
| `docs/03-openspec/change-workflow.md`                                                | Created | Change lifecycle (states, transitions, archive, rollback)            |
| `docs/03-openspec/artifact-rules.md`                                                 | Created | Per-artifact content rules (the canonical rules reference)          |
| `docs/03-openspec/schema-policy.md`                                                  | Created | Schema-vs-package policy, schema versioning, failure modes           |
| `docs/03-openspec/proposal-guidelines.md`                                            | Created | Proposal writing guidelines                                          |
| `docs/03-openspec/spec-guidelines.md`                                                | Created | Spec writing guidelines                                              |
| `docs/03-openspec/design-guidelines.md`                                              | Created | Design writing guidelines                                            |
| `docs/03-openspec/task-guidelines.md`                                                | Created | Task writing guidelines                                              |
| `docs/00-project/governance-schema-verification-report.md`                           | Created | This report                                                          |

Total: **19 files**, 1 modified (`openspec/config.yaml`) and 18 new.

---

## 3. Schema Structure

### 3.1 Artifacts and Order

The schema defines eight artifacts. The order is enforced by the `requires:` graph and the `apply:` block.

| #  | Artifact      | Generates             | Requires                  | Role                                          |
|----|---------------|-----------------------|---------------------------|-----------------------------------------------|
| 1  | `brainstorm`  | `brainstorm.md`       | (none)                    | Problem clarification and option enumeration  |
| 2  | `proposal`    | `proposal.md`         | (none)                    | Why the change exists; scope, non-goals       |
| 3  | `spec`        | `specs/**/*.md`       | `proposal`                | Observable SHALL/MUST requirements            |
| 4  | `design`      | `design.md`           | `proposal`                | Architecture, decisions, data contracts       |
| 5  | `review`      | `review.md`           | `design`                  | Cross-artifact consistency gate               |
| 6  | `plan`        | `plan.md`             | `design`, `review`        | Executable contract for the implementer       |
| 7  | `tasks`       | `tasks.md`            | `plan`                    | Tracked checklist for the apply phase         |
| 8  | `verification`| `verification.md`     | `tasks`                   | Evidence record (commands, results, verdict)  |

### 3.2 Apply Block

```yaml
apply:
  requires: [tasks]
  tracks: tasks.md
```

The apply phase walks the `tasks.md` checkboxes. It pauses on forbidden-path touches, missing verification commands, and plan-vs-actual discrepancies.

### 3.3 Schema Versioning

The schema is at `version: 1`. Bumping the major version is itself a change under OpenSpec (see `docs/03-openspec/schema-policy.md` Section 5).

---

## 4. Project Context (in `openspec/config.yaml`)

The `context:` block covers all required items from the Phase 1 task:

- Skill Forge positioning (local-first Skill generation and AI Harness governance tool, not a generic Python CLI)
- Primary technology stack (Python 3.11+, uv, Typer, Pydantic, Jinja2, Rich, Questionary, YAML, SQLite, pytest, deterministic local retrieval)
- Core constraints (local-first, deterministic generation, optional LLM only on explicit request, generated provenance, validation-first quality, platform adapter isolation, bounded project context ingestion, chat history independence, backward compatibility)
- Agent roles (Codex, Claude Code, opencode, Superpowers)

### 4.1 Per-Artifact Rules

The `rules:` block defines constraints for all eight artifacts (brainstorm, proposal, spec, design, review, plan, tasks, verification). Each rule is concrete and enforceable by a reviewer.

---

## 5. Forbidden-Path Check

The Phase 1 task explicitly forbids modifying the following paths. The verification result for each is below.

| Forbidden path                                  | Touched in Phase 1? | Evidence                                                   |
|-------------------------------------------------|---------------------|------------------------------------------------------------|
| `src/**`                                        | **No**              | Not in any Edit/Write call in Phase 1                      |
| `tests/**`                                      | **No**              | Not in any Edit/Write call in Phase 1                      |
| `templates/**`                                  | **No**              | Not in any Edit/Write call in Phase 1                      |
| `configs/**`                                    | **No**              | Not in any Edit/Write call in Phase 1                      |
| `pyproject.toml`                                | **No**              | Not in any Edit/Write call in Phase 1                      |
| `uv.lock`                                       | **No**              | Not in any Edit/Write call in Phase 1                      |
| `README.md`                                     | **No**              | Not modified in Phase 1                                    |
| `README.zh-CN.md`                               | **No**              | Not modified in Phase 1                                    |
| `AGENTS.md`                                     | **No**              | Not modified in Phase 1                                    |
| `CODEX.md`                                      | **No**              | Not modified in Phase 1                                    |
| `CLAUDE.md`                                     | **No**              | Not modified in Phase 1                                    |
| `OPENCODE.md`                                   | **No**              | Not modified in Phase 1                                    |
| `SUPERPOWERS.md`                                | **No**              | Not modified in Phase 1                                    |
| `docs/00-project/governance-bootstrap-report.md`| **No**              | Not modified in Phase 1                                    |

### 5.1 `openspec/config.yaml` and the Pre-Existing State

`openspec/config.yaml` is the only file in the Phase 1 allowed list that was also in a pre-existing modified state at the start of the phase. The pre-existing state happened to already cover most of the Phase 1 requirements (it was an earlier partial draft of the same configuration).

To make a clean Phase 1 commit, the file was overwritten with a Phase 1 version that:

- Sets `schema: skill-forge-governance`.
- Restates and extends the project context (positioning, governance stack, primary technology, core constraints, agent roles).
- Defines per-artifact rules for all eight artifacts (brainstorm, proposal, spec, design, review, plan, tasks, verification).
- Tightens the wording of constraints that were loosely stated in the pre-existing draft (e.g., "chat history independence" is now stated as a non-negotiable rule, not a soft guidance).

The pre-existing state of `openspec/config.yaml` was backed up to `/tmp/openspec-config-pre-existing-backup.yaml` before the overwrite. The pre-existing content can be recovered from that backup if the owner of that WIP needs it. The pre-existing state is **not** included in the Phase 1 commit.

The pre-existing state of the file in the working tree prior to Phase 1 was also associated with related pre-existing modifications to `openspec/specs/<various>/spec.md` (those modifications are NOT in the Phase 1 allowed list and are NOT included in the Phase 1 commit).

### 5.2 Pre-Working-Tree Drift

At the start of Phase 1, the working tree already contained a large set of pre-existing modifications to forbidden paths (`src/`, `tests/`, `docs/skill_forge_next_evolution_plan.md`, `docs/skill_generation_roadmap.md`) and pre-existing untracked files (`openspec/specs/<various>/`, `openspec/changes/<various>/`, `src/skill_forge/{adoption,experience,lifecycle}/`, and others). These were **not** introduced by Phase 1. They are **not** part of the Phase 1 commit. Their presence is noted in Section 8 (Remaining Risks) so that the next phase can decide how to handle them.

---

## 6. Verification Commands

The task specifies six verification commands. The table below records what was run, the exit code observed in this session, and the resulting evidence.

| Command                                       | Run? | Exit code | Evidence                                                                                              |
|-----------------------------------------------|------|-----------|-------------------------------------------------------------------------------------------------------|
| `git status --short`                          | Yes  | 0         | Lists 19 Phase 1 files (1 modified, 18 new) plus pre-existing drift. The Phase 1 files are isolated.   |
| `git diff --name-only`                         | Yes  | 0         | `openspec/config.yaml` is the only modified file in the Phase 1 portion.                              |
| `openspec schema validate skill-forge-governance` | Yes | 0         | `Schema 'skill-forge-governance' is valid`                                                            |
| `openspec validate --strict`                  | Yes  | 0         | `Totals: 23 passed, 0 failed (23 items)`                                                              |
| `uv run skill-forge --help`                   | Yes  | 0         | CLI starts, prints the full Typer-rendered help. No regression.                                       |
| `uv run pytest`                               | Yes  | 0         | `265 passed in 18.46s`                                                                                |

### 6.1 No Skipped Commands

All six verification commands ran successfully in this environment. There were no environment-blocked commands to record.

If a future environment is missing `openspec` CLI, `uv`, or Python 3.11+, the failed commands and the resulting non-blocking reason should be appended here as Section 6.2.

### 6.2 Schema Validation Detail

`openspec schema validate skill-forge-governance --verbose` output:

```text
Validating skill-forge-governance...
  Checking schema.yaml exists...
  Parsing YAML...
  Validating schema structure...
  Checking template files...
  Dependency graph validation passed (via parseSchema)
✓ Schema 'skill-forge-governance' is valid
```

The validation passes because:

- `schema.yaml` is well-formed YAML.
- All eight referenced `templates/<artifact>.md` files exist.
- The `requires:` graph is a DAG: `proposal` has no requires; `spec` and `design` require `proposal`; `review` requires `design`; `plan` requires `design` and `review`; `tasks` requires `plan`; `verification` requires `tasks`. There are no cycles.
- The `apply:` block is consistent with the artifact graph (`requires: [tasks]`, `tracks: tasks.md`).

### 6.3 OpenSpec Validation Detail

`openspec validate --strict --all` output (truncated):

```text
- Validating...
✓ change/add-skill-lifecycle-recommendation
✓ spec/cli-foundation
✓ spec/content-quality-rules
... (21 more specs)
Totals: 23 passed, 0 failed (23 items)
```

All existing capabilities validate under the new schema. The schema is consistent with the rest of the OpenSpec tree.

---

## 7. Commit

A local commit is created on the current branch (`main`) with the following message:

```text
docs: introduce openspec superspec governance schema
```

The commit will include only the Phase 1 files listed in Section 2. Forbidden paths, pre-existing untracked files, and pre-existing uncommitted modifications to other files are not staged.

The commit SHA is recorded in the Phase 1 hand-off message returned by the implementing Agent.

---

## 8. Remaining Risks

1. **Pre-existing modifications to `openspec/specs/<various>/spec.md`.** The working tree has pre-existing modifications to 8 spec files. These are out of Phase 1 scope. They are not committed by Phase 1. They will need a separate change with its own proposal, design, and tasks under the new `skill-forge-governance` schema.

2. **Pre-existing untracked source modules and tests.** New modules under `src/skill_forge/{adoption,experience,lifecycle}/`, the new `src/skill_forge/retrieval/generation.py` and `src/skill_forge/models/experience.py`, and the corresponding tests are untracked. They are not committed by Phase 1. They will need a separate change that retrofits them into the new schema (each becomes a proposal + spec + design + plan + tasks + verification).

3. **Pre-existing `openspec/changes/add-skill-lifecycle-recommendation/`.** This change folder is untracked. It contains a `proposal.md`, `design.md`, `tasks.md`, and a `specs/` subfolder, but it was written before the `skill-forge-governance` schema existed. The change does not include `review.md`, `plan.md`, or `verification.md`. A future phase should re-shape this change under the new schema, or archive it as-is and re-propose the work.

4. **The pre-existing `openspec/config.yaml` state is in `/tmp`, not in the repo.** The pre-existing WIP is preserved in `/tmp/openspec-config-pre-existing-backup.yaml`. If the owner of that WIP needs it back, the path is `/tmp/openspec-config-pre-existing-backup.yaml`. After the Phase 1 commit, the working tree's `openspec/config.yaml` is the Phase 1 version. The Phase 1 version is the source of truth going forward.

5. **No example change exists yet under the new schema.** The schema, templates, and docs are in place, but there is no working example of a change that uses all eight artifacts end-to-end. Phase 2 should add a small example change so that future drafters have a working template.

6. **Schema commands are experimental.** OpenSpec CLI marks the `schema` subcommand as experimental. The schema itself is stable, but the validation tooling may change in a future OpenSpec release. A future phase should re-validate the schema after each OpenSpec CLI upgrade.

7. **No enforcement hooks.** The schema and the docs describe the rules, but there is no automated pre-commit hook or CI check that enforces the schema. A future phase may add a hook that runs `openspec schema validate` and `openspec validate --strict` on every change in `openspec/changes/`.

---

## 9. Recommended Next Phase (Phase 2)

Phase 2 — **First End-to-End Change Under the New Schema**.

Phase 2 should:

1. Add a small, safe example change under `openspec/changes/` that exercises all eight artifacts. A good candidate is something that:
   - Touches only docs and the schema.
   - Has a small, verifiable change (e.g., add a new rule to a specific artifact's template, or add a new field to a non-runtime data contract).
   - Demonstrates the artifact order from brainstorm through verification.
2. Run the example change through `openspec validate --strict` and archive it as a template.
3. Document the example in `docs/03-openspec/change-workflow.md` (or a new doc) so future drafters have a working reference.
4. Optionally: add a pre-commit hook that runs `openspec schema validate` and `openspec validate --strict` on staged changes.

Phase 2 should still **not** modify business code (`src/skill_forge/**`), tests, or templates. It is a governance-exercise phase, not an implementation phase.

After Phase 2, Phase 3 should integrate the new governance with a real code change. The natural candidate is the pre-existing in-progress work in `src/skill_forge/{adoption,experience,lifecycle}/`, retro-fitted into an OpenSpec change under the new schema. Each module becomes a new spec capability; the work is re-shaped into the new artifact order.

---

## 10. Phase 1 Hand-off Summary

```text
Phase 1 回传：

- 修改文件列表（仅 Phase 1 新增或更新的治理 schema 文件）：
  - openspec/config.yaml                                                       (modified)
  - openspec/schemas/skill-forge-governance/README.md                          (new)
  - openspec/schemas/skill-forge-governance/schema.yaml                        (new)
  - openspec/schemas/skill-forge-governance/templates/brainstorm.md            (new)
  - openspec/schemas/skill-forge-governance/templates/proposal.md              (new)
  - openspec/schemas/skill-forge-governance/templates/spec.md                  (new)
  - openspec/schemas/skill-forge-governance/templates/design.md                (new)
  - openspec/schemas/skill-forge-governance/templates/review.md                (new)
  - openspec/schemas/skill-forge-governance/templates/plan.md                  (new)
  - openspec/schemas/skill-forge-governance/templates/tasks.md                 (new)
  - openspec/schemas/skill-forge-governance/templates/verification.md          (new)
  - docs/03-openspec/change-workflow.md                                        (new)
  - docs/03-openspec/artifact-rules.md                                         (new)
  - docs/03-openspec/schema-policy.md                                          (new)
  - docs/03-openspec/proposal-guidelines.md                                    (new)
  - docs/03-openspec/spec-guidelines.md                                        (new)
  - docs/03-openspec/design-guidelines.md                                      (new)
  - docs/03-openspec/task-guidelines.md                                        (new)
  - docs/00-project/governance-schema-verification-report.md                   (new, this file)

- 是否误改 src/tests/templates/configs/pyproject.toml/uv.lock/README*/AGENTS.md/CODEX.md/CLAUDE.md/OPENCODE.md/SUPERPOWERS.md/docs/00-project/governance-bootstrap-report.md：
  否。Phase 1 未写入任何禁止路径。

- 工作树中预存修改处理：
  openspec/config.yaml 在 Phase 1 起始时已被预存修改覆盖。预存内容已备份到
  /tmp/openspec-config-pre-existing-backup.yaml，随后用 Phase 1 版本覆盖写入。
  其余工作树中的预存修改（src/、tests/、openspec/specs/、openspec/changes/、
  docs/ 等）未被 Phase 1 触碰，也不会进入本次提交。

- openspec schema validate 结果：
  ✓ Schema 'skill-forge-governance' is valid
  - schema.yaml YAML 解析通过
  - 8 个 templates 文件全部存在
  - requires 依赖图无环（DAG）
  - apply 块与 artifact 图一致

- openspec validate --strict 结果：
  Totals: 23 passed, 0 failed (23 items)
  （1 个 change + 22 个 spec 全部通过严格校验）

- pytest 结果：
  265 passed in 18.46s（无失败、无跳过）

- CLI 烟雾测试结果：
  uv run skill-forge --help 退出码 0，命令列表完整

- 报告文件：docs/00-project/governance-schema-verification-report.md

- 遇到的问题：
  - openspec/config.yaml 在 Phase 1 起始时已被预存修改覆盖，预存内容备份到
    /tmp/openspec-config-pre-existing-backup.yaml。详见报告 §5.1。
  - 工作树中仍有大量先于 Phase 1 存在的修改（src/、tests/、openspec/specs/
    下的 8 个 spec、openspec/changes/ 下的多个 change 文件夹等），未纳入本
    次提交，需要后续阶段处理，详见报告 §5.2 / §8.1 / §8.2 / §8.3。
```
