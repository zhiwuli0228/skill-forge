# Plan: <change-id>

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, spec.md, design.md, review.md
>
> The plan is the executable contract between the planning agent
> and the implementation agent. It must be runnable by a weaker
> agent that has not seen the conversation history.

## Change Id

`<change-id>`

## Allowed Paths

<!-- Explicit list of paths the implementation may modify. -->

- <path>
- <path>

## Forbidden Paths

<!-- Explicit list of paths the implementation must NOT modify.
     This is not the same as "paths not on the allowed list".
     A path may be neither allowed nor forbidden if it is irrelevant
     to this change; if it is touched, that is scope drift. -->

- <path>
- <path>

## Pre-Conditions

<!-- What must be true before step 1 runs. -->

- [ ] `review.md` verdict is `approve`
- [ ] Working tree is clean (or all uncommitted changes are
      documented and out of scope for this change)
- [ ] The required tools are present: <tool list>

## Steps

<!-- Numbered. Each step has: a short title, the exact files to
     change, the exact commands to run for verification, the
     expected exit code and observation, and the escalation rule. -->

### Step 1: <short title>

- **Files**: <path>, <path>
- **Action**: <what to do, briefly>
- **Verification**:
  - Command: <command>
  - Expected exit code: <code>
  - Expected observation: <what success looks like>
- **Escalation**: <what to do if verification fails>

### Step 2: <short title>

- **Files**: <path>
- **Action**: <what to do, briefly>
- **Verification**:
  - Command: <command>
  - Expected exit code: <code>
  - Expected observation: <what success looks like>
- **Escalation**: <what to do if verification fails>

### Step N: <short title>

- **Files**: <path>
- **Action**: <what to do, briefly>
- **Verification**:
  - Command: <command>
  - Expected exit code: <code>
  - Expected observation: <what success looks like>
- **Escalation**: <what to do if verification fails>

## Final Verification

<!-- The exact commands to run at the end of all steps.
     These are repeated in tasks.md and verification.md. -->

- Command: <command>
- Command: <command>

## Rollback

<!-- The exact actions to revert the change if verification
     fails after the last step. -->

1. <rollback step>
2. <rollback step>

## Hand-off Note

<!-- A short note the implementation agent will see first.
     State the single most important rule for this change. -->

- <rule>
