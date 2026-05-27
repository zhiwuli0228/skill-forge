# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
