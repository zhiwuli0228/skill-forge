# Review: <change-id>

> Status: draft
> Schema: skill-forge-governance
> Reviewer: <name or agent>
> Date: <YYYY-MM-DD>
>
> The review is the gate between planning and execution. It must
> be produced AFTER design.md and BEFORE plan.md is finalized.
> A change with verdict `block` cannot proceed to plan. A change
> with verdict `request-changes` cannot proceed to tasks.

## Change Id

`<change-id>`

## Scope Coverage

<!-- For each artifact, the verdict on whether it satisfies the
     schema rules. List missing required sections. -->

| Artifact     | File         | Verdict      | Missing Sections      |
|--------------|--------------|--------------|-----------------------|
| proposal     | proposal.md  | <verdict>    | <sections or "none">  |
| spec         | specs/...    | <verdict>    | <sections or "none">  |
| design       | design.md    | <verdict>    | <sections or "none">  |
| brainstorm   | brainstorm.md| <verdict>    | <sections or "none">  |

`<verdict>` is one of: `ok`, `minor-issues`, `missing`, `incorrect`.

## Cross-Artifact Consistency

<!-- Check that artifacts agree on the change id, the capability
     names, the data contracts, the allowed paths, and the
     verification commands. -->

- Capability names in proposal match the spec files: <yes / no>
- Data contracts in design match the affected files in plan: <yes / no>
- Allowed-path list in plan matches the files in tasks: <yes / no>
- Verification commands in tasks match the commands in plan: <yes / no>

## Allowed Path List

<!-- Confirm the explicit allowed and forbidden paths in plan.md. -->

### Allowed

- <path>
- <path>

### Forbidden

- <path>
- <path>

### Discrepancies

<!-- Reject the change if the list is missing, or if a task
     touches a forbidden path. -->

- <discrepancy or "none">

## Verification Readiness

<!-- Each verification command must be runnable in the current
     environment. List any command that depends on a missing tool. -->

| Command           | Tool / Env | Status      |
|-------------------|------------|-------------|
| <command>         | <tool>     | <ok / missing> |
| <command>         | <tool>     | <ok / missing> |

## Required Changes

<!-- Required for verdict `request-changes`. Each change must be
     specific enough that the drafter can apply it without
     re-reading the entire change. Empty when verdict is `approve`. -->

1. <file>: <specific change>
2. <file>: <specific change>

## Verdict

<!-- One of:
     - approve
     - request-changes
     - block -->

`<verdict>`
