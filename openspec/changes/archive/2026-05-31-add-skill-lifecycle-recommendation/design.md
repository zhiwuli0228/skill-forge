## Context

The lifecycle index change established a read-only summary of a generated Skill's health from provenance, quality, eval, and experience facts. Users still need to translate that summary into an action, and that translation is currently implicit and manual.

This change adds a deterministic recommendation layer on top of the lifecycle summary. It must stay local, explainable, and read-only so it can be reused by the later promote/rollback change without introducing a second source of truth.

## Goals / Non-Goals

**Goals:**

- Translate lifecycle summaries into a clear next best action with a stable reason string.
- Compare two generated Skills and explain which one is healthier or more ready for the next step.
- Keep the recommendation logic deterministic and driven by existing lifecycle facts.
- Preserve read-only behavior and avoid mutation or side effects.

**Non-Goals:**

- No promote, rollback, install, or file rewrite behavior.
- No LLM scoring or natural-language generation.
- No new persistence layer or background job.
- No replacement of the lifecycle index service; this layer consumes it.

## Decisions

1. **Build on lifecycle summaries instead of rereading package files**

   The recommendation layer will consume `LifecycleSummary` objects from the lifecycle index service rather than opening `skill-forge.json` and `eval-report.json` directly. This keeps lifecycle fact extraction centralized and ensures the recommendation logic reuses the same state model as the first change.

   Alternatives considered:
   - Read local files directly in the recommendation service. Rejected because it would duplicate lifecycle parsing and likely drift from the index layer.
   - Add recommendation logic into the lifecycle service. Rejected because the lifecycle index should remain a focused read model and the next step deserves its own abstraction.

2. **Use a small action vocabulary**

   The first version will map lifecycle states to a limited set of actions such as `investigate-missing-facts`, `run-eval`, `repair-regression`, `consider-upgrade`, `promote`, and `hold`. The compare command will use the same vocabulary to identify a preferred package and explain the tie-breaker.

   Alternatives considered:
   - Return a generic text-only recommendation. Rejected because later changes need a structured action.
   - Expose many specialized actions. Rejected because it would be hard to interpret and would blur the line with the promote/rollback layer.

3. **Prefer deterministic ordering over score-only comparison**

   For compare, the service will order lifecycle states conservatively first, then use quality score, eval pass/fail counts, and missing facts as tiebreakers. This gives a stable outcome even when packages are only partially populated.

   Alternatives considered:
   - Compare only by quality score. Rejected because quality score alone does not capture missing eval, regressions, or unknown provenance.
   - Introduce a composite numeric score. Rejected because that would be less explainable than a rank plus reason breakdown.

4. **Keep CLI rendering thin**

   The CLI should display recommendation and comparison objects returned by the service. It should not interpret lifecycle state itself, so the command behavior stays testable and future action commands can reuse the same service output.

   Alternatives considered:
   - Embed recommendation branching inside the CLI. Rejected because it would make the rules hard to reuse and harder to test.

5. **Expose compare as a sibling view, not a mutation path**

   `lifecycle compare` will remain a read-only analytical command. It should help users decide between two generated Skills, but it should not install, promote, or rewrite either package.

   Alternatives considered:
   - Merge compare into upgrade or promote flows. Rejected because comparison is broader than upgrade candidates and should remain generic.

## Risks / Trade-offs

- [Action vocabulary drift] If the action labels diverge from future promote/rollback semantics, the recommendation layer could become misleading. → Keep the vocabulary small and align it with the later promotion layer.
- [Overconfidence] A recommendation may look authoritative even when facts are sparse. → Always include missing-fact notes and conservative fallbacks.
- [Comparison ambiguity] Two packages may have different strengths that are not captured by a single winner. → Report the preferred package and the tie-breaker reasons instead of pretending the choice is absolute.
- [Duplication risk] If future action logic is implemented separately in promotion code, the rules may diverge. → Reuse the recommendation service and its state ordering from the start.

## Migration Plan

No data migration is required. The recommendation layer is derived from existing lifecycle summaries and only adds CLI and service code. If the change is removed later, no persisted state needs to be cleaned up.

## Open Questions

- Should the first action vocabulary explicitly include `promote`, or should the recommendation layer say `ready-to-promote` and leave the verb for the later change?
- Should compare report a single winner only, or always show a side-by-side breakdown even when the winner is obvious?
- Should we surface upgrade candidate comparison as a special case, or keep the compare command fully generic for any two generated Skills?
