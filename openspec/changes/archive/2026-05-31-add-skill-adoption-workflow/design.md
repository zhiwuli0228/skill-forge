## Context

Skill Forge currently has two adjacent but disconnected flows:

```text
create -> validate -> quality report -> library -> eval/upgrade/install
update -> search -> cached corpus examples
```

The recent community discovery work lets configured GitHub repositories produce individual cached `SKILL.md` examples, and search can rank them as local corpus results. Those results are not yet first-class local library packages, so users must manually inspect cache paths or copy files if they want to evaluate or install a discovered Skill.

The adoption workflow should bridge that gap without changing search into a networked command and without treating community content as automatically trusted.

## Goals / Non-Goals

**Goals:**

- Provide a deterministic local `adopt` command for cached corpus Skill documents.
- Make search results expose stable local references usable by `adopt`.
- Preserve adopted `SKILL.md` content unless the user explicitly requests package naming changes.
- Store adoption provenance in `skill-forge.json`.
- Reuse existing validation, quality report, repair suggestion, library, eval, diff, upgrade, and install behavior after adoption.
- Keep the workflow local and testable with existing SQLite/cache boundaries.

**Non-Goals:**

- Do not fetch remote content during `adopt`.
- Do not implement GitHub-wide search or a public marketplace.
- Do not automatically install adopted Skills.
- Do not automatically rewrite or repair community Skill content.
- Do not rank by stars, forks, downloads, or other social signals.
- Do not require a new database schema unless implementation proves the existing corpus metadata is insufficient.

## Decisions

1. Adopt from stable corpus IDs, not transient search result positions.

   `skill-forge adopt --document-id <id>` is the first supported input. If a document has a related `skill_examples.id`, the command may also accept `--example-id <id>` to disambiguate later, but the minimum contract is document-based adoption.

   Rationale: Search result numbers are ordering-dependent and can change with ranking, rerank, `--top-k`, query text, or corpus freshness. Corpus document IDs are already persisted in SQLite and represent the local cached object users are adopting.

   Alternative considered: `skill-forge adopt --result 1` immediately after search. That requires session state or query replay semantics and creates ambiguity when ranking changes.

2. Expose corpus references in search output.

   `SearchResult` should carry `document_id` and optional `example_id` from `CorpusDocument`. CLI search output should show these IDs in compact form, or through an existing/detail output mode if the table becomes too wide.

   Rationale: Users need an ergonomic bridge from search to adoption, and exposing IDs keeps the bridge explicit and local.

   Alternative considered: Ask users to inspect normalized cache paths. That leaks implementation details and is harder to document.

3. Introduce a focused adoption service.

   Add a small service boundary, for example `skill_forge.adoption.service.SkillAdoptionService`, responsible for loading a corpus document by ID, validating it as adoptable Skill content, choosing the output package path, writing `SKILL.md`, writing provenance, and returning validation/quality results.

   Rationale: Adoption touches corpus storage, package writing, provenance, and validation. Keeping it outside `cli.py` and outside the generator avoids mixing generated-from-requirement logic with adopted-from-corpus logic.

   Alternative considered: Reuse `SkillGenerator`. That would incorrectly imply the content is regenerated from requirements and could accidentally apply blueprints or templates to community content.

4. Preserve content and only rename package metadata when explicit.

   By default, adoption writes the cached Skill body as `SKILL.md` unchanged. The package directory name is derived from frontmatter `name` when available, or from the document title as a slug fallback. If the user passes `--name`, the package directory and provenance use that package name, but `SKILL.md` content is not rewritten in the first version.

   Rationale: The first adoption workflow should be a trust-preserving import, not a transformation pipeline. Existing validation warnings can tell users when frontmatter and package names diverge.

   Alternative considered: Rewrite frontmatter `name` when `--name` is supplied. That is convenient but changes third-party content and needs clearer ownership semantics.

5. Store adoption provenance as an extension of existing package metadata.

   Extend `skill-forge.json` with fields that can represent generated and adopted origins. Adoption metadata should include at least origin type, source name, source/document URL when available, `document_id`, optional `example_id`, platform, content hash, and adoption timestamp.

   Rationale: Library `show`, `diff`, upgrade, and future governance features need to know whether a package came from local generation or external adoption.

   Alternative considered: Store adoption metadata only in SQLite. That would make copied packages less self-describing and weaken library compatibility.

6. Reuse validation and quality reporting after writing the package.

   After adoption writes the package, run the existing validator and quality report builder. CLI output should mirror `create`/`validate` behavior, including deterministic repair suggestions.

   Rationale: Community Skills should enter the same quality gate as locally generated packages, but adoption should not block on warnings.

   Alternative considered: Validate before writing only. That fails for package-name lint and provenance/library integration checks that depend on the final package path.

7. Conflicts fail by default.

   If the target package directory already exists, adoption exits with a clear error. A later `--force` can be proposed if users need replacement semantics, but the first version should avoid accidental overwrites.

   Rationale: Adopted packages may be manually edited or evaluated after import. Silent replacement would risk data loss.

   Alternative considered: Automatically suffix names like `-2`. That avoids errors but creates hard-to-predict package names and weakens reproducibility.

## Risks / Trade-offs

- Cached corpus content may not be a valid Skill package -> Adoption still writes the package only when `SKILL.md` content is present, then reports validation errors and repair suggestions clearly.
- Search output may become too wide -> Keep IDs short and numeric, or expose them in detailed output while documenting the adopt flow.
- A corpus document can have multiple examples -> Start with document adoption and support optional `example_id` when needed; do not invent search session state.
- `--name` without frontmatter rewrite can trigger package/name mismatch warnings -> Accept this for first version and surface the existing lint warning instead of silently modifying content.
- Existing provenance model may be generation-centric -> Add origin fields compatibly so old `skill-forge.json` files remain readable.
- Adopted community content may contain unsafe attachment references -> First version adopts only `SKILL.md`; validator and future attachment handling can address richer packages separately.

## Migration Plan

No migration is required for existing generated packages or existing corpus data.

Implementation should be additive:

1. Add search result ID fields and CLI display.
2. Add corpus document lookup helpers without replacing existing `load_documents`.
3. Add adoption provenance fields with backwards-compatible defaults for existing metadata.
4. Add the adoption service and CLI command.
5. Reuse existing validation, quality report, library display, and tests.

Rollback is straightforward because adopted packages are ordinary local output directories. Removing the command does not affect existing generated package readability.

## Open Questions

- Should first-version `adopt` accept `--example-id`, or should it be reserved until a real multiple-example document case appears?
- Should search always show corpus IDs, or should it add a dedicated option such as `--show-ids` to avoid changing compact output too much?
- Should a later change add a content-rewriting `repair` or `normalize` flow for adopted packages after validation?
