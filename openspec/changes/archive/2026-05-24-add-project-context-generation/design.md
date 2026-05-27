## Context

Skill Forge can already generate, refine, validate, install, update, and search Skills. The remaining core design goal is project-aware generation: a generated Skill should reflect the project where it will be used, especially local agent instructions, OpenSpec workflow requirements, README guidance, and platform-specific Skill folders.

The current generator accepts a structured `SkillRequirement` and renders constraints into `SKILL.md`. This change should enrich that requirement before generation by reading a bounded set of project context files. The implementation must stay local-only and deterministic.

## Goals / Non-Goals

**Goals:**

- Add `create "<requirement>" --project <path>`.
- Scan a bounded set of project rule/documentation files.
- Detect agent tooling such as OpenSpec, opencode, Claude, Codex, and AGENTS-style instructions.
- Skip binary files, large files, dependency/build output directories, and unrelated source trees.
- Produce a simple project context summary.
- Convert project context into generated Skill constraints.
- Support project context in both non-interactive and interactive create flows.
- Persist project path and project context summary in draft state.
- Keep all behavior testable with local fixture projects.

**Non-Goals:**

- No LLM summarization.
- No deep source-code analysis.
- No full repository indexing.
- No project file modification.
- No automatic install after project-aware generation.
- No network access.

## Decisions

1. Use an allowlist-oriented project scanner.

   Rationale: Project context should be precise and safe. The scanner should target known rule and documentation files/directories such as `AGENTS.md`, `CLAUDE.md`, `README.md`, `.opencode/`, `.claude/`, `.agents/`, `openspec/`, `config.yaml`, and `project.md`.

   Alternative considered: recursively read all text files. That is risky for large repositories and can inject noisy implementation details into generated Skills.

2. Treat summarization as deterministic rule extraction.

   Rationale: MVP must not depend on LLMs. Deterministic keyword and path-based detection can identify useful rules such as OpenSpec workflow, test requirements, avoiding unrelated changes, and agent platform usage.

   Alternative considered: LLM summary generation. That may improve quality later but adds latency, cost, and test instability.

3. Inject context by enriching `SkillRequirement.constraints`.

   Rationale: The existing template already renders constraints. Enriching the requirement keeps generator changes minimal and avoids creating a parallel rendering path.

   Alternative considered: Add a separate project context section to the template. That is more visible, but it expands the generated contract more than needed for this MVP.

4. Store project path and summary in drafts for interactive create.

   Rationale: Draft state already has optional project fields. Persisting these values makes resume behavior deterministic and avoids rescanning unexpectedly during resume.

   Alternative considered: Rescan every resume. That can surprise users if project files changed after draft creation.

5. Use strict file size and binary checks.

   Rationale: Reading a project path should be predictable and fast. Size limits and binary detection prevent accidental ingestion of build artifacts, lock files, media, or generated files.

   Alternative considered: Rely only on directory allowlists. Individual allowed directories can still contain large or binary files, so per-file checks are still needed.

## Risks / Trade-offs

- Rule extraction may miss project-specific nuance. -> Keep detected rules conservative and expose summary/constraints in generated output for user review.
- Allowlist scanning may miss useful context files. -> Centralize patterns so future changes can expand the allowlist safely.
- Context constraints could duplicate user-provided constraints. -> Deduplicate constraints before generation.
- Interactive draft context may become stale. -> Persisting summary favors reproducibility; future changes can add an explicit refresh option.
- OpenSpec directory can be large. -> Read only bounded files such as spec/change markdown and config, subject to size and total character limits.

## Migration Plan

This change is additive. Existing `create` behavior remains unchanged when `--project` is not provided. Existing drafts without project fields remain valid because those fields are optional.

Rollback removes the `--project` option, project context modules, and constraint enrichment. Existing generated Skills and stored drafts remain readable.

## Open Questions

- Should future `resume` offer a `--refresh-project-context` option?
- Should project context eventually combine with search retrieval results when generating Skills?
