## 1. Project Context Models

- [x] 1.1 Add project context models for scanned files, skipped files, detected tools, detected rules, summary text, and derived constraints.
- [x] 1.2 Define scanning defaults for supported files/directories, ignored directories, per-file size limit, and total character limit.
- [x] 1.3 Add tests for model defaults and deterministic ordering assumptions.

## 2. Project Context Reader

- [x] 2.1 Implement a reader that scans supported project files and directories under a provided project path.
- [x] 2.2 Skip binary files, oversized files, dependency/build outputs, and unsupported paths.
- [x] 2.3 Enforce deterministic file ordering and total character limits.
- [x] 2.4 Add tests for supported file detection, skipped file reporting, binary/large file handling, and total limit behavior.

## 3. Summary And Constraint Extraction

- [x] 3.1 Implement deterministic detection for OpenSpec, opencode, Claude, Codex, and AGENTS-style project tooling.
- [x] 3.2 Implement rule extraction for OpenSpec workflow, testing requirements, avoiding unrelated changes, and bounded implementation scope.
- [x] 3.3 Convert detected rules into concise Skill constraints.
- [x] 3.4 Deduplicate project-derived constraints against existing requirement constraints.
- [x] 3.5 Add tests for summary generation, rule detection, constraint conversion, and deduplication.

## 4. Create And Draft Integration

- [x] 4.1 Add `--project <path>` to `skill-forge create`.
- [x] 4.2 Enrich non-interactive create requirements with project-derived constraints before generation.
- [x] 4.3 Enrich interactive create drafts with project path and project context summary before wizard execution.
- [x] 4.4 Ensure resume keeps stored project context data without rescanning by default.
- [x] 4.5 Add CLI tests for non-interactive project-aware generation and interactive draft persistence.

## 5. Verification And Tracking

- [x] 5.1 Run `uv run pytest`.
- [x] 5.2 Run `openspec.cmd validate "add-project-context-generation" --strict`.
- [x] 5.3 Run an isolated `skill-forge create "<requirement>" --project <fixture>` verification.
- [x] 5.4 Update `docs/openspec_change_plan.md` with proposal progress.
