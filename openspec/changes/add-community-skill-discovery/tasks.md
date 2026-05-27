## 1. Source Metadata and Models

- [x] 1.1 Add structured discovery metadata parsing for GitHub sources, including branch and `skill_file_patterns`.
- [x] 1.2 Add models for discovered GitHub Skill candidates and fetched discovered Skill files.
- [x] 1.3 Preserve compatibility for existing docs sources and GitHub sources without discovery metadata.

## 2. GitHub Discovery

- [x] 2.1 Implement a GitHub repository URL parser for supported `https://github.com/<owner>/<repo>` URLs.
- [x] 2.2 Implement repository tree retrieval using mocked-testable HTTP boundaries.
- [x] 2.3 Match tree file paths against configured Skill file patterns.
- [x] 2.4 Fetch discovered `SKILL.md` file content through stable raw or API content URLs.
- [x] 2.5 Handle per-file fetch failures without aborting the whole source when other discovered files succeed.

## 3. Skill Extraction and Storage

- [x] 3.1 Parse discovered `SKILL.md` frontmatter for name and description.
- [x] 3.2 Derive fallback metadata from file path and normalized content when frontmatter is incomplete.
- [x] 3.3 Store each discovered Skill as a separate raw and normalized corpus document.
- [x] 3.4 Store one `skill_examples` row per discovered Skill with platform, tags, summary, and quality score metadata.
- [x] 3.5 Preserve hash-based skip behavior for unchanged discovered Skill files.

## 4. Update Integration

- [x] 4.1 Route GitHub sources with discovery metadata through the discovery pipeline.
- [x] 4.2 Keep existing single-document update behavior for docs sources and GitHub sources without discovery metadata.
- [x] 4.3 Report source-level update outcomes for discovery sources, including updated, skipped, failed, and partial-failure cases.
- [x] 4.4 Update default or example source configuration to show opt-in community discovery without enabling broad crawling by default.

## 5. Search Integration

- [x] 5.1 Ensure discovered community Skill examples are loaded by `CorpusReader`.
- [x] 5.2 Verify `skill-forge search "code review skill"` can return a discovered community Skill result.
- [x] 5.3 Verify `--platform` ranking boosts apply to discovered community Skill examples.
- [x] 5.4 Preserve search as an offline local-corpus operation.

## 6. Tests and Verification

- [x] 6.1 Add mocked tests for repository URL parsing, tree discovery, pattern matching, and raw file fetch.
- [x] 6.2 Add mocked tests for frontmatter extraction, fallback metadata, cache writes, and hash skip behavior.
- [x] 6.3 Add update integration tests for discovered Skill storage and partial failures.
- [x] 6.4 Add search tests for discovered code review Skill results and platform filtering/boosting.
- [x] 6.5 Run `uv run pytest`.
- [x] 6.6 Run `openspec validate "add-community-skill-discovery" --strict`.
