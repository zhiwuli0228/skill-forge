## Why

Skill Forge can now generate, validate, and score structured Skill packages deterministically, but vague or nuanced requirements still rely on simple rule extraction. An optional LLM refinement path can improve descriptions, workflows, constraints, and validator-warning guidance while preserving the current local default.

## What Changes

- Add an opt-in `skill-forge create --llm` mode.
- Introduce an LLM refinement boundary that can enrich an analyzed `SkillRequirement` before blueprint enrichment and rendering.
- Add a simple, testable LLM client interface with clear configuration errors when required environment variables are missing.
- Validate and quality-report generated output after LLM refinement using the existing post-generation validation flow.
- Keep default `create` fully deterministic and offline when `--llm` is not supplied.

## Capabilities

### New Capabilities

- `llm-assisted-generation`: Covers optional LLM refinement, provider configuration behavior, failure handling, and validation requirements.

### Modified Capabilities

- `local-skill-generation`: `create` gains an opt-in `--llm` path while preserving existing non-LLM behavior.
- `generation-quality-report`: generated packages from the LLM path still go through the same validation and quality reporting flow.

## Impact

- Affected code: `src/skill_forge/cli.py`, a new LLM/refinement module, requirement models or helpers, and tests.
- Affected command: `skill-forge create "<requirement>" --llm`.
- Existing `httpx` dependency can be reused for OpenAI-compatible HTTP calls; no new dependency is required.
- Network/LLM usage remains opt-in and does not affect the default generation path.
