## Context

Skill Forge already has `SkillRequirement` as the normalized input to template rendering. The next generation of fast Skill creation needs task-specific defaults, but connecting those defaults to generation before the file format and validation are stable would make later changes harder to reason about.

This change introduces blueprints as inspectable configuration data only. The existing `create` command remains unchanged, and later changes can decide how to merge blueprints into `SkillRequirement`.

## Goals / Non-Goals

**Goals:**

- Define a minimal `SkillBlueprint` model that mirrors the reusable parts of `SkillRequirement`.
- Store built-in blueprints as repository-owned YAML files.
- Load blueprints deterministically from a known built-in directory.
- Validate required fields and stable IDs at load time.
- Expose read-only CLI commands for listing and showing blueprints.

**Non-Goals:**

- Do not modify `skill-forge create`.
- Do not merge blueprints into generated Skills.
- Do not support user-defined blueprint directories.
- Do not support blueprint inheritance, composition, variables, or templating.
- Do not generate references, assets, or scripts from blueprints.
- Do not add LLM behavior.

## Decisions

### Use YAML files for built-in blueprints

Blueprints will live in a small built-in config directory and use one YAML document per blueprint. YAML matches the existing config style and is easy to review in diffs.

Alternative considered: Python constants. That would be simpler to load but worse for future external/user-defined blueprints and less readable for non-code contributors.

### Keep fields close to `SkillRequirement`

The first blueprint model will include `id`, `name`, `description`, `task_type`, `when_to_use`, `when_not_to_use`, `required_inputs`, `workflow`, `constraints`, `expected_outputs`, and `quality_gates`.

This avoids inventing a second vocabulary before generation integration exists.

Alternative considered: a more abstract schema with sections and weighted rules. That is too broad for the first change and would be harder to validate.

### Add a `blueprints` Typer sub-app

The CLI will expose:

```bash
skill-forge blueprints list
skill-forge blueprints show <blueprint-id>
```

This keeps blueprint discovery separate from generation commands and leaves room for future commands such as validation or user blueprint paths.

Alternative considered: top-level `list-blueprints` and `show-blueprint` commands. A sub-app is cleaner as the feature grows.

### Fail clearly on invalid blueprint data

The loader will raise a dedicated blueprint error for invalid files, duplicate IDs, unreadable YAML, or missing blueprints. CLI commands will translate those errors into non-zero exits with user-readable messages.

Alternative considered: skip invalid blueprints and continue. That hides repository errors and makes tests less reliable.

## Risks / Trade-offs

- Blueprint schema may be too small for future package generation needs. Mitigation: keep this change explicitly limited to data and inspection; extend schema in later changes.
- CLI subcommand naming may conflict with future commands. Mitigation: group under `blueprints`, which is broad enough for later list/show/validate commands.
- Built-in directory path resolution can be brittle after packaging. Mitigation: resolve relative to the installed `skill_forge` package path instead of the current working directory.
