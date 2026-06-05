# Design: add-governance-enforcement-hooks

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, specs/governance-enforcement-hooks/spec.md
>
> This is the design for the small, additive governance-tooling
> change. Business code, schema, config, and pre-existing WIP
> are preserved untouched.

## Context

Phases 0-3 established a full eight-artifact governance stack
under the `skill-forge-governance` schema. The stack is real,
but its enforcement is still documentation-only: a contributor
has to remember which commands to run, in which order, with
which flags. The pre-existing Phase 3 verification report
shows that the gates do pass; the question is whether the
gates are easy to run.

What is missing for the next step is a single local command
that runs the known gates in sequence, prints a stable
PASS/FAIL/SKIP line per command, returns non-zero on required
failure, and supports a `--quick` mode for the fast inner
loop. The design below is a single new Python script that
contains two command lists, a result-aggregation loop, and
a stdlib-only subprocess runner.

The script is a developer tool, not a runtime library. It
lives in `scripts/governance_check.py` and uses only the
Python standard library, so it can be read in one pass and
run without installing anything.

## Goals / Non-Goals

### Goals

- Define a single command-list construction function that
  returns the six-command full-mode list or the two-command
  `--quick` list.
- Define a result-aggregation function that takes a list of
  per-command results and returns `(passed_count,
  failed_count, skipped_count, exit_code)`. `exit_code` is
  `1` if any required command failed or any required command
  was skipped due to a missing tool, `0` otherwise.
- Define a runner that uses `subprocess.run` to execute each
  command in the working directory the script was invoked
  from, with a captured timeout, and a printed PASS/FAIL/SKIP
  line per command.
- Cover at least six unit tests: full-mode command list,
  `--quick` command list, result aggregation for an all-pass
  run, non-zero exit on a required failure, skip reporting
  for a missing optional tool, and a no-mutation assertion
  on the working directory.

### Non-Goals

- No CI integration. CI is intentionally out of scope for
  Phase 4. A GitHub Actions workflow or equivalent is a
  follow-up change.
- No pre-commit hook. pre-commit is a third-party dependency
  and would require a new tool config file. It is out of
  scope.
- No new runtime dependency. `pyproject.toml` and `uv.lock`
  are not modified. The script uses only the standard
  library.
- No business code change. The script does not modify
  anything under `src/`.
- No schema or config change. `openspec/schemas/**` and
  `openspec/config.yaml` are forbidden by the Phase 4
  allowed-path list.
- No modification of the Phase 3 lifecycle files. The
  pre-existing `src/skill_forge/lifecycle/recommendation_rules.py`
  and the pre-existing WIP under `src/skill_forge/lifecycle/`
  are preserved.
- No per-command flag (`--only`, `--skip`). A per-command
  flag is a follow-up.
- No color output. The script prints plain text only.

## Decisions

### Decision 1: A single Python script with a `main()` and helpers

- **Decision**: place the script's command lists,
  result-aggregation function, and runner in
  `scripts/governance_check.py`. The script exposes a
  `build_command_list(quick: bool) -> list[Command]`
  function, a `summarize_results(results: list[Result]) ->
  Summary` function, a `run_command(cmd: list[str],
  cwd: str) -> Result` function, and a `main(argv:
  list[str]) -> int` function.
- **Rationale**: keeping every function in a single file
  makes the script readable in one pass. The unit tests can
  import the helpers and test them in isolation. The script
  has no global state and no class hierarchy.
- **Alternatives considered**:
  - "Put each function in a separate file under a new
    `scripts/governance_check/` package" — rejected. The
    script is small; a package is heavier than the change
    needs.
  - "Use a class with static methods" — rejected. A class
    is heavier than the change needs and matches no
    existing pattern in the project.

### Decision 2: Command list as a list of dataclass-like dicts

- **Decision**: each command is a dict with keys `label`,
  `argv`, `required`, and `reason`. The script iterates the
  list, runs each command, and prints a stable line per
  command.
- **Rationale**: a list of dicts is the smallest shape that
  still carries per-command metadata. A dataclass would be
  equivalent but heavier.
- **Alternatives considered**:
  - "Use a `@dataclass`" — rejected. A dict is enough for
    the four fields and avoids importing `dataclasses` for
    a single internal shape.
  - "Use a tuple of tuples" — rejected. A tuple of strings
    cannot carry `required` and `reason`.

### Decision 3: Standard library only

- **Decision**: the script imports only `argparse`, `os`,
  `shutil`, `subprocess`, `sys`, and `time`. No third-party
  dependency is added.
- **Rationale**: the Phase 4 taskbook forbids new
  dependencies and forbids modifying `pyproject.toml` or
  `uv.lock`. The standard library is enough for everything
  the script needs: argument parsing, subprocess
  invocation, exit-code handling, and elapsed-time
  measurement.
- **Alternatives considered**:
  - "Use `sh` or `pexpect`" — rejected. Both are
    third-party.
  - "Use `pytest` for the runner" — rejected. pytest is a
    test tool, not a runner.

### Decision 4: Skip behavior is per-command and explicit

- **Decision**: each command carries an explicit `required`
  flag. When the underlying tool is missing, the script
  prints `[SKIP] <label> (reason: <text>)` and counts the
  command as a skip. A skipped required command causes a
  non-zero exit; a skipped optional command does not.
- **Rationale**: the Phase 4 taskbook requires "report
  skipped commands with reasons". Per-command metadata is
  the cleanest way to express that requirement.
- **Alternatives considered**:
  - "Always treat a missing tool as a failure" — rejected.
    The taskbook requires the skip-reason path for
    optional commands.
  - "Always treat a missing tool as a skip" — rejected.
    The taskbook requires non-zero exit on a required
    failure.

### Decision 5: No repository mutation

- **Decision**: the script reads the working directory but
  does not write to it. The unit tests assert no file in
  the working directory is created, modified, or deleted
  during a run.
- **Rationale**: the Phase 4 taskbook requires
  "no repository mutation". The script's job is to report,
  not to change.
- **Alternatives considered**:
  - "Write a results JSON to a temp file" — rejected. The
    taskbook requires no mutation, and the script's
    console output is enough.

### Decision 6: No CI integration in Phase 4

- **Decision**: the script is run manually from the
  repository root. It is not wired into CI or pre-commit.
- **Rationale**: the Phase 4 taskbook explicitly lists
  "no CI hook" and "no pre-commit" as non-goals. A future
  phase can wire the script into CI by adding a workflow
  file (a separate change).
- **Alternatives considered**:
  - "Wire the script into a CI workflow as part of
    Phase 4" — rejected. CI integration is a separate
    change and is forbidden by the taskbook.
  - "Wire the script into pre-commit as part of
    Phase 4" — rejected. pre-commit requires a new
    third-party dependency and a new tool config file,
    both of which are forbidden.

## Data Contracts

No stored artifact schema changes. The script does not read
or write `skill-forge.json`, `eval-report.json`,
`config.yaml`, blueprint schema, or any other on-disk
artifact.

The only data contracts introduced are in-memory
shapes used by the script itself:

```yaml
Command:
  label: str        # e.g. "openspec schema validate"
  argv: list[str]   # the command and its arguments
  required: bool    # True for required commands, False for optional
  reason: str       # human-readable description, printed on skip/fail

Result:
  label: str        # copied from Command.label
  status: str       # one of "PASS", "FAIL", "SKIP"
  exit_code: int    # 0 for PASS, non-zero for FAIL, 0 for SKIP
  reason: str       # human-readable detail (error text, skip reason, or "")
  elapsed_seconds: float  # wall-clock duration of the run
  skipped: bool     # True when the command was skipped
```

The `Result.status` enum and the `Command.required` flag
are the only contracts a future change needs to maintain
when the command list evolves.

## Module Boundaries

### Added

- `scripts/governance_check.py`: the script. Exposes
  `build_command_list(quick: bool) -> list[Command]`,
  `summarize_results(results: list[Result]) -> Summary`,
  `run_command(cmd: list[str], cwd: str) -> Result`, and
  `main(argv: list[str]) -> int`. Imports only from
  `argparse`, `os`, `shutil`, `subprocess`, `sys`, and
  `time`.
- `tests/test_governance_check.py`: unit tests for the
  script. Uses `pytest`, `monkeypatch`, and `unittest.mock`
  to substitute the subprocess runner. The tests do not
  invoke `openspec` or `uv` directly.
- `openspec/changes/add-governance-enforcement-hooks/`:
  the eight OpenSpec artifacts for this change.
- `docs/00-project/governance-enforcement-verification-report.md`:
  the human-readable verification report.

### Modified

- None. No file outside the four paths above is modified
  by this change.

### Untouched

- `src/**`: every business module is preserved.
- `tests/test_lifecycle_recommendation_rules.py`: the
  Phase 3 test file is preserved.
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`,
  `SUPERPOWERS.md`: every governance document is
  preserved.
- `README.md`, `README.zh-CN.md`: every README is
  preserved.
- `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**`: every governance-doc tree is
  preserved.
- `openspec/config.yaml`, `openspec/schemas/**`: the
  OpenSpec config and schema are preserved.
- `openspec/changes/example-governance-stack-walkthrough/**`
  and `openspec/changes/add-skill-lifecycle-recommendation/**`:
  the example and Phase 3 changes are preserved.
- `templates/**`, `configs/**`, `pyproject.toml`,
  `uv.lock`: every other config artifact is preserved.

## Compatibility Impact

- Claude Code: no effect. The script is a developer tool.
- Codex: no effect. Codex does not invoke the script.
- opencode: no effect. opencode does not invoke the script.
- Generated Skill packages: no effect. The script does not
  read or write any package file.

## Offline and Deterministic Mode

- Network unavailable: no effect. The script does not
  perform network I/O. The `uv run pytest` command may
  need network access to resolve the local environment,
  but that is `uv`'s behavior, not the script's.
- LLM disabled: no effect. The script does not invoke
  any LLM.
- LLM enabled but config missing: no effect. Same.

## Security and Filesystem

- Reads: nothing. The script does not read any file.
- Writes: nothing. No file system write.
- Environment variables: `PATH` only. The script uses
  `shutil.which` to detect missing tools.

## Risks / Trade-offs

- [The script's command list may drift from the project's
  actual governance gates] -> Mitigation: the command
  list is a single list-of-dicts in the script body, and
  a unit test asserts the exact full-mode and quick-mode
  command lists. Any drift fails the unit test.
- [The script may take a long time in full mode because
  `uv run pytest` is included] -> Mitigation: `--quick`
  mode excludes `uv run pytest` and runs only the two
  fastest gates. The verification report records the
  elapsed time of full mode.
- [A new contributor may not know to run the script from
  the repository root] -> Mitigation: the script's
  docstring and `--help` text say "run from the
  repository root". The verification report records the
  exact working directory used to produce the recorded
  results.
- [A future change may add a per-command flag, and the
  unit tests will need to be updated] -> Mitigation: the
  per-command flag is a follow-up. The unit tests assert
  the exact command lists at Phase 4; a follow-up that
  changes the command lists will update the tests in
  the same change.

## Migration Plan

### Deploy

1. Land `scripts/governance_check.py`.
2. Land `tests/test_governance_check.py`.
3. Land the eight OpenSpec artifacts under
   `openspec/changes/add-governance-enforcement-hooks/`.
4. Run `openspec validate
   add-governance-enforcement-hooks --strict`.
5. Run `openspec validate --strict --all`.
6. Run `uv run pytest tests/test_governance_check.py`.
7. Run `uv run pytest` for the full suite.
8. Run `uv run skill-forge --help` for the smoke test.
9. Run `python scripts/governance_check.py --quick`.
10. Run `python scripts/governance_check.py` (full mode).
11. Land the verification report under
    `docs/00-project/`.

### Rollback

1. Delete `scripts/governance_check.py`.
2. Delete `tests/test_governance_check.py`.
3. Delete the folder
   `openspec/changes/add-governance-enforcement-hooks/`.
4. Delete
   `docs/00-project/governance-enforcement-verification-report.md`.
5. No data migration. The script did not write to disk.
6. No business code, schema, or config was changed, so
   no rollback is needed outside the four paths above.

## Open Questions

- [non-blocking] Should the script's exit code distinguish
  between a required failure and a required skip? Resolved:
  both produce exit code `1`. The two cases are
  distinguishable in the printed output, and a future
  change can refine the exit code if needed.
- [non-blocking] Should the script print elapsed time per
  command? Resolved: yes. The verification report needs
  the elapsed time to show that full mode is acceptable.
- [non-blocking] Should the script support a JSON output
  mode for machine consumption? Resolved: no, for now. A
  JSON output mode is a follow-up.
