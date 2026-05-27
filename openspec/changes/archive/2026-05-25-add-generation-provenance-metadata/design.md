## Context

Skill Forge already returns runtime package metadata through `GeneratedSkillPackage`, and the CLI computes a post-generation quality report after writing the package. That information is currently transient. The local library manager reconstructs package metadata from `SKILL.md` and file counts, so it cannot answer how a package was generated.

This change adds a durable, package-local metadata file:

```text
<skill-name>/
├── SKILL.md
├── skill-forge.json
└── references/
```

## Goals / Non-Goals

**Goals:**

- Persist generation provenance for newly generated packages.
- Include enough metadata for inspection, diffing, future evals, and future upgrade workflows.
- Keep older packages without `skill-forge.json` fully manageable by `list`, `show`, and `diff`.
- Avoid storing full project context content or sensitive source files.

**Non-Goals:**

- Do not implement `upgrade`.
- Do not implement historical version management.
- Do not store full prompts, LLM responses, or project context text.
- Do not make generated packages invalid when metadata is missing.

## Decisions

1. Write metadata after validation and quality report generation.

   Rationale: The quality score and status are not known until after validation. Writing metadata after validation also lets the file include generated attachment manifests from `GeneratedSkillPackage`.

   Alternative considered: Write metadata inside `SkillGenerator.generate`. That would centralize package writes but cannot include the final quality report without making the generator responsible for validation.

2. Use a Pydantic model with `schema_version`.

   Rationale: Provenance data will evolve. A schema version gives later upgrade/eval changes a stable compatibility branch.

3. Store only bounded provenance.

   Metadata should include:

   ```text
   schema_version
   generated_at
   skill_name
   requirement_text
   target_platform
   language
   task_type
   blueprint_id
   blueprint_source
   llm_enabled
   project_context_path
   quality_score
   quality_status
   references/assets/scripts
   ```

   Rationale: This is enough to explain generation without persisting full project context or LLM responses.

4. Track applied blueprint details on `SkillRequirement`.

   Rationale: After enrichment, CLI generation needs to know which blueprint actually applied. Storing applied blueprint ID/source on the requirement keeps metadata creation straightforward across automatic and explicit selection.

5. Make library metadata optional.

   Rationale: Existing packages predate this feature. `show` should display `-` for missing provenance fields, and `diff` should still compare `SKILL.md`.

## Risks / Trade-offs

- Requirement text may contain sensitive details → Mitigation: keep only the original user-provided requirement string and avoid storing project file contents or LLM responses.
- Metadata can become stale if users manually edit `SKILL.md` → Mitigation: metadata is explicitly generation provenance, not a live content checksum in this change.
- `diff` output can become noisy → Mitigation: keep metadata diff separate and only emit it when both or either metadata file differs.

## Migration Plan

No migration is required. New packages get `skill-forge.json`; old packages continue to work without it.

Rollback is straightforward: stop writing metadata and keep library manager fallbacks for missing metadata.
