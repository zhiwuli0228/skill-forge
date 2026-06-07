# Skill Forge

[中文文档](README.zh-CN.md)

Skill Forge is a local-first CLI workspace for designing, generating, validating, updating, searching, and installing AI agent Skills.

It generates standard `SKILL.md` packages from natural-language requirements, supports interactive drafts, can inject project context, keeps a local research corpus, and installs generated Skills into Codex, opencode, or Claude-compatible directories.

The default generation path is deterministic and does not require an LLM. Optional LLM-assisted refinement is available when explicitly requested with `--llm`.

## Governance Entry Points

Skill Forge is governed by a layered entry-point set. **This README is the user entry.** The files below are the **Agent entry points** — every AI Agent (Codex, Claude Code, opencode, and any other) must read them in the listed order before working on this repository.

| File             | Purpose                                                                          |
|------------------|----------------------------------------------------------------------------------|
| `AGENTS.md`      | Universal entry point — positioning, reading order, scope rules, stop conditions |
| `CODEX.md`       | Codex entry — design, planning, OpenSpec/SuperSpec change artifacts              |
| `CLAUDE.md`      | Claude Code entry — implementation, tests, verification, evidence collection     |
| `OPENCODE.md`    | opencode entry — fallback execution under strict scope                            |
| `SUPERPOWERS.md` | Execution discipline — methodology and phase mapping, not project authority       |

**Read the governance entry points first for any non-trivial change.** A non-trivial change is anything that touches more than one module, changes a public CLI surface, changes a stored artifact format (`skill-forge.json`, `eval-report.json`, config schema, blueprint schema), or introduces a new lifecycle phase, agent role, or governance rule.

The governance stack is being built in phases:

- **Phase 0 (this phase):** entry-point files only, no schema changes.
- **Phase 1 (next):** OpenSpec + SuperSpec governance schema under `openspec/config.yaml`, `openspec/schemas/`, and `docs/03-openspec/`.

The governance files define the rules. The OpenSpec change under `openspec/changes/` is where each change is tracked.

## Features

- Generate a Skill package from a natural-language requirement.
- Apply built-in, user, or project blueprints automatically or explicitly with `--blueprint`.
- Optionally refine requirements with a configured LLM through `--llm`.
- Refine Skill requirements through an interactive wizard.
- Save and resume interactive drafts.
- Generate post-create validation and quality reports.
- Run deterministic Skill authoring lint checks as validation warnings.
- Display deterministic suggested fixes for validation and quality-report issues.
- Write generation provenance metadata to `skill-forge.json`.
- Run deterministic local eval cases and persist the latest `eval-report.json`.
- Generate upgrade candidates from provenance and current blueprint standards.
- Validate Skill package structure and `SKILL.md` frontmatter.
- Install generated Skills to Codex, opencode, or Claude directories.
- Refresh a local research corpus from configured documentation sources.
- Search the local corpus with TF-IDF ranking and platform-aware boosts.
- Read project rules such as `AGENTS.md`, `CLAUDE.md`, `README.md`, `.opencode/`, `.claude/`, `.agents/`, and `openspec/` and convert them into generation constraints.
- Inspect built-in and custom blueprints and manage generated Skill packages with list, show, and diff commands.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management and local command execution

## Installation

From the repository root:

```bash
uv sync
```

Run the CLI without installing it globally:

```bash
uv run skill-forge --help
```

For editable local development:

```bash
uv pip install -e .
```

## Quick Start

Initialize the local Skill Forge workspace:

```bash
uv run skill-forge init
```

Generate a Skill:

```bash
uv run skill-forge create "Java 存量代码 bug 定位 skill"
```

Generation automatically runs validation and prints a deterministic quality report.

Validate the generated package:

```bash
uv run skill-forge validate E:/009workspace/skills/java-bug-investigation
```

Install it into the current project for opencode:

```bash
uv run skill-forge install java-bug-investigation --target opencode --scope project
```

Use `--project` to choose a project directory explicitly:

```bash
uv run skill-forge install java-bug-investigation --target opencode --scope project --project /path/to/project
```

## Commands

### `init`

Creates the local workspace, default config, and SQLite database.

```bash
uv run skill-forge init
```

By default, Skill Forge uses `~/.skill-forge`. For isolated runs or tests:

```bash
uv run skill-forge init --home /tmp/skill-forge-home
```

You can also set:

```bash
export SKILL_FORGE_HOME=/tmp/skill-forge-home
```

### `create`

Generates a Skill package under the configured output directory, defaulting to `E:/009workspace/skills`.

```bash
uv run skill-forge create "git commit workflow skill"
```

Override the output directory for a single command:

```bash
uv run skill-forge create "git commit workflow skill" --output-dir E:/tmp/skills
```

When the analyzer detects a supported task type, Skill Forge applies a matching built-in blueprint before rendering. You can also select a built-in or custom blueprint explicitly:

```bash
uv run skill-forge create "Python service review skill" --blueprint code-review
```

Interactive mode saves a resumable draft:

```bash
uv run skill-forge create "OpenSpec change analysis skill" --interactive
```

Project-aware generation reads supported project rule files and injects derived constraints:

```bash
uv run skill-forge create "OpenSpec change skill" --project .
```

Interactive and project-aware generation can be combined:

```bash
uv run skill-forge create "OpenSpec change skill" --project . --interactive
```

Optional LLM-assisted refinement is available for non-interactive generation when `SKILL_FORGE_LLM_API_KEY` and `SKILL_FORGE_LLM_MODEL` are configured. `SKILL_FORGE_LLM_BASE_URL` can point to an OpenAI-compatible endpoint.

```bash
uv run skill-forge create "release process skill" --llm
```

LLM output is merged only into supported structured requirement fields, then the generated package still goes through validation and quality reporting.

### `blueprints`

Inspects built-in, user-level, and project-level generation blueprints.

```bash
uv run skill-forge blueprints list
uv run skill-forge blueprints show bug-investigation
```

Current built-in blueprints cover bug investigation, code review, OpenSpec change workflows, and test generation.

User custom blueprints can be placed in:

```text
~/.skill-forge/blueprints
```

Project custom blueprints are included when `--project` is supplied and can be placed in:

```text
<project>/.skill-forge/blueprints
```

```bash
uv run skill-forge blueprints list --project .
uv run skill-forge create "team review skill" --blueprint team-code-review --project .
```

### `resume`

Resumes an interactive draft from `~/.skill-forge/drafts`.

```bash
uv run skill-forge resume <draft-id>
```

### `validate`

Validates a Skill package directory.

```bash
uv run skill-forge validate E:/009workspace/skills/java-bug-investigation
```

Validation checks include:

- Skill directory exists.
- `SKILL.md` exists.
- Frontmatter exists.
- `name` and `description` are present.
- Recommended sections such as Purpose, Workflow, Output format, and Quality gates are present.
- Authoring lint warnings for name format, package/name mismatch, weak descriptions, empty sections, thin workflows, and thin quality gates.

When validation reports errors or warnings, the CLI also displays deterministic suggested fixes. Suggestions are advisory and do not modify files.

### `eval`

Runs deterministic local eval cases against a generated Skill package. Eval cases are YAML files with a target skill name and static assertions.

```bash
uv run skill-forge eval java-bug-investigation --case evals/java-bug-basic.yaml
uv run skill-forge eval java-bug-investigation --cases evals/
```

Supported assertions:

- `required_sections`: each section must appear in `SKILL.md`.
- `required_constraints`: each constraint phrase must appear in `SKILL.md`.
- `forbidden_phrases`: each phrase must be absent from `SKILL.md`.

The command writes the latest `eval-report.json` into the evaluated Skill package and exits non-zero when any assertion fails.

### `install`

Installs a generated Skill package to a target platform.

```bash
uv run skill-forge install <skill-name> --target <codex|opencode|claude> --scope <project|user>
```

Project-scope destinations:

| Target | Destination |
|---|---|
| `codex` | `<project>/.codex/skills/<skill-name>` |
| `opencode` | `<project>/.opencode/skills/<skill-name>` |
| `claude` | `<project>/.claude/skills/<skill-name>` |

User-scope destinations are configurable and default to:

| Target | Destination |
|---|---|
| `codex` | `~/.codex/skills/<skill-name>` |
| `opencode` | `~/.config/opencode/skills/<skill-name>` |
| `claude` | `~/.claude/skills/<skill-name>` |

Existing installations are not overwritten unless `--force` is passed:

```bash
uv run skill-forge install java-bug-investigation --target opencode --scope project --force
```

### `update`

Refreshes the local research corpus from configured sources.

```bash
uv run skill-forge update
```

Skill Forge stores raw and normalized source content, updates SQLite metadata, skips unchanged content by hash, and tolerates partial source failures. If every enabled source fails, the command exits non-zero.

The summary reports `ok`, `partial`, or `failed` status with updated, skipped, failed, and disabled counts. Failed source rows include retry guidance after the source issue is resolved.

Default source configuration lives in `configs/sources.yaml`. A user override can be placed at:

```text
~/.skill-forge/sources.yaml
```

### `search`

Searches the local research corpus.

```bash
uv run skill-forge search "skill creator"
```

Limit results:

```bash
uv run skill-forge search "bug investigation" --top-k 3
```

Prefer a target platform:

```bash
uv run skill-forge search "skill creator" --platform codex
```

Explain deterministic ranking components:

```bash
uv run skill-forge search "skill creator" --platform codex --explain
```

Explanation output includes relevance, authority, completeness, freshness, platform boost, and final score values.

Optionally rerank TF-IDF candidates with the built-in offline lexical reranker:

```bash
uv run skill-forge search "skill creator" --rerank
```

Filter by collection state:

```bash
uv run skill-forge search "skill creator" --collection promoted
```

Boost promoted Skills in ranking:

```bash
uv run skill-forge search "skill creator" --promoted-boost
```

Use optional semantic retrieval mode (local TF-IDF similarity):

```bash
uv run skill-forge search "skill creator" --semantic
```

Search output identifies the retrieval mode, such as `tfidf`, `tfidf+rerank`, or `semantic-tfidf`. If rerank is disabled or unavailable, search falls back to TF-IDF and prints a warning. If semantic mode is unavailable, it falls back to default retrieval.

If the corpus is empty, run `skill-forge update` first.

### `collection`

Manages governed collection states for local Skills.

Score a Skill to create or update its collection record:

```bash
uv run skill-forge collection score <skill-name>
```

List all collection records:

```bash
uv run skill-forge collection list
```

Filter by collection state:

```bash
uv run skill-forge collection list --state promoted
```

Show collection details for a Skill:

```bash
uv run skill-forge collection show <skill-id>
```

Update the collection state manually:

```bash
uv run skill-forge collection update <skill-id> --state curated --rationale "High quality evidence"
```

Valid collection states: `candidate`, `curated`, `promoted`, `rejected`.

Collected Skills are examples with governance metadata, not blueprint templates. Adoption does not auto-promote Skills; state changes require explicit scoring or manual override.

### `list`

Lists generated Skill packages from the configured output directory.

```bash
uv run skill-forge list
```

### `show`

Shows metadata for a generated Skill package, including frontmatter, package paths, attachment counts, provenance, and the latest eval summary when present.

```bash
uv run skill-forge show java-bug-investigation
```

### `diff`

Compares the `SKILL.md` files of two generated Skill packages.

```bash
uv run skill-forge diff skill-a skill-b
```

### `upgrade`

Generates a new upgrade candidate for an existing generated Skill package using its `skill-forge.json` provenance and the current recorded blueprint.

```bash
uv run skill-forge upgrade java-bug-investigation
```

The default candidate name is `<skill-name>-upgraded`. You can choose a different name:

```bash
uv run skill-forge upgrade java-bug-investigation --candidate-name java-bug-v2
```

Existing candidates are not overwritten unless `--force` is passed:

```bash
uv run skill-forge upgrade java-bug-investigation --force
```

The source Skill package is never modified. After upgrading, compare the source and candidate:

```bash
uv run skill-forge diff java-bug-investigation java-bug-investigation-upgraded
```

Packages without `skill-forge.json` cannot be upgraded because Skill Forge cannot reliably reconstruct the original requirement and blueprint source.

## Configuration

Skill Forge writes its default config to:

```text
~/.skill-forge/config.yaml
```

Default values:

```yaml
update:
  mode: manual
  stale_after_days: 7
  check_on_create: true
  auto_update_on_create: false
create:
  default_target: opencode
  default_language: zh-CN
  output_dir: E:/009workspace/skills
  interactive_by_default: false
retrieval:
  top_k: 5
  use_tfidf: true
  rerank_enabled: true
  rerank_by_default: false
  rerank_provider: lexical
  rerank_candidate_multiplier: 3
platforms:
  opencode:
    user_skills_path: ~/.config/opencode/skills
  claude:
    user_skills_path: ~/.claude/skills
  codex:
    user_skills_path: ~/.codex/skills
```

## Local Data Layout

The default workspace is:

```text
~/.skill-forge/
├── config.yaml
├── sources.yaml
├── collections/
│   ├── manifests/
│   ├── snapshots/
│   └── indexes/
├── corpus/
│   ├── raw/
│   └── normalized/
├── db/
│   └── skill_forge.sqlite
├── blueprints/
├── drafts/
├── index/
├── logs/
└── output/
```

## Generated Skill Shape

A generated package contains at least:

```text
<skill-name>/
└── SKILL.md
```

Blueprint-backed packages may also include declared references, assets, or scripts, for example:

```text
<skill-name>/
├── SKILL.md
├── skill-forge.json
├── eval-report.json
└── references/
    └── diagnosis-checklist.md
```

The generated `SKILL.md` includes:

- Frontmatter with `name` and `description`.
- Purpose.
- When to use.
- When not to use.
- Required inputs.
- Workflow.
- Constraints.
- Output format.
- Quality gates.

`skill-forge.json` records bounded generation provenance such as schema version, generation time, original requirement text, target platform, language, applied blueprint, LLM usage, project path, quality score, and generated attachment paths.

`eval-report.json` records the latest deterministic eval run summary and assertion-level case results.

## Development

Run the full test suite:

```bash
uv run pytest
```

Run a focused test file:

```bash
uv run pytest tests/test_cli.py
```

Useful local verification flow:

```bash
uv run skill-forge init --home /tmp/skill-forge-verify
uv run skill-forge create "Java 存量代码 bug 定位 skill" --home /tmp/skill-forge-verify
uv run skill-forge validate /tmp/skill-forge-verify/output/java-bug-investigation
uv run skill-forge list --home /tmp/skill-forge-verify
uv run skill-forge blueprints list
uv run skill-forge search "skill creator" --home /tmp/skill-forge-verify
```

On Windows PowerShell, replace `/tmp/skill-forge-verify` with a Windows path such as `E:\tmp\skill-forge-verify`.

## Project Structure

```text
src/skill_forge/
├── cli.py
├── config.py
├── evals/
├── generator/
├── installer/
├── interaction/
├── models/
├── project_context/
├── requirement/
├── research/
├── retrieval/
├── storage/
└── validator/
```

Supporting files:

- `templates/common/SKILL.md.j2` contains the default Skill template.
- `configs/sources.yaml` contains default research sources.
- `docs/skill_forge_design_doc.md` contains the product and architecture design.
- `docs/openspec_change_plan.md` tracks the completed OpenSpec implementation phases.
- `openspec/specs/` contains the archived capability specs.

## Current Scope

Implemented:

- Local deterministic Skill generation.
- Built-in, user, and project blueprint-backed generation with explicit blueprint selection.
- Blueprint-declared reference, asset, and script generation.
- Generation provenance metadata in `skill-forge.json`.
- Deterministic local eval cases with persisted `eval-report.json`.
- Interactive drafts and resume.
- Validation and installation.
- Post-generation quality reports.
- Authoring lint warnings in validation and quality reports.
- Deterministic suggested fixes for validation and quality-report issues.
- Research corpus update.
- Local search and ranking.
- Project context injection.
- Optional LLM-assisted requirement refinement.
- Generated Skill library commands: `list`, `show`, `diff`, and eval summary display.
- Upgrade candidate generation with `upgrade`.
- Skill collection governance with `candidate`, `curated`, `promoted`, and `rejected` states.
- Deterministic collection scoring from validation, quality, eval, lifecycle, provenance, and reuse signals.
- Collection-aware search filtering and promoted-boost ranking.
- Promoted reference preference in generation and experience accumulation.
- Optional local semantic retrieval with `--semantic` flag.

Not implemented:

- Web UI.
- Background scheduled updates.
- Remote vector database retrieval.
- Automatic in-place Skill replacement or remote migration.
