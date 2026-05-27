## 1. Validation Models and Module Structure

- [x] 1.1 Add validation model module with `ValidationIssue` and `ValidationResult`.
- [x] 1.2 Add validator package/module for reusable Skill package validation.
- [x] 1.3 Define stable validation issue codes for missing directory, missing `SKILL.md`, missing frontmatter, missing metadata, and missing recommended sections.

## 2. Skill Validator

- [x] 2.1 Implement validation for missing or non-directory Skill paths.
- [x] 2.2 Implement validation for missing `SKILL.md`.
- [x] 2.3 Parse `SKILL.md` frontmatter with `python-frontmatter`.
- [x] 2.4 Report errors for missing `name`, missing `description`, and empty description.
- [x] 2.5 Report warnings for missing recommended sections.
- [x] 2.6 Return structured `ValidationResult` with separate errors and warnings.

## 3. Installer Module

- [x] 3.1 Add installer package/module with source package lookup by skill name.
- [x] 3.2 Resolve generated package source path from configured output directory.
- [x] 3.3 Resolve opencode project and user destination paths.
- [x] 3.4 Resolve Claude project and user destination paths.
- [x] 3.5 Resolve Codex project and user destination paths.
- [x] 3.6 Copy entire Skill package directory to the destination.
- [x] 3.7 Fail clearly when the generated source package does not exist.
- [x] 3.8 Prevent overwrite by default and support forced overwrite.

## 4. CLI Integration

- [x] 4.1 Add `skill-forge validate <skill-path>` command.
- [x] 4.2 Display validation errors and warnings clearly.
- [x] 4.3 Return non-zero exit code when validation has errors.
- [x] 4.4 Add `skill-forge install <skill-name> --target <codex|opencode|claude> --scope <project|user>` command.
- [x] 4.5 Add `--force` support for install overwrite.
- [x] 4.6 Load config and resolve output/user platform paths for install.
- [x] 4.7 Display installed destination path on success.
- [x] 4.8 Return non-zero exit code for missing source or existing destination without force.

## 5. Tests

- [x] 5.1 Add validator tests for valid generated packages.
- [x] 5.2 Add validator tests for missing directory, missing `SKILL.md`, and missing frontmatter.
- [x] 5.3 Add validator tests for missing metadata and recommended section warnings.
- [x] 5.4 Add installer tests for opencode, Claude, and Codex path resolution.
- [x] 5.5 Add installer tests for successful copy, missing source failure, no-overwrite, and force overwrite.
- [x] 5.6 Add CLI tests for `validate` success and failure.
- [x] 5.7 Add CLI tests for `install` success, missing source, existing destination, and force overwrite.
- [x] 5.8 Run the test suite and fix failures for this change.

## 6. Documentation and Verification

- [x] 6.1 Confirm the local MVP sequence works in an isolated home: `init`, `create`, `validate`, and `install`.
- [x] 6.2 Confirm `install java-bug-investigation --target opencode --scope project` creates `./.opencode/skills/java-bug-investigation/SKILL.md` in an isolated project directory.
- [x] 6.3 Confirm `openspec validate add-validation-and-installation --strict` passes.
- [x] 6.4 Update `docs/openspec_change_plan.md` to mark `add-validation-and-installation` progress.
