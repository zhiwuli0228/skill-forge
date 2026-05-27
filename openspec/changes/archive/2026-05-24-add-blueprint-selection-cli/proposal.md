## Why

Blueprint-backed generation currently depends on automatic task recognition. That is useful for obvious requests, but users need a deterministic way to force a specific built-in blueprint when the request wording is ambiguous or the analyzer would classify it incorrectly.

## What Changes

- Add `--blueprint <blueprint-id>` to `skill-forge create`.
- Load and apply the specified built-in blueprint before rendering.
- Make explicit blueprint selection take precedence over automatic task-type matching.
- Return a clear non-zero error when the specified blueprint does not exist or cannot be loaded.
- Preserve existing automatic matching and generic fallback when `--blueprint` is not provided.
- Keep interactive create and `--project` behavior compatible with explicit blueprint selection.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `local-skill-generation`: `create` supports explicit blueprint selection via `--blueprint`.
- `skill-blueprints`: built-in blueprints can be selected by ID for requirement enrichment.

## Impact

- Updates the Typer `create` command signature and error handling.
- Extends blueprint enrichment to support explicit blueprint IDs.
- Adds tests for explicit selection, missing blueprint errors, automatic matching fallback, and project/interactive compatibility.
- Does not add a blueprint editor, interactive blueprint selector, references/assets/scripts generation, or new dependencies.
