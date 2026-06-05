# Brainstorm: add-governance-enforcement-hooks

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 4 (governance enforcement hooks)
> Date: 2026-06-06
>
> Brainstorm is the first artifact. It is required because this
> change introduces a new governance rule: a local, repeatable
> enforcement hook that turns the governance stack from
> documentation into a one-command check.

## Problem

Phases 0-3 established a full eight-artifact governance stack
(`skill-forge-governance` schema, OpenSpec validation, Superpowers
execution discipline, one real code slice). The stack is real, but
its enforcement is still documentation-only: a contributor has to
remember which commands to run, in which order, with which flags.
The result is that the gating rules are easy to skip.

How do we add lightweight, local, repeatable enforcement so the
governance stack can be run in one command by a weak agent
without inventing the steps?

## Context

- `AGENTS.md` Section 5 codifies strict-scope discipline; the
  pre-existing WIP in the working tree is preserved.
- `openspec/schemas/skill-forge-governance/schema.yaml` defines
  the eight-artifact flow and the apply phase.
- `openspec/changes/add-skill-lifecycle-recommendation/` is the
  first real change run end-to-end under the new schema. Its
  verification report shows `openspec validate --strict --all`
  passes, `uv run pytest` passes (280 tests), and
  `uv run skill-forge --help` passes.
- `openspec/changes/example-governance-stack-walkthrough/` shows
  the full eight-artifact structure.
- The repository does not yet have a `scripts/` directory.
- The repository does not yet have a CI configuration file.
- The project rule (`AGENTS.md` Section 5) is strict-scope. Phase 4
  may only touch `scripts/governance_check.py`,
  `tests/test_governance_check.py`,
  `openspec/changes/add-governance-enforcement-hooks/**`, and
  `docs/00-project/governance-enforcement-verification-report.md`.
- The governance stack's gating commands are known and stable:
  `openspec schema validate`,
  `openspec validate <change> --strict`,
  `openspec validate --strict --all`,
  `uv run skill-forge --help`,
  `uv run pytest`.

## Options

### Option A: A local Python script `scripts/governance_check.py`

- **Changes**: add `scripts/governance_check.py` that runs the
  governance commands in sequence, prints PASS/FAIL/SKIP per
  command, returns non-zero on required failure, and supports
  `--quick`. Add a unit test file
  `tests/test_governance_check.py` that uses monkeypatching and
  subprocess mocking to verify the command list, the result
  aggregation, the non-zero exit, and the skip reporting. Add
  a new change folder
  `openspec/changes/add-governance-enforcement-hooks/` with
  the eight governance artifacts.
- **Does not change**: business code under `src/`, the existing
  Phase 3 lifecycle files, the OpenSpec schema/config, the
  pre-existing WIP, the dependency set, CI configuration.
- **Top risk**: the script becomes too complex for a "weak
  agent" to read. Mitigation: keep it stdlib-only, keep each
  command list as a plain list of dicts, and keep result
  aggregation as a single loop.
- **Effort**: small (one script, one test file, eight OpenSpec
  artifacts, one verification report).

### Option B: Shell-script or Makefile-based enforcement

- **Changes**: add a `Makefile` or shell script that runs the
  governance commands.
- **Does not change**: business code, schema, dependencies.
- **Top risk**: a shell script mixes control flow and command
  invocation, which is harder to unit test. The `tests/`
  directory already uses pytest and Python; a Python script
  fits the existing test discipline.
- **Effort**: small.

### Option C: Pre-commit hook configuration

- **Changes**: add a `.pre-commit-config.yaml` with hooks that
  run the governance commands.
- **Does not change**: business code, schema, dependencies
  (pre-commit is itself a dependency that would need to be
  installed).
- **Top risk**: pre-commit is a third-party dependency and a
  new tool. Installing it would modify `pyproject.toml` or
  introduce a new tool config file. Both are out of scope for
  Phase 4. A pre-commit hook also runs in the developer's
  local environment, which the user may not have.
- **Effort**: small if pre-commit is available, but violates
  the no-dependency rule.

### Option D: CI configuration

- **Changes**: add a GitHub Actions workflow that runs the
  governance commands on every push.
- **Does not change**: business code, schema, dependencies.
- **Top risk**: CI integration is intentionally out of scope
  for Phase 4 (Phase 4 taskbook, "Non-Goals": "no CI hook").
  The user has not authorized creating a workflow file.
- **Effort**: small, but forbidden.

## Assumptions

- [verified] The list of governance commands is stable and is
  the right starting set for Phase 4.
- [verified] `python` is available on the PATH in the current
  environment (the script uses only the standard library).
- [verified] The repository has no `scripts/` directory yet, so
  the script can be created at the repo root without
  overwriting anything.
- [unverified] The pre-existing WIP under `src/`, `tests/`, and
  `openspec/` will remain untouched by Phase 4. The allowed-path
  list explicitly forbids those directories except
  `tests/test_governance_check.py`.
- [unverified] The user will not immediately add CI or
  pre-commit. Phase 4's design.md records CI and pre-commit
  integration as explicit non-goals and recommends them as
  Phase 5+ work.

## Open Questions

- [blocking, resolved] Should the script live in
  `scripts/governance_check.py` or in a new package under
  `src/skill_forge/`? Resolved: `scripts/`. The script is a
  development tool, not a runtime library, and Phase 4 may
  not modify `src/`.
- [blocking, resolved] Should the script use only the Python
  standard library? Resolved: yes. The Phase 4 taskbook
  forbids new dependencies and forbids modifying
  `pyproject.toml` or `uv.lock`.
- [non-blocking] Should the script print in color? Resolved:
  no. The output is plain text so the script is easy to
  copy-paste into a chat.
- [non-blocking] Should the script support running individual
  commands by name? Resolved: no, for now. The Phase 4
  taskbook requires only `--quick` and the default full mode.
  A per-command flag is a follow-up.

## Recommendation

- Recommended: **Option A** (a local Python script
  `scripts/governance_check.py` with a unit test file and a
  full eight-artifact change folder).
- Reason: it is the smallest diff that satisfies the task. The
  script is stdlib-only, the test file uses monkeypatching to
  avoid running real external commands, and the change folder
  re-uses the `skill-forge-governance` schema that Phases 1-3
  already validated. Option A also leaves CI and pre-commit
  integration for a later phase, which matches the taskbook's
  "Non-Goals" list.
