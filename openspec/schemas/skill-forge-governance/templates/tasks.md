# Tasks: <change-id>

> Status: draft
> Schema: skill-forge-governance
> Depends on: plan.md
>
> The apply phase parses checkboxes to track progress. Tasks not
> using `- [ ]` will not be tracked. Each task must have an
> observable completion condition and cite the file(s) it touches.

## 1. <Group Name>

- [ ] 1.1 <Task description>. Files: <path>. Observation: <completion signal>.
- [ ] 1.2 <Task description>. Files: <path>. Observation: <completion signal>.

## 2. <Group Name>

- [ ] 2.1 <Task description>. Files: <path>. Observation: <completion signal>.
- [ ] 2.2 <Task description>. Files: <path>. Observation: <completion signal>.

## 3. <Group Name>

- [ ] 3.1 <Task description>. Files: <path>. Observation: <completion signal>.
- [ ] 3.2 <Task description>. Files: <path>. Observation: <completion signal>.

## N. Final Verification

- [ ] N.1 Run final verification commands from plan.md. Record exit codes in verification.md.
- [ ] N.2 Write verification.md (commands, results, skipped, risks, verdict).
- [ ] N.3 Run `openspec validate <change-id> --strict`. Must pass.
