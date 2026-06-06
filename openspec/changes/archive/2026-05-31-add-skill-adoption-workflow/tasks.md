## 1. Corpus References

- [x] 1.1 Add `document_id` and optional `example_id` fields to search result models.
- [x] 1.2 Populate search result corpus reference fields from indexed corpus documents.
- [x] 1.3 Add a corpus reader lookup method for loading a single cached document by `document_id`.
- [x] 1.4 Include source/document URL metadata in the corpus lookup result when available.
- [x] 1.5 Update search CLI output to display adoptable local corpus references.

## 2. Adoption Provenance

- [x] 2.1 Extend generated package provenance models to represent adopted origins without breaking existing generated metadata.
- [x] 2.2 Add adoption metadata fields for origin type, adopted timestamp, source name, source URL, document ID, optional example ID, platform, and content hash.
- [x] 2.3 Update library metadata loading so adopted package provenance is parsed and displayed.
- [x] 2.4 Update library diff behavior to include adoption provenance differences through existing metadata diff output.

## 3. Adoption Service

- [x] 3.1 Add an adoption service module for creating packages from cached corpus documents.
- [x] 3.2 Implement default package name derivation from Skill frontmatter `name`.
- [x] 3.3 Implement slug fallback naming from corpus document title when frontmatter `name` is missing.
- [x] 3.4 Implement explicit package naming with `--name` semantics that do not rewrite `SKILL.md`.
- [x] 3.5 Reject missing corpus documents with a clear adoption error.
- [x] 3.6 Reject existing target package directories with a clear conflict error.
- [x] 3.7 Write adopted `SKILL.md` content without applying generator templates, blueprints, or automatic repairs.
- [x] 3.8 Write `skill-forge.json` adoption provenance after package creation.
- [x] 3.9 Run validation and build a quality report for the written adopted package.

## 4. CLI Integration

- [x] 4.1 Add `skill-forge adopt --document-id <id>`.
- [x] 4.2 Add `--name <package-name>` to the adoption command.
- [x] 4.3 Add `--home` and `--output-dir` adoption options consistent with existing library commands.
- [x] 4.4 Display adoption success output including package path and provenance summary.
- [x] 4.5 Display validation errors, warnings, quality report, and deterministic repair suggestions after adoption.
- [x] 4.6 Return non-zero for missing documents, package conflicts, and adopted packages with validation errors.

## 5. Tests

- [x] 5.1 Add search retrieval tests for result `document_id` and `example_id` propagation.
- [x] 5.2 Add CLI search tests for displayed adoptable references.
- [x] 5.3 Add corpus reader tests for document lookup success, missing document, and URL metadata.
- [x] 5.4 Add adoption service tests for successful adoption from valid cached Skill content.
- [x] 5.5 Add adoption service tests for missing document, missing frontmatter name fallback, explicit name override, package conflict, and invalid adopted Skill content.
- [x] 5.6 Add library tests for listing/showing adopted packages and displaying adoption provenance.
- [x] 5.7 Add CLI adoption tests for success, validation warning suggestions, validation error exit, missing document, package conflict, and name override.

## 6. Documentation and Verification

- [x] 6.1 Update `README.md` with the search-to-adopt workflow.
- [x] 6.2 Update `README.zh-CN.md` with the search-to-adopt workflow.
- [x] 6.3 Run focused tests for search, corpus reader, adoption service, library, and CLI adoption behavior.
- [x] 6.4 Run `uv run pytest`.
- [x] 6.5 Run `openspec validate "add-skill-adoption-workflow" --strict`.
- [x] 6.6 Run `openspec validate --all --strict`.
