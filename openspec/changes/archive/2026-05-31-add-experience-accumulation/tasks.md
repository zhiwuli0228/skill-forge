## 1. Experience Store

- [x] 1.1 Add an `experience` directory path to Skill Forge workspace paths.
- [x] 1.2 Define experience rule, evidence, derivation result, and applied-rule context models.
- [x] 1.3 Implement local experience store read/write/list behavior under `~/.skill-forge/experience/`.
- [x] 1.4 Ensure missing or empty experience directories are treated as valid no-experience state.
- [x] 1.5 Add tests for rule persistence, stable IDs, empty store behavior, and clearing the directory.

## 2. Evidence Collection

- [x] 2.1 Scan generated Skill packages and load `skill-forge.json` provenance metadata.
- [x] 2.2 Load persisted `eval-report.json` files when present and extract failed assertion evidence.
- [x] 2.3 Extract low content quality evidence from workflow specificity, constraint verifiability, and quality gate clarity scores.
- [x] 2.4 Skip missing, malformed, or incomplete evidence files without failing the derivation run.
- [x] 2.5 Add tests for eval evidence, quality evidence, and skipped missing evidence.

## 3. Rule Derivation

- [x] 3.1 Implement deterministic derivation for repeated eval failure patterns scoped by task type.
- [x] 3.2 Implement deterministic derivation for repeated low content quality dimensions scoped by task type.
- [x] 3.3 Enforce minimum sample and repeated-evidence thresholds before storing rules.
- [x] 3.4 Preserve evidence references in each derived rule without copying full Skill content.
- [x] 3.5 Add tests that the same evidence produces stable rule IDs and content.

## 4. Rule Selection and Application

- [x] 4.1 Implement deterministic rule selection by task type, language, target platform, specificity, and priority.
- [x] 4.2 Add deterministic generation integration that applies matching rules without overriding user-provided fields.
- [x] 4.3 Extend LLM-assisted generation context to include applicable experience rules as guidance.
- [x] 4.4 Preserve existing LLM structured field validation and fallback when experience rules are present.
- [x] 4.5 Add tests for matching, nonmatching, conflicting, deterministic, and LLM-assisted rule application.

## 5. Provenance and CLI

- [x] 5.1 Extend generated package provenance with applied experience rule IDs.
- [x] 5.2 Record an empty applied experience rule list when no rules apply.
- [x] 5.3 Display applied experience rule IDs in generated Skill `show` output when provenance is present.
- [x] 5.4 Add or update CLI entry points for deriving/rebuilding local experience rules from generated packages.
- [x] 5.5 Add CLI tests for rule derivation, applied-rule provenance, and no-experience baseline behavior.

## 6. Validation

- [x] 6.1 Run focused tests for experience, eval evidence, quality evidence, LLM refiner, CLI generation, and library show behavior.
- [x] 6.2 Run the full test suite.
- [x] 6.3 Run `openspec validate "add-experience-accumulation" --strict`.
- [x] 6.4 Run `openspec validate --all --strict`.
