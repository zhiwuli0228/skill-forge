## 1. Blueprint Data

- [x] 1.1 Add the `SkillBlueprint` model with validation for required fields and kebab-case IDs.
- [x] 1.2 Add a built-in `bug-investigation` blueprint YAML file.
- [x] 1.3 Implement blueprint loading, deterministic sorting, duplicate detection, and lookup errors.

## 2. CLI

- [x] 2.1 Add a `blueprints` CLI command group.
- [x] 2.2 Implement `skill-forge blueprints list`.
- [x] 2.3 Implement `skill-forge blueprints show <blueprint-id>`.
- [x] 2.4 Translate blueprint loading and lookup errors into clear CLI messages and non-zero exits where appropriate.

## 3. Tests and Verification

- [x] 3.1 Add unit tests for blueprint model validation and loader behavior.
- [x] 3.2 Add CLI tests for blueprint list/show and missing blueprint errors.
- [x] 3.3 Verify existing `create`, `validate`, and `install` behavior remains unchanged.
- [x] 3.4 Run `uv run pytest` and `openspec validate add-blueprint-data-model --strict`.
