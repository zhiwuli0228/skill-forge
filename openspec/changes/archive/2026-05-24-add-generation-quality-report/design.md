## Context

`skill-forge create` generates a package and prints package paths. Users must run `skill-forge validate` separately to discover structural errors or warnings. The validator already returns structured `ValidationResult` data, and generated packages already carry attachment metadata, so quality reporting can be built deterministically on top of existing validation behavior.

## Goals / Non-Goals

**Goals:**

- Produce a deterministic quality report after non-interactive generation.
- Reuse `SkillValidator` so `create` and `validate` agree on errors and warnings.
- Include a stable numeric score that tests can assert.
- Keep warning-only reports successful and make error reports fail clearly.
- Keep report presentation concise in the CLI.

**Non-Goals:**

- No automatic repair.
- No LLM scoring, rewriting, or remote calls.
- No new validator rules beyond the report plumbing.
- No changes to interactive draft generation in this slice.

## Decisions

1. Add a small quality report model/helper around `ValidationResult`.

   Rationale: scoring and next-action text should not live directly in CLI printing code. A model such as `GenerationQualityReport` can keep score computation deterministic and reusable.

   Alternative considered: add score fields directly to `ValidationResult`. That would mix package validity with generation-quality presentation and make the standalone validator responsible for generation-specific guidance.

2. Score from validation issues with fixed penalties.

   Rationale: deterministic penalties make behavior transparent and testable. Errors should have a larger penalty than warnings, and scores should be clamped to `0..100`.

   Alternative considered: infer quality from generated text length or section richness. That is more subjective and likely to create brittle tests.

3. Validate attachment metadata during post-generation reporting.

   Rationale: the generator returns generated references/assets/scripts; passing those relative paths into the validator keeps the post-create report aligned with the attachment safety checks added by the previous change.

   Alternative considered: validate only the package directory. That would omit existing attachment metadata checks during the exact workflow that creates attachments.

4. Keep `validate` output unchanged except for shared helper reuse if useful.

   Rationale: this change targets generation feedback, not the standalone validation command’s contract.

## Risks / Trade-offs

- Score can imply more precision than the validator provides -> keep the score simple and tie report details to concrete errors and warnings.
- `create` failing after files are written can leave an invalid package on disk -> clearly report the invalid package path and errors; automatic cleanup or repair remains out of scope.
- CLI output changes can break tests that assert exact output -> update tests to check stable report labels rather than table formatting internals.
