# Data Flow

## Purpose

This document describes the five core flows in Skill Forge — creation, validation, lifecycle recommendation, governance check, and optional LLM refinement — at the level of inputs, components, outputs, and verification. It is the reference an implementer reads before editing any module involved in a flow.

## Scope

- Applies to: end-to-end flows that cross at least two architectural layers.
- Owns: the per-flow input/output contracts, the components each flow touches, and the verification command for each flow.
- Does **not** own: per-module internals (see `module-boundaries.md`) or domain semantics (see `docs/06-domain/`).

## Current Rules

### Flow 1: Skill Creation

**Input.** A natural-language requirement string from the user (CLI `create` command). Optional inputs: `--blueprint`, `--output-dir`, `--interactive`, `--project <path>`, `--llm`.

**Main components.** In order: `cli.create` → `requirement.RequirementAnalyzer` → `blueprints.BlueprintRequirementEnricher` → `generator.SkillGenerator` → `validator.SkillValidator` → `library.write_provenance` (writes `skill-forge.json`).

**Output.** A generated Skill package directory containing `SKILL.md`, an optional `skill-forge.json` (provenance), and any blueprint-declared attachments (`references/`, `assets/`, `scripts/`). The CLI prints a deterministic quality report and any validation warnings or errors.

**Flow contract.**

- The requirement string is the only user input that must be present.
- The `SkillRequirement` Pydantic model is the contract between the analyzer and the enricher.
- The `GeneratedSkillPackage` Pydantic model is the contract between the generator and the validator.
- The `ValidationResult` is the contract between the validator and the CLI.
- `skill-forge.json` is the contract between the library writer and the upgrade path.

**Verification.** `uv run skill-forge create "<requirement>" --output-dir <tmp>` must exit 0 on a deterministic requirement. The output directory must contain `SKILL.md`. The CLI must print a quality report. The full test suite must pass: `uv run pytest tests/test_requirement_analyzer.py tests/test_skill_generator.py tests/test_skill_validator.py tests/test_cli.py`.

### Flow 2: Validation

**Input.** A path to a Skill package directory (CLI `validate` command) or a freshly generated `GeneratedSkillPackage` (internal call from the create flow).

**Main components.** `cli.validate` → `validator.SkillValidator.validate_package` → static checks → `ValidationResult` with errors, warnings, and deterministic suggested fixes.

**Output.** A `ValidationResult` containing the list of errors, the list of warnings (authoring lint), the list of suggested fixes, and the per-section presence flags. The CLI prints a human-readable summary and the suggested fixes.

**Flow contract.**

- The validator is **pure**: no file writes, no DB writes, no LLM calls, no network.
- The validator's input is a directory path or a parsed `GeneratedSkillPackage`; never raw user text.
- The validator's output is the only object the CLI uses to decide exit code.

**Verification.** `uv run skill-forge validate <path>` must exit 0 on a well-formed package, exit non-zero on a malformed package, and print suggested fixes when warnings are present. The full test suite must pass: `uv run pytest tests/test_skill_validator.py tests/test_cli.py`.

### Flow 3: Lifecycle Recommendation

**Input.** A summary of a Skill package — its current lifecycle signals (provenance, eval report, install history) — and the configured lifecycle rules. The summary is built by the lifecycle service from local storage; the rules are pure functions in `lifecycle/recommendation.py`.

**Main components.** `cli.lifecycle <subcommand>` → `lifecycle.service.LifecycleService` → `lifecycle.recommendation.recommend(summary, rules)` → typed `Recommendation` → CLI prints the recommendation and the rationale.

**Output.** A typed `Recommendation` containing the recommended action, the reason, the confidence, and the next-step pointer. The CLI prints the recommendation in a deterministic format.

**Flow contract.**

- `lifecycle.recommendation.recommend` is **pure**: no I/O, no network, no DB, no LLM. The function is callable from tests, from the service adapter, and from any future front-end.
- The service adapter owns all I/O. It loads the summary, calls the pure rules, formats the output, and persists state if needed.
- The recommendation must include a reason. A recommendation without a reason is invalid.

**Verification.** The pure rules must have parity tests that confirm the same input produces the same output. The service adapter must have tests that confirm the orchestration loads the summary, calls the rules, and writes the right log line. The full test suite must pass: `uv run pytest tests/test_lifecycle_recommendation.py tests/test_lifecycle_recommendation_rules.py tests/test_lifecycle.py tests/test_promotion.py`.

### Flow 4: Governance Check

**Input.** The repository root (default), the OpenSpec configuration under `openspec/`, and the governance check script under `scripts/governance_check.py`.

**Main components.** `python scripts/governance_check.py` (or `--quick`) → `openspec validate --strict --all` → `uv run skill-forge --help` → `uv run pytest`. The script runs the checks in order, prints a PASS/FAIL line per check, and exits with a non-zero code on any failure.

**Output.** A summary line: `Summary: N passed, 0 failed, 0 skipped` on success, or a failure line with the failing check and exit code. The script must be runnable in `--quick` mode (OpenSpec strict all + CLI smoke) and in full mode (adds `openspec schema validate`, the two example-change strict validations, and the full test suite).

**Flow contract.**

- The quick mode is the minimum gate for a docs-only change.
- The full mode is the gate for a schema/governance change and for any code change.
- A failing check is a stop condition, not a warning. The implementer reports the failure with the command, exit code, error excerpt, suspected cause, and proposed next step.

**Verification.** `python scripts/governance_check.py --quick` and `python scripts/governance_check.py` must both exit 0 on a clean repository.

### Flow 5: Optional LLM Refinement

**Input.** A `SkillRequirement` (output of the requirement analyzer) and the LLM configuration from the environment (`SKILL_FORGE_LLM_API_KEY`, `SKILL_FORGE_LLM_MODEL`, `SKILL_FORGE_LLM_BASE_URL`).

**Main components.** `cli.create --llm` → `llm.refiner.LLMRefiner.refine_requirement(requirement, config)` → LLM call → structured fields merged back into the requirement → `generator` continues with the merged requirement.

**Output.** A `SkillRequirement` with the LLM's structured fields filled in (subject, scope, constraints, etc.) but with the original user requirement preserved as the source of truth. The provenance records `llm_used: true` and the model name.

**Flow contract.**

- LLM refinement is **opt-in only**. The default `create` flow does not call the LLM.
- LLM output is merged only into supported structured fields. Free-form LLM text is never injected into `SKILL.md`.
- The generated package still passes through `validator` and the quality report regardless of LLM usage.
- Failure to reach the LLM (missing key, network error, model refusal) is treated as a refinement failure: the CLI prints a clear message and continues with the unrefined requirement. The create flow does not abort.
- Provenance records whether the LLM was used, the model, and a short note when the refinement failed.

**Verification.** The LLM refiner has tests that confirm the structured-field merge, the refusal-to-merge policy on free-form text, and the provenance record. The full test suite must pass: `uv run pytest tests/test_llm_refiner.py`. The CLI smoke test (`uv run skill-forge --help`) must succeed without LLM credentials configured.

## Related Files

- `docs/01-architecture/architecture-overview.md` — layer model.
- `docs/01-architecture/module-boundaries.md` — which module owns each component.
- `docs/02-harness/verification-policy.md` — when each flow must be verified.
- `docs/06-domain/lifecycle-rules.md` — lifecycle recommendation semantics.
- `src/skill_forge/cli.py`, `src/skill_forge/requirement/`, `src/skill_forge/blueprints/`, `src/skill_forge/generator/`, `src/skill_forge/validator/`, `src/skill_forge/lifecycle/`, `src/skill_forge/llm/` — flow components.
- `scripts/governance_check.py` — the governance check script.

## What Not To Do

- Do not call the LLM from the default `create` flow. The default path is deterministic.
- Do not let the validator write files or call the LLM.
- Do not let `lifecycle.recommendation` import from `storage/`, `retrieval/`, or any I/O module.
- Do not let the governance check skip a failing command. A failure is a stop.
- Do not let the upgrade path reconstruct a requirement from anywhere other than `skill-forge.json`.
- Do not introduce a flow that does not have a verification command. Every flow listed here has one.
