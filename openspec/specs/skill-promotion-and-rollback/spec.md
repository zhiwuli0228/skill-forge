# skill-promotion-and-rollback Specification

## Purpose
Define a local, reversible promote and rollback flow for generated Skill packages. This capability preserves snapshot history in the Skill Forge home directory so active packages can be replaced and restored without mutating the only copy of a known-good version.
## Requirements
### Requirement: Skills can be promoted locally with rollback history preserved
The system SHALL provide a local promote operation that copies a generated candidate Skill into an active target package while preserving the previous active package as a rollback snapshot.

#### Scenario: Promote candidate to active target
- **WHEN** a user runs `skill-forge promote <candidate-name>` for an existing generated candidate Skill
- **THEN** the system SHALL copy the candidate into the active target package
- **AND** the system SHALL preserve the previous active package as a snapshot before overwriting it
- **AND** the command SHALL display the promoted source, target, and snapshot information

#### Scenario: Promote command preserves the source candidate
- **WHEN** a user promotes a candidate Skill
- **THEN** the source candidate package SHALL remain present in the output directory
- **AND** the source candidate package SHALL remain unchanged by the promote operation

#### Scenario: Promote missing candidate fails clearly
- **WHEN** a user runs `skill-forge promote <candidate-name>` for a missing generated package
- **THEN** the command SHALL exit non-zero with a clear missing generated Skill message

### Requirement: Skills can be rolled back to a recorded version snapshot
The system SHALL provide a local rollback operation that restores a previously recorded version snapshot for an active Skill package.

#### Scenario: Roll back to a known version
- **WHEN** a user runs `skill-forge rollback <skill-name> --to <version-name>`
- **THEN** the system SHALL restore the recorded snapshot for that version
- **AND** the system SHALL preserve the current active package as a new snapshot before restoring the requested version
- **AND** the command SHALL display the restored version and new snapshot information

#### Scenario: Roll back missing version fails clearly
- **WHEN** a user runs `skill-forge rollback <skill-name> --to <version-name>` and the requested version snapshot is not recorded
- **THEN** the command SHALL exit non-zero with a clear rollback history message

#### Scenario: Rollback command preserves existing candidate artifacts
- **WHEN** a user rolls back an active Skill package
- **THEN** the operation SHALL NOT delete unrelated generated Skill packages
- **AND** the operation SHALL NOT mutate the source version snapshot

### Requirement: Promotion and rollback history is recorded locally
The system SHALL record promotion and rollback provenance in a local registry under the Skill Forge home directory.

#### Scenario: Registry stores promotion history
- **WHEN** a promote or rollback operation completes
- **THEN** the system SHALL append a registry entry containing the target Skill name, source version label, snapshot path, and operation timestamp

#### Scenario: Registry supports deterministic snapshot lookup
- **WHEN** a user requests rollback to a specific version label
- **THEN** the system SHALL locate the exact recorded snapshot for that label
- **AND** the lookup SHALL be deterministic

### Requirement: Promote and rollback remain local and reversible
The system SHALL perform promote and rollback operations only on local Skill packages and local history artifacts.

#### Scenario: No remote release dependency
- **WHEN** promote or rollback runs
- **THEN** the system SHALL NOT require network access
- **AND** the system SHALL NOT call an external release service

#### Scenario: Promote/rollback preserve original content
- **WHEN** a promote or rollback operation completes
- **THEN** the original source package content SHALL remain available in its recorded snapshot
- **AND** the command output SHALL explain the chosen source and destination paths
