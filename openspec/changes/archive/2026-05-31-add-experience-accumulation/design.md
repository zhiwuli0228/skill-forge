## Context

Skill Forge already persists generated package provenance, deterministic content quality metrics, and latest eval reports. LLM-assisted generation and retrieval augmentation can improve individual outputs, but there is no feedback loop that turns repeated eval failures or low-quality dimensions into reusable local guidance. The roadmap calls for experience accumulation only after content quality rules and enough samples exist, with local storage and deterministic rule derivation.

This change introduces a local experience layer that derives explainable generation rules from existing local artifacts and applies matching rules during future generation without requiring remote sync, LLM-based mining, or blueprint mutation.

## Goals / Non-Goals

**Goals:**

- Store derived experience rules locally under the Skill Forge home directory.
- Derive rules from persisted eval failures, generation provenance, task type, and content quality metrics.
- Keep each rule explainable by linking it to source generated packages, eval cases, or low-quality dimensions.
- Apply matching rules to deterministic requirement analysis and LLM-assisted prompt context as optional guidance.
- Record applied rule IDs in generated package provenance.
- Allow clearing the experience directory to restore no-experience generation behavior.

**Non-Goals:**

- Remote sync or shared team experience publishing.
- Using an LLM to mine or summarize rules.
- Automatically modifying built-in, user, or project blueprints.
- Replacing retrieval augmentation or content quality scoring.
- Applying rules globally without task-type or evidence constraints.

## Decisions

1. Store experience as local structured files.

   Experience rules will live under `~/.skill-forge/experience/` as deterministic JSON or YAML records. File storage is enough for the first increment, keeps review/debug simple, and matches the roadmap requirement that clearing the directory reverts behavior.

2. Derive narrow rules from explicit signals.

   The derivation pass will use eval assertion failures, low content quality dimensions, task type, language, target platform, and provenance context. It will not infer broad semantic lessons from arbitrary text. This reduces overfitting and keeps rule explanations auditable.

3. Require sample thresholds before deriving rules.

   The experience service will skip derivation when there are too few generated samples or too little repeated evidence for a pattern. This matches the roadmap's sample-size prerequisite and avoids producing rules from isolated failures.

4. Apply rules as guidance, not mandatory rewrites.

   Deterministic generation can use rules to add missing constraints or quality gates when the rule is directly applicable. LLM-assisted generation can receive matching rules as prompt guidance. Existing validation, content quality scoring, and LLM field fallback remain the final guardrails.

5. Keep provenance lightweight.

   Generated packages will record applied experience rule IDs, but not copy full evidence payloads into every `skill-forge.json`. The rule store remains the source of evidence details.

## Risks / Trade-offs

- Rules overfit a small sample set -> Require minimum sample and repeated-pattern thresholds before deriving rules.
- Conflicting rules produce noisy guidance -> Scope rules by task type and priority; skip lower-priority conflicts when a more specific rule applies.
- Experience makes generation harder to reason about -> Record applied rule IDs in provenance and provide rule evidence in the local store.
- Rule derivation misses useful lessons -> Start with deterministic failure and low-quality signals; expand only after measured benefit.
- Clearing experience loses improvements -> This is intentional rollback behavior; users can regenerate rules from local artifacts.
