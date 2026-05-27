## Context

Skill Forge’s validation and linting are package-level quality checks. They verify structure and authoring quality, but they do not let a team encode task-specific expectations such as “a code review Skill must mention Findings and Tests” or “never say looks good without findings.”

This change introduces static eval cases. The evaluator reads generated `SKILL.md` content and checks deterministic assertions. It does not run an Agent, execute user code, or contact external services.

## Goals / Non-Goals

**Goals:**

- Add a deterministic eval case YAML format.
- Run one case file or all case files in a directory.
- Produce pass/fail results with assertion-level messages.
- Persist the latest eval report in the Skill package.
- Display latest eval summary in `skill-forge show`.

**Non-Goals:**

- Do not run real Agent conversations.
- Do not execute code or shell commands from eval files.
- Do not call an LLM.
- Do not implement a remote eval service.
- Do not change generation behavior based on eval results.

## Decisions

1. Use YAML eval cases.

   Rationale: The project already depends on PyYAML for config and blueprints. YAML is readable for team-maintained local standards.

2. Keep assertion types intentionally small.

   Initial assertion fields:

   ```yaml
   assertions:
     required_sections:
       - Findings
     required_constraints:
       - Findings first
     forbidden_phrases:
       - looks good
   ```

   Rationale: These map to static content checks and are enough for the first eval layer.

3. Resolve generated Skill packages through `SkillLibraryManager`.

   Rationale: The library manager already centralizes output directory lookup and missing-package errors.

4. Persist report as `eval-report.json`.

   Rationale: This avoids changing `skill-forge.json` schema and lets `show` read the latest eval summary independently.

5. Batch directory mode reads `.yaml` and `.yml` files in deterministic filename order.

   Rationale: Stable ordering keeps output and tests predictable.

## Risks / Trade-offs

- Static evals cannot prove real Agent behavior -> Mitigation: document this as the first deterministic layer and keep real execution out of scope.
- Simple substring matching can miss semantic equivalents -> Mitigation: assertions are explicit team checks, not semantic scoring.
- Persisting only latest report loses history -> Mitigation: history/versioning can be a later change.

## Migration Plan

No migration is required. Existing packages have no eval report until `skill-forge eval` runs.
