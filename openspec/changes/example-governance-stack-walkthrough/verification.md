# Verification: example-governance-stack-walkthrough

> Status: example
> Schema: skill-forge-governance
> Depends on: tasks.md
>
> **EXAMPLE ONLY.** This verification is the example's own evidence
> record. The verdict is `done-as-example` to make the example status
> explicit and prevent accidental archiving.

## Change Id

`example-governance-stack-walkthrough`

## Executed Commands

### `ls openspec/changes/example-governance-stack-walkthrough/`

- Working directory: repository root.
- Exit code: 0.
- Output summary: the eight artifact files are present.

### `ls openspec/changes/example-governance-stack-walkthrough/specs/governance-example-walkthrough/`

- Working directory: repository root.
- Exit code: 0.
- Output summary: `spec.md` is present at the nested path.

### `openspec validate example-governance-stack-walkthrough --strict`

- Working directory: repository root.
- Exit code: 0.
- Output summary: `✓ change/example-governance-stack-walkthrough`.

### `openspec validate --strict --all`

- Working directory: repository root.
- Exit code: 0.
- Output summary: the example change is included in the passed list, alongside the 1 existing change and 22 existing specs.

### `git status --short`

- Working directory: repository root.
- Exit code: 0.
- Output summary: at the time of Phase 2 commit, only the eight files under `openspec/changes/example-governance-stack-walkthrough/` are added (plus the other Phase 2 files). The pre-existing dirty worktree (out of scope) is also listed.

## Test Results

- Test framework: pytest.
- Collected: 265.
- Passed: 265.
- Failed: 0.
- Skipped: 0.
- Summary: `============================ 265 passed in 18.46s =============================`

## OpenSpec Validation

- Command: `openspec validate example-governance-stack-walkthrough --strict`.
- Result: `valid`.
- Summary: the example change passes strict validation. The schema accepts the eight artifacts.

## Skipped Commands

| Command       | Reason     | Impact    |
|---------------|------------|-----------|
| `openspec archive example-governance-stack-walkthrough` | The example is never archived. Archiving would move the folder under `openspec/changes/archive/`, defeating the example's purpose. | none |
| `uv run pytest` for the example itself | The example is a governance artifact, not a runtime module. There is no test to run. | none |

## Deviations from Plan

- Planned: eight files.
- Actual: eight files.
- Reason: no deviation.

## Remaining Risks

- [A future drafter mistakes the example for a real change and tries to archive it] -> Mitigation: every artifact is marked `> Status: example` and `> **EXAMPLE ONLY.**`; this verification file records the verdict as `done-as-example`; `openspec archive` is not part of the change's flow.
- [The example becomes stale as the schema evolves] -> Mitigation: re-validate the example whenever the schema is bumped. A future phase should add a CI check.
- [The example pollutes `openspec validate --all` output] -> Mitigation: this is acceptable; the example is short and clearly marked.

## Follow-up Changes

- A future phase should add a CI check that re-validates the example against the current schema.
- A future phase may add a `status` field to the schema that lets drafters mark changes as `example`, so the OpenSpec CLI can filter them out of `--all` output. Not in Phase 2 scope.

## Verdict

`done-as-example`
