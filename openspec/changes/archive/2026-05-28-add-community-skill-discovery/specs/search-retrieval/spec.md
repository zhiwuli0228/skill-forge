## ADDED Requirements

### Requirement: Search returns discovered community Skills
The search command SHALL return discovered community Skill examples from the local corpus when they match the user's query.

#### Scenario: Search finds discovered code review Skill
- **WHEN** the local corpus contains a discovered community Skill whose metadata or content matches `code review skill`
- **THEN** `skill-forge search "code review skill"` SHALL display that discovered Skill as a search result

#### Scenario: Search preserves discovered Skill metadata
- **WHEN** search displays a discovered community Skill result
- **THEN** the result SHALL include the discovered Skill name or title, source name, platform when known, summary, and score

#### Scenario: Platform boost applies to discovered Skills
- **WHEN** a user searches with `--platform <platform>` and discovered Skill examples include matching platform metadata
- **THEN** matching discovered Skill results SHALL receive the existing platform ranking boost

#### Scenario: Search remains offline
- **WHEN** a user runs search after community Skills have been discovered by update
- **THEN** search SHALL use only the local corpus and SHALL NOT perform GitHub discovery or network fetches
