# Plan: example-governance-stack-walkthrough

> Status: example
> Schema: skill-forge-governance
> Depends on: proposal.md, spec.md, design.md, review.md
>
> **EXAMPLE ONLY.** This plan describes the creation of the example
> folder itself. There is no external work. The "implementation" is the
> act of writing the eight artifact files into the folder.

## Change Id

`example-governance-stack-walkthrough`

## Allowed Paths

- `openspec/changes/example-governance-stack-walkthrough/brainstorm.md`
- `openspec/changes/example-governance-stack-walkthrough/proposal.md`
- `openspec/changes/example-governance-stack-walkthrough/specs/governance-example-walkthrough/spec.md`
- `openspec/changes/example-governance-stack-walkthrough/design.md`
- `openspec/changes/example-governance-stack-walkthrough/review.md`
- `openspec/changes/example-governance-stack-walkthrough/plan.md`
- `openspec/changes/example-governance-stack-walkthrough/tasks.md`
- `openspec/changes/example-governance-stack-walkthrough/verification.md`

## Forbidden Paths

- Every other path. The example is self-referential. Any modification outside the allowed list is a scope violation.

## Pre-Conditions

- [ ] `review.md` verdict is `approve`.
- [ ] Working tree has been read; the example is the only work in flight.
- [ ] The required tools are present: `openspec` CLI, `bash`, `cat`, `ls`.

## Steps

### Step 1: Create the example folder

- **Files**: `openspec/changes/example-governance-stack-walkthrough/` (new directory).
- **Action**: create the directory and the `specs/governance-example-walkthrough/` subdirectory.
- **Verification**:
  - Command: `ls openspec/changes/example-governance-stack-walkthrough/`
  - Expected exit code: 0
  - Expected observation: directory exists (no files yet is acceptable at this step).
- **Escalation**: stop and report if `openspec/changes/` does not exist or is not writable.

### Step 2: Write the eight artifacts

- **Files**: all eight allowed paths.
- **Action**: write each artifact file. Each starts with `> Status: example` and `> **EXAMPLE ONLY.**` and follows the corresponding template's section structure.
- **Verification**:
  - Command: `ls openspec/changes/example-governance-stack-walkthrough/` and `ls openspec/changes/example-governance-stack-walkthrough/specs/governance-example-walkthrough/`
  - Expected exit code: 0
  - Expected observation: eight files present, including the nested spec file.
- **Escalation**: stop and report if any file is missing or empty.

### Step 3: Run strict validation

- **Files**: none (read-only check).
- **Action**: run `openspec validate example-governance-stack-walkthrough --strict`.
- **Verification**:
  - Command: `openspec validate example-governance-stack-walkthrough --strict`
  - Expected exit code: 0
  - Expected observation: `✓` mark for the example change.
- **Escalation**: if validation fails, fix the offending artifact (the schema tells you which one) and re-run. Do not skip validation.

## Final Verification

- Command: `openspec validate --strict --all`
- Command: `ls openspec/changes/example-governance-stack-walkthrough/`
- Command: `cat openspec/changes/example-governance-stack-walkthrough/verification.md | head -20`

## Rollback

1. Delete the folder `openspec/changes/example-governance-stack-walkthrough/`.
2. No other rollback is needed.

## Hand-off Note

- The example is a meta-artifact. Its purpose is to teach the flow. The implementer is the same Agent that drafted the artifacts. Verification is "the example exists, is internally consistent, and passes `openspec validate --strict`."
