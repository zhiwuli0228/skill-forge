## Context

The archived `cli-foundation` change provides a working Typer CLI, local workspace initialization, default configuration, path helpers, and SQLite baseline schema. The next product step is to make the CLI generate a usable Skill package locally.

The design document calls for a first version that does not require LLMs, network access, retrieval, project context, validation, or installation. This change should therefore focus on deterministic generation from a requirement string using rules and templates.

## Goals / Non-Goals

**Goals:**

- Add `skill-forge create "<requirement>"` as a non-interactive command.
- Convert natural language requirements into a structured `SkillRequirement`.
- Generate a stable skill name, with the Java bug investigation example producing `java-bug-investigation`.
- Render `SKILL.md` through Jinja2 templates instead of assembling Markdown in CLI code.
- Write a Skill package under the configured output directory.
- Include standard sections expected by later validator work.
- Add tests for analyzer, rendering, generation output, and CLI integration.

**Non-Goals:**

- No interactive wizard or draft persistence.
- No validator command or automatic validation result.
- No install command.
- No research corpus lookup or search.
- No project context reader.
- No LLM-powered parsing or rewriting.
- No network refresh or cache staleness prompt.

## Decisions

1. Introduce generation-specific models separate from configuration models.

   Rationale: `SkillRequirement` and `GeneratedSkillPackage` are product domain models. Keeping them under a models package avoids mixing generation state with app configuration and gives later validator, installer, and interactive workflows a shared contract.

   Alternative considered: use dictionaries throughout the generator. That would move field assumptions into templates and tests, making later changes more brittle.

2. Use a rule-based analyzer with conservative defaults.

   Rationale: The first version must work offline and without an LLM. Keyword rules can cover the documented MVP example and provide useful defaults for general requirements.

   Alternative considered: require the user to pass all fields explicitly. That would undermine the value of `create "<requirement>"` and push users toward the later interactive flow too early.

3. Keep Markdown generation in templates.

   Rationale: The design document explicitly prefers templates over hardcoded generated Markdown. Templates also make platform-specific variants easier to add later.

   Alternative considered: build `SKILL.md` with string concatenation in the generator. This is simpler initially but harder to test and extend.

4. Let `create` ensure the workspace exists enough to write output.

   Rationale: Users may run `create` before `init`. The command should be useful by creating required output directories and default config as needed, while still preserving `init` as the explicit setup command.

   Alternative considered: fail unless `skill-forge init` has already run. That creates an avoidable first-use failure for local generation.

5. Do not overwrite existing generated Skill packages by default.

   Rationale: Generated output is user-visible work. The first implementation should avoid silently replacing a previous package. A later change may add explicit overwrite options if needed.

   Alternative considered: always overwrite. That is convenient for tests but unsafe for users.

## Risks / Trade-offs

- Rule-based parsing can be imperfect. -> Keep analyzer output predictable, test the primary design example, and allow future interactive/LLM changes to refine fields.
- Non-overwrite behavior may force users to delete output manually during iteration. -> This is safer for the MVP; explicit overwrite can be added later.
- Template defaults may produce generic sections for vague requirements. -> Ensure all required sections exist so later validation can reason about the output.
- `create` touching workspace files before `init` may surprise users. -> Limit automatic setup to config/output paths needed for generation and report the generated package path clearly.

## Migration Plan

This change is additive. Existing `init` behavior remains unchanged. The CLI gains a `create` subcommand, new modules are added for analysis and generation, and tests cover the new path. No database migration is required.

Rollback would remove the new command and generation modules while leaving the archived CLI foundation intact.

## Open Questions

- Should the later validator change make `create` automatically validate generated output, or should validation remain an explicit command?
- Should overwrite behavior be added to this command later as `--force`, or handled only by future version-management features?
