## 1. OpenSpec Artifacts

- [x] 1.1 Create proposal, design, delta specs, and task checklist for optional LLM-assisted generation.

## 2. LLM Refinement Core

- [x] 2.1 Add LLM provider/refiner module with environment-based configuration and clear errors.
- [x] 2.2 Parse structured JSON LLM responses and merge only supported non-empty requirement fields.
- [x] 2.3 Add unit tests for successful refinement, unknown-field ignoring, malformed responses, and missing configuration.

## 3. Create Command Integration

- [x] 3.1 Add `skill-forge create --llm` and run refinement before blueprint enrichment.
- [x] 3.2 Preserve the existing deterministic create path when `--llm` is absent.
- [x] 3.3 Add CLI tests for default behavior, successful LLM-assisted generation, and LLM error output.

## 4. Verification

- [x] 4.1 Run automated tests and strict OpenSpec validation.
