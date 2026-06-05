# Governance Enforcement Hooks Specification

> Status: draft
> Schema: skill-forge-governance
> Capability: `governance-enforcement-hooks`
> File: `specs/governance-enforcement-hooks/spec.md`
>
> This spec describes the minimal, additive, stdlib-only
> governance enforcement hooks added in Phase 4. The change
> does not modify business code, schema, config, or
> pre-existing WIP.

## Purpose

Provide a one-command local check that runs the project's
known governance gates, prints a stable PASS/FAIL/SKIP line
per command, and returns a non-zero exit code when any
required command fails. The check supports a `--quick` mode
for the fast inner loop and a full mode for the full gate
suite.

## ADDED Requirements

### Requirement: Governance check runs in full and quick mode

The system SHALL provide a `scripts/governance_check.py`
Python script that runs a sequence of governance commands
and reports a stable PASS/FAIL/SKIP line per command.

#### Scenario: Full mode runs the full gate suite

- **WHEN** a contributor runs `python scripts/governance_check.py`
  from the repository root
- **THEN** the script runs, in order, the commands
  `openspec schema validate`,
  `openspec validate example-governance-stack-walkthrough --strict`,
  `openspec validate add-skill-lifecycle-recommendation --strict`,
  `openspec validate --strict --all`,
  `uv run skill-forge --help`, and `uv run pytest`
- **AND** the script prints a `[PASS]`, `[FAIL]`, or
  `[SKIP]` line per command

#### Scenario: Quick mode runs the fast subset

- **WHEN** a contributor runs
  `python scripts/governance_check.py --quick` from the
  repository root
- **THEN** the script runs, in order, the commands
  `openspec validate --strict --all` and
  `uv run skill-forge --help`
- **AND** the script does not run `uv run pytest` in quick
  mode

### Requirement: Governance check uses only the standard library

The system SHALL implement `scripts/governance_check.py`
using only the Python standard library. The script SHALL NOT
import any third-party module.

#### Scenario: Script imports are all standard library

- **WHEN** a reviewer reads `scripts/governance_check.py`
- **THEN** every `import` statement refers to a
  standard-library module
- **AND** no third-party dependency is added to
  `pyproject.toml` or `uv.lock`

### Requirement: Governance check returns non-zero on required failure

The system SHALL return a non-zero exit code from
`scripts/governance_check.py` when any required command
fails or when any required command is skipped because the
underlying tool is missing.

#### Scenario: Required failure produces non-zero exit

- **WHEN** a required command in the script's command
  list exits with a non-zero status
- **THEN** the script prints a `[FAIL]` line for that
  command
- **AND** the script's process exit code is non-zero

#### Scenario: All required commands pass produces zero exit

- **WHEN** every required command in the script's
  command list exits with a zero status
- **THEN** the script's process exit code is zero

### Requirement: Governance check reports skipped commands with reasons

The system SHALL report, for every command in its command
list whose underlying tool is missing, a `[SKIP]` line
followed by a parenthesized reason.

#### Scenario: Missing optional tool is skipped with reason

- **WHEN** an optional command's underlying tool is not
  present on `PATH`
- **THEN** the script prints `[SKIP] <label> (reason: ...)`
  with a human-readable reason
- **AND** the script does not treat the skip as a failure
  for the purpose of the process exit code

### Requirement: Governance check does not mutate the repository

The system SHALL NOT modify, create, or delete any file in
the working directory as a side effect of running
`scripts/governance_check.py`.

#### Scenario: Script run does not mutate files

- **WHEN** a contributor runs
  `python scripts/governance_check.py --quick` or
  `python scripts/governance_check.py` from the repository
  root
- **THEN** the working directory's file list is unchanged
  after the run
- **AND** no file under `src/`, `tests/`, `templates/`,
  `configs/`, `docs/`, or any other location is created,
  modified, or deleted

### Requirement: Governance check is unit-testable

The system SHALL provide unit tests for
`scripts/governance_check.py` under
`tests/test_governance_check.py` that use `pytest`,
`monkeypatch`, and `unittest.mock` to substitute the
subprocess runner, so that no real `openspec` or `uv`
invocation is required.

#### Scenario: Unit tests cover command lists and aggregation

- **WHEN** `uv run pytest tests/test_governance_check.py`
  is run
- **THEN** at least six tests pass, covering full-mode
  command list, `--quick` command list, result aggregation,
  non-zero exit on required failure, skip reporting for a
  missing optional tool, and no repository mutation

## MODIFIED Requirements

None. The pre-existing capabilities in
`openspec/specs/` are out of scope for this slice. They
will be re-evaluated when a future phase wires the script
into CI or pre-commit.

## REMOVED Requirements

### Requirement: (none)

This capability does not remove any existing requirement.

## RENAMED Requirements

### Requirement: (none)

This capability does not rename any existing requirement.
