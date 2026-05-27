## Context

The updater already records per-source outcomes with `updated`, `skipped`, `failed`, and `disabled` statuses. The CLI currently prints only updated/skipped/failed counts, so disabled and partial-success states are not visible in the summary.

Search ranking already computes relevance plus deterministic boosts for authority, completeness, freshness, and platform match. The CLI currently displays only the final score, even though component values are already present on `SearchResult`.

## Goals / Non-Goals

**Goals:**

- Make update summaries clearly show disabled sources.
- Mark partial update success when at least one source succeeds and at least one source fails.
- Show retry guidance for failed sources.
- Add optional `search --explain` output for ranking components.
- Preserve existing default output and ranking behavior.

**Non-Goals:**

- Do not alter ranking weights or retrieval algorithm.
- Do not introduce semantic/vector search.
- Do not automatically retry failed sources.
- Do not change `create` behavior.
- Do not add remote monitoring or scheduled updates.

## Decisions

1. Extend `UpdateResult` with computed properties rather than changing outcome storage.

   Rationale: Existing tests and callers already rely on `SourceUpdateOutcome`. Computed properties keep the model simple and backward compatible.

2. Add `partial_failure_count` and `disabled_count` derived from outcomes.

   Rationale: These two counts are enough for user-facing summary without inventing new statuses.

3. Keep failed outcome status as `failed` and add retry guidance in CLI rendering.

   Rationale: Persisting a separate retry field is unnecessary for deterministic CLI guidance.

4. Add `SearchResult.explanation` as a derived property.

   Rationale: Score components already exist, and a stable formatted explanation avoids duplicate formatting logic.

5. Gate explanation output behind `--explain`.

   Rationale: Default search output should remain compact and compatible.

## Risks / Trade-offs

- More columns can make CLI tables wider -> Mitigation: only add update summary counts as text and keep search explanation optional.
- Static retry guidance may be generic -> Mitigation: include the actual failure message and a concrete next command.
- Explaining boosts can expose small implementation details -> Mitigation: the values are already deterministic result fields and useful for debugging.

## Migration Plan

No migration is required. Existing data and source outcome statuses remain valid. Users who do not pass `--explain` keep the same search workflow.
