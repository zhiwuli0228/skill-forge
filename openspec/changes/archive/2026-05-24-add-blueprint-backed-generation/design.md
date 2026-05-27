## Context

The current `create` flow is:

```text
requirement text
  -> RequirementAnalyzer.analyze(...)
  -> optional ProjectContextEnricher.enrich(...)
  -> SkillGenerator.generate(...)
```

`add-blueprint-data-model` introduced `SkillBlueprint` and a built-in `bug-investigation` blueprint, but generation does not use it yet.

This change inserts a deterministic enrichment step after requirement analysis and before project context enrichment.

## Goals / Non-Goals

**Goals:**

- Match built-in blueprints by `SkillRequirement.task_type`.
- Apply blueprint defaults to missing or generic requirement fields.
- Preserve explicitly parsed user constraints and outputs.
- Preserve project context injection behavior.
- Preserve fallback behavior when no blueprint matches.

**Non-Goals:**

- Do not add `--blueprint`.
- Do not add more blueprints.
- Do not generate references/assets/scripts.
- Do not add quality scoring.
- Do not introduce LLM behavior.

## Decisions

### Match by `task_type`

The enricher will use `SkillRequirement.task_type` to find a blueprint with the same `task_type`.

This avoids broad keyword matching in two places. The analyzer remains responsible for task classification; blueprints provide defaults after classification.

Alternative considered: match directly against requirement text. That would duplicate analyzer logic and make later explicit blueprint selection harder to reason about.

### Merge into `SkillRequirement`

The enrichment step will mutate or return a `SkillRequirement` with blueprint defaults merged into existing fields. The renderer will continue to receive the same model type.

Alternative considered: passing both requirement and blueprint to the generator. That spreads merge rules into rendering and makes project context injection order less clear.

### Preserve user-derived data first

For list fields, user-derived values remain first and blueprint values are appended only when not already present. For scalar fields, existing requirement values win.

This keeps the analyzer and future interactive input authoritative while letting blueprints fill gaps.

### Apply project context after blueprint defaults

`create --project` should still add project-specific constraints after blueprint defaults. That keeps project rules visible and prevents blueprint enrichment from accidentally dropping context constraints.

## Risks / Trade-offs

- The current Java bug analyzer already produces rich task-specific fields, so the blueprint may only append a small amount at first. Mitigation: tests should assert that a field uniquely provided by the blueprint appears in generated output.
- Merging can duplicate semantically similar but differently worded constraints. Mitigation: exact case-insensitive de-duplication is enough for this change; semantic de-duplication can come later.
- A malformed built-in blueprint could break `create`. Mitigation: loader validation already fails clearly, and tests cover the built-in blueprint.
