## ADDED Requirements

### Requirement: Skill package attachment paths are safe
The system SHALL report invalid Skill packages that contain unsafe attachment paths when attachment paths are supplied for validation.

#### Scenario: Validate safe generated attachments
- **WHEN** a generated Skill package contains reference files under the Skill package directory
- **THEN** validation SHALL continue to validate the package successfully when `SKILL.md` is valid

#### Scenario: Reject unsafe attachment path metadata
- **WHEN** validation is given an attachment path that is absolute or contains `..`
- **THEN** validation SHALL report an error for unsafe attachment path metadata
