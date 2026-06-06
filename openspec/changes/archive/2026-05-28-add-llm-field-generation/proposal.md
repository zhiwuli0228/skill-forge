## Why

`skill-forge create --llm` currently runs LLM refinement before blueprint enrichment and treats malformed known fields as whole-response failures. That makes it hard to use blueprint defaults as fallback content and hard to prove that LLM assistance improves the generated Skill's workflow, constraints, and quality gates.

This change turns LLM assistance into field-level generation after blueprint enrichment, while preserving the deterministic non-LLM path and adding enough content quality measurement to validate whether the new behavior is actually better.

## What Changes

- Move the `--llm` refinement point to after blueprint enrichment, and after project context enrichment when project context is supplied.
- Change the LLM prompt contract from generic requirement refinement to task-specific Skill requirement field generation.
- Allow LLM output to generate or rewrite `workflow`, `constraints`, and `quality_gates`, while continuing to refine supported descriptive fields.
- Add field-level validation and fallback so a malformed known list field falls back to its pre-LLM value without failing the whole create.
- Keep whole-request LLM failures recoverable by falling back to the blueprint-enriched non-LLM requirement for `create --llm`.
- Record field-level LLM provenance in generated metadata, including generated fields, fallback fields, and optionally refined fields.
- Add a minimum deterministic content quality baseline for workflow specificity, constraint verifiability, and quality gate clarity.
- Preserve existing default behavior when `--llm` is not supplied.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llm-assisted-generation`: LLM assistance changes from whole-requirement refinement before blueprint enrichment to field-level generation after blueprint enrichment with field fallback.
- `local-skill-generation`: The create pipeline, LLM/blueprint ordering, project-context ordering, and generated provenance metadata change for LLM-assisted non-interactive creation.
- `generation-quality-report`: Quality reports gain deterministic content quality metrics used to compare LLM-assisted output against deterministic output.

## Impact

- Affected source areas:
  - `src/skill_forge/cli.py`
  - `src/skill_forge/llm/refiner.py`
  - `src/skill_forge/models/generated.py`
  - `src/skill_forge/models/quality.py`
  - `src/skill_forge/generator/skill_generator.py`
- Affected tests:
  - `tests/test_llm_refiner.py`
  - `tests/test_cli.py`
  - `tests/test_generation_quality_report.py`
  - `tests/test_skill_generator.py`
- No new provider, model registry, strategy flag, Ollama client, RAG flow, or default automatic LLM behavior is introduced.
