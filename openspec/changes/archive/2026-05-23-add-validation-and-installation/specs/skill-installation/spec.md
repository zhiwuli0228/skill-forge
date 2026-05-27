## ADDED Requirements

### Requirement: Install command copies generated Skills to platform directories
The system SHALL provide an `install <skill-name>` command that copies a generated Skill package into a target agent platform directory.

#### Scenario: Project opencode install succeeds
- **WHEN** a user runs `skill-forge install java-bug-investigation --target opencode --scope project`
- **THEN** the system SHALL copy the generated package to `./.opencode/skills/java-bug-investigation/`

#### Scenario: Install reports destination path
- **WHEN** installation completes successfully
- **THEN** the command SHALL display the installed destination path

### Requirement: Installer resolves supported platform and scope paths
The installer SHALL resolve installation paths for supported target platforms and scopes.

#### Scenario: opencode paths are resolved
- **WHEN** target is `opencode`
- **THEN** project scope SHALL resolve under `<project>/.opencode/skills/<skill-name>/` and user scope SHALL resolve under the configured opencode user skills path

#### Scenario: Claude paths are resolved
- **WHEN** target is `claude`
- **THEN** project scope SHALL resolve under `<project>/.claude/skills/<skill-name>/` and user scope SHALL resolve under the configured Claude user skills path

#### Scenario: Codex paths are resolved
- **WHEN** target is `codex`
- **THEN** user scope SHALL resolve under the configured Codex user skills path and project scope SHALL resolve under `<project>/.codex/skills/<skill-name>/`

### Requirement: Installer protects existing installed Skills
The installer SHALL avoid overwriting existing installed Skill directories unless force is explicitly requested.

#### Scenario: Existing destination is not overwritten by default
- **WHEN** the destination Skill directory already exists and `--force` is not provided
- **THEN** installation SHALL fail with a clear message and leave the existing destination unchanged

#### Scenario: Force overwrites existing destination
- **WHEN** the destination Skill directory already exists and `--force` is provided
- **THEN** installation SHALL replace the destination with the generated Skill package

### Requirement: Installer validates source package availability
The installer SHALL fail clearly when the named generated Skill package cannot be found.

#### Scenario: Missing generated package fails install
- **WHEN** a user installs a skill name that does not exist under the configured output directory
- **THEN** installation SHALL fail with a clear message and a non-zero exit code

### Requirement: Skill installation is covered by automated tests
The system SHALL include automated tests for installation behavior.

#### Scenario: Tests cover installation workflow
- **WHEN** the test suite runs
- **THEN** it SHALL verify platform path resolution, successful install, missing source failure, default no-overwrite behavior, force overwrite behavior, and CLI install integration using isolated paths
