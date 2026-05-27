## Context

Skill Forge can now create, validate, install, and refine Skills locally. The next capability is to build a local research corpus that later generation and search workflows can use. The design document calls for manual updates, source configuration, raw and normalized caches, SQLite metadata, hash-based skipping, and partial failure handling.

This change should implement the update pipeline only. Search, TF-IDF indexing, ranking, create-time stale prompts, and project-context generation remain separate changes.

## Goals / Non-Goals

**Goals:**

- Add `skill-forge update` as the manual research refresh command.
- Provide default source configuration in `configs/sources.yaml`.
- Support user override source configuration at `~/.skill-forge/sources.yaml`.
- Fetch enabled docs and GitHub-style sources.
- Save raw content and normalized text/Markdown to the local corpus.
- Store source/document/skill-example metadata in SQLite.
- Compute content hashes and skip unchanged documents.
- Continue after individual source failures and summarize results.
- Return non-zero only when all enabled sources fail.
- Keep components testable with mocked fetchers and isolated storage.

**Non-Goals:**

- No `search` command.
- No TF-IDF index creation.
- No ranking implementation.
- No automatic update on create.
- No scheduled background update.
- No complex pattern extraction.
- No LLM summarization.

## Decisions

1. Keep the updater as an orchestrator over smaller components.

   Rationale: Fetching, normalization, and persistence have different failure modes and tests. A small orchestrator can report source-level outcomes without owning every detail.

   Alternative considered: implement all update logic in the CLI command. That would be faster initially but difficult to test and extend for search.

2. Load user source config in preference to bundled defaults when present.

   Rationale: Users need to customize sources without editing project files. This mirrors the design document's `~/.skill-forge/sources.yaml` override.

   Alternative considered: merge default and user source files. That is useful later, but replacement semantics are simpler and predictable for the MVP.

3. Persist raw and normalized content as files, and metadata in SQLite.

   Rationale: Raw files preserve traceability. Normalized files support future indexing. SQLite keeps metadata queryable without forcing full-text storage into the database.

   Alternative considered: store all content in SQLite. That complicates large document handling and makes manual inspection harder.

4. Use content hash to skip unchanged documents.

   Rationale: Repeated updates should avoid rewriting normalized files and metadata when fetched content has not changed.

   Alternative considered: always rewrite. Simpler, but it loses useful change detection and makes update output noisy.

5. Treat source failures as isolated unless all enabled sources fail.

   Rationale: Network sources are inherently unreliable. A single failing source should not block cached updates from other sources.

   Alternative considered: fail fast on the first source error. That would be fragile for a multi-source research corpus.

## Risks / Trade-offs

- Network tests can be flaky. -> Use mocked fetchers for automated tests and keep real network behavior behind injectable components.
- HTML normalization quality can vary. -> Keep the MVP normalization conservative and persist raw content for later improvements.
- GitHub source fetching can expand in scope. -> MVP should fetch URL content directly and leave repository tree traversal or API-specific crawling for later.
- Schema needs may grow during search implementation. -> Use existing baseline tables and additive fields only when necessary.

## Migration Plan

This change is additive. Existing commands remain unchanged. The existing SQLite baseline tables are reused. `skill-forge update` should initialize the workspace/database if needed before writing corpus data.

Rollback would remove the update command, source config, and research/corpus modules. Generated Skills and existing local MVP commands are unaffected.

## Open Questions

- Should future search create the TF-IDF index during `update` or as a separate `search` bootstrap step?
- Should later updates merge bundled and user sources instead of replacing bundled sources when a user source file exists?
