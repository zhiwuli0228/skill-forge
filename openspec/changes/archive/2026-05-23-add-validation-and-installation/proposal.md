## Why

Skill Forge can now initialize a workspace and generate a local Skill package, but users cannot yet verify package quality or install generated Skills into agent platforms. This change completes the local MVP loop by adding static validation and controlled installation.

## What Changes

- Add `skill-forge validate <skill-path>` to statically validate Skill package structure and `SKILL.md` content.
- Add validation models for errors, warnings, and aggregate validation results.
- Check required package elements such as directory existence, `SKILL.md`, frontmatter, `name`, and `description`.
- Warn on missing recommended sections such as Purpose, When to use, When not to use, Workflow, Output format, and Quality gates.
- Add `skill-forge install <skill-name> --target <codex|opencode|claude> --scope <project|user>` to install generated Skills.
- Resolve install paths for opencode, Claude Code, and configurable Codex user paths.
- Prevent overwriting existing installed Skills unless `--force` is provided.
- Add focused tests for validator behavior, installer path resolution, no-overwrite behavior, force overwrite behavior, and CLI integration.

## Capabilities

### New Capabilities

- `skill-validation`: Covers static validation of generated or existing Skill packages and reporting errors separately from warnings.
- `skill-installation`: Covers installing generated Skill packages into supported agent platform directories with target/scope path resolution and overwrite protection.

### Modified Capabilities

- None.

## Impact

- Affected command surface: adds `validate` and `install` commands.
- Affected source areas: new validation models, validator module, installer module, and CLI command wiring.
- Affected local filesystem: reads generated Skill packages from configured output directories and copies them into platform-specific skill directories.
- Affected dependencies: uses existing `python-frontmatter` and standard library filesystem utilities; no new runtime dependency is expected.
- Completes the documented local MVP sequence after `init` and `create`.
