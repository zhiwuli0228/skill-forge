## Why

Skill Forge now has a lifecycle index and a deterministic recommendation layer, but it still lacks the final operational step: moving a validated candidate into an active package while preserving a rollback path. Users need a local, auditable way to promote a candidate Skill and restore a previous version when the new one is not acceptable.

## What Changes

- Add a local promote flow that copies a chosen candidate Skill into an active target package while preserving the previous version as a rollback snapshot.
- Add a local rollback flow that restores a previously recorded version snapshot for a promoted Skill.
- Record promotion and rollback provenance in a local registry so history stays traceable without mutating the source candidate.
- Add `skill-forge promote <candidate-name>` and `skill-forge rollback <skill-name> --to <version-name>` as read-write lifecycle commands.
- Keep the change local and deterministic; do not add remote sync or external release automation.

## Capabilities

### New Capabilities
- `skill-promotion-and-rollback`: Local promote and rollback operations for generated Skills, including snapshot history and promotion provenance.

### Modified Capabilities
- None

## Impact

Affected code: a new promotion service under `src/skill_forge/lifecycle/`, new CLI commands, a local promotion registry under the Skill Forge home directory, and tests covering promote, rollback, and history persistence.
