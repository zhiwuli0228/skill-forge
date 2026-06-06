## Why

Skill Forge now records deterministic content quality metrics and eval results, but generation does not yet learn from repeated failures or low-quality patterns. Experience accumulation closes that loop by deriving local, explainable improvement rules from accumulated generated packages, eval reports, and quality metadata once enough samples exist.

## What Changes

- Add a local experience store under the Skill Forge home directory for derived generation rules and their source evidence.
- Analyze persisted eval reports and generation provenance to identify recurring task-type failure patterns and low content-quality dimensions.
- Derive deterministic, explainable experience rules without using an LLM for rule mining.
- Inject applicable experience rules into deterministic requirement analysis and LLM-assisted prompt context as optional guidance.
- Record when experience rules are applied during generation and which rule IDs influenced the result.
- Keep experience optional and locally scoped; clearing the experience directory returns generation to the no-experience baseline.

## Capabilities

### New Capabilities

- `experience-accumulation`: Local collection, derivation, storage, and application of explainable generation improvement rules from eval and quality data.

### Modified Capabilities

- `skill-evaluation`: Eval reports become a source signal for experience rule derivation.
- `generation-quality-report`: Content quality metrics become a source signal for low-quality pattern detection and before/after comparison.
- `llm-assisted-generation`: LLM-assisted generation can receive applicable experience rules as guidance while preserving structured output validation and fallback.
- `local-skill-generation`: Generated package metadata records applied experience rule IDs and generation remains unchanged when no experience rules apply.

## Impact

- Affected code: new `src/skill_forge/experience/` module, `src/skill_forge/requirement/analyzer.py`, `src/skill_forge/llm/refiner.py`, CLI generation orchestration, provenance metadata models, eval/quality report readers, and tests.
- User-facing behavior: no remote sync or new model dependency; generation may improve when local experience rules exist and match the current task type.
- Storage: local files under `~/.skill-forge/experience/` with rule metadata, evidence references, and derived signals.
- Compatibility: deterministic generation, LLM-assisted generation, eval execution, and quality reporting must continue when the experience store is missing, empty, or cleared.
