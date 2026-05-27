## 1. Blueprint Loading

- [x] 1.1 Add user blueprint directory support to Skill Forge paths and default initialization.
- [x] 1.2 Add loaded blueprint source metadata while keeping blueprint YAML schema unchanged.
- [x] 1.3 Update `BlueprintLoader` to load built-in, user, and project roots deterministically.
- [x] 1.4 Reject duplicate blueprint IDs across all in-scope roots with clear diagnostics.

## 2. CLI Integration

- [x] 2.1 Update `blueprints list` to include user and project roots and display source metadata.
- [x] 2.2 Update `blueprints show` to include source and path metadata.
- [x] 2.3 Add `--project` support to blueprint inspection commands for project custom blueprints.
- [x] 2.4 Update `create --blueprint` to load user and project custom blueprints in scope.

## 3. Tests

- [x] 3.1 Add loader tests for user custom blueprints, project custom blueprints, missing custom roots, and duplicate IDs.
- [x] 3.2 Add CLI tests for listing, showing, and creating with custom blueprints.
- [x] 3.3 Run focused tests and full `uv run pytest`.

## 4. OpenSpec Verification

- [x] 4.1 Run `openspec validate "add-user-custom-blueprints" --strict`.
- [x] 4.2 Run `openspec validate --all --strict`.
