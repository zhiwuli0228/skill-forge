## ADDED Requirements

### Requirement: Validator reports authoring lint warnings
The validator SHALL report deterministic authoring lint findings as warnings without changing validation error semantics.

#### Scenario: Invalid name slug warns
- **WHEN** `SKILL.md` frontmatter contains a `name` that is not lowercase kebab-case
- **THEN** validation SHALL include a `name_not_slug` warning

#### Scenario: Package name mismatch warns
- **WHEN** the Skill package directory name differs from the frontmatter `name`
- **THEN** validation SHALL include a `package_name_mismatch` warning

#### Scenario: Weak description warns
- **WHEN** frontmatter `description` is present but too short or lacks trigger or exclusion guidance
- **THEN** validation SHALL include authoring warnings for the missing description qualities

#### Scenario: Empty recommended section warns
- **WHEN** a recommended section heading exists but its body has no meaningful content
- **THEN** validation SHALL include an `empty_section` warning

#### Scenario: Thin workflow or quality gates warn
- **WHEN** Workflow or Quality gates sections contain too few actionable items
- **THEN** validation SHALL include authoring warnings for the thin section

#### Scenario: Lint warnings do not invalidate package
- **WHEN** validation finds authoring lint warnings and no errors
- **THEN** validation SHALL keep `ok` true
