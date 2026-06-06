## Context

Content quality metrics were introduced to compare deterministic and LLM-assisted Skill generation without relying only on validation warnings or errors. The current implementation records aggregate scores for workflow specificity, constraint verifiability, and quality gate clarity, and persists them in provenance for `show`.

The next intelligent-generation stages need these scores to behave like a contract: deterministic, explainable enough to debug, and stable across future changes. The design keeps the metrics local and rule-based so generation remains available without LLM access.

## Goals / Non-Goals

**Goals:**
- Make content quality scoring dimensions explicit and covered by tests.
- Keep scores normalized to 0.0 through 1.0 and deterministic for identical input.
- Preserve existing generation behavior: content quality is informational and does not fail generation.
- Store and display metrics consistently through quality reports and generated Skill provenance.
- Leave room for rule-level signals to support future explanation and regression tests.

**Non-Goals:**
- Do not use an LLM to judge quality.
- Do not automatically rewrite low-quality generated content.
- Do not change CLI flags or default LLM selection behavior.
- Do not make content quality part of package validity.

## Decisions

1. Keep the evaluator deterministic and local.

   The evaluator will remain a pure rule-based scoring path over structured `SkillRequirement` content. This keeps scores reproducible in tests and usable in offline generation. LLM-based judging was rejected because it would make the quality signal non-deterministic and unavailable in deterministic mode.

2. Score dimensions separately before aggregation.

   Workflow, constraints, and quality gates will each be scored against their own rule set and normalized independently. This avoids hiding a weak dimension behind a stronger one and gives future RAG or experience work clearer feedback.

3. Treat rule signals as implementation-facing evidence.

   The public contract remains the three normalized scores already exposed in reports and provenance. Internally, the evaluator can retain rule-level signals or reasons for tests and future CLI/reporting improvements. This avoids expanding user-facing output before the signals prove useful.

4. Keep low content quality informational.

   Validation remains responsible for generated package validity. Content quality can influence next actions and comparisons, but it must not fail `create` on its own. This protects backward compatibility and avoids turning subjective heuristics into hard blockers.

## Risks / Trade-offs

- Rule scoring can reward shallow keyword matches -> Mitigation: test representative low-quality and high-quality examples, including generic wording that should not receive full credit.
- Scores may drift as rules improve -> Mitigation: isolate rule tests and update expected values deliberately when rule semantics change.
- Explanation signals could overexpose implementation details -> Mitigation: persist and display only stable aggregate metrics until rule evidence has a clear user-facing design.
- Human judgment may disagree with deterministic scores -> Mitigation: keep the roadmap validation question focused on manual spot checks before using scores as gates for later RAG or experience work.
