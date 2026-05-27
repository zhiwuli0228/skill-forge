## Context

Skill Forge already has a local research corpus update path:

```text
source config
  -> fetch one URL
  -> normalize one document
  -> store raw/normalized cache
  -> write one document and one skill_examples row
  -> search over local corpus
```

This works for official documentation pages, but it does not discover individual Skill packages from community repositories. A `type: github` source is currently fetched like any other URL, so a GitHub repository becomes one cached HTML document instead of multiple searchable `SKILL.md` examples.

The new capability should remain repo-scoped and configuration-driven. It should not crawl the public internet or install community Skills automatically.

## Goals / Non-Goals

**Goals:**

- Discover `SKILL.md` files from configured GitHub repositories.
- Fetch discovered Skill files as raw content from stable raw URLs or API content endpoints.
- Cache each discovered Skill as an individual document.
- Parse `SKILL.md` frontmatter and content into `skill_examples` metadata.
- Make discovered community Skills searchable through the existing `search` command.
- Preserve existing docs-source update behavior.
- Cover discovery with mocked tests, not live GitHub network calls.

**Non-Goals:**

- Do not implement GitHub-wide search.
- Do not implement a public marketplace.
- Do not install discovered Skills automatically.
- Do not rank by stars, forks, downloads, or social signals.
- Do not require a GitHub token for public repositories.
- Do not change the search command into a networked command.

## Decisions

1. Use GitHub API tree discovery instead of parsing GitHub HTML.

   Rationale: The GitHub tree API returns structured paths and blob metadata, which is more stable than scraping repository pages. Public unauthenticated access is enough for small MVP tests, and optional token support can be added through environment configuration later.

   Alternative considered: Fetch repository HTML and parse links. This is fragile, harder to test, and couples the feature to GitHub UI markup.

2. Make discovery opt-in through source metadata.

   Rationale: Existing `type: github` behavior should remain compatible unless a source declares discovery metadata. This also lets users control path patterns and avoid unexpectedly scanning large repositories.

   Example:

   ```yaml
   metadata:
     platform: codex
     tags: [skills, community]
     discovery:
       branch: main
       skill_file_patterns:
         - "*/SKILL.md"
         - "skills/*/SKILL.md"
         - ".codex/skills/*/SKILL.md"
         - ".claude/skills/*/SKILL.md"
         - ".opencode/skills/*/SKILL.md"
   ```

   Alternative considered: Discover from every `type: github` source automatically. That risks slow updates, rate-limit surprises, and unexpected repository traversal.

3. Reuse existing corpus tables for MVP storage.

   Rationale: `documents` can represent each discovered `SKILL.md`, and `skill_examples` can store parsed name, description, platform, summary, tags, quality score, and normalized path. This keeps the change small and avoids schema migration unless implementation reveals a concrete gap.

   Alternative considered: Add dedicated `discovered_skills` table. That gives richer provenance but is not required to make search work.

4. Store discovered Skill document URLs as stable per-file identifiers.

   Rationale: Hash-based skip behavior needs each discovered Skill to have a stable URL. Use a raw content URL or API blob URL that includes owner, repo, branch, and path.

   Alternative considered: Use the repository URL for every discovered document. That would collapse multiple files into one document row and break per-Skill caching.

5. Keep search offline and unchanged from the user's perspective.

   Rationale: `search` already indexes local corpus documents and should not fetch remote content. Community discovery belongs to `update`.

## Risks / Trade-offs

- GitHub API rate limits may interrupt large repo discovery -> Mitigate by keeping discovery opt-in, adding clear partial failure reporting, and testing with small mocked trees.
- Repositories may contain invalid or incomplete `SKILL.md` files -> Mitigate by storing valid text when possible and deriving fallback metadata from path/content while reporting skipped invalid files clearly.
- Path patterns may match too many files -> Mitigate with default conservative patterns and a maximum discovered file count per source if needed.
- Branch names vary (`main`, `master`, custom) -> Mitigate with configurable branch and a default that can be overridden in source metadata.
- Existing `github` sources without discovery metadata may behave differently by accident -> Mitigate by preserving the current single-document fetch path unless discovery metadata is present.
