## 1. Retrieval Context Preparation

- [x] 1.1 Inspect existing retrieval APIs and identify the smallest adapter needed for generation reference lookup.
- [x] 1.2 Implement a generation retrieval context model that carries used/skipped status, skipped reason, source names, and extracted patterns.
- [x] 1.3 Add local TF-IDF lookup for similar Skill references without remote refresh, vector search, or rerank.
- [x] 1.4 Add corpus-size, relevance, and content-quality gates that skip RAG when reference quality is insufficient.

## 2. Pattern Extraction

- [x] 2.1 Extract compact workflow patterns from retrieved Skill content.
- [x] 2.2 Extract compact constraint patterns from retrieved Skill content.
- [x] 2.3 Extract compact quality gate patterns from retrieved Skill content.
- [x] 2.4 Limit extracted context size and remove empty or duplicate patterns before prompt injection.

## 3. LLM Prompt Integration

- [x] 3.1 Extend LLM refiner context building to accept optional retrieval patterns after blueprint and project context enrichment.
- [x] 3.2 Update the LLM prompt to treat retrieved patterns as reference guidance only.
- [x] 3.3 Preserve existing structured response parsing, unknown-field ignoring, field-level fallback, and whole-response fallback with retrieval context present.
- [x] 3.4 Ensure retrieval errors fall back to the existing no-RAG LLM prompt without failing generation.

## 4. Provenance and Reporting

- [x] 4.1 Extend provenance metadata with retrieval augmentation usage status, skipped/fallback reason, and referenced Skill names or identifiers.
- [x] 4.2 Write retrieval augmentation metadata for LLM-assisted generated packages.
- [x] 4.3 Ensure deterministic and `--no-llm` generation do not perform retrieval augmentation or claim RAG usage.
- [x] 4.4 Confirm content quality metrics are present for with-RAG and without-RAG comparison.

## 5. Tests and Validation

- [x] 5.1 Add unit tests for generation retrieval lookup, quality gates, and skip reasons.
- [x] 5.2 Add unit tests for pattern extraction and context-size limiting.
- [x] 5.3 Add LLM refiner tests covering prompt context with RAG, malformed LLM field fallback with RAG, and retrieval failure fallback.
- [x] 5.4 Add CLI or generation tests verifying provenance for used, skipped, and disabled retrieval augmentation states.
- [x] 5.5 Run focused tests for retrieval, LLM refiner, CLI generation, and quality reports.
- [x] 5.6 Run `openspec validate "add-retrieval-augmentation" --strict`.
