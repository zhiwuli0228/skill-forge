## Context

The current `SkillValidator` returns structured errors and warnings. Errors are reserved for invalid packages, while warnings are already consumed by `GenerationQualityReport` to reduce score without failing generation. This makes warning-only lint rules the lowest-risk path for authoring quality checks.

## Goals / Non-Goals

**Goals:**

- Add deterministic Skill authoring checks as validation warnings.
- Keep generated packages valid unless structural errors exist.
- Make lint warnings visible in `validate` and post-create quality reports.
- Keep rules simple and testable without LLMs or network access.

**Non-Goals:**

- Do not implement automatic repair suggestions.
- Do not call an LLM for semantic analysis.
- Do not execute Skill eval cases.
- Do not make lint warnings fail `validate` or `create`.

## Decisions

1. Represent authoring lint as normal `ValidationIssue` warnings.

   Rationale: The quality report already accepts structured warnings and applies deterministic penalties. A separate lint result model would add complexity without new behavior in this change.

2. Use conservative deterministic heuristics.

   Initial lint rules:

   - `name_not_slug`: frontmatter `name` is not lowercase kebab-case.
   - `package_name_mismatch`: package directory name does not match frontmatter `name`.
   - `description_too_short`: description is too short to guide triggering.
   - `description_missing_trigger`: description does not include trigger guidance such as "use this skill" or equivalent Chinese wording.
   - `description_missing_exclusion`: description does not include exclusion guidance such as "do not use" or equivalent Chinese wording.
   - `empty_section`: a recommended section exists but has no meaningful body.
   - `workflow_too_short`: workflow contains fewer than two numbered or bullet steps.
   - `quality_gates_too_few`: quality gates contains fewer than two checklist items.

   Rationale: These rules are concrete, stable, and map to common Skill quality failures.

3. Run lint even if structural warnings exist, but avoid noisy follow-on checks when frontmatter is missing.

   Rationale: A missing frontmatter file should not trigger misleading slug/description lint warnings. Section lint can still run where content exists.

4. Keep warning codes stable.

   Rationale: The next change, deterministic repair suggestions, will map issue codes to suggested fixes.

## Risks / Trade-offs

- Heuristics can produce false positives for concise but valid Skills -> Mitigation: warnings do not fail validation or generation.
- Generated Skills may no longer get 100/100 if their descriptions lack explicit exclusion wording -> Mitigation: update generator inputs or tests only where the new lint intentionally applies.
- Multilingual trigger/exclusion detection is limited -> Mitigation: support simple English and Chinese phrases first.

## Migration Plan

No migration is required. Existing packages remain valid; they may show additional warnings during validation.

Rollback is straightforward by removing the lint warning checks and tests.
