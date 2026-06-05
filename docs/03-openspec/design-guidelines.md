# Design Guidelines

A `design.md` file explains HOW a change will be implemented. It is the bridge between the proposal/spec (the "what") and plan/tasks (the "executable contract"). Design is about architecture, not line-by-line edits.

This document collects the writing rules for design docs. The structural rules are in `artifact-rules.md`; the schema-enforced rules are in `openspec/schemas/skill-forge-governance/schema.yaml` and `openspec/schemas/skill-forge-governance/templates/design.md`.

## 1. When a Design Doc Is Required

A design doc is required for any change that meets one or more of:

- Touches more than one module under `src/skill_forge/`.
- Changes a data contract (config, blueprint, validation result, package metadata, provenance).
- Adds a new module or removes an existing one.
- Changes the public CLI surface.
- Has multiple reasonable implementation approaches that a reviewer would want to compare.

A design doc is optional (but recommended) for changes that are single-file, single-module, and do not change any data contract. The drafter can skip it; the reviewer may still request it.

## 2. Voice and Length

Design docs are written for an implementation agent that will produce `plan.md` and `tasks.md`. The reader is not the user. The reader is the implementer.

Design docs are typically 2-4 pages. They are longer than proposals because they cover architecture. They are shorter than `plan.md` because they describe decisions, not executable steps.

## 3. `## Context`

`## Context` is the background. It states:

- The current state of the relevant code or system. Cite files by path.
- The constraints that bound the design (e.g., backward compatibility, performance budget, security requirements).
- The stakeholders (which agents, which users, which other systems are affected).

A design doc that starts with a long history of the project is in the wrong tone. State the current state, not the project history.

## 4. `## Goals / Non-Goals`

`## Goals` is a bullet list of what the design achieves. Restate the proposal's `## What Changes` in design language.

`## Non-Goals` is a bullet list of what the design explicitly does NOT achieve. Restate the proposal's `## Non-Goals`. A reviewer will check the design's non-goals against the proposal's non-goals; they must be consistent.

## 5. `## Decisions`

`## Decisions` is the most important section. It is a list of key technical choices, each in the format:

```markdown
### Decision N: <title>

- **Decision**: <what we will do>
- **Rationale**: <why this over the alternatives>
- **Alternatives considered**: <what we rejected and why>
```

Rules:

- One decision per heading. If a heading covers two choices, split it.
- The decision is a single sentence or a short paragraph. "We will use a state machine with three states: pending, active, archived." Not "We will think about state machines."
- The rationale is one or two paragraphs. It explains WHY this is the right choice.
- The alternatives list is explicit. "We considered X and Y. X is rejected because [reason]. Y is rejected because [reason]."

A design with only one decision is suspicious. Either the design is trivial, or the other decisions are hidden and need to be made explicit.

## 6. `## Data Contracts`

`## Data Contracts` shows the shape of every schema that changes. Skip the section if no schemas change.

For each schema:

```markdown
### `<schema-name>` (e.g., `skill-forge.json`, `eval-report.json`, `config.yaml`)

\`\`\`yaml
# Before
<old shape>

# After
<new shape with field-level comments>
\`\`\`
```

Rules:

- One subsection per schema.
- The before/after pair makes the change reviewable without re-reading the code.
- New fields are commented. Removed fields are listed in a `### Removed fields` subsection under the schema.

## 7. `## Module Boundaries`

`## Module Boundaries` is a categorized list:

- **Added**: new modules (with their purpose).
- **Modified**: existing modules that are touched (with what changes).
- **Untouched**: existing modules that are deliberately left alone (with why).

A reviewer uses this section to confirm the change did not expand. If a module is listed as "Untouched" and the change's diff shows it being modified, the design is wrong.

## 8. `## Compatibility Impact`

`## Compatibility Impact` covers the effect on the four audiences:

- Claude Code: how the change affects Claude Code's implementation entry.
- Codex: how the change affects Codex's planning entry.
- opencode: how the change affects opencode's fallback entry.
- Generated Skill packages: how the change affects already-generated packages.

For each, state the effect (none, additive, breaking) and the user-visible signal.

## 9. `## Offline and Deterministic Mode`

Skill Forge is local-first and deterministic by default. The design must state the behavior under:

- Network unavailable: the user is offline.
- LLM disabled: `--no-llm` is passed.
- LLM enabled but config missing: required env vars are not set.

For each, state the behavior (fallback, error, default). If the design does not change the behavior under any of these, say so explicitly.

## 10. `## Security and Filesystem`

`## Security and Filesystem` lists:

- **Reads**: paths the change reads, and under which conditions (which file or env var triggers the read).
- **Writes**: paths the change writes, and under which conditions.
- **Environment variables**: variables that influence behavior, and the effect of each value.

A reviewer uses this section to confirm the change does not read or write unexpected paths. A change that reads `~/.ssh/` or writes outside `~/.skill-forge/` is a security red flag.

## 11. `## Risks / Trade-offs`

`## Risks / Trade-offs` is a list of known limitations. Format: `[Risk] -> [mitigation]`.

Rules:

- Risks are stated as the failure mode, not the cause. "If the corpus is empty, search returns no results" is a risk. "Corpus could be empty" is a cause.
- Mitigations are concrete. "Add a check at the start of search" is a mitigation. "We will handle it" is not.

## 12. `## Migration Plan`

`## Migration Plan` is two sub-sections:

- **Deploy**: the steps to roll the change out.
- **Rollback**: the steps to revert.

For a doc-only change, both are usually trivial. For a schema change, both involve bumping versions. For a runtime change, both involve code paths and possibly user data.

A design with no rollback is a design that cannot be safely merged.

## 13. `## Open Questions`

`## Open Questions` is a list of outstanding decisions or unknowns, each tagged `[blocking]` or `[non-blocking]`. A blocking question means the design is not finished; the design cannot move to review until the question is answered.

A design with no open questions is the norm for a small change. A large or cross-cutting change typically has 2-5 open questions, most of them non-blocking.

## 14. Common Mistakes

- **The design is a code walkthrough.** Move the walkthrough to `plan.md`. The design describes decisions, not code.
- **The design duplicates the proposal or spec.** Reference them by section. Do not restate.
- **A decision is hidden in the rationale of another decision.** Surface it as its own `### Decision N`.
- **Data contracts are described in prose.** Show the YAML before/after.
- **Risks are stated as causes, not failure modes.** State the failure mode.
- **The migration plan is missing.** A design without a deploy/rollback plan is not safe to merge.

## 15. Reviewer Checklist

A reviewer should be able to answer "yes" to all of the following:

- Does `## Context` cite the affected files by path?
- Are goals and non-goals consistent with the proposal?
- Does each decision have a rationale and explicit alternatives?
- Does `## Data Contracts` show before/after for every changed schema?
- Are modules categorized as Added / Modified / Untouched?
- Is the compatibility impact stated for all four audiences?
- Is the offline / deterministic / LLM-disabled behavior explicit?
- Are reads, writes, and env vars listed?
- Are risks stated as failure modes with concrete mitigations?
- Are deploy and rollback steps present?

If any answer is "no", the design needs another draft.
