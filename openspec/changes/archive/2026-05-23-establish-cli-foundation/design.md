## Context

Skill Forge is intended to be a local-first Python CLI, but the current package only exposes a placeholder `main()` function. Later changes depend on a stable command surface, predictable local data paths, configuration loading, and a database schema that can be reused by generation, validation, installation, research updates, and retrieval.

The design document defines Python 3.11+, Typer, Rich, Pydantic, PyYAML / pydantic-settings, and SQLite as the foundation stack. This change should use those existing dependencies and avoid introducing new ones.

## Goals / Non-Goals

**Goals:**

- Provide a real `skill-forge` CLI application backed by Typer.
- Implement `skill-forge --help` and `skill-forge init`.
- Create the standard local data layout under a configurable Skill Forge home directory.
- Generate a default user configuration when none exists.
- Load configuration with defaults and user overrides.
- Initialize a SQLite database with the baseline tables described by the design document.
- Keep modules small enough for later changes to build on without refactoring the foundation.

**Non-Goals:**

- No Skill generation, validation, installation, research update, search, interaction wizard, or project context behavior.
- No network access.
- No LLM integration.
- No destructive reset of existing user data.
- No automatic migration framework beyond idempotent baseline schema creation.

## Decisions

1. Use Typer for the command application and keep the package script entry point as `skill_forge:main`.

   Rationale: `pyproject.toml` already maps `skill-forge` to `skill_forge:main`, and Typer matches the design document. The package-level `main()` should delegate to the CLI app so future commands can be added without changing the script contract.

   Alternative considered: keep direct argument parsing in `__init__.py`. This would be faster initially but would make command growth and testing worse.

2. Separate path resolution, configuration, and SQLite initialization into dedicated modules.

   Rationale: Later changes need the same paths and configuration. A small module boundary prevents `init` from becoming a pile of filesystem and serialization logic.

   Alternative considered: implement everything inside the CLI command. This would pass the first acceptance test but would create duplication when `create`, `install`, `update`, and `search` need the same state.

3. Make initialization idempotent and non-destructive.

   Rationale: Users may run `skill-forge init` multiple times. Existing configuration and database files must not be overwritten by default.

   Alternative considered: always rewrite the config and recreate the database. That risks losing user settings and future metadata.

4. Support configurable home directory through code-level path resolution, while defaulting to `~/.skill-forge`.

   Rationale: Production behavior should use the documented default, but tests need isolated temporary homes. The implementation can expose a path resolver parameter or environment-aware helper without adding a new public CLI option in this change.

   Alternative considered: hardcode `Path.home() / ".skill-forge"` everywhere. That makes tests brittle and risks touching real user data during test runs.

5. Use SQLite `CREATE TABLE IF NOT EXISTS` statements for the baseline schema.

   Rationale: This satisfies first-run initialization and repeated initialization without a migration system. Later changes can introduce migrations if schema evolution becomes necessary.

   Alternative considered: add a full migration tool now. That is premature for the foundation change.

## Risks / Trade-offs

- Baseline schema may need refinement when later corpus or draft behavior is implemented. -> Keep schema creation isolated in one storage module and use idempotent table creation.
- Tests could accidentally write to the real home directory. -> Design path helpers so tests can pass an isolated home directory.
- Rich output could make CLI tests brittle. -> Assert stable command results and key text rather than exact terminal styling.
- `init` can report success even when an existing config is old. -> This change only guarantees baseline initialization; schema/config upgrades can be handled by later changes.

## Migration Plan

Implementation can be introduced directly because no existing user-facing behavior is available yet. The placeholder `main()` should be replaced by delegation to the Typer app.

Rollback is straightforward: remove the new modules and restore the placeholder entry point, though later changes should not be started until this foundation is stable.

## Open Questions

- Should a future change add a public `--home` option for all commands, or keep test-only path injection internal?
- Should future schema updates use explicit migrations, a schema version table, or idempotent additive DDL for the first few releases?
