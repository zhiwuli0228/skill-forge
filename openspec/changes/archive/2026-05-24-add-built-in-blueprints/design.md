## Context

Skill Forge now enriches generated Skills with built-in blueprint defaults when `RequirementAnalyzer` sets a matching `task_type`. The blueprint infrastructure and merge path are already in place.

This change should only increase the useful built-in coverage and add deterministic recognition rules. It should not change the blueprint schema or introduce explicit blueprint selection.

## Goals / Non-Goals

**Goals:**

- Add built-in blueprints for code review, test generation, and OpenSpec change workflows.
- Preserve the existing bug investigation blueprint.
- Add deterministic analyzer rules for the new task types.
- Ensure each new blueprint produces visibly task-specific generated content.

**Non-Goals:**

- Do not add a `--blueprint` CLI option.
- Do not add user-defined blueprint directories.
- Do not add references/assets/scripts generation.
- Do not add quality scoring or LLM behavior.
- Do not redesign the existing blueprint model or loader.

## Decisions

### Add three new blueprints first

The first expansion targets `code-review`, `test-generation`, and `openspec-change` because they are common coding-agent workflows and map cleanly to stable prompts.

Alternative considered: add many more blueprints at once. That would increase coverage but dilute review quality and make recognition errors harder to isolate.

### Keep recognition deterministic and conservative

The analyzer will use keyword rules for common English and Chinese phrasing. It should classify only obvious requests for the new task types.

Alternative considered: fuzzy scoring across all blueprints. That belongs in a later selection change and would be harder to test.

### Let blueprints provide task-specific content

The analyzer should identify `task_type`, name, domain, and basic description, while the blueprint should provide the detailed workflow, outputs, constraints, and quality gates through the existing enrichment path.

This keeps task-specific generation content in YAML files instead of expanding hardcoded analyzer branches.

## Risks / Trade-offs

- Keyword rules may misclassify overlapping terms such as “review tests”. Mitigation: order rules from more specific to less specific and test representative examples.
- Generated names may be basic for Chinese-only requests. Mitigation: add task-specific names for recognized task types.
- Blueprint content may become generic. Mitigation: tests should assert task-specific phrases unique to each blueprint appear in generated output.
