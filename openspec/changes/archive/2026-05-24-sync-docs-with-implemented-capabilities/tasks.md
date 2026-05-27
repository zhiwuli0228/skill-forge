## 1. Documentation Audit

- [x] 1.1 Compare `skill-forge --help` and relevant subcommand help with `README.md` and `README.zh-CN.md`.
- [x] 1.2 Identify stale current-scope statements that conflict with implemented LLM, blueprint, quality report, and library management capabilities.
- [x] 1.3 Confirm which docs need command examples updated for `--blueprint`, `--llm`, `blueprints list/show`, and `list/show/diff`.

## 2. README Synchronization

- [x] 2.1 Update `README.md` to document implemented generation options, blueprint inspection, quality reporting, and generated Skill library commands.
- [x] 2.2 Update `README.zh-CN.md` with equivalent current capability descriptions.
- [x] 2.3 Remove or revise stale "not implemented" entries for LLM-assisted generation and generated Skill library commands.
- [x] 2.4 Keep future-work lists limited to capabilities that remain genuinely unimplemented.

## 3. Roadmap and Design Doc Alignment

- [x] 3.1 Update `docs/skill_generation_roadmap.md` with a next-stage roadmap section that separates completed archived changes from future enhancement candidates.
- [x] 3.2 Add a short documentation maintenance note describing which files to update after future OpenSpec changes are archived.
- [x] 3.3 Review `docs/skill_forge_design_doc.md` and update command/capability references only where they conflict with current implemented behavior.

## 4. Spec Cleanup

- [x] 4.1 Replace the placeholder Purpose in `openspec/specs/llm-assisted-generation/spec.md`.
- [x] 4.2 Replace the placeholder Purpose in `openspec/specs/skill-library-management/spec.md`.
- [x] 4.3 Avoid changing existing requirement text unless a real documented behavior conflict is found.

## 5. Verification

- [x] 5.1 Run `openspec validate "sync-docs-with-implemented-capabilities" --strict`.
- [x] 5.2 Run `uv run pytest` to confirm the documentation cleanup did not introduce runtime regressions.
- [x] 5.3 Spot-check CLI help for the documented commands after README updates.
