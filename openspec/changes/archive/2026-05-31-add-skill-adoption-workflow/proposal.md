## Why

Skill Forge can now discover community Skill examples and make them searchable, but search results remain references rather than managed local Skill packages. Users need a local adoption workflow that turns a trusted cached Skill into something they can validate, evaluate, compare, upgrade, and install through the existing library lifecycle.

## What Changes

- Add an `adopt` workflow that creates a local generated Skill package from a cached corpus Skill document.
- Allow users to adopt by stable local corpus reference, starting with `document_id` and optionally `example_id` when available.
- Expose adoptable corpus references in search output so users can move from discovery to adoption without inspecting SQLite or cache files manually.
- Preserve the original Skill content during adoption while allowing an explicit package name override to avoid conflicts.
- Write adoption provenance to `skill-forge.json`, including source name, source URL or document URL, corpus IDs, platform metadata when available, and adoption timestamp.
- Run the existing validation, quality report, and deterministic repair suggestion flow after adoption.
- Manage adopted packages through the existing `list`, `show`, `diff`, `eval`, `upgrade`, and `install` commands.
- Do not add remote marketplace behavior, GitHub-wide search, automatic installation, automatic trust, social ranking, or automatic content rewriting.

## Capabilities

### New Capabilities
- `skill-adoption-workflow`: Defines how cached corpus Skill documents are adopted into local managed Skill packages with provenance and post-adoption validation.

### Modified Capabilities
- `search-retrieval`: Search results SHALL expose stable local corpus references that can be used by the adoption workflow.
- `skill-library-management`: Adopted Skill packages SHALL be discoverable and inspectable as generated library packages with adoption provenance.
- `skill-validation`: Adoption SHALL reuse existing validation, quality reporting, and repair suggestion behavior after writing the local package.

## Impact

- Affected CLI:
  - New `skill-forge adopt` command.
  - Search output gains adoptable reference metadata.
- Affected modules:
  - `src/skill_forge/cli.py`
  - `src/skill_forge/models/search.py`
  - `src/skill_forge/retrieval/`
  - `src/skill_forge/storage/corpus_reader.py`
  - `src/skill_forge/models/generated.py`
  - New adoption service under `src/skill_forge/adoption/` or equivalent local package boundary.
  - Existing library and validation integration points.
- Affected tests:
  - Search output tests for corpus reference IDs.
  - Adoption service tests for successful adoption, missing corpus document, invalid Skill content, package name override, and package conflicts.
  - CLI tests for adoption output, provenance display, and post-adoption validation/repair reporting.
- No new runtime dependency is expected.
