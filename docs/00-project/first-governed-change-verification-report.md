# Phase 3 First Governed Change Verification Report

> Repository: `https://github.com/zhiwuli0228/skill-forge`
> Phase: **Phase 3 — First Real Governed Change Slice**
> Change: `add-skill-lifecycle-recommendation`
> Date: 2026-06-06
> Status: **Complete. Local commit prepared.**

This report records what Phase 3 changed, what it deliberately did
not change, the verification commands that were run, the
commands that were not run, and the recommended follow-up for
Phase 4. It is the human-readable counterpart to the change
folder's `verification.md`.

---

## 1. Selected Slice

The change folder `openspec/changes/add-skill-lifecycle-recommendation/`
predated Phase 3 with four artifacts (`proposal.md`, `design.md`,
`tasks.md`, `specs/skill-lifecycle-recommendation/spec.md`) under
the old `spec-driven` schema. The change also had pre-existing
WIP in the working tree: a service-level
`LifecycleRecommendationService`, a CLI integration, and a
service-level test file.

Phase 3 selects the **smallest deterministic, testable slice**
of the broader recommendation feature. The slice is:

- A pure `LifecycleRecommendationInput` Pydantic model.
- A pure `recommend_lifecycle_action(input) -> LifecycleRecommendation`
  module-level function.
- Unit tests for the pure function.
- The eight OpenSpec artifacts in the change folder, reshaped
  to the new `skill-forge-governance` schema.

The slice is explicitly **out of scope** for the following
items, which are preserved as pre-existing WIP:

- CLI integration (`skill-forge lifecycle recommend` and
  `skill-forge lifecycle compare`).
- Persistence (no file writes from the pure function).
- Templates (no template files are touched).
- Dependencies (`pyproject.toml` and `uv.lock` are untouched).
- The pre-existing `LifecycleRecommendationService` and its
  tests.

---

## 2. Modified Files

The Phase 3 commit touches the following paths exactly.

### 2.1 OpenSpec change folder

- `openspec/changes/add-skill-lifecycle-recommendation/.openspec.yaml`
  — schema changed from `spec-driven` to `skill-forge-governance`.
- `openspec/changes/add-skill-lifecycle-recommendation/brainstorm.md`
  — new file.
- `openspec/changes/add-skill-lifecycle-recommendation/proposal.md`
  — reshaped to the new template; narrowed to the minimal slice.
- `openspec/changes/add-skill-lifecycle-recommendation/design.md`
  — reshaped to the new template; narrowed to the minimal slice.
- `openspec/changes/add-skill-lifecycle-recommendation/review.md`
  — new file.
- `openspec/changes/add-skill-lifecycle-recommendation/plan.md`
  — new file.
- `openspec/changes/add-skill-lifecycle-recommendation/tasks.md`
  — reshaped to the new template.
- `openspec/changes/add-skill-lifecycle-recommendation/verification.md`
  — new file (written at the end of the change).
- `openspec/changes/add-skill-lifecycle-recommendation/specs/skill-lifecycle-recommendation/spec.md`
  — reshaped to the new template; requirements narrowed to
  the pure function.

### 2.2 Code

- `src/skill_forge/lifecycle/recommendation_rules.py` — new
  module. Defines `LifecycleRecommendationInput` and the
  pure `recommend_lifecycle_action` function. Imports the
  existing `LifecycleRecommendation` result model and
  `LifecycleState` literal; does not modify either.

### 2.3 Tests

- `tests/test_lifecycle_recommendation_rules.py` — new test
  file. 15 tests covering state mapping for all five
  `LifecycleState` values, outdated provenance, current valid
  metadata, invalid or incomplete input (4 cases), and
  determinism (3 cases).

### 2.4 Documentation

- `docs/00-project/first-governed-change-verification-report.md`
  — this report.

---

## 3. Forbidden-Path Check

The Phase 3 strict-scope forbids modifying the following paths.
A `git status --short` after the change confirms that none of
the forbidden paths is staged, and the explicit `git add`
list (see Section 6) does not include any of them.

- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md` — not modified.
- `README.md`, `README.zh-CN.md` — not modified.
- `docs/03-openspec/**`, `docs/04-superpowers/**`, `.superpowers/**` — not modified.
- `openspec/config.yaml` — not modified.
- `openspec/schemas/**` — not modified.
- `openspec/changes/example-governance-stack-walkthrough/**` — not modified.
- `templates/**`, `configs/**` — not modified.
- `pyproject.toml`, `uv.lock` — not modified.
- Every other file under `src/skill_forge/lifecycle/` that is
  not `recommendation_rules.py` (i.e., the existing
  `__init__.py`, `models.py`, `service.py`, `recommendation.py`,
  and `promotion.py`) — not modified.
- Every other file under `tests/` that is not
  `test_lifecycle_recommendation_rules.py` — not modified.
- Every other file under `docs/00-project/` that is not this
  report — not modified.

Forbidden paths changed: **no**.

---

## 4. Dirty Worktree Handling

The repository's working tree contained substantial pre-existing
WIP at the start of Phase 3. The WIP includes untracked
directories such as `src/skill_forge/lifecycle/`,
`src/skill_forge/adoption/`, `src/skill_forge/experience/`,
`src/skill_forge/retrieval/`, and `openspec/changes/add-skill-lifecycle-recommendation/`,
plus many modified files under `src/skill_forge/`,
`tests/`, `docs/`, and `openspec/specs/`.

Phase 3 follows the dirty-worktree rule:

- The pre-existing WIP is not reset.
- The pre-existing WIP is not deleted.
- The pre-existing WIP is not included in the Phase 3 commit.
- `git add .` is not used.
- `git add -A` is not used.
- Only the explicit Phase 3 file list (Section 2) is staged.

The Phase 3 commit therefore has a clean, minimal file list
that does not silently consume unrelated WIP. A reviewer who
runs `git show --stat <sha>` sees exactly the Phase 3 files
and nothing else.

---

## 5. OpenSpec Artifact Summary

The change folder now contains the eight artifacts required by
the `skill-forge-governance` schema:

| Artifact     | File                                              | Status     |
|--------------|---------------------------------------------------|------------|
| brainstorm   | `brainstorm.md`                                   | written    |
| proposal     | `proposal.md`                                     | reshaped   |
| spec         | `specs/skill-lifecycle-recommendation/spec.md`    | reshaped   |
| design       | `design.md`                                       | reshaped   |
| review       | `review.md`                                       | written    |
| plan         | `plan.md`                                         | written    |
| tasks        | `tasks.md`                                        | reshaped   |
| verification | `verification.md`                                 | written    |

The `proposal.md`, `design.md`, `tasks.md`, and the spec file
are reshaped to the new template: each starts with
`> Status: draft` and `> Schema: skill-forge-governance`, and
each contains the sections required by the schema. The
`brainstorm.md`, `review.md`, `plan.md`, and `verification.md`
are new.

The four pre-existing artifacts were also narrowed to the
minimal slice. CLI integration, persistence, the compare view,
and the service-level adapter are explicitly listed as
non-goals. The pre-existing WIP for those items is preserved
as-is and is not modified.

---

## 6. Code Summary

The new module `src/skill_forge/lifecycle/recommendation_rules.py`
is a single Python file. It defines:

- `LifecycleRecommendationInput` — a Pydantic `BaseModel` with
  `extra="forbid"`, `skill_name: str = Field(min_length=1)`,
  `state: LifecycleState`, and the structured fact fields
  (`reason`, `missing_facts`, `quality_score`,
  `quality_status`, `eval_total`, `eval_passed`,
  `eval_failed`, `applied_experience_rule_ids`).
- `recommend_lifecycle_action(input) -> LifecycleRecommendation`
  — a module-level pure function. The function:
  - Does not read from disk.
  - Does not write to disk.
  - Does not perform network I/O.
  - Does not depend on a clock or a logger.
  - Does not mutate the input.
  - Returns a `LifecycleRecommendation` from the existing
    `src/skill_forge/lifecycle/recommendation.py` module.

The rule is keyed on `LifecycleState`. Each of the five
states maps to exactly one of the action labels in the
existing vocabulary: `unknown` -> `investigate-missing-facts`,
`needs-eval` -> `run-eval`, `regressed` -> `repair-regression`,
`needs-upgrade` -> `consider-upgrade`, `healthy` ->
`ready-to-promote`.

---

## 7. Test Summary

`tests/test_lifecycle_recommendation_rules.py` contains 15
tests. The tests are grouped by concern.

| Group                    | Test                                                                       |
|--------------------------|----------------------------------------------------------------------------|
| State mapping (happy)    | `test_unknown_state_recommends_investigate_missing_facts`                  |
| State mapping (happy)    | `test_unknown_state_without_explicit_missing_facts_is_still_conservative`  |
| State mapping (happy)    | `test_outdated_provenance_recommends_investigate_missing_facts`            |
| State mapping (happy)    | `test_current_valid_metadata_recommends_ready_to_promote`                  |
| State mapping (happy)    | `test_needs_eval_state_recommends_run_eval`                                |
| State mapping (happy)    | `test_regressed_state_recommends_repair_regression`                        |
| State mapping (happy)    | `test_needs_upgrade_state_recommends_consider_upgrade`                      |
| Invalid or incomplete    | `test_invalid_state_raises_validation_error`                               |
| Invalid or incomplete    | `test_empty_skill_name_raises_validation_error`                            |
| Invalid or incomplete    | `test_missing_required_state_raises_validation_error`                      |
| Invalid or incomplete    | `test_extra_field_raises_validation_error`                                 |
| Determinism              | `test_function_is_deterministic_on_repeated_calls`                         |
| Determinism              | `test_function_does_not_mutate_input`                                      |
| Determinism              | `test_signals_are_produced_in_a_stable_order`                              |
| Purity guard             | `test_module_does_not_depend_on_disk_or_clock`                             |

The required test cases from the Phase 3 task — "new or
unknown skill state", "outdated provenance", "current valid
metadata", "invalid or incomplete input", and "deterministic
behavior" — are all covered. The "outdated provenance" case is
covered by `test_outdated_provenance_recommends_investigate_missing_facts`.

---

## 8. Verification Results

The following commands were run from the repository root. The
exit code and a short output summary are recorded for each.

| Command                                                         | Exit | Summary                                                                                              |
|-----------------------------------------------------------------|------|------------------------------------------------------------------------------------------------------|
| `git status --short`                                            | 0    | Pre-existing WIP and the new Phase 3 files are listed; no forbidden path is staged.                  |
| `git diff --name-only`                                          | 0    | Lists the pre-existing dirty WIP; Phase 3 files are untracked and do not appear.                     |
| `openspec validate add-skill-lifecycle-recommendation --strict` | 0    | `Change 'add-skill-lifecycle-recommendation' is valid`.                                              |
| `openspec validate --strict --all`                              | 0    | `Totals: 24 passed, 0 failed (24 items)`. The change is included in the passed list.                |
| `uv run pytest tests/test_lifecycle_recommendation_rules.py`    | 0    | `15 passed`. All 15 new tests are green.                                                              |
| `uv run pytest`                                                 | 0    | `============================ 280 passed in 16.38s =============================`.                     |
| `uv run skill-forge --help`                                     | 0    | CLI loads; the pre-existing `lifecycle` command is preserved. No new command is added by this slice. |

The full pytest summary is `280 passed` (265 pre-existing +
15 new). The OpenSpec validation is green at both the
single-change level and the `--all` level.

---

## 9. Remaining Risks

- [The pure function's state-mapping rule is duplicated with
  the pre-existing service-level rule in
  `src/skill_forge/lifecycle/recommendation.py`] ->
  Mitigation: the new module is additive. A future phase can
  refactor the service to call the pure function without
  changing the service's public API. That refactor is out of
  scope for Phase 3.
- [The pre-existing WIP under `src/skill_forge/lifecycle/`
  and `tests/test_lifecycle_recommendation.py` is not
  exercised by the new test file] -> Mitigation: the
  pre-existing service-level tests are preserved as-is. A
  future phase can add a parity test that compares the
  service-level recommendation to the pure-function
  recommendation for the same `LifecycleSummary`.
- [The change folder's `verification.md` is part of the
  change folder itself, so it is staged together with the
  other Phase 3 files] -> Mitigation: the `verification.md`
  is written at the end of the change, after the
  implementation and tests pass, as required by the schema.
- [The Phase 3 commit lands while the working tree has
  substantial uncommitted WIP. A reviewer who runs
  `git diff --name-only` after the commit sees only the
  pre-existing WIP, not the Phase 3 files] -> Mitigation:
  the commit's `git show --stat` output is the authoritative
  file list, and this report records every Phase 3 file by
  path in Section 2.

---

## 10. Recommended Phase 4

Phase 4 should add an **adapter** that lets the existing
`LifecycleRecommendationService` call the new pure function
without changing the service's public API. Concretely:

- Add a private helper in
  `src/skill_forge/lifecycle/recommendation.py` that maps a
  `LifecycleSummary` to a `LifecycleRecommendationInput`.
- Have the service's `recommend` method call
  `recommend_lifecycle_action` and use the returned
  `LifecycleRecommendation` instead of its own state-based
  mapping.
- Add a parity test that compares the service's output to
  the pure function's output for the same `LifecycleSummary`
  inputs. The parity test guards against future drift.

Phase 4 is a refactor of pre-existing WIP, not new behavior.
It should be run as a separate change under the
`skill-forge-governance` schema, with its own
`openspec/changes/refactor-recommendation-service-to-use-pure-rules/`
folder.

A separate, optional Phase 5 can add the compare view. The
compare view would also be a pure function in
`src/skill_forge/lifecycle/recommendation_rules.py` (or a
sibling module), taking two `LifecycleRecommendationInput`
values and returning a `LifecycleComparison`. That work is
explicitly out of scope for Phase 3 and Phase 4.

---

## 11. Commit

- Commit message: `feat: add governed skill lifecycle recommendation slice`.
- Commit SHA: `44f60fbad51d5ff11bfea860fcd65cf2f1fbe10b` (short: `44f60fb`).
- Files changed: 12 (1 docs, 8 OpenSpec artifacts in the change
  folder, 1 nested spec file, 1 source module, 1 test file).
- Insertions: 1977 lines.

The commit's file list is exactly the Phase 3 file list in
Section 2. The pre-existing dirty WIP is not included.
