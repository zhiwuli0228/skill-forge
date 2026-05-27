## 1. OpenSpec Artifacts

- [x] 1.1 Create proposal, design, specs, and task checklist for local Skill library management.

## 2. Library Reader

- [x] 2.1 Add a library module that discovers generated Skill packages under the configured output directory.
- [x] 2.2 Add metadata extraction from `SKILL.md` frontmatter and attachment counts.
- [x] 2.3 Add unified diff support for generated `SKILL.md` files.
- [x] 2.4 Add unit tests for listing, showing, missing packages, diff, and no-difference diff behavior.

## 3. CLI Integration

- [x] 3.1 Add `skill-forge list` with `--home` support and empty-library output.
- [x] 3.2 Add `skill-forge show <skill-name>` with `--home` support and missing-package errors.
- [x] 3.3 Add `skill-forge diff <skill-a> <skill-b>` with `--home` support and missing-package errors.
- [x] 3.4 Add CLI tests for the new library commands against isolated generated packages.

## 4. Verification

- [x] 4.1 Run automated tests and strict OpenSpec validation.
