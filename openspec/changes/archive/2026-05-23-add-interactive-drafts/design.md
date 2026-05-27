## Context

Skill Forge now supports the local MVP sequence: initialize, create, validate, and install. The current `create` command is intentionally non-interactive and expects the rule-based analyzer to produce a complete requirement from one input string. The product design calls out that users often cannot describe a high-quality Skill in one pass, so the next step is to add interactive refinement and resumable draft state.

This change should keep the existing local generation path intact. The interactive flow should refine a `SkillRequirement`, persist it as a draft, and then reuse the existing generator to produce the final package.

## Goals / Non-Goals

**Goals:**

- Add `create --interactive` to start an interactive draft from an analyzed requirement.
- Add `resume <draft-id>` to continue an existing draft.
- Persist draft JSON under the Skill Forge drafts directory.
- Save draft state after each answered step.
- Track current step, draft status, project path placeholder, project context summary placeholder, selected examples, and generated package metadata.
- Keep prompts limited to high-value fields and avoid re-asking completed steps.
- Make the interaction layer testable by separating prompt orchestration from direct CLI code.

**Non-Goals:**

- No project context reader implementation.
- No LLM enhancement.
- No research corpus retrieval or example selection.
- No automatic install prompt after generation.
- No background autosave outside explicit interactive steps.
- No terminal UI beyond Questionary prompts and Rich command output.

## Decisions

1. Store drafts as JSON files in `~/.skill-forge/drafts/<draft-id>.json`.

   Rationale: JSON draft files are easy to inspect, test, and recover. SQLite can index drafts later if needed, but file-based state keeps the MVP simple.

   Alternative considered: store draft state only in SQLite. That adds schema and migration pressure before draft behavior is stable.

2. Model draft state with Pydantic.

   Rationale: The existing project uses Pydantic for structured data. A `SkillDraftState` model gives the wizard, CLI, and future project-context flow a stable contract.

   Alternative considered: use untyped dictionaries. That would make resume behavior fragile and harder to test.

3. Represent interactive steps as named fields rather than hardcoded prompt position only.

   Rationale: Resume needs to skip completed work. Named steps make it clear where a draft resumes and reduce coupling to prompt order.

   Alternative considered: store only a numeric step index. That is compact but brittle when steps are added or reordered.

4. Keep the wizard as a thin refinement layer over `SkillRequirement`.

   Rationale: Existing analyzer and generator already define the main generation contract. The wizard should confirm or edit fields, not fork generation behavior.

   Alternative considered: create a separate interactive-only generation pipeline. That duplicates logic and increases risk of divergent output.

5. Make prompt functions injectable in tests.

   Rationale: Interactive CLI prompts are hard to test directly. Injecting prompt adapters allows deterministic tests for wizard behavior and resume logic.

   Alternative considered: test only through manual CLI flows. That would leave draft state transitions under-tested.

## Risks / Trade-offs

- Questionary prompts can be difficult to automate. -> Keep prompt calls behind a small adapter and test wizard state transitions with fake answers.
- Drafts may become incompatible if models change. -> Include timestamps and status, and keep fields explicit; future migrations can be added when needed.
- Users may abandon drafts. -> This change only implements resume; listing/pruning drafts can be a later enhancement.
- Existing package output may collide when a resumed draft generates the same name. -> Reuse existing generator no-overwrite behavior and surface the same failure.

## Migration Plan

This change is additive. Existing non-interactive `create` behavior remains unchanged. The `create` command gains an optional interactive branch, and a new `resume` command is added. No database migration is required.

Rollback would remove the interactive branch, draft model/store, wizard, and resume command while keeping local generation behavior intact.

## Open Questions

- Should a later change add `skill-forge drafts list` and draft deletion?
- Should future project-context generation extend the same draft model or create a project-specific draft subtype?
