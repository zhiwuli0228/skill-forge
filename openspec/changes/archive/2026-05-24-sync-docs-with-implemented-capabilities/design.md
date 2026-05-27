## Context

Skill Forge has completed the initial MVP and the follow-up roadmap for blueprint-backed generation, built-in blueprints, explicit blueprint selection, blueprint-declared attachments, generation quality reports, optional LLM-assisted generation, and generated Skill library management.

The current documentation set is not fully synchronized:

- `docs/skill_generation_roadmap.md` records those roadmap changes as archived.
- `src/skill_forge/cli.py` exposes the corresponding commands and flags.
- `README.zh-CN.md` still lists LLM-assisted generation and generated Skill library commands as not implemented.
- Some archived main specs still have placeholder `Purpose` text.

This change is documentation-only. It should make the current product surface explicit without changing CLI behavior.

## Goals / Non-Goals

**Goals:**

- Align README documentation with implemented commands and flags.
- Make completed capabilities and remaining future work easy to distinguish.
- Replace placeholder spec purposes for already implemented capabilities.
- Preserve the existing roadmap history while adding a forward-looking next-stage section.
- Keep documentation examples executable with the current CLI.

**Non-Goals:**

- Do not implement new CLI commands.
- Do not change generated Skill behavior.
- Do not change storage schemas, dependencies, or installation paths.
- Do not introduce a new documentation generator.
- Do not rewrite the whole design document beyond targeted capability alignment.

## Decisions

1. Treat CLI output and main OpenSpec specs as the implementation truth for this cleanup.

   Rationale: The CLI and tests represent the current executable surface, while the main specs represent archived capability contracts. README files should describe those facts, not outdated roadmap assumptions.

   Alternative considered: Use only roadmap docs as the source of truth. That would miss accidental drift between roadmap text and actual commands.

2. Keep roadmap history intact and add a new next-stage section instead of rewriting archived progress.

   Rationale: `docs/skill_generation_roadmap.md` is useful as historical implementation tracking. The problem is not the completed record; it is the lack of a current forward-looking section after the original roadmap reached `none`.

   Alternative considered: Delete completed change details and replace them with a short summary. That would remove useful audit context.

3. Update stale README claims directly rather than adding footnotes.

   Rationale: Users read README files for current usage. Footnotes around stale claims would make the docs harder to scan and still leave contradictory text.

   Alternative considered: Add a separate "recently implemented" section. That helps release notes, but it does not fix incorrect current-scope text.

4. Keep validation lightweight and documentation-focused.

   Rationale: This change does not affect runtime behavior. Verification should run existing tests to confirm no accidental code regression and run OpenSpec validation to confirm artifacts are well-formed.

   Alternative considered: Add automated documentation drift tests. That may be useful later, but it is larger than this cleanup and requires choosing durable command-output snapshots.

## Risks / Trade-offs

- Documentation may drift again after future changes -> Mitigate by adding a short maintenance note in the roadmap describing which files to update after archived changes.
- README examples may become too long if every command is documented in full -> Mitigate by grouping related commands and linking to details instead of duplicating every option.
- Specs might be edited as prose rather than requirements -> Mitigate by limiting spec edits to placeholder `Purpose` text unless a real requirement changes.
