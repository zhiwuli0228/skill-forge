## ADDED Requirements

### Requirement: Blueprints can be matched for generation
The system SHALL allow generation code to find a built-in Skill blueprint by task type.

#### Scenario: Match blueprint by task type
- **WHEN** generation requests a blueprint for task type `bug-investigation`
- **THEN** the system returns the built-in `bug-investigation` blueprint

#### Scenario: No matching blueprint
- **WHEN** generation requests a blueprint for an unknown task type
- **THEN** the system reports no match without failing generation

### Requirement: Blueprint defaults can enrich requirements
The system SHALL merge matching blueprint defaults into a `SkillRequirement` before rendering.

#### Scenario: Fill missing requirement lists
- **WHEN** a matching blueprint has defaults for a list field that is empty on the requirement
- **THEN** the system copies those defaults into the requirement

#### Scenario: Preserve existing requirement values
- **WHEN** the requirement already contains values for a field
- **THEN** the system preserves those values and appends non-duplicate blueprint defaults only where appropriate
