## Context

Generated Skill packages live under the configured create output directory, typically `~/.skill-forge/output/<skill-name>/`. Each package should contain `SKILL.md` with YAML frontmatter. The existing CLI already resolves `--home`, writes default config, and computes the configured output directory for create. Library commands can reuse that path resolution and inspect the file system directly.

## Goals / Non-Goals

**Goals:**

- List generated Skill package directories containing `SKILL.md`.
- Show package metadata and attachment counts for a selected generated Skill.
- Diff two generated `SKILL.md` files with a unified diff.
- Return clear non-zero errors for missing Skills or missing `SKILL.md`.
- Keep output deterministic and testable.

**Non-Goals:**

- No persistent library database.
- No remote marketplace.
- No automatic upgrades or repairs.
- No changes to generation quality scoring.
- No recursive diff of every attachment file in this slice.

## Decisions

1. Implement file-system based library discovery.

   Rationale: generated packages already exist as directories under output. A database would add migration and consistency concerns without current benefit.

   Alternative considered: record every generated package at create time. That would miss existing output directories and couple library management to generation internals.

2. Parse `SKILL.md` frontmatter for metadata.

   Rationale: `name` and `description` are canonical Skill metadata today, and `python-frontmatter` is already used by validation.

   Alternative considered: infer metadata only from directory names. That is useful as fallback but loses description and target package identity.

3. Use unified diffs for `diff`.

   Rationale: `difflib.unified_diff` is deterministic, dependency-free, and familiar for comparing text files.

   Alternative considered: render side-by-side rich tables. That is harder to test and less useful for command-line copy/paste.

4. Reuse configured output path resolution.

   Rationale: library commands should inspect the same output directory used by `create`, including test `--home` overrides.

## Risks / Trade-offs

- Packages with malformed frontmatter may be hard to inspect -> fall back to directory name where possible and keep `show` errors focused on missing package or missing `SKILL.md`.
- A top-level command named `list` may overlap with shell/common terms -> it is simple and matches the roadmap; Typer supports it directly.
- Diff only covers `SKILL.md` -> sufficient for first slice and keeps attachment comparison out of scope.
