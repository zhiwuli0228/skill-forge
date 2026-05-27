## 1. Draft Models and Storage

- [x] 1.1 Add `SkillDraftState` model with draft id, requirement, current step, status, optional project fields, selected examples, timestamps, and generated package metadata.
- [x] 1.2 Add draft status constants or enum values for `draft`, `in_progress`, `ready_to_generate`, `generated`, and `installed`.
- [x] 1.3 Add a file-based draft store that saves drafts to `drafts/<draft-id>.json`.
- [x] 1.4 Implement draft loading by id from the drafts directory.
- [x] 1.5 Ensure saved draft JSON includes all required fields and ISO-style timestamps.

## 2. Interactive Wizard

- [x] 2.1 Add an interaction package/module for the Skill creation wizard.
- [x] 2.2 Implement wizard initialization from an analyzed `SkillRequirement`.
- [x] 2.3 Implement injectable prompt adapter functions for text/list confirmation steps.
- [x] 2.4 Implement step progression with named current steps.
- [x] 2.5 Save draft state after each completed step.
- [x] 2.6 Skip completed steps when resuming from an existing draft.
- [x] 2.7 Mark the draft `ready_to_generate` when refinement is complete.
- [x] 2.8 Generate the final Skill package through the existing generator and mark draft `generated`.

## 3. CLI Integration

- [x] 3.1 Add `--interactive` option to `skill-forge create`.
- [x] 3.2 Route non-interactive create through the existing behavior unchanged.
- [x] 3.3 Route interactive create through analyzer, draft store, and wizard.
- [x] 3.4 Add `skill-forge resume <draft-id>` command.
- [x] 3.5 Return a clear error and non-zero exit when a draft id does not exist.
- [x] 3.6 Display draft id, status, and generated package path when relevant.

## 4. Tests

- [x] 4.1 Add model tests for `SkillDraftState` defaults and serialization.
- [x] 4.2 Add draft store tests for save and load by id.
- [x] 4.3 Add wizard tests for step progression and per-step persistence using fake prompt answers.
- [x] 4.4 Add wizard tests for resume skipping completed steps.
- [x] 4.5 Add wizard tests for final generation through the existing generator.
- [x] 4.6 Add CLI tests for non-interactive create remaining unchanged.
- [x] 4.7 Add CLI tests for interactive create with injected or monkeypatched prompt behavior.
- [x] 4.8 Add CLI tests for missing draft resume failure.
- [x] 4.9 Run the test suite and fix failures for this change.

## 5. Documentation and Verification

- [x] 5.1 Confirm `skill-forge create "Java bug 定位 skill" --interactive` creates a draft and can generate a Skill in an isolated home.
- [x] 5.2 Confirm `skill-forge resume <draft-id>` loads saved draft state and continues without repeating completed steps.
- [x] 5.3 Confirm `openspec validate add-interactive-drafts --strict` passes.
- [x] 5.4 Update `docs/openspec_change_plan.md` to mark `add-interactive-drafts` progress.
