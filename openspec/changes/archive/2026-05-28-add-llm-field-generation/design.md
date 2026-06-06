## Context

The current non-interactive `create` flow analyzes the requirement, optionally calls `RequirementLLMRefiner`, then applies blueprint defaults, optional project context, rendering, validation, quality reporting, and provenance writing. This means the LLM cannot use blueprint defaults as context or fallback values. The current LLM response parser also treats malformed known list fields as whole-response errors, which prevents partial success when only one generated field is invalid.

The existing `RequirementLLMRefiner` already accepts `workflow`, `constraints`, and `quality_gates`; the missing piece is not schema expansion alone. The change needs a generation-oriented prompt, field-level validation, field-level provenance, and a minimum deterministic way to compare content quality against the rule/blueprint path.

## Goals / Non-Goals

**Goals:**

- Run LLM field generation after blueprint enrichment and after project context enrichment when `--project` is supplied.
- Generate or rewrite task-specific `workflow`, `constraints`, and `quality_gates` from the user requirement plus enriched defaults.
- Continue supporting refinement of descriptive fields such as `description`, `when_to_use`, `when_not_to_use`, and `expected_outputs`.
- Fall back per field when a known field is malformed, empty, or unusable.
- Fall back to the pre-LLM enriched requirement when a configured LLM request fails or returns unusable top-level content.
- Record `llm_generated_fields`, `llm_fallback_fields`, and `llm_refined_fields` in generated provenance metadata.
- Add minimum deterministic content quality metrics for workflow specificity, constraint verifiability, and quality gate clarity.

**Non-Goals:**

- No default automatic LLM behavior; `create` without `--llm` remains deterministic and offline.
- No `--strategy`, `--model`, `--no-fallback`, model registry, Ollama client, or provider abstraction beyond the existing OpenAI-compatible client.
- No RAG, experience store, or automatic repair.
- No LLM-based quality scoring.

## Decisions

1. Run LLM after enrichment.

   The `create --llm` path will become `RequirementAnalyzer -> BlueprintRequirementEnricher -> ProjectContextEnricher -> RequirementLLMRefiner -> SkillGenerator`. This lets the LLM see the same blueprint-backed content the deterministic path would use and lets fallback restore those field values without re-running earlier pipeline steps. The alternative was to keep the current order and teach the LLM about blueprint candidates separately, but that would duplicate blueprint selection behavior and make explicit blueprint precedence harder to preserve.

2. Keep one structured LLM request, but validate fields independently.

   The client will still request one JSON object containing supported fields. The refiner will parse the object, ignore unknown fields, and validate known fields one by one. A malformed known field will be recorded in `llm_fallback_fields` and left unchanged, while valid fields are applied. This avoids per-field network calls and keeps prompt cost bounded. The alternative was one LLM request per generated field, which would simplify attribution but make generation slower and more failure-prone.

3. Separate generated, refined, and fallback provenance.

   `workflow`, `constraints`, and `quality_gates` are generated fields when accepted from the LLM. Descriptive fields are refined fields when accepted. Any supported field the LLM returned but the refiner rejected is a fallback field. If the whole response fails, all core generated fields that had pre-LLM values are fallback fields. This gives users and tests a stable audit trail without storing raw prompts or responses in `skill-forge.json`.

4. Keep explicit configuration errors fatal.

   Missing `SKILL_FORGE_LLM_API_KEY` or `SKILL_FORGE_LLM_MODEL` remains a clear non-zero error for `--llm`, because the user explicitly requested LLM assistance and no provider can be called. Runtime request failures, empty responses, invalid JSON, and invalid field values fall back to the enriched deterministic requirement so generation can continue. The alternative was to make all `--llm` failures fatal, but that would contradict the field-level fallback goal.

5. Add minimum content quality metrics to `GenerationQualityReport`.

   The first version will compute deterministic scores from the generated requirement or rendered sections:
   - workflow specificity
   - constraint verifiability
   - quality gate clarity

   These scores are informational and must not change validation success. They provide the comparison signal needed before later changes alter default behavior. The alternative was to rely on the existing 0-100 quality score, but that score is mainly driven by validation warnings/errors and does not measure whether content is task-specific.

## Risks / Trade-offs

- LLM output may include Markdown wrappers, wrong types, or generic content -> parse fenced JSON only as an input tolerance, then enforce strict field types and fallback rejected fields.
- Partial fallback could hide poor LLM behavior -> record fallback fields in provenance and expose minimum content quality metrics for comparison.
- Moving LLM after blueprint enrichment could change `--llm` outputs for users who depend on current ordering -> keep the command interface unchanged and preserve non-LLM behavior exactly.
- Content quality heuristics may be mechanical -> keep them informational, deterministic, and minimal in this change; expand them later in `add-content-quality-rules`.

## Migration Plan

1. Add field-level refiner result metadata without changing the public `--llm` option.
2. Reorder the non-interactive `create --llm` pipeline after blueprint and project context enrichment.
3. Extend generated provenance metadata with optional LLM field lists and content quality metrics.
4. Add focused tests for refiner parsing/fallback, CLI ordering, provenance, and quality metrics.
5. Rollback by restoring the previous LLM call point and removing the new optional provenance and quality fields; generated Skill packages remain valid because metadata additions are non-breaking.

## Open Questions

- Should `show` display content quality metrics in this change, or should that wait for `add-content-quality-rules`?
- Should whole-response invalid JSON mark all supported fields as fallback, or only the core generated fields that had pre-LLM values?
