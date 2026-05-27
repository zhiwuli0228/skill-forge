## Why

Skill Forge can generate, validate, and install Skills locally, but users still need to provide a complete requirement in one command. This change adds an interactive workflow and resumable drafts so users can refine Skill requirements step by step without losing progress.

## What Changes

- Add `skill-forge create "<requirement>" --interactive` to confirm and refine generated requirement fields before generation.
- Add `skill-forge resume <draft-id>` to continue an interrupted interactive draft.
- Add `SkillDraftState` and draft persistence under `~/.skill-forge/drafts/<draft-id>.json`.
- Save draft state after each interactive step.
- Track draft status, current step, requirement data, and generated package metadata.
- Reuse the existing rule-based analyzer and Skill generator rather than creating a separate generation path.
- Add tests for draft serialization, wizard step behavior, resume behavior, and CLI integration.

## Capabilities

### New Capabilities

- `interactive-drafts`: Covers interactive requirement refinement, draft persistence, and resuming draft-based Skill generation.

### Modified Capabilities

- `local-skill-generation`: The existing `create` command gains an interactive mode that uses the same local generation pipeline after draft confirmation.

## Impact

- Affected command surface: extends `create` with `--interactive` and adds `resume <draft-id>`.
- Affected source areas: new draft model, draft store, interaction wizard, and CLI command wiring.
- Affected local filesystem: writes draft JSON files under the configured Skill Forge drafts directory.
- Affected dependencies: uses existing Questionary dependency for prompts; no new runtime dependency is expected.
- Out of scope: project context reading, LLM enhancement, research corpus lookup, automatic install prompt, and network behavior.
