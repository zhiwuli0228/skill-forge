## Context

Skill Forge currently loads blueprints from a single repository-owned built-in directory. That keeps built-in generation deterministic, but it prevents teams from maintaining their own reusable Skill standards without modifying the project source tree.

The existing blueprint model is already close to what custom blueprints need: YAML files are validated with Pydantic, duplicate IDs are rejected within one directory, and generation can enrich a `SkillRequirement` by explicit blueprint ID or task type. This change should extend the source roots while preserving deterministic behavior.

## Goals / Non-Goals

**Goals:**

- Load built-in, user-level, and project-level blueprint YAML files through one loader path.
- Preserve current built-in behavior when no custom blueprint directories exist.
- Surface blueprint source information in CLI output.
- Allow `create --blueprint <id>` to use custom blueprints.
- Reject duplicate IDs across all loaded roots instead of relying on hidden precedence.

**Non-Goals:**

- Do not implement a remote blueprint marketplace.
- Do not implement interactive blueprint editing.
- Do not introduce blueprint versioning or upgrade behavior.
- Do not change the blueprint YAML schema beyond source metadata exposed after loading.

## Decisions

1. Represent loaded blueprints with source metadata outside the YAML schema.

   Rationale: User YAML should remain compatible with the existing `SkillBlueprint` format. Source metadata is about where the file was loaded from, not author-provided blueprint content.

   Alternative considered: Add `source` fields to blueprint YAML. That would make user files noisier and allow incorrect source declarations.

2. Add a wrapper model for loaded blueprints.

   The loader will return records that contain:

   ```text
   blueprint: SkillBlueprint
   source: builtin | user | project
   path: Path
   ```

   Rationale: Existing generation code needs the `SkillBlueprint`, while CLI display and duplicate diagnostics need source/path.

3. Load roots in deterministic order and reject duplicates globally.

   Proposed order:

   ```text
   builtin
   user
   project
   ```

   The order is stable for output, but it is not precedence. If the same ID appears in more than one loaded root, loading fails with a clear duplicate ID error.

   Rationale: Hidden override behavior would make `create --blueprint <id>` hard to debug. Explicit failure is safer for the first custom-blueprint version.

4. Keep project blueprints opt-in through `--project`.

   Project roots are included only when the CLI command receives a project path. The default project blueprint root is:

   ```text
   <project>/.skill-forge/blueprints
   ```

   Rationale: This keeps normal global commands bounded and avoids surprising scans of the current working directory.

5. Create the user blueprint directory during `init`.

   The default user root is:

   ```text
   <home>/blueprints
   ```

   Rationale: It gives users a discoverable place to put private blueprints without requiring additional setup.

## Risks / Trade-offs

- Duplicate ID failures may initially surprise users who expect project overrides → Mitigation: use clear diagnostics that include source and path for duplicates.
- CLI output can become wider when adding source/path → Mitigation: show `Source` in list and keep full path only in `show`.
- Project custom blueprints require passing `--project` to list/show/create → Mitigation: document this as intentional opt-in behavior.
- Existing tests may assume built-in-only loader return types → Mitigation: keep convenience methods that return `SkillBlueprint` where generation code expects it.

## Migration Plan

No data migration is required. Existing built-in blueprints remain valid, and existing commands keep their behavior when no user or project blueprint directories contain YAML files.

The change can be rolled back by restoring the single-root loader and removing the new CLI/project-root wiring.

## Open Questions

- Should a future change allow explicit project override precedence instead of duplicate failure?
- Should a future change add `skill-forge blueprints validate <path>` for standalone blueprint authoring?
