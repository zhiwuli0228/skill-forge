# Spec Guidelines

A `spec.md` file (one per capability) defines the observable behavior of the change. It uses `### Requirement:` and `#### Scenario:` headings, and SHALL/MUST-style normative language. Specs are the contract that verification checks against.

This document collects the writing rules for specs. The structural rules are in `artifact-rules.md`; the schema-enforced rules are in `openspec/schemas/skill-forge-governance/schema.yaml` and `openspec/schemas/skill-forge-governance/templates/spec.md`.

## 1. What a Spec Is

A spec is a list of requirements. Each requirement is a single, observable behavior of the system. Each requirement is paired with at least one scenario, which is a concrete test case (the `WHEN` / `THEN` pair).

A spec is NOT:

- A list of implementation tasks.
- A list of internal design choices.
- A list of best practices or recommendations.

When a sentence in a spec describes how the implementation works, it is in the wrong file. Move it to `design.md`.

## 2. The `# <Capability Name> Specification` Heading

The first line is `# <Capability Name> Specification`. The capability name is in title case; the kebab-case form is in the file path and in the `## Capabilities` section of the proposal.

Examples:

- `# User Auth Specification` (file: `specs/user-auth/spec.md`)
- `# Skill Lifecycle Recommendation Specification` (file: `specs/skill-lifecycle-recommendation/spec.md`)

## 3. The `## Purpose` Section

`## Purpose` is 1-2 sentences. It states what the capability is for. It is restated in the proposal's `### New Capabilities` description.

`## Purpose` does not contain "and". If it does, the capability is two capabilities.

## 4. Delta Operations: ADDED, MODIFIED, REMOVED, RENAMED

A spec for a change uses delta operations. The order, when multiple are present, is:

```text
## ADDED Requirements
## MODIFIED Requirements
## REMOVED Requirements
## RENAMED Requirements
```

### ADDED Requirements

New requirements introduced by the change. Format:

```markdown
## ADDED Requirements

### Requirement: <name>

The system SHALL <observable behavior>.

#### Scenario: <scenario name>

- **WHEN** <trigger>
- **THEN** <observable outcome>
```

### MODIFIED Requirements

Existing requirements whose behavior is changing. **The full updated content must appear under this header.** A partial diff loses detail at archive time.

```markdown
## MODIFIED Requirements

### Requirement: <name>  (header text must match the original requirement name)

The system SHALL <updated observable behavior>.   (full updated text)

#### Scenario: <scenario name>  (full updated scenario text)

- **WHEN** <trigger>
- **THEN** <observable outcome>
```

Pitfall: putting only the changed lines under `## MODIFIED Requirements`. The archive step will overwrite the original with what you wrote, which loses the unchanged parts. Always copy the FULL requirement (from `### Requirement:` through all scenarios) and edit.

### REMOVED Requirements

Existing requirements being retired. Each must include a `**Reason**` and a `**Migration**`:

```markdown
## REMOVED Requirements

### Requirement: <name>

**Reason**: <why this requirement is being removed>
**Migration**: <how existing users or systems should adapt>
```

### RENAMED Requirements

Requirements whose name is changing without a behavior change. Use `**FROM**` / `**TO**` format:

```markdown
## RENAMED Requirements

### Requirement: <new name>

**FROM**: <old name>
**TO**: <new name>
```

## 5. Requirements

A requirement is a single, observable behavior. Format:

```markdown
### Requirement: <name>

The system SHALL <observable behavior>.
```

Rules:

- Use `SHALL` or `MUST` for normative requirements. Avoid `should` and `may` for normative behavior; reserve them for non-normative guidance that does not belong in a spec.
- The requirement name is short and stable. It is the identifier. Do not put verbs in the name.
- One observable behavior per requirement. If the requirement has two behaviors, it is two requirements.
- The requirement name must match the original (case-insensitive, whitespace-insensitive) for `MODIFIED Requirements`.

## 6. Scenarios

A scenario is a concrete test case. Format:

```markdown
#### Scenario: <scenario name>

- **WHEN** <trigger>
- **THEN** <observable outcome>
```

Rules:

- Use exactly four hashtags (`####`). Three hashtags will be parsed as a requirement, not a scenario, and will fail silently.
- The `**WHEN**` is a precondition or trigger.
- The `**THEN**` is an observable outcome. It is what a test would assert.
- A scenario may have additional `**AND**` lines for multi-step outcomes.
- Every requirement must have at least one scenario.

## 7. Distinguishing Internal Behavior from Generated Skill Behavior

Skill Forge has two layers:

- The CLI's internal behavior (how `skill-forge create` works, how validation runs, etc.).
- The generated Skill package's behavior (what the SKILL.md instructs an Agent to do, how the package is consumed by Codex / opencode / Claude Code).

Spec requirements must make this distinction clear. A requirement about CLI behavior is phrased as "the system SHALL". A requirement about generated Skill behavior is phrased as "generated packages SHALL" or "the generated SKILL.md SHALL".

The distinction matters for verification: internal behavior is verified by `pytest`. Generated Skill behavior is verified by `eval-report.json` and by `validate`.

## 8. Implementation Details

Do not encode implementation details as requirements unless they are externally observable.

- Externally observable: CLI output, artifact schema, exit code, side effect on disk, behavior in the face of missing config, time/space bound that the user can measure.
- Internally observable only: function names, module paths, internal data structures, the order of internal calls.

If a constraint is internal, it goes in `design.md`, not in the spec.

## 9. Common Mistakes

- **The spec describes the implementation.** Move to design.
- **The spec uses `should` or `may` for normative behavior.** Replace with SHALL or MUST.
- **A scenario is missing the `**WHEN**` or `**THEN**`.** Both are required.
- **Scenarios use three hashtags instead of four.** Will fail silently.
- **`MODIFIED Requirements` are partial diffs.** Include the full updated content.
- **A requirement is not observable.** Replace with a testable statement.
- **The spec mixes CLI behavior and generated Skill behavior without distinction.** Use "the system SHALL" vs "generated packages SHALL".

## 10. Reviewer Checklist

A reviewer should be able to answer "yes" to all of the following:

- Does the heading match the capability name (kebab-case in path, title case in heading)?
- Is the `## Purpose` section 1-2 sentences?
- Are the delta operations in the correct order?
- Does every requirement use SHALL or MUST?
- Does every requirement have at least one scenario with `**WHEN**` and `**THEN**`?
- Are scenarios using exactly four hashtags?
- For `MODIFIED Requirements`, is the full updated content present?
- For `REMOVED Requirements`, are `**Reason**` and `**Migration**` present?
- Is the spec free of implementation details that are not externally observable?

If any answer is "no", the spec needs another draft.
