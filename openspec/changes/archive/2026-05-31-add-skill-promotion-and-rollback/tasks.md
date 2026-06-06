## 1. Promotion and Rollback Models and Storage

- [x] 1.1 Define promotion registry, history entry, and result models under `src/skill_forge/lifecycle/`.
- [x] 1.2 Add a local promotions directory to `SkillForgePaths` and create it with the workspace directories.
- [x] 1.3 Implement a promotion service that snapshots the current active package before copying a candidate into place.
- [x] 1.4 Implement rollback logic that restores a recorded snapshot by version label.

## 2. CLI Integration

- [x] 2.1 Add `skill-forge promote <candidate-name>` to the CLI.
- [x] 2.2 Add `skill-forge rollback <skill-name> --to <version-name>` to the CLI.
- [x] 2.3 Render promotion and rollback summaries with source, target, snapshot, and registry details.

## 3. Tests and Validation

- [x] 3.1 Add focused tests for promotion success, missing candidate failure, and source preservation.
- [x] 3.2 Add focused tests for rollback success, missing history failure, and snapshot preservation.
- [x] 3.3 Add CLI tests for promote and rollback output and read-only candidate preservation.
- [x] 3.4 Run focused tests for lifecycle, CLI, and installer behavior.
- [x] 3.5 Run the full test suite.
- [x] 3.6 Run `openspec validate \"add-skill-promotion-and-rollback\" --strict`.
- [x] 3.7 Update the lifecycle governance plan with implementation progress and next-step status.
