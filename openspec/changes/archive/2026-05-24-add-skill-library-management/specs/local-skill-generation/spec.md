## ADDED Requirements

### Requirement: Generated packages are discoverable
Generated Skill packages SHALL be discoverable by local Skill library management commands after creation.

#### Scenario: Created package appears in library
- **WHEN** `skill-forge create "<requirement>"` successfully generates a Skill package
- **THEN** `skill-forge list` SHALL be able to display that generated package from the configured output directory
