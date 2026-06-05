# Design: <change-id>

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, spec.md

## Context

<!-- Background, current state, constraints, stakeholders. Cite files by path. -->

## Goals / Non-Goals

### Goals

- <goal>

### Non-Goals

- <non-goal> (restate from proposal.md)

## Decisions

<!-- Key technical choices. Format: Decision / Rationale / Alternatives. -->

### Decision 1: <title>

- **Decision**: <what we will do>
- **Rationale**: <why this over the alternatives>
- **Alternatives considered**: <what we rejected and why>

### Decision 2: <title>

- **Decision**: <what we will do>
- **Rationale**: <why this over the alternatives>
- **Alternatives considered**: <what we rejected and why>

## Data Contracts

<!-- For each schema that changes, show the new shape.
     Skip this section if no schema changes. -->

### `<schema-name>` (e.g., `skill-forge.json`, `eval-report.json`, `config.yaml`)

```yaml
# Before
<old shape>

# After
<new shape with field-level comments>
```

## Module Boundaries

<!-- New modules added, existing modules touched, modules left untouched. -->

### Added

- `<module path>`: <purpose>

### Modified

- `<module path>`: <what changes>

### Untouched

- `<module path>`: <why not touched>

## Compatibility Impact

<!-- Effect on Claude Code, Codex, opencode, and generated Skill packages. -->

- Claude Code: <effect>
- Codex: <effect>
- opencode: <effect>
- Generated Skill packages: <effect>

## Offline and Deterministic Mode

<!-- Behavior when network is unavailable or the user opts out of LLM refinement. -->

- Network unavailable: <behavior>
- LLM disabled: <behavior>
- LLM enabled but config missing: <behavior>

## Security and Filesystem

<!-- Paths read, paths written, environment variables that matter. -->

- Reads: <paths and which file or which env var>
- Writes: <paths and under which conditions>
- Environment variables: <name> -> <effect>

## Risks / Trade-offs

<!-- Known limitations. Format: [Risk] -> Mitigation. -->

- [Risk] -> [mitigation]
- [Risk] -> [mitigation]

## Migration Plan

<!-- Steps to deploy, steps to rollback. -->

### Deploy

1. <step>
2. <step>

### Rollback

1. <step>
2. <step>

## Open Questions

<!-- Outstanding decisions or unknowns. Each marked blocking / non-blocking. -->

- [blocking] <question>
- [non-blocking] <question>
