## Context

Skill Forge currently generates Skills from deterministic requirement analysis, blueprint enrichment, optional project context, and optional LLM-assisted field generation. The LLM path already validates structured fields and records fallback provenance. Search retrieval already uses a local TF-IDF index with deterministic quality signals, and the roadmap requires retrieval augmentation only after the LLM field generation path and quality signals exist.

The next increment is to let LLM-assisted generation use similar high-quality local Skills as reference context without changing the default deterministic path or replacing the existing retrieval foundation.

## Goals / Non-Goals

**Goals:**

- Gather similar local Skill references before LLM-assisted generation when the local corpus is available and quality-gated.
- Extract compact workflow, constraint, and quality gate patterns from retrieved Skills.
- Inject those patterns into the LLM prompt as reference context, not as content to copy.
- Record retrieval augmentation status, skipped/fallback reason, and referenced Skill names in provenance.
- Keep failures non-blocking so LLM-assisted generation falls back to the existing no-RAG prompt.
- Make RAG benefit measurable by comparing deterministic content quality metrics with and without retrieval context.

**Non-Goals:**

- Replacing TF-IDF retrieval with vector search.
- Introducing semantic reranking, embedding models, or remote retrieval dependencies.
- Adding new CLI options for generation strategy.
- Automatically copying retrieved Skill content into the generated Skill.
- Enabling retrieval augmentation for deterministic or `--no-llm` generation.

## Decisions

1. Reuse local TF-IDF retrieval for generation references.

   The generation path will call a small retrieval adapter that uses the existing local index and ranking signals. This keeps retrieval augmentation offline and consistent with the `search` command. Vector search is deferred because the roadmap explicitly says not to replace TF-IDF for this change.

2. Apply a corpus quality gate before prompt injection.

   Retrieval augmentation will run only when enough local Skill-like references are available and retrieved candidates meet a minimum relevance and content-quality threshold. This prevents sparse or low-quality corpus entries from adding noise to the prompt. If the gate fails, generation continues without RAG context and records the skipped reason.

3. Extract patterns, not full documents.

   The prompt will receive short lists such as `workflow_patterns`, `constraint_patterns`, and `quality_gate_patterns`, plus source names for traceability. Full retrieved documents are not injected because they increase token cost, raise copying risk, and make output less predictable.

4. Keep RAG inside the LLM context-building path.

   Retrieval augmentation belongs before the LLM request, after requirement analysis, blueprint enrichment, and project context enrichment. The LLM refiner can then format one structured prompt that includes baseline requirement fields and optional RAG patterns. Field-level validation and fallback remain unchanged after the response.

5. Provenance records reference metadata, not retrieved body text.

   `skill-forge.json` will record whether retrieval augmentation was used, why it was skipped or failed, and the names/identifiers of referenced Skills. It will not store full retrieved content.

## Risks / Trade-offs

- Low-quality retrieved examples add prompt noise -> Gate by relevance, content quality, and minimum corpus size; skip RAG when signals are weak.
- Prompt length increases -> Inject compact extracted patterns with configurable top-k limits instead of full documents.
- LLM copies retrieved wording too closely -> Prompt frames patterns as references only, and provenance stores source names for auditability.
- Retrieval failure blocks generation -> Treat retrieval errors as non-fatal and continue with the existing LLM-assisted path.
- Measured improvement may be insignificant -> Require with-RAG versus without-RAG content quality comparison before continuing deeper RAG investment.
