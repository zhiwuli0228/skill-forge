## 1. Rule Model

- [x] 1.1 Review the existing `assess_content_quality` implementation and identify which scoring signals already satisfy the new rule contract.
- [x] 1.2 Add or refine rule-level scoring helpers for workflow specificity, constraint verifiability, and quality gate clarity.
- [x] 1.3 Ensure each dimension returns a deterministic normalized score from 0.0 through 1.0, including empty-content behavior.

## 2. Reporting and Provenance

- [x] 2.1 Keep generated quality reports populated with the rule-backed content quality metrics when requirement content is available.
- [x] 2.2 Ensure low content quality does not alter the validation-derived quality status or fail `create`.
- [x] 2.3 Verify `skill-forge.json` stores content quality metrics and `skill-forge show` displays persisted metrics when present.

## 3. Tests and Validation

- [x] 3.1 Add focused tests comparing specific and generic workflow scoring.
- [x] 3.2 Add focused tests comparing checkable and vague constraint scoring.
- [x] 3.3 Add focused tests comparing clear and vague quality gate scoring.
- [x] 3.4 Add regression tests for deterministic scoring, empty-content scores, report status preservation, and `show` display.
- [x] 3.5 Run targeted tests and `openspec validate "dd-content-quality-rules" --strict`.
