## Context

Validation issues already carry stable `code` values, and quality reports already aggregate errors, warnings, score, status, and next actions. The newly added authoring lint codes make issue-to-suggestion mapping practical because the system can provide deterministic advice for each known problem.

## Goals / Non-Goals

**Goals:**

- Add a structured `RepairSuggestion` model.
- Map known validation and lint issue codes to stable repair guidance.
- Separate suggestions for errors and warnings by preserving issue level and code.
- Display suggestions in `validate` and `create` output only when issues exist.
- Keep future automation possible by attaching suggestions to quality reports.

**Non-Goals:**

- Do not automatically edit `SKILL.md`.
- Do not introduce a `repair` command.
- Do not call an LLM.
- Do not attempt complex semantic rewrites.

## Decisions

1. Build suggestions from issue codes, not message text.

   Rationale: Codes are stable and testable; messages may change for readability.

2. Store suggestions on `GenerationQualityReport`.

   Rationale: The create path already constructs this object before printing. Adding suggestions there gives future commands a single quality object to inspect.

3. Use the same builder for `validate` output.

   The CLI can call the same suggestion builder for raw validation results, ensuring `validate` and `create` remain consistent.

4. Provide a generic fallback for unknown issue codes.

   Rationale: Future validators may emit new codes before a dedicated suggestion is added. A generic suggestion is better than silence.

## Risks / Trade-offs

- Generic suggestions can be less helpful -> Mitigation: add specific mappings for all current issue codes.
- Suggestion output may make CLI tables longer -> Mitigation: display suggestions in a separate table only when issues exist.
- Future auto-repair will need stricter semantics -> Mitigation: keep suggestions advisory and non-mutating in this change.

## Migration Plan

No migration is required. Existing validation and generation outputs gain additional suggestion tables only when validation issues exist.
