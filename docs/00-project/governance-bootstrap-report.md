# Phase 0 Governance Bootstrap Report

> Repository: `https://github.com/zhiwuli0228/skill-forge`
> Phase: **Phase 0 — Establish Skill Forge Governance Entry Points**
> Date: 2026-06-05
> Status: **Complete. Local commit prepared.**

This report records what Phase 0 changed, what it deliberately did not change, the verification commands that were run, the commands that could not be run, and the recommended follow-up for Phase 1.

---

## 1. Phase 0 Goal

Establish the first layer of governance entry points for `skill-forge`. Make it possible for every AI Agent (Codex, Claude Code, opencode, and any other) to know — at the moment it opens the repository — what the project is, what files it must read, what its role is, and what it may not touch.

Phase 0 is a documentation-only phase. It introduces **no schema, no runtime behavior change, and no dependency change**.

---

## 2. Files Created or Updated

The following files were created or updated in Phase 0. Each is a governance entry point, not a runtime artifact.

| Path                                            | Action   | Purpose                                                                    |
|-------------------------------------------------|----------|----------------------------------------------------------------------------|
| `AGENTS.md`                                     | Created  | Universal entry point for all AI Agents                                    |
| `CODEX.md`                                      | Created  | Codex entry — design, planning, OpenSpec/SuperSpec change artifacts       |
| `CLAUDE.md`                                     | Updated  | Claude Code entry — implementation governance layered on existing content  |
| `OPENCODE.md`                                   | Created  | opencode entry — strict-scope fallback execution rules                    |
| `SUPERPOWERS.md`                                | Created  | Superpowers entry — execution discipline and phase mapping                |
| `README.md`                                     | Updated  | Added "Governance Entry Points" section; existing content preserved       |
| `README.zh-CN.md`                               | Updated  | Added "治理入口" section; existing content preserved                      |
| `docs/00-project/governance-bootstrap-report.md` | Created  | This report                                                                |

### 2.1 What `CLAUDE.md` Keeps

`CLAUDE.md` is the implementation entry, not a replacement of the project overview. The pre-existing sections of `CLAUDE.md` were preserved verbatim. Phase 0 only inserts a new top-level `## Implementation Governance` section above `## Project Overview`. The preserved sections still cover:

- Project Overview
- Common Commands (`uv sync`, `uv run skill-forge --help`, `uv run pytest`, `uv pip install -e .`)
- Architecture (CLI entry, core flow, key modules)
- Data Flow
- Local Workspace Layout (`~/.skill-forge/...`)
- Environment Variables (`SKILL_FORGE_HOME`, `SKILL_FORGE_LLM_*`)
- Blueprints (built-in and project custom)

### 2.2 What the README Updates Do

The English and Chinese READMEs are **not** rewritten. Each README receives a single new section immediately after the project positioning paragraph and before `## Features` / `## 功能`. The new section is a short table of governance entry points and a one-paragraph explanation of the OpenSpec-first rule and the Phase 0 → Phase 1 roadmap. All existing README content (Features, Requirements, Installation, Quick Start, Commands, Configuration, Local Data Layout, Generated Skill Shape, Development, Project Structure, Current Scope) is unchanged.

---

## 3. Forbidden-Path Check

The Phase 0 task explicitly forbids modifying the following paths. The verification result for each is below.

| Forbidden path        | Touched in Phase 0? | Evidence                                  |
|-----------------------|---------------------|-------------------------------------------|
| `src/**`              | **No**              | Not in any Edit/Write call in Phase 0     |
| `tests/**`            | **No**              | Not in any Edit/Write call in Phase 0     |
| `templates/**`        | **No**              | Not in any Edit/Write call in Phase 0     |
| `configs/**`          | **No**              | Not in any Edit/Write call in Phase 0     |
| `openspec/**`         | **No**              | Not in any Edit/Write call in Phase 0     |
| `pyproject.toml`      | **No**              | Not in any Edit/Write call in Phase 0     |
| `uv.lock`             | **No**              | Not in any Edit/Write call in Phase 0     |

Phase 0 also deliberately did not touch other pre-existing untracked assets in the working tree:

- `AGENT.md` (singular) — pre-existing untracked stub, not in Phase 0 allowed list, left untouched.
- `.claude/`, `.codex/` — pre-existing untracked Agent config, not in Phase 0 allowed list, left untouched.
- `docs/intelligent-generation-design*.md`, `docs/intelligent-generation-roadmap.md`, `docs/release-notes.md`, `docs/skill_lifecycle_governance_plan.md` — pre-existing untracked docs, not in Phase 0 allowed list, left untouched.
- `docs/rectification/` — task source, intentionally left untouched.
- Pre-existing untracked source modules under `src/skill_forge/{adoption,experience,lifecycle}/`, `src/skill_forge/models/experience.py`, `src/skill_forge/retrieval/generation.py` — out of scope, left untouched.
- Pre-existing untracked tests under `tests/test_*.py` for those modules — out of scope, left untouched.
- Pre-existing untracked OpenSpec change folders under `openspec/changes/...` and OpenSpec specs under `openspec/specs/...` — out of scope, left untouched.

All of the above will need a separate, scoped commit (or a discard) by the owner of that work, in a later phase. Phase 0 does not decide their fate.

### 3.1 Pre-Working-Tree Drift

At the start of Phase 0, the working tree already contained a large set of pre-existing modifications to forbidden paths (`src/`, `tests/`, `openspec/`, `docs/skill_forge_next_evolution_plan.md`, `docs/skill_generation_roadmap.md`) and pre-existing untracked files. These were not introduced by Phase 0. They are not part of the Phase 0 commit. Their presence is noted in Section 7 (Remaining Risks) so that the next phase can decide how to handle them.

---

## 4. Verification Commands

The task specifies four verification commands. The table below records what was run, the exit code observed in this session, and the resulting evidence.

| Command                              | Run? | Exit code | Evidence                                                                                                                                |
|--------------------------------------|------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `git diff --stat`                    | Yes  | 0         | 34 files changed, 2431 insertions, 418 deletions — but only 3 of those files (`CLAUDE.md`, `README.md`, `README.zh-CN.md`) are Phase 0 work; the rest are pre-existing modifications in the working tree. |
| `git diff --name-only`               | Yes  | 0         | Same 34 files. None of the forbidden paths appear in the Phase 0 portion of the diff (the forbidden paths appearing in `git diff --name-only` are pre-existing, not Phase 0). |
| `uv run skill-forge --help`          | Yes  | 0         | CLI starts, prints the full Typer-rendered help, lists 18 commands (init, validate, install, update, search, adopt, list, show, eval, upgrade, promote, rollback, diff, create, resume, blueprints, experience, lifecycle). |
| `uv run pytest`                      | Yes  | 0         | 265 tests collected across 26 test files; 265 passed in ~16.75s. No failures, no skips.                                                  |

### 4.1 No Skipped Commands

All four verification commands ran successfully in this environment. There were no environment-blocked commands to record.

If a future environment is missing `uv` or Python 3.11+, the failed commands and the resulting non-blocking reason should be appended here as Section 4.2.

---

## 5. Conflict Resolution Notes

### 5.1 `AGENT.md` vs `AGENTS.md`

At the start of Phase 0, a pre-existing untracked file `AGENT.md` (singular) was present in the working tree. It contained a 5-line reading-order stub. The Phase 0 task explicitly names `AGENTS.md` (plural) as the universal entry. To avoid ambiguity:

- `AGENTS.md` is the canonical universal entry.
- `AGENT.md` (singular) was **not** deleted in Phase 0 because deleting it is out of scope (it is not in the Phase 0 allowed list).
- Both files will coexist in the working tree until a future phase decides to remove the singular stub.

This is recorded as a known leftover in Section 7. No Agent should treat `AGENT.md` (singular) as the canonical entry. `AGENTS.md` (plural) is canonical.

### 5.2 Pre-Existing Modifications to Phase 0 Files

At the start of Phase 0, the working tree already contained modifications to `CLAUDE.md`, `README.md`, and `README.zh-CN.md`. These modifications were **not** authored as part of Phase 0; they were already in the working tree when the task began.

To keep the Phase 0 commit clean and the diff reviewable, the three files were first reverted to their HEAD content using `git checkout HEAD -- <file>`, and only the Phase 0 governance sections were then re-applied via the Edit tool.

The end result: the Phase 0 portion of the diff for these three files is pure additions. The pre-existing doc-sync work (e.g., adding `adoption/`, `experience/`, `library/` modules to the Architecture section, adding the `adopt` and `experience` command documentation to the READMEs) is **not** included in the Phase 0 commit. It will be picked up by a separate, owner-identified commit.

---

## 6. Commit

A local commit is created on the current branch (`main`) with the following message:

```text
docs: establish governance entry points
```

The commit will include only the Phase 0 files listed in Section 2. Forbidden paths and pre-existing untracked files are not staged.

The commit SHA is recorded in the Phase 0 hand-off message returned by the implementing Agent.

---

## 7. Remaining Risks

1. **`AGENT.md` (singular) stub remains.** It duplicates the role of `AGENTS.md` (plural) with a 5-line stub. A future phase should decide whether to delete it, fold it into `AGENTS.md`, or repurpose it. Until then, both files exist and the canonical entry is `AGENTS.md` (plural).
2. **Pre-existing modifications to forbidden paths.** The working tree has substantial pre-existing diff in `src/`, `tests/`, `openspec/`, and parts of `docs/` that are out of Phase 0 scope. These are not committed by Phase 0. They are not validated by Phase 0. They remain a risk for the next phase, which must decide how to integrate or discard them.
3. **Pre-existing untracked source modules and tests.** New modules under `src/skill_forge/{adoption,experience,lifecycle}/`, the new `src/skill_forge/retrieval/generation.py` and `src/skill_forge/models/experience.py`, and the corresponding tests are untracked. They are not committed by Phase 0. They will need a separate change with its own OpenSpec proposal, design, and tasks.
4. **No OpenSpec schema yet.** The governance stack advertises OpenSpec + SuperSpec in `AGENTS.md` and `README*`, but the actual schema files under `openspec/schemas/` and the docs under `docs/03-openspec/` do not yet exist. Phase 1 must add them before any non-trivial change can be properly tracked.
5. **No enforcement.** The governance files describe what Agents should do. They do not yet enforce it. A future phase may add hooks (e.g., pre-commit checks, OpenSpec validation) to make the rules structural. Phase 0 is documentation only.

---

## 8. Recommended Next Phase (Phase 1)

Phase 1 — **Introduce OpenSpec + SuperSpec Governance Schema**.

Phase 1 owns the schema layer. It should:

1. Add the schema files under `openspec/schemas/skill-forge-governance/` (e.g., `change.schema.json`, `proposal.schema.json`, `design.schema.json`, `tasks.schema.json`).
2. Update `openspec/config.yaml` to register the new schemas and bind them to the existing spec directories.
3. Add docs under `docs/03-openspec/` that explain how a change moves from `proposal.md` → `design.md` → `tasks.md` → `verification.md` → `archive.md`, and how the new schemas enforce the rules.
4. Cross-link the schema docs from `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, and `OPENCODE.md` so that the Agent entry points can reference concrete schema requirements.
5. Add a small example change under `openspec/changes/` (something safe, like `add-governance-schema-example`) that uses the new schema end-to-end, so the next implementer has a working template.

Phase 1 should still **not** modify business code (`src/skill_forge/**`), tests, or templates. It is a governance-schema phase, not an implementation phase.

After Phase 1, Phase 2 should be the first phase that integrates the new governance with a real code change. The natural candidate is the pre-existing in-progress work in `src/skill_forge/{adoption,experience,lifecycle}/`, retro-fitted into an OpenSpec change.

---

## 9. Phase 0 Hand-off Summary

```text
Phase 0 回传：

- 修改文件列表（仅 Phase 0 新增或更新的治理文件）：
  - AGENTS.md                                        (new)
  - CODEX.md                                         (new)
  - OPENCODE.md                                      (new)
  - SUPERPOWERS.md                                   (new)
  - CLAUDE.md                                        (modified — +44 lines, "Implementation Governance" section only)
  - README.md                                        (modified — +21 lines, "Governance Entry Points" section only)
  - README.zh-CN.md                                  (modified — +21 lines, "治理入口" section only)
  - docs/00-project/governance-bootstrap-report.md   (new, this file)

- 是否误改 src/tests/templates/configs/openspec/pyproject.toml/uv.lock：
  否。Phase 0 未写入任何禁止路径。

- 验证命令结果：
  - git diff --stat           : 0
  - git diff --name-only      : 0
  - uv run skill-forge --help : 0 (18 commands listed)
  - uv run pytest             : 0 (265 passed in ~16.75s)

- 报告文件：docs/00-project/governance-bootstrap-report.md

- 遇到的问题：
  - AGENT.md（单数）与 AGENTS.md（复数）并存，单数版本未删除（不在 Phase 0 允许列表内），详见报告 Section 5.1。
  - 工作树中已存在大量与 Phase 0 范围外的预存修改（src/、tests/、openspec/ 等），未纳入本提交，详见报告 Section 3.1 / 7.2。
```
