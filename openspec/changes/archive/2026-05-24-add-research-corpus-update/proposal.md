## Why

Skill Forge can create Skills locally, but generated output cannot yet benefit from up-to-date official and community Skill references. This change adds a manual research update pipeline that fetches configured sources, stores raw and normalized content, and records corpus metadata for later search and generation quality improvements.

## What Changes

- Add a default `configs/sources.yaml` containing official and standards-oriented Skill documentation sources.
- Add `skill-forge update` to run a manual corpus refresh.
- Load source definitions from the project default config and allow a user override file in the Skill Forge home directory.
- Fetch enabled docs and GitHub-style sources with `httpx`.
- Save raw fetched content under the local corpus raw directory.
- Normalize fetched content into text/Markdown and save it under the local corpus normalized directory.
- Compute content hashes and skip unchanged documents.
- Write source, document, and extracted Skill example metadata to SQLite.
- Continue updating other sources when one source fails.
- Return non-zero when all enabled sources fail.
- Add focused tests using mocked fetchers and isolated storage paths.

## Capabilities

### New Capabilities

- `research-corpus-update`: Covers configured source loading, manual network update, raw/normalized corpus caching, SQLite metadata persistence, content-hash skipping, and partial failure handling.

### Modified Capabilities

- None.

## Impact

- Affected command surface: adds `skill-forge update`.
- Affected source areas: new research updater, fetcher/extractor/normalizer components, corpus store helpers, source models, and CLI wiring.
- Affected local filesystem: reads `configs/sources.yaml`, optionally reads `~/.skill-forge/sources.yaml`, and writes under `~/.skill-forge/corpus/raw`, `~/.skill-forge/corpus/normalized`, and SQLite.
- Affected dependencies: uses existing `httpx`, `PyYAML`, `trafilatura`/HTML extraction support, and SQLite.
- Out of scope: search/retrieval command, TF-IDF index creation, complex pattern extraction, scheduled updates, and automatic create-time refresh prompts.
