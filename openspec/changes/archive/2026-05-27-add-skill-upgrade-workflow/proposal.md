## Why

Skill Forge can now generate, validate, trace, lint, repair-suggest, evaluate, and inspect Skill packages, but it cannot regenerate an existing Skill against the current blueprint standards. A deterministic upgrade workflow closes the loop for teams that evolve custom blueprints and need candidate packages they can compare before adopting.

## What Changes

- Add `skill-forge upgrade <skill-name>` for generated Skill packages with provenance metadata.
- Reconstruct an upgrade requirement from `skill-forge.json`.
- Reapply the current matching blueprint by ID when available.
- Generate an upgrade candidate into a separate package directory.
- Validate the candidate and display old/new quality scores.
- Display diff guidance for comparing the original Skill and candidate.
- Reject upgrades for packages without provenance metadata.
- Reject upgrades when the recorded blueprint is missing.
- Reject upgrades when the candidate package already exists unless `--force` is provided.
- Do not overwrite the source Skill package.

## Capabilities

### New Capabilities

- `skill-upgrade-workflow`: Deterministic upgrade candidate generation for existing generated Skill packages.

### Modified Capabilities

- `skill-library-management`: Generated Skill library workflows include upgrade candidate packages as normal generated packages that can be shown and diffed.

## Impact

- Affected CLI:
  - New `skill-forge upgrade <skill-name>`
  - New `--candidate-name`
  - New `--force`
- Affected modules:
  - New `src/skill_forge/upgrade/`
  - `src/skill_forge/cli.py`
  - `src/skill_forge/library/manager.py`
  - `src/skill_forge/models/`
- Affected tests:
  - New `tests/test_skill_upgrade.py`
  - CLI tests for success, missing provenance, missing blueprint, and existing candidate behavior
- No new third-party dependencies are expected.
