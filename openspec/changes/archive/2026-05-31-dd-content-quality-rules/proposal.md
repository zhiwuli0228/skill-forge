## Why

Skill Forge already records deterministic content quality metrics, but the rule set is still too implicit to serve as a stable contract for future RAG and experience-accumulation work. This change defines those rules as an inspectable, tested capability so quality scores can be trusted as comparison signals rather than incidental implementation details.

## What Changes

- Define explicit rule dimensions for workflow specificity, constraint verifiability, and quality gate clarity.
- Normalize each content quality dimension to stable 0.0-1.0 scores with deterministic aggregation.
- Preserve content quality scoring as informational only; low scores must not fail generation by themselves.
- Include rule-level reasons or signals in internal quality results so tests and future reporting can explain why a score changed.
- Keep `show` and generated provenance aligned with the content quality metrics already written during `create`.

## Capabilities

### New Capabilities
- `content-quality-rules`: Deterministic, explainable rules for evaluating generated Skill workflow, constraints, and quality gates.

### Modified Capabilities
- `generation-quality-report`: Quality reports expose content quality as a stable rule-backed metric set rather than an opaque score bundle.
- `skill-library-management`: Generated Skill inspection continues to show persisted content quality metrics from provenance.

## Impact

- Affected code: `src/skill_forge/models/quality.py`, `src/skill_forge/models/generated.py`, `src/skill_forge/cli.py`, and library metadata presentation paths.
- Affected tests: `tests/test_generation_quality_report.py`, `tests/test_cli.py`, and focused tests for deterministic rule scoring.
- No CLI flag changes and no generation-blocking behavior changes.
