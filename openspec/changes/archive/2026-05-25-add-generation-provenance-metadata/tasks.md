## 1. Provenance Models

- [x] 1.1 Add generation provenance metadata models with schema version and attachment manifests.
- [x] 1.2 Add applied blueprint metadata fields to `SkillRequirement` during blueprint enrichment.

## 2. Metadata Writing

- [x] 2.1 Write `skill-forge.json` after successful non-interactive generation quality reporting.
- [x] 2.2 Include requirement text, target platform, language, task type, blueprint ID/source, LLM flag, project path, quality summary, and attachments.
- [x] 2.3 Ensure metadata does not persist full project context summary text.

## 3. Library Integration

- [x] 3.1 Read optional `skill-forge.json` in `SkillLibraryManager.show`.
- [x] 3.2 Display provenance summary in `skill-forge show`.
- [x] 3.3 Extend `skill-forge diff` to include `skill-forge.json` differences when metadata differs.
- [x] 3.4 Preserve `list`, `show`, and `diff` behavior for old packages without metadata.

## 4. Tests

- [x] 4.1 Add generator/CLI tests for writing provenance metadata.
- [x] 4.2 Add library tests for show with provenance and show without provenance.
- [x] 4.3 Add diff tests for metadata differences and missing metadata.
- [x] 4.4 Run focused tests and full `uv run pytest`.

## 5. OpenSpec Verification

- [x] 5.1 Run `openspec validate "add-generation-provenance-metadata" --strict`.
- [x] 5.2 Run `openspec validate --all --strict`.
