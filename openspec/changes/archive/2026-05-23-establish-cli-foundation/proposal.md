## Why

Skill Forge currently only has a minimal package entry point and cannot be used as the CLI tool described in the design document. This change establishes the executable foundation needed before Skill generation, validation, installation, research updates, or retrieval can be built safely.

## What Changes

- Introduce a Typer-based `skill-forge` CLI application.
- Replace the placeholder package entry point with a real CLI entry point.
- Add an `init` command that prepares the local Skill Forge workspace.
- Add configuration models and default configuration generation.
- Add path resolution for the user data directory and standard subdirectories.
- Initialize a SQLite database file with the baseline metadata schema needed by later changes.
- Add focused tests for CLI help, initialization behavior, configuration defaults, and database initialization.

## Capabilities

### New Capabilities

- `cli-foundation`: Covers the executable CLI shell, initialization command, local configuration, standard data directories, and baseline SQLite initialization.

### Modified Capabilities

- None.

## Impact

- Affected source areas: `src/skill_forge/__init__.py`, new CLI/config/storage modules under `src/skill_forge/`, and tests.
- Affected command surface: `skill-forge --help` and `skill-forge init`.
- Affected local filesystem: creates `~/.skill-forge/` with config, database, corpus, drafts, output, index, and logs directories.
- Affected dependencies: uses existing project dependencies including Typer, Rich, Pydantic, pydantic-settings, PyYAML, and SQLite from the Python standard library.
