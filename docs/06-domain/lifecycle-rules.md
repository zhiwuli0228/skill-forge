# Lifecycle Rules

## Purpose

This document defines the lifecycle recommendation subsystem in Skill Forge: its purpose, the pure recommendation rule, the service adapter relationship, the lifecycle states, the no-network / no-database / deterministic rule, and how lifecycle recommendation evolves through governed changes.

## Scope

- Applies to: the `lifecycle/` module and the CLI's `lifecycle` command surface.
- Owns: the recommendation rules, the service adapter contract, the conceptual lifecycle states, the determinism guarantees, and the change governance for lifecycle work.
- Does **not** own: the authoring pipeline (see `skill-authoring-domain.md`), the platform adapter (see `docs/01-architecture/module-boundaries.md`), or the governance mechanics (see `docs/03-openspec/`).

## Current Rules

### 1. Lifecycle Recommendation Purpose

A generated Skill package has a lifecycle: it can be a draft, an active Skill installed on a platform, a candidate for promotion, a candidate for rollback, or deprecated. Lifecycle recommendation is the subsystem that, given a summary of a package's current signals, recommends the next action and the reason for the action.

The recommendation is **advisory**. The CLI prints the recommendation; the user decides whether to act. The recommendation is the input to the platform's `install` / `promote` / `rollback` commands, but the recommendation is not the action.

The purpose of the recommendation is to make the next step visible. The author or the operator reads the recommendation, reads the reason, and decides.

### 2. The Pure Recommendation Rule

`src/skill_forge/lifecycle/recommendation.py` is **pure rules**. The file contains functions that take typed inputs and return typed outputs. The rules are not allowed to:

- Read or write the file system.
- Read or write the SQLite database.
- Call the network.
- Call the LLM.
- Call a logger that touches a handler.
- Depend on `time.time()`, `datetime.now()`, `uuid.uuid4()`, or any other non-deterministic source.
- Import from `storage/`, `retrieval/`, `cli/`, or any module that owns I/O.

The rules are allowed to:

- Import from `src/skill_forge/models/` (Pydantic models for the typed inputs and outputs).
- Use `enum.Enum` for lifecycle states and recommended actions.
- Compute deterministic scores from the typed input.

The pure rules are reusable in tests, in the service adapter, in future front-ends, and in any tool that needs to compute a recommendation without doing I/O.

### 3. Service Adapter Relationship

`src/skill_forge/lifecycle/service.py` is the **service adapter**. It owns the I/O and the orchestration that calls the pure rules.

The service adapter:

- Loads the package summary from `storage/` (provenance, eval report, install history).
- Builds the typed input to the pure rules.
- Calls the pure rules.
- Formats the typed output for the CLI (and, when applicable, persists a record to `storage/`).
- Surfaces errors to the CLI without swallowing them.

The service adapter must not:

- Import from `cli/`.
- Duplicate any rule that lives in `lifecycle/recommendation.py`. The adapter calls the rules; it does not re-implement them.
- Add non-determinism. The adapter may read from `storage/`, but the recommendation itself is deterministic given the same summary.

The split between the pure rules and the service adapter is enforced by code review, by the parity tests for the rules, and by the import boundaries documented in `docs/01-architecture/module-boundaries.md`.

### 4. Lifecycle States (Conceptual)

A Skill package's lifecycle is described by a small set of states. The states are conceptual; the implementation lives in `src/skill_forge/models/lifecycle.py` (or equivalent) and in `lifecycle/recommendation.py`. The exact state set may grow through governed changes; the conceptual model is:

- **Draft.** The package was created and has not been evaluated. No eval report, no install history.
- **Evaluated.** The package has an `eval-report.json` with a passing run. It is a candidate for promotion.
- **Active.** The package has been installed on a target platform. It is in use.
- **Stale.** The package is installed, but the eval report is older than the configured staleness threshold, or a newer candidate exists.
- **Promote candidate.** A newer package is available that the recommendation engine flags for promotion. Promotion is the user's decision.
- **Rollback candidate.** The currently active package is failing evals or has a known regression, and a previous version is available. Rollback is the user's decision.
- **Deprecated.** The package is no longer recommended for any platform. The CLI still supports `show` and `list`, but `install` warns.

A package may be in more than one state at the conceptual level. The recommendation engine resolves the multiple states into a single recommended action with a reason.

### 5. No Network / No Database / Deterministic Rule

The recommendation engine (pure rules + service adapter) must satisfy three guarantees:

- **No network.** The recommendation does not call out to a remote service. The LLM refiner and the research corpus are not on the recommendation path.
- **No database in the rules.** The pure rules do not read from the SQLite database. The service adapter reads from `storage/`, but the rules operate on a typed summary that has already been loaded.
- **Deterministic.** The same summary produces the same recommendation. The recommendation does not depend on wall-clock time, random sampling, or external state. The service adapter may add an audit row to `storage/` (a timestamped record of the recommendation) without violating determinism, because the audit row is a side effect, not part of the recommendation.

These guarantees are enforced by the parity tests for the rules (`tests/test_lifecycle_recommendation_rules.py`) and by the import boundaries in `module-boundaries.md`.

### 6. How Lifecycle Recommendation Evolves

Lifecycle recommendation evolves only through OpenSpec changes. The procedure:

1. **Brainstorm.** The planner (typically Codex) uses the `brainstorm` skill from `SUPERPOWERS.md` to compare 2+ candidate approaches. A change to the recommendation rules is non-trivial; it affects user-visible CLI output and may affect promotion and rollback behavior.
2. **Propose.** The planner writes `openspec/changes/<change-id>/proposal.md` with a clear "what changes" and "what does not change" section. The proposal must call out any new lifecycle state, any new recommended action, and any change to the typed input/output shapes.
3. **Spec.** The planner writes `openspec/changes/<change-id>/specs/lifecycle/spec.md` (or extends the existing lifecycle spec) with the new requirements in `## ADDED Requirements` form.
4. **Design.** The planner writes `openspec/changes/<change-id>/design.md` covering: the new rule, the new typed shape, the parity test plan, and the migration path for any existing package whose recommendation may change.
5. **Implement.** The implementer (typically Claude Code) follows TDD: write a parity test for the new rule first, see it fail for the right reason, then add the rule. The implementer must not modify the parity tests for the existing rules unless the change explicitly proposes a new behavior for those rules.
6. **Verify.** The implementer runs `uv run pytest tests/test_lifecycle_recommendation.py tests/test_lifecycle_recommendation_rules.py tests/test_lifecycle.py tests/test_promotion.py` and the full governance check. The parity tests must pass.
7. **Archive.** When the change is `done`, `openspec archive` moves the change folder under `openspec/changes/archive/` and merges the `ADDED Requirements` into the capability spec.

A change that breaks the pure-rule contract (for example, by adding a database read to the rules) is a hard stop. The planner must re-design the change so the rules stay pure, and the service adapter owns the I/O.

### 7. Why the Split Matters

The split between the pure rules and the service adapter is the single most important architectural choice in the lifecycle subsystem. The split exists because:

- The recommendation rules are reused in tests, in the service adapter, in parity tests, and (in the future) in alternative front-ends. A non-pure rule forces every caller to set up the same I/O scaffolding.
- The pure rules are the only piece of the lifecycle subsystem that can be reasoned about without reading the storage layer. The reasoning is local: input, output, no side effects.
- The service adapter is the only piece that owns I/O. The adapter can be replaced (for example, with a different storage backend) without touching the rules.
- The split is the only way to keep the recommendation engine deterministic. A non-deterministic recommendation is not a recommendation; it is a guess.

Any change that erodes the split is a regression, not a refactor.

## Historical Context

The lifecycle subsystem was delivered through three progressive OpenSpec changes, all archived: `add-skill-lifecycle-index`, `add-skill-lifecycle-recommendation`, `add-skill-promotion-and-rollback` (see `docs/99-archive/superseded-roadmaps/skill_lifecycle_governance_plan.md`). The original design principles still apply: deterministic over LLM, one main user behavior per change, every recommendation explainable from provenance / eval / quality / experience, and promote / rollback must preserve the original fact sources. The current rules refine those principles into the pure-rule / service-adapter split documented above.

## Related Files

- `docs/06-domain/skill-authoring-domain.md` — Skill package concept, provenance.
- `docs/01-architecture/architecture-overview.md` — layer model and governance layer.
- `docs/01-architecture/module-boundaries.md` — module ownership of `lifecycle/`.
- `docs/01-architecture/data-flow.md` — lifecycle recommendation flow.
- `docs/03-openspec/change-workflow.md` — how a change moves from draft to archive.
- `src/skill_forge/lifecycle/recommendation.py` — pure rules.
- `src/skill_forge/lifecycle/service.py` — service adapter.
- `src/skill_forge/lifecycle/promotion.py` — promotion and rollback logic.
- `tests/test_lifecycle_recommendation.py`, `tests/test_lifecycle_recommendation_rules.py`, `tests/test_lifecycle.py`, `tests/test_promotion.py` — the lifecycle test suite.

## What Not To Do

- Do not import from `storage/`, `retrieval/`, or `cli/` in `lifecycle/recommendation.py`. The rules are pure.
- Do not re-implement a rule in the service adapter. The adapter calls the rule.
- Do not call the network, the LLM, or the database from the recommendation engine (rules or adapter).
- Do not depend on wall-clock time, `random`, or `uuid` in the rules.
- Do not add a lifecycle state, a recommended action, or a typed input/output field without an OpenSpec change.
- Do not modify a parity test to make a new behavior pass. Update the test as part of the change and record the new behavior in the proposal.
- Do not let a non-trivial recommendation change skip TDD. The parity test is the anchor.
- Do not let the service adapter swallow an error from the pure rules. Surface it.
