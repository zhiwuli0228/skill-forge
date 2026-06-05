# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

It is the **Claude Code implementation entry** for the `skill-forge` repository. Universal rules (reading order, scope discipline, OpenSpec-first rule, source-of-truth rule, verification rule, stop conditions) are defined in `AGENTS.md` and are not duplicated here. This file layers implementation-specific rules on top of them.

## Implementation Governance

### Pre-Implementation

1. **Read `AGENTS.md` first.** Then read this file. Then read `SUPERPOWERS.md`. Then read the project docs (`README.md` / `README.zh-CN.md`) and the relevant `docs/`.
2. **Confirm the plan.** Implementation must follow a `plan.md` and a `tasks.md` produced by Codex (or a directly user-scoped instruction). If neither exists for a non-trivial change, **stop and ask** — do not improvise.
3. **Confirm the OpenSpec change.** Non-trivial changes per `AGENTS.md` Section 6 require an OpenSpec change on disk before implementation. If the change is not yet on disk, stop and report.
4. **Confirm the allowed-path list.** Read the plan's allowed/forbidden paths and write them down before touching any file. If a step requires a path that is not on the allowed list, stop and ask.

### During Implementation

1. **Stay inside scope.** Only modify paths explicitly listed in the plan. Do not edit adjacent files for "consistency". Do not reformat unrelated code. Do not rename things.
2. **No opportunistic refactors.** "While I'm here" is a scope violation. If a refactor is genuinely needed, surface it as a follow-up task; do not fold it into the current diff.
3. **No silent scope expansion.** If a plan step cannot be completed without touching a forbidden path, stop and report. Do not work around the boundary.
4. **Prefer minimal diffs.** Touch the smallest set of files that satisfies the plan step. Avoid new abstractions for a single occurrence.
5. **Preserve existing behavior.** Do not change public CLI surfaces, artifact formats, or config schemas unless the plan explicitly says so.
6. **Do not commit without permission.** Commit preparation is allowed only when the user explicitly asks. Pushing requires a separate explicit instruction.

### Post-Implementation

1. **Run verification.** Execute every verification command listed in the plan and in the OpenSpec change. Record the exact commands, exit statuses, and observed outputs.
2. **Record evidence.** Verification evidence must be written into the change artifacts (e.g., the OpenSpec change folder or a verification log) — not only into chat.
3. **On failure, do not paper over it.** If a verification step fails:
   - Do not modify the diff to make the test pass without understanding the root cause.
   - Apply `systematic-debugging` (see `SUPERPOWERS.md`) before touching code.
   - Report the failure with: command, exit code, error excerpt, suspected cause, and proposed next step.
4. **Stop conditions.** Stop and output **BLOCKED** (or an explicit failure reason) when:
   - Required context is missing.
   - A verification command cannot run for non-environmental reasons.
   - The diff would have to touch a forbidden path to complete the plan.
   - The plan and the actual repository state disagree in a way that affects the diff.

### Hand-off Format

When handing implementation back to the user (or to Codex for review), include:

- Changed files (exact paths).
- Verification commands run, with exit status.
- Test results (pass/fail counts, or a clear "skipped" reason).
- Any deviations from the plan and the reason for each.
- Any blockers or open questions.

## Project Overview

Skill Forge is a local-first CLI tool for generating, validating, and installing AI agent Skills (SKILL.md packages) for platforms like Codex, opencode, and Claude Code.

## Common Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run skill-forge --help
uv run skill-forge <command>

# Run tests
uv run pytest
uv run pytest tests/test_cli.py  # single test file

# Editable install for local development
uv pip install -e .
```

## Architecture

The CLI entry point is `src/skill_forge/cli.py` using Typer. Commands delegate to service classes in each module.

**Core flow for `create` command:**
```
cli.create → RequirementAnalyzer → BlueprintRequirementEnricher → SkillGenerator → SkillValidator → provenance written to skill-forge.json
```

**Key modules:**
- `generator/` - Jinja2 template rendering and SKILL.md generation
- `validator/` - Static validation of generated Skill packages
- `requirement/` - Rule-based requirement parsing from natural language
- `blueprints/` - Built-in and custom blueprint loading/enriching
- `research/` / `retrieval/` - Corpus update and TF-IDF search
- `project_context/` - Reads AGENTS.md, CLAUDE.md, openspec/ for project constraints
- `installer/` - Installs Skills to platform-specific directories
- `evals/` - Deterministic eval case runner
- `upgrade/` - Generates upgrade candidates from provenance + current blueprints

## Data Flow

User requirement string → `SkillRequirement` Pydantic model → Jinja2 template → `GeneratedSkillPackage` → `ValidationResult` → Optional `skill-forge.json` provenance

## Local Workspace Layout

Default: `~/.skill-forge/`
- `config.yaml` - User configuration
- `sources.yaml` - Research corpus sources
- `db/skill_forge.sqlite` - Metadata
- `corpus/raw/` and `corpus/normalized/` - Research content
- `drafts/` - Interactive creation drafts
- `output/` - Generated Skill packages
- `blueprints/` - User custom blueprints

## Environment Variables

- `SKILL_FORGE_HOME` - Override default workspace path
- `SKILL_FORGE_LLM_API_KEY`, `SKILL_FORGE_LLM_MODEL`, `SKILL_FORGE_LLM_BASE_URL` - LLM refinement settings

## Blueprints

Built-in blueprints in `blueprints/` define task-specific templates. Project custom blueprints at `<project>/.skill-forge/blueprints/` are included when `--project` is supplied.
