## 1. Refiner Contract

- [x] 1.1 Update the LLM system prompt and request payload to ask for task-specific Skill requirement fields.
- [x] 1.2 Add field-level parsing for supported string and list fields, ignoring unknown fields.
- [x] 1.3 Add field-level fallback metadata for known fields with invalid types, empty usable content, or rejected values.
- [x] 1.4 Add whole-response fallback handling for empty responses, invalid JSON, and non-object JSON.
- [x] 1.5 Preserve missing LLM configuration as a clear `--llm` configuration error.

## 2. Create Pipeline

- [x] 2.1 Move the non-interactive `create --llm` call point after blueprint enrichment.
- [x] 2.2 Ensure `create --llm --project <path>` calls LLM after project context enrichment.
- [x] 2.3 Preserve non-LLM create behavior when `--llm` is omitted.
- [x] 2.4 Preserve explicit blueprint precedence and blueprint fallback values during LLM-assisted generation.

## 3. Provenance Metadata

- [x] 3.1 Extend generated metadata models with optional `llm_generated_fields`, `llm_fallback_fields`, and `llm_refined_fields`.
- [x] 3.2 Populate field-level LLM provenance for successful field generation, field fallback, and accepted descriptive refinements.
- [x] 3.3 Include content quality metrics in generated metadata when available.
- [x] 3.4 Update metadata serialization without breaking existing generated package metadata.

## 4. Content Quality Baseline

- [x] 4.1 Add deterministic workflow specificity, constraint verifiability, and quality gate clarity metric models.
- [x] 4.2 Compute content quality metrics for generated Skill content or the final Skill requirement.
- [x] 4.3 Include content quality metrics in `GenerationQualityReport` without changing validation-derived status semantics.
- [x] 4.4 Display or expose the metrics consistently for both deterministic and LLM-assisted generation.

## 5. Tests

- [x] 5.1 Add refiner tests for successful workflow, constraints, and quality gates generation.
- [x] 5.2 Add refiner tests for malformed known fields falling back per field.
- [x] 5.3 Add refiner tests for empty response, invalid JSON, non-object JSON, and unknown fields.
- [x] 5.4 Add CLI tests proving non-LLM create behavior is unchanged.
- [x] 5.5 Add CLI tests proving LLM-assisted create applies blueprint and project context before LLM generation.
- [x] 5.6 Add CLI or generator tests for field-level provenance metadata.
- [x] 5.7 Add quality report tests for deterministic content quality metrics and stable repeated scoring.

## 6. Verification

- [x] 6.1 Run focused tests for LLM refiner, CLI create, generator metadata, and generation quality report.
- [x] 6.2 Run the full Python test suite.
- [x] 6.3 Run `openspec validate "add-llm-field-generation" --strict`.
- [x] 6.4 Run `openspec validate --all --strict`.
- [x] 6.5 Update `docs/intelligent-generation-roadmap.md` with proposal creation, validation commands, and next implementation step.
