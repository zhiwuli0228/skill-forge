# Testing Guide

## Purpose

This document is the testing strategy and the rules for adding, running, and interpreting tests in the Skill Forge repository.

## Scope

- Applies to: every test under `tests/` and every verification command that runs pytest.
- Owns: test strategy, when to add unit vs. parity tests, how to test CLI help, how to run targeted vs. full tests, and how to interpret failures.
- Does **not** own: the verification floor per change type (see `docs/02-harness/verification-policy.md`) or per-flow verification mechanics (see `docs/01-architecture/data-flow.md`).

## Current Rules

### 1. Test Strategy

Skill Forge is a deterministic local CLI. The test strategy reflects that.

- **Unit tests** cover pure functions, Pydantic model validation, rule-based parsers, and small helpers. They run in milliseconds and have no fixtures beyond a few inputs.
- **Service tests** cover the orchestration in each `service.py` module. They exercise the I/O boundary with a temp directory and a temporary SQLite database, and they assert the typed contracts that the CLI consumes.
- **Parity tests** cover the lifecycle recommendation rules, the LLM refiner, and the platform adapter. They assert that a given input produces the same output across refactors.
- **CLI tests** cover the Typer command surface end-to-end. They use Typer's `CliRunner` to invoke a command and assert on the exit code, the stdout, and the resulting files on disk.
- **Eval tests** cover the deterministic local eval case runner. They assert that an eval case fails on a malformed package and passes on a well-formed one.
- **Governance tests** are not pytest tests; they live in `scripts/governance_check.py` and the OpenSpec validation flow. The pytest run inside the full governance check is the "governance" layer's contract.

Every test file under `tests/` corresponds to a module under `src/skill_forge/`. The naming is `test_<module>.py` for `src/skill_forge/<module>.py`, with the exception of `tests/test_cli.py` (the CLI surface) and the tests under `tests/test_lifecycle_recommendation.py` / `tests/test_lifecycle_recommendation_rules.py` (the split between the rules and the service).

### 2. When to Add a Unit Test

Add a unit test when:

- A new pure function is added to a module. The test pins the function's behavior to a known input/output pair.
- A Pydantic model gains a new field with validation. The test confirms the validation rejects the bad input and accepts the good input.
- A new rule is added to the requirement analyzer. The test exercises the new rule's match path.
- A new lint warning is added to the validator. The test confirms the warning is raised on the relevant input.
- A new authoring lint warning is added to the quality report. The test confirms the warning appears in the report output.

A unit test does not need a temp directory or a database. If it does, it is a service test, not a unit test.

### 3. When to Add a Parity Test

Add a parity test when:

- A pure rule is refactored. The parity test pins the rule's output to a fixed input so the refactor cannot silently change behavior.
- The lifecycle recommendation rules are extended. The new behavior is covered by a parity test that captures the expected output for a representative input.
- The LLM refiner changes how it merges structured fields. The parity test confirms the merge order and the refusal-to-merge policy on free-form text.
- The platform adapter's path resolution changes. The parity test confirms a representative install path on each supported platform.

A parity test is a "this is what the world looked like yesterday" anchor. The implementation agent must not modify a parity test to make it pass against a new behavior; if the behavior is intentionally changing, the parity test is updated as part of the change, and the change's `proposal.md` records the new behavior.

### 4. How to Test CLI Help

The CLI help is part of the public surface. A change that adds a new command, removes a command, or renames a flag must update the help test.

- `uv run skill-forge --help` must list the expected command set.
- `uv run skill-forge <command> --help` must list the expected options.
- The Typer `CliRunner` is the canonical way to test CLI help from pytest.
- A change that alters CLI output must update `tests/test_cli.py` and run the targeted test plus the full test suite.

A new command without a help test is incomplete. The help test is the contract for users reading the help text to discover the command.

### 5. How to Run Targeted Tests

- One test file: `uv run pytest tests/test_<name>.py`.
- One test function: `uv run pytest tests/test_<name>.py::test_<func>`.
- One test class: `uv run pytest tests/test_<name>.py::TestClass`.
- Tests by keyword: `uv run pytest -k "<keyword>"`.
- Tests with output: `uv run pytest -s` (prints stdout/stderr from the test).
- Stop at first failure: `uv run pytest -x`.
- Show the slowest N tests: `uv run pytest --durations=N`.
- Verbose: `uv run pytest -v`.

The implementation agent runs the targeted tests that cover the touched module(s) on every code change. For the lifecycle recommendation code, that means `tests/test_lifecycle_recommendation.py` and `tests/test_lifecycle_recommendation_rules.py`. For the validator, `tests/test_skill_validator.py`. For the CLI, `tests/test_cli.py`.

### 6. How to Run the Full Test Suite

```bash
uv run pytest
```

Runs the full suite under the project's virtual environment. The implementation agent runs the full suite on every refactor and on every change that touches a shared module (a module imported by more than one other module). The full suite is also part of the full governance check.

The full suite is expected to pass in well under a minute on a developer laptop. A test that runs longer than a few seconds must use a small fixture, not a real corpus.

### 7. How to Interpret Failures

A test failure is information, not a verdict. The implementation agent follows `systematic-debugging` from `SUPERPOWERS.md`:

1. **Reproduce.** Run the failing test by itself with the same command. The reproduction must be the same inputs and the same environment.
2. **Locate the root cause.** Read the assertion, the actual value, the expected value, and the trace. Do not "fix" the symptom.
3. **Add a regression test** that would have caught the bug. The test must fail without the fix and pass with the fix.
4. **Only then change the implementation.** The change is the minimum to make the regression test pass plus any other tests that broke.
5. **Re-run the minimum verification floor** plus the targeted test for the fix.

Common failure modes and their meaning:

- **`AssertionError` on a structured JSON output** — the model or the writer changed shape. Re-read the model and the writer; the model is the source of truth.
- **`ValidationError` from Pydantic in a test** — the test fed input the model rejects. Either the input is wrong (fix the test fixture) or the model rejected a value it should accept (fix the model and add a regression test).
- **`subprocess.CalledProcessError` from a `uv run` call inside a test** — the CLI exited non-zero. Run the same command in a shell to see the actual error.
- **`FileNotFoundError` on a path under `~/.skill-forge/`** — the test did not set `--home` to a temp directory and leaked into the user's real workspace. Set `--home` to `tmp_path` or to a `pytest` `tmp_path_factory` fixture.
- **Flaky test on a timing-sensitive assertion** — the test relied on wall-clock time. Refactor to inject a clock or use freezegun; do not add `time.sleep` to mask the flake.
- **Test passes locally but fails in CI** — check the line-ending warnings in the test file's git history and check the Python version (`python --version` vs. CI's pinned version). CRLF/LF mismatches in test fixtures can cause token-level diffs in JSON assertions.

### 8. Test Hygiene

- Tests are independent. No test depends on the order in which pytest collected them.
- Tests do not mutate the real `~/.skill-forge/` workspace. Every test that needs a workspace uses `tmp_path` and the `--home` flag.
- Tests do not call the LLM. The LLM refiner is tested with a stub client that records the call and returns a fixed response.
- Tests do not hit the network. The research corpus tests use a local fixture corpus.
- Tests are deterministic. `time.time()` is injected; `random` is seeded; `uuid` is injected.

## Related Files

- `docs/05-development/local-development.md` — common commands and read-only vs. mutating.
- `docs/02-harness/verification-policy.md` — minimum verification per change type.
- `docs/04-superpowers/execution-discipline.md` — TDD and debugging.
- `docs/01-architecture/data-flow.md` — per-flow verification commands.
- `tests/` — the test suite.
- `scripts/governance_check.py` — the gate script that runs the full suite.

## What Not To Do

- Do not modify a parity test to make a new behavior pass. The parity test is the contract; the change is the change.
- Do not add `time.sleep` to mask a flake. Inject a clock.
- Do not call the LLM from a test. Stub the client.
- Do not hit the network from a test. Use a local fixture.
- Do not mutate the real `~/.skill-forge/` workspace from a test. Use `tmp_path`.
- Do not skip a test to make a CI run green. Skip with a recorded reason; do not delete the test.
- Do not run a test that depends on a forbidden path. The test must exercise the public surface, not the internals.
