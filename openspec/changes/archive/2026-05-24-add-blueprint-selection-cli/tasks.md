## 1. Enrichment Support

- [x] 1.1 Extend blueprint enrichment to accept an optional explicit blueprint ID.
- [x] 1.2 Ensure explicit blueprint selection overrides task-type matching.
- [x] 1.3 Preserve existing merge behavior for scalar fields and list de-duplication.

## 2. CLI Integration

- [x] 2.1 Add `--blueprint <blueprint-id>` to `skill-forge create`.
- [x] 2.2 Return a clear non-zero CLI error when the specified blueprint is missing or invalid.
- [x] 2.3 Preserve automatic matching behavior when `--blueprint` is not provided.
- [x] 2.4 Preserve interactive create and project context behavior with explicit blueprint selection.

## 3. Tests and Verification

- [x] 3.1 Add unit tests for explicit blueprint enrichment and override behavior.
- [x] 3.2 Add CLI tests for explicit selection and missing blueprint errors.
- [x] 3.3 Add regression tests for automatic matching and generic fallback.
- [x] 3.4 Run `uv run pytest` and `openspec validate add-blueprint-selection-cli --strict`.
