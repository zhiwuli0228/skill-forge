## Why

Skill Forge already records provenance, validation, eval, and experience facts, but those signals live in separate commands and files. Users still have to mentally reconstruct whether a Skill is healthy, stale, regressed, or ready for the next action. A lifecycle index gives the project a single read-only view of that state before we add recommendation or promotion logic.

## What Changes

- Add a local lifecycle index that aggregates provenance, quality, eval, and experience facts for a generated Skill.
- Add a `skill-forge lifecycle show <skill-name>` command that summarizes the current lifecycle state and the evidence behind it.
- Classify each Skill into a small set of deterministic lifecycle states such as `healthy`, `needs-eval`, `needs-upgrade`, and `regressed`.
- Keep the change read-only: no promotion, rollback, or file mutation.
- Preserve existing `show`, `list`, `diff`, and `upgrade` behavior.

## Capabilities

### New Capabilities
- `skill-lifecycle-index`: Read-only lifecycle aggregation and status view for generated Skills, including provenance, quality, eval, and experience evidence.

### Modified Capabilities
- None

## Impact

Affected code: a new `src/skill_forge/lifecycle/` module, CLI lifecycle commands, lifecycle summary tests, and lightweight read-only integration with existing provenance, eval, quality, and experience artifacts.
