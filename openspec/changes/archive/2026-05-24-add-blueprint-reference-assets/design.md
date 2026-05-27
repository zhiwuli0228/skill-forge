## Context

The generator currently writes:

```text
<skill-name>/
└── SKILL.md
```

`GeneratedSkillPackage` already has `references`, `assets`, and `scripts` metadata fields, but they are unused. Built-in blueprints are YAML data and can now be selected automatically or explicitly before generation.

This change introduces a minimal attachment mechanism driven by blueprint data.

## Goals / Non-Goals

**Goals:**

- Add blueprint-declared generated files.
- Support `references`, `assets`, and `scripts` groups in the blueprint model.
- Write declared files into the generated Skill package.
- Prevent absolute paths and `..` path traversal.
- Keep no-attachment blueprints producing only `SKILL.md`.

**Non-Goals:**

- Do not add Jinja templating for attachment content.
- Do not generate files through LLM output.
- Do not add quality scoring.
- Do not add user-defined blueprint directories.
- Do not add rich validation for attachment semantics beyond path safety.

## Decisions

### Store attachment content inline in blueprint YAML

The initial model will use:

```yaml
references:
  - path: references/checklist.md
    content: |
      # Checklist
      ...
```

This keeps the implementation simple and avoids introducing a second template directory or copy mechanism.

Alternative considered: store attachment templates as separate files. That is more scalable, but it adds packaging and path resolution complexity before the feature shape is proven.

### Attach blueprint data to `SkillRequirement`

Generation already receives a `SkillRequirement`, not the selected blueprint. The blueprint enricher will copy declared file specs into new requirement fields, and `SkillGenerator` will write them.

Alternative considered: change `SkillGenerator.generate` to accept a blueprint. That would spread blueprint concerns across the CLI and generator and complicate non-blueprint fallback.

### Validate relative paths in model and generator

The model should reject obviously unsafe paths, and the generator should still resolve each output path and ensure it remains inside the package directory. This gives defense in depth for future user-defined blueprint sources.

## Risks / Trade-offs

- Inline content can make YAML files long. Mitigation: this change only adds a small first reference file; separate template files can be added later if needed.
- Mutating `SkillRequirement` with file declarations expands its scope. Mitigation: the model already has `references_needed`, `assets_needed`, and `scripts_needed`; this change adds concrete declared files to match existing generated package metadata.
- Validators could overreach into attachment requirements. Mitigation: this change validates only path safety and leaves content quality for later changes.
