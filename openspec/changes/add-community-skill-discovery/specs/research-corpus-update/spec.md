## ADDED Requirements

### Requirement: Update processes discovered GitHub Skills
The update command SHALL process GitHub research sources with discovery metadata by discovering and storing individual Skill files from the configured repository.

#### Scenario: Update discovers repository Skills
- **WHEN** a user runs `skill-forge update` and an enabled GitHub source declares Skill discovery metadata
- **THEN** the updater SHALL discover matching `SKILL.md` files in that repository
- **AND** it SHALL store each successfully fetched discovered Skill as an individual corpus document and skill example

#### Scenario: Update reports discovery source outcome
- **WHEN** a GitHub discovery source is processed
- **THEN** the update output SHALL report whether discovered Skills were updated, skipped, or failed for that source

#### Scenario: Existing docs sources still update normally
- **WHEN** a user runs `skill-forge update` with enabled docs sources
- **THEN** docs sources SHALL continue to be fetched, cached, and reported using the existing single-document behavior

#### Scenario: Existing GitHub sources without discovery remain compatible
- **WHEN** a GitHub source has no discovery metadata
- **THEN** update SHALL continue to process that source using the existing single-document behavior
