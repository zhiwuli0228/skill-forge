## 1. Blueprint Attachment Model

- [x] 1.1 Add a generated file declaration model with relative path and content.
- [x] 1.2 Add references/assets/scripts declarations to `SkillBlueprint`.
- [x] 1.3 Validate attachment paths reject absolute paths and `..` traversal.
- [x] 1.4 Add at least one built-in reference declaration to a blueprint.

## 2. Generation

- [x] 2.1 Copy applied blueprint file declarations into `SkillRequirement`.
- [x] 2.2 Update `SkillGenerator` to write declared references/assets/scripts.
- [x] 2.3 Ensure generated file paths resolve inside the package directory before writing.
- [x] 2.4 Preserve single-file output for blueprints without declarations and generic fallback.

## 3. Validation and Tests

- [x] 3.1 Add validation support for optional attachment path metadata.
- [x] 3.2 Add tests for blueprint declaration loading and unsafe path rejection.
- [x] 3.3 Add tests for generated reference files and metadata.
- [x] 3.4 Add regression tests for no-attachment packages.
- [x] 3.5 Run `uv run pytest` and `openspec validate add-blueprint-reference-assets --strict`.
