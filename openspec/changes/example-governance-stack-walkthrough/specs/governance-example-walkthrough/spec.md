# Governance Example Walkthrough Specification

> Status: example
> Schema: skill-forge-governance
> Capability: `governance-example-walkthrough`
> File: `specs/governance-example-walkthrough/spec.md`
>
> **EXAMPLE ONLY.** This spec does not define a real capability. It is
> part of the example change `example-governance-stack-walkthrough`, which
> exists to demonstrate the full eight-artifact governance flow. The
> requirements below are phrased as if the example were a real change,
> so that a reader can use the example as a worked template.

## Purpose

Define a self-referential example OpenSpec change that exercises all eight governance artifacts under the `skill-forge-governance` schema, without modifying any external file. The example is a teaching artifact, not a feature.

## ADDED Requirements

### Requirement: Example change folder contains all eight artifacts

The system SHALL have a change folder under `openspec/changes/example-governance-stack-walkthrough/` that contains the eight artifacts `brainstorm.md`, `proposal.md`, `spec.md` (in `specs/governance-example-walkthrough/spec.md`), `design.md`, `review.md`, `plan.md`, `tasks.md`, and `verification.md`.

#### Scenario: All eight artifacts exist

- **WHEN** a reviewer lists the files in `openspec/changes/example-governance-stack-walkthrough/`
- **THEN** the eight artifact files are present
- **AND** the spec file is nested under `specs/governance-example-walkthrough/spec.md`

#### Scenario: Each artifact is marked as Example Only

- **WHEN** a reviewer opens any of the eight artifact files
- **THEN** the file's first ten lines contain the marker `> **EXAMPLE ONLY.**` and the marker `> Status: example`

### Requirement: Example change does not modify any external file

The example change SHALL NOT modify any file outside the folder `openspec/changes/example-governance-stack-walkthrough/`.

#### Scenario: No external file is modified

- **WHEN** the example change is complete
- **THEN** `git status` shows modifications only inside `openspec/changes/example-governance-stack-walkthrough/`
- **AND** no file under `src/`, `tests/`, `templates/`, `configs/`, `docs/`, or any other location has been changed by this change

### Requirement: Example change passes strict validation

The example change SHALL pass `openspec validate example-governance-stack-walkthrough --strict`.

#### Scenario: Strict validation returns valid

- **WHEN** the user runs `openspec validate example-governance-stack-walkthrough --strict`
- **THEN** the command exits with code 0
- **AND** the output includes a `✓` mark for the example change

### Requirement: Example change is self-describing

Every artifact in the example change SHALL state that it is an example, and SHALL explain the role of the artifact in the governance flow.

#### Scenario: Each artifact states its role

- **WHEN** a reviewer reads any artifact in the example change
- **THEN** the artifact contains a section explaining the artifact's role in the eight-artifact flow
- **AND** the artifact cites at least one other artifact in the same change folder by filename

## REMOVED Requirements

### Requirement: (none)

This capability does not remove any existing requirement.

## RENAMED Requirements

### Requirement: (none)

This capability does not rename any existing requirement.
