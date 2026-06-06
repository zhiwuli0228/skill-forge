## ADDED Requirements

### Requirement: Search results expose adoptable corpus references
The system SHALL include stable local corpus references in search results so users can adopt cached Skill documents.

#### Scenario: Search result includes document ID
- **WHEN** search returns a corpus result
- **THEN** the result SHALL include the local corpus document ID

#### Scenario: Search result includes example ID when available
- **WHEN** search returns a corpus result associated with a skill example row
- **THEN** the result SHALL include the local skill example ID

#### Scenario: Search reference is local
- **WHEN** search displays corpus reference IDs
- **THEN** those IDs SHALL refer to locally cached corpus records and SHALL NOT require network access to resolve

### Requirement: Search output supports adoption workflow
The search command SHALL display enough reference metadata for a user to run the adoption command for a returned result.

#### Scenario: Search output shows adoptable ID
- **WHEN** a user runs `skill-forge search "<query>"`
- **THEN** the command output SHALL show the document ID or another documented local reference that can be passed to `skill-forge adopt`

#### Scenario: Empty search remains unchanged
- **WHEN** search returns no results
- **THEN** the command SHALL preserve the existing empty-result behavior and SHALL NOT display adoption guidance for missing results
