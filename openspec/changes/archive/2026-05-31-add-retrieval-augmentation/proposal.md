## Why

LLM-assisted generation can create richer workflow, constraints, and quality gates, but it currently relies only on the user's requirement, blueprint defaults, and project context. Skill Forge already has local TF-IDF retrieval and content quality signals, so generation should be able to use high-quality similar Skills as reference context when enough local corpus data exists.

## What Changes

- Add retrieval-augmented context gathering to LLM-assisted `create` before the LLM prompt is built.
- Extract reusable workflow, constraint, and quality gate patterns from similar high-quality local Skill results.
- Inject extracted patterns into the LLM prompt as reference material only; generated output still must pass the existing structured field validation and field-level fallback.
- Skip retrieval augmentation when the local corpus is empty, insufficient, low quality, or retrieval fails.
- Record retrieval augmentation usage, skipped/fallback reason, and referenced Skill names in provenance metadata.
- Preserve existing TF-IDF search as the retrieval foundation; do not replace it with vector search or semantic reranking for generation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llm-assisted-generation`: LLM-assisted generation can receive retrieval-derived reference patterns and must preserve structured output validation and fallback behavior.
- `local-skill-generation`: Non-interactive generated package metadata records retrieval augmentation usage when LLM-assisted generation uses or skips RAG context.
- `search-retrieval`: Existing TF-IDF retrieval is reusable by generation as a local, non-blocking source of similar Skill references without invoking optional rerank.
- `generation-quality-report`: Quality metrics support comparing LLM generation with and without retrieval augmentation.

## Impact

- Affected code: `src/skill_forge/llm/refiner.py`, retrieval modules under `src/skill_forge/retrieval/`, CLI create orchestration, provenance metadata models, and related tests.
- User-facing CLI: no new command or option is required; retrieval augmentation is an implicit enhancement for LLM-assisted generation when local corpus quality is sufficient.
- Dependencies: no new remote services, vector database, semantic reranker, or model dependency.
- Compatibility: deterministic generation and explicit `--no-llm` remain unchanged; retrieval failures must not block Skill generation.
