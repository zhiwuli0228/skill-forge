# Schema: `skill-forge-governance`

`skill-forge-governance` is the project-local OpenSpec schema for `skill-forge`. It defines the structured change artifacts and the order in which they must be produced.

This schema is an extension of the default `spec-driven` schema. It adds three artifacts that the default schema does not have:

- `brainstorm` — clarification of the problem before any artifact is written.
- `review` — cross-artifact consistency check between design and plan.
- `verification` — evidence record produced at the end of implementation.

The eight artifacts are produced in the order:

```text
brainstorm  ->  proposal  ->  spec  ->  design  ->  review  ->  plan  ->  tasks  ->  verification
```

`brainstorm` is optional for trivial changes. The other seven are required for any non-trivial change.

## Governance model

```text
OpenSpec                          — owns lifecycle (artifact order, status transitions)
SuperSpec-style schema (this one) — owns structured change artifacts
Superpowers                      — owns execution discipline (TDD, debugging, verification)
Project Harness (Skill Forge)     — owns Skill Forge-specific constraints
```

The four layers are additive. A change that satisfies Superpowers but violates the Project Harness is still wrong. A change that satisfies the schema but skips verification is still not done.

## Where the schema lives

This schema is checked into the repository under `openspec/schemas/skill-forge-governance/`. The schema is referenced from `openspec/config.yaml` by setting `schema: skill-forge-governance`. The OpenSpec CLI resolves the schema from the project, not from the package default.

## Files in this schema

```text
openspec/schemas/skill-forge-governance/
├── README.md           # this file
├── schema.yaml         # OpenSpec schema definition (artifacts, requires, apply)
└── templates/
    ├── brainstorm.md
    ├── proposal.md
    ├── spec.md
    ├── design.md
    ├── review.md
    ├── plan.md
    ├── tasks.md
    └── verification.md
```

## How to start a change

From the repository root:

```bash
openspec new --change <change-id> --schema skill-forge-governance
```

OpenSpec will scaffold the change folder under `openspec/changes/<change-id>/` with empty files for each artifact. Fill the artifacts in the order listed above. Use the templates in `templates/` as the starting point for each artifact.

## How to verify a change

Before archiving, run:

```bash
openspec validate <change-id> --strict
openspec status <change-id>
```

Both commands must pass. A change that does not pass `validate --strict` cannot be archived.

## Versioning

This schema follows OpenSpec's schema versioning. The current version is `1`. Bumping the major version requires:

- A change proposal under `openspec/changes/`.
- A migration plan in `docs/03-openspec/change-workflow.md` for any in-flight changes.
- An entry in the verification report of the bumping change.
