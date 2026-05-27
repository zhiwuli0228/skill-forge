## 1. CLI Structure

- [x] 1.1 Add a Typer CLI module for the `skill-forge` application.
- [x] 1.2 Update `src/skill_forge/__init__.py` so `main()` delegates to the Typer app.
- [x] 1.3 Add the `init` command with user-facing Rich output.
- [x] 1.4 Verify `skill-forge --help` lists the `init` command.

## 2. Paths and Configuration

- [x] 2.1 Add path helpers for the Skill Forge home directory and standard subdirectories.
- [x] 2.2 Add Pydantic configuration models for update, create, retrieval, and platform settings.
- [x] 2.3 Implement default configuration creation as YAML.
- [x] 2.4 Implement configuration loading with defaults and user config overrides.
- [x] 2.5 Ensure existing `config.yaml` is preserved when `init` runs again.

## 3. Workspace Initialization

- [x] 3.1 Implement directory creation for `corpus`, `drafts`, `output`, `index`, `logs`, and `db`.
- [x] 3.2 Implement SQLite initialization for `sources`, `documents`, `skill_examples`, `skill_patterns`, and `drafts`.
- [x] 3.3 Make workspace and database initialization idempotent.
- [x] 3.4 Return clear success information from `skill-forge init`.

## 4. Tests

- [x] 4.1 Add CLI tests for help output and the `init` command.
- [x] 4.2 Add tests for default configuration values and config preservation.
- [x] 4.3 Add tests for path helpers using isolated temporary directories.
- [x] 4.4 Add tests that verify the SQLite baseline tables are created.
- [x] 4.5 Run the test suite and fix failures for this change.

## 5. Documentation and Verification

- [x] 5.1 Confirm `skill-forge --help` succeeds from the project environment.
- [x] 5.2 Confirm `skill-forge init` creates the documented local workspace.
- [x] 5.3 Update `docs/openspec_change_plan.md` to mark `establish-cli-foundation` progress after implementation begins or completes.
