## Context

Skill Forge now has four built-in blueprints and can automatically enrich requirements when `RequirementAnalyzer` identifies a matching `task_type`. The next roadmap step is to make selection explicit through CLI input, without changing blueprint data structures or adding package asset generation.

Current flow:

```text
RequirementAnalyzer.analyze
  -> BlueprintRequirementEnricher.enrich by task_type
  -> optional ProjectContextEnricher
  -> SkillGenerator
```

The new flow when `--blueprint` is passed:

```text
RequirementAnalyzer.analyze
  -> BlueprintRequirementEnricher.enrich by blueprint id
  -> optional ProjectContextEnricher
  -> SkillGenerator
```

## Goals / Non-Goals

**Goals:**

- Add `skill-forge create "<requirement>" --blueprint <blueprint-id>`.
- Ensure explicit blueprint ID selection overrides automatic task-type matching.
- Preserve requirement-derived scalar fields such as generated name and description.
- Preserve existing create behavior when no blueprint is specified.
- Surface missing blueprint IDs as clear CLI errors.

**Non-Goals:**

- Do not add an interactive blueprint picker.
- Do not add blueprint editing commands.
- Do not add user-defined blueprint directories.
- Do not generate references/assets/scripts.
- Do not add quality scoring or LLM behavior.

## Decisions

### Extend the existing enricher

`BlueprintRequirementEnricher` will gain an optional blueprint ID path. If an ID is supplied, it loads that blueprint directly and merges defaults. If not, it keeps the current task-type matching behavior.

Alternative considered: handle explicit selection entirely inside `cli.py`. That would duplicate merge/error behavior and make future callers harder to reuse.

### Preserve analyzer-derived identity

Explicit blueprint selection will not overwrite `SkillRequirement.name`, `description`, `target_platform`, or `language`. It only enriches list fields through the existing merge rules.

This keeps `skill-forge create "Python 服务 review" --blueprint code-review` output named from the request/analyzer while using the selected blueprint content.

### Error before project context and generation

If a specified blueprint is missing, `create` fails before project context reading and before writing output. This avoids partial output and makes the failure easy to understand.

## Risks / Trade-offs

- Users can choose a blueprint that does not semantically match the request. Mitigation: this is intentional; explicit selection is an override.
- Requirement names may not match the selected blueprint. Mitigation: this change preserves current naming behavior; explicit name controls can be considered separately.
- Interactive draft content changes when a blueprint is explicit. Mitigation: enrichment happens before draft creation, matching the existing automatic enrichment path.
