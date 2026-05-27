## Context

Generated Skill packages now carry `skill-forge.json` provenance metadata with the original requirement text, target platform, language, task type, applied blueprint, and prior quality result. The generator already creates packages from `SkillRequirement`, and `SkillLibraryManager` already resolves generated packages and reads provenance.

The upgrade workflow should use those existing seams instead of introducing a separate package format. It should create a candidate package that users can validate, inspect, evaluate, and diff with existing commands.

## Goals / Non-Goals

**Goals:**

- Generate an upgrade candidate from existing provenance metadata.
- Reapply the current version of the recorded blueprint.
- Validate the candidate and report old/new quality scores.
- Preserve the source Skill package unchanged.
- Make the candidate usable by existing `list`, `show`, `diff`, `validate`, and `eval` workflows.

**Non-Goals:**

- Do not merge user hand edits from the existing `SKILL.md`.
- Do not overwrite the source package by default.
- Do not support complex migration for packages without `skill-forge.json`.
- Do not call an LLM.
- Do not run eval cases automatically.
- Do not implement a remote sync or marketplace upgrade flow.

## Decisions

1. Add a dedicated upgrade service.

   Rationale: CLI should stay thin, while generation, provenance writing, validation, and candidate naming form a reusable workflow.

2. Reconstruct requirements from `requirement_text`, target platform, and language, then reapply the recorded blueprint ID.

   Rationale: This mirrors the original deterministic create path and allows current blueprint defaults to affect the candidate. It intentionally does not parse old `SKILL.md` content.

3. Require provenance metadata.

   Rationale: Without `skill-forge.json`, Skill Forge cannot reliably know the original requirement, blueprint, target platform, or language.

4. Require the recorded blueprint when provenance names one.

   Rationale: An upgrade based on a missing blueprint would silently change the standard being applied. A clear error is safer.

5. Use `<skill-name>-upgraded` as the default candidate name.

   Rationale: It is predictable and works naturally with existing `diff` commands. `--candidate-name` covers users who need another name.

6. Persist candidate provenance with the new candidate name and current validation quality.

   Rationale: Candidates should be first-class generated packages with their own provenance and quality data.

## Risks / Trade-offs

- User hand edits are not preserved -> Mitigation: generate a separate candidate and point users to `skill-forge diff`.
- Blueprint changes can produce large diffs -> Mitigation: candidate is never written over the source package unless the user explicitly handles replacement outside this command.
- Missing blueprint blocks upgrade -> Mitigation: the error names the missing blueprint so users can restore or choose a new generation path.
- Existing candidate names can collide -> Mitigation: fail by default and allow `--force` to replace only the candidate package.

## Migration Plan

No migration is required. Existing packages with `skill-forge.json` become upgradeable. Existing packages without provenance remain manageable through `list`, `show`, `diff`, `validate`, and `eval`, but `upgrade` reports a clear unsupported state.
