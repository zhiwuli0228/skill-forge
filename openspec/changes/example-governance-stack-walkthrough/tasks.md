# Tasks: example-governance-stack-walkthrough

> Status: example
> Schema: skill-forge-governance
> Depends on: plan.md
>
> **EXAMPLE ONLY.** These tasks describe the creation of the example
> change folder itself. There is no external work. Marking a task done
> is the act of writing the corresponding artifact file.

## 1. Folder Setup

- [ ] 1.1 Create the directory `openspec/changes/example-governance-stack-walkthrough/` and the subdirectory `specs/governance-example-walkthrough/`. Observation: `ls openspec/changes/example-governance-stack-walkthrough/` exits 0 and reports the directory exists.

## 2. Write Artifacts

- [ ] 2.1 Write `openspec/changes/example-governance-stack-walkthrough/brainstorm.md`. Observation: file exists and starts with `> Status: example` and `> **EXAMPLE ONLY.**`.
- [ ] 2.2 Write `openspec/changes/example-governance-stack-walkthrough/proposal.md`. Observation: file exists and starts with `> Status: example` and `> **EXAMPLE ONLY.**`.
- [ ] 2.3 Write `openspec/changes/example-governance-stack-walkthrough/specs/governance-example-walkthrough/spec.md`. Observation: file exists, is nested under `specs/governance-example-walkthrough/`, and starts with `> Status: example` and `> **EXAMPLE ONLY.**`.
- [ ] 2.4 Write `openspec/changes/example-governance-stack-walkthrough/design.md`. Observation: file exists and starts with `> Status: example` and `> **EXAMPLE ONLY.**`.
- [ ] 2.5 Write `openspec/changes/example-governance-stack-walkthrough/review.md`. Observation: file exists, verdict is `approve`, and starts with `> Status: example` and `> **EXAMPLE ONLY.**`.
- [ ] 2.6 Write `openspec/changes/example-governance-stack-walkthrough/plan.md`. Observation: file exists and starts with `> Status: example` and `> **EXAMPLE ONLY.**`.
- [ ] 2.7 Write `openspec/changes/example-governance-stack-walkthrough/tasks.md` (this file). Observation: file exists and the checkboxes above are present.

## 3. Final Verification

- [ ] 3.1 Run `openspec validate example-governance-stack-walkthrough --strict`. Observation: command exits 0 with a `✓` mark for the example change.
- [ ] 3.2 Run `openspec validate --strict --all`. Observation: command exits 0 and the example change is included in the passed list.
- [ ] 3.3 Write `openspec/changes/example-governance-stack-walkthrough/verification.md`. Observation: file exists, starts with `> Status: example` and `> **EXAMPLE ONLY.**`, and verdict is `done-as-example`.
- [ ] 3.4 Run `git status --short` from the repository root. Observation: only files under `openspec/changes/example-governance-stack-walkthrough/` are listed (plus any pre-existing untracked work that is out of scope).
