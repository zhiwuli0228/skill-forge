## Context

Skill Forge already has the local foundation and non-interactive Skill generation. Generated packages contain `SKILL.md`, but there is no static quality check and no way to place generated Skills into target agent platform directories. The design document defines validator and installer as separate modules so later workflows can reuse them after interactive generation, project-context generation, or corpus-assisted generation.

This change should complete the local MVP loop while remaining offline and deterministic.

## Goals / Non-Goals

**Goals:**

- Add `skill-forge validate <skill-path>` for static Skill package validation.
- Add `skill-forge install <skill-name> --target <codex|opencode|claude> --scope <project|user>`.
- Represent validation results with structured error and warning models.
- Use `python-frontmatter` to parse `SKILL.md` metadata.
- Keep validator and installer reusable outside CLI code.
- Resolve install paths consistently for project and user scopes.
- Prevent overwrite by default and support explicit `--force`.
- Add tests for both module-level behavior and CLI integration.

**Non-Goals:**

- No interactive overwrite confirmation; MVP uses `--force`.
- No automatic validation during `create`.
- No automatic install prompt after generation.
- No backup creation before overwrite.
- No package versioning, diffing, or upgrade command.
- No network, LLM, retrieval, or project context behavior.

## Decisions

1. Keep validation as a pure local static check.

   Rationale: The validator should only inspect a Skill directory and its `SKILL.md`, returning errors and warnings. It should not mutate files or call generation logic.

   Alternative considered: make `validate` repair missing sections. That would blur responsibility and belongs in a later quality enhancement change.

2. Treat missing required package elements as errors and missing recommended sections as warnings.

   Rationale: Missing directory, `SKILL.md`, frontmatter, `name`, or `description` makes a Skill unusable. Missing sections reduce quality but do not necessarily make the package invalid.

   Alternative considered: fail on every missing recommended section. That is too strict for validating third-party Skills and conflicts with the design document's warning levels.

3. Install by copying the generated package directory.

   Rationale: Copying preserves future package files such as references, assets, or scripts. Installing only `SKILL.md` would constrain later generated package structures.

   Alternative considered: copy only `SKILL.md`. Simpler for MVP but inconsistent with the product goal of generating standard Skill packages.

4. Resolve generated packages by name from the configured output directory.

   Rationale: The documented command is `install <skill-name>`, so the installer should look up `output_dir/<skill-name>` rather than requiring a path.

   Alternative considered: require a source path. That can be added later, but it does not match the MVP command shape.

5. Use explicit platform and scope enums at the CLI boundary.

   Rationale: Typer can constrain valid choices and make errors user-visible before filesystem operations. Installer internals can work with strings from those validated values.

   Alternative considered: accept arbitrary strings and fail later. That gives worse error messages and makes path handling less predictable.

## Risks / Trade-offs

- Codex project-level path is not defined in the design document. -> Support user-scope Codex through config and use a conservative project path of `.codex/skills/<skill-name>` for project scope.
- Overwrite with `--force` can delete user modifications in the install target. -> Keep default no-overwrite behavior and make `--force` explicit.
- Validation warnings may be subjective. -> Limit MVP warnings to documented standard sections and description specificity.
- Existing generated packages from earlier tests may cause install conflicts. -> Tests should use isolated home and project directories.

## Migration Plan

This change is additive. Existing `init` and `create` behavior remains unchanged. New modules and commands are added, and tests extend the suite. No database migration is required.

Rollback would remove the `validate` and `install` commands and their modules while preserving generation output.

## Open Questions

- Should future install behavior create backups before forced overwrite?
- Should future `create` run validator automatically and report warnings immediately?
