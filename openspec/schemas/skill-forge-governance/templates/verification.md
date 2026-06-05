# Verification: <change-id>

> Status: draft
> Schema: skill-forge-governance
> Depends on: tasks.md
>
> Verification is written AT THE END of the change, after tasks
> are complete, not before. A change without a verification record
> is not done.

## Change Id

`<change-id>`

## Executed Commands

<!-- Exact commands run, in the order run. For each: command,
     working directory, exit code, short output summary. -->

### `<command 1>`

- Working directory: <path>
- Exit code: <code>
- Output summary: <one or two lines>

### `<command 2>`

- Working directory: <path>
- Exit code: <code>
- Output summary: <one or two lines>

## Test Results

<!-- Pass/fail counts. The full pytest summary line is enough. -->

- Test framework: pytest
- Collected: <count>
- Passed: <count>
- Failed: <count>
- Skipped: <count>
- Summary: `<paste pytest summary line>`

## OpenSpec Validation

<!-- Output of `openspec validate <change-id> --strict`.
     Must be `valid` or the change is not done. -->

- Command: `openspec validate <change-id> --strict`
- Result: <valid / invalid>
- Summary: <one or two lines>

## Skipped Commands

<!-- Commands the implementation did not run, with the reason
     for skipping. The reason is required. "I forgot" is not
     a reason. -->

| Command       | Reason     | Impact    |
|---------------|------------|-----------|
| <command>     | <reason>   | <none / blocking / non-blocking> |

## Deviations from Plan

<!-- Differences between the planned file list and the actual
     file list, with the reason. Empty when none. -->

- Planned: <file>
- Actual: <file>
- Reason: <reason>

## Remaining Risks

<!-- Anything that could still break or surprise. Format:
     [Risk] -> Mitigation / Follow-up. -->

- [Risk] -> [mitigation or follow-up]
- [Risk] -> [mitigation or follow-up]

## Follow-up Changes

<!-- OpenSpec changes that should follow this one. If none,
     say "None". -->

- <change id and one-line description> or "None"

## Verdict

<!-- One of:
     - done
     - done-with-risks
     - not-done -->

`<verdict>`
