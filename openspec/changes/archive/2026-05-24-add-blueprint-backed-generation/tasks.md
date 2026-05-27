## 1. Blueprint Matching and Enrichment

- [x] 1.1 Add a service that finds a built-in blueprint by `task_type`.
- [x] 1.2 Add merge logic that enriches `SkillRequirement` list fields with non-duplicate blueprint defaults.
- [x] 1.3 Preserve existing scalar requirement fields and user-derived list values during enrichment.

## 2. Create Flow Integration

- [x] 2.1 Insert blueprint enrichment after `RequirementAnalyzer.analyze`.
- [x] 2.2 Keep project context enrichment after blueprint enrichment.
- [x] 2.3 Keep unmatched requirements on the existing generic generation path.

## 3. Tests and Verification

- [x] 3.1 Add unit tests for blueprint matching, no-match behavior, and merge de-duplication.
- [x] 3.2 Add CLI or generator tests proving Java bug generation includes blueprint-provided defaults.
- [x] 3.3 Add regression tests proving generic create still works without a matching blueprint.
- [x] 3.4 Run `uv run pytest` and `openspec validate add-blueprint-backed-generation --strict`.
