## Context

Skill Forge already persists the facts needed to judge a Skill's health: generation provenance, content quality metrics, eval reports, upgrade candidates, and local experience rules. Today those facts are distributed across separate commands and files, so the user has to synthesize the current state manually. This change introduces a read-only lifecycle index that turns those facts into a single status view before any recommendation or promotion logic is added.

The design must stay local, deterministic, and lightweight. It should not introduce a new source of truth or mutate existing packages.

## Goals / Non-Goals

**Goals:**

- Aggregate provenance, quality, eval, and experience facts into a single lifecycle summary for one generated Skill.
- Provide a `skill-forge lifecycle show <skill-name>` command that explains the lifecycle state and the evidence behind it.
- Classify Skills into a small deterministic set of lifecycle states.
- Handle missing facts gracefully and still return a useful summary.

**Non-Goals:**

- No recommendation engine.
- No promote or rollback flow.
- No file mutation or automated repair.
- No LLM involvement.

## Decisions

1. **Make the lifecycle index read-only and derived**

   The index will be computed on demand from existing local files instead of being stored as a separate persistent database. This keeps the first increment simple, avoids synchronization problems, and ensures the lifecycle view always reflects the current package state.

   Alternatives considered:
   - Persist a separate lifecycle cache. Rejected because it would add invalidation complexity and duplicate the source of truth.
   - Rebuild lifecycle state inside `show` only. Rejected because the logic needs to be reusable by later recommendation and promotion changes.

2. **Centralize lifecycle aggregation in a dedicated service**

   Introduce a new `LifecycleService` under `src/skill_forge/lifecycle/` that reads provenance, eval, quality, and experience evidence and returns a structured lifecycle summary. The CLI should only render the summary, not compute it inline.

   Alternatives considered:
   - Embed lifecycle logic into `library.manager`. Rejected because lifecycle crosses package discovery, eval, and experience concerns.
   - Add logic directly to the CLI command. Rejected because it would be hard to test and reuse.

3. **Use a small deterministic state model**

   The first version should expose a compact status set such as `healthy`, `needs-eval`, `needs-upgrade`, and `regressed`, plus an optional `unknown` fallback when too much information is missing. The state must be easy to reason about and stable across repeated runs.

   Alternatives considered:
   - Expose many fine-grained states. Rejected because it would be difficult for users to interpret and would complicate the next recommendation step.
   - Use a score-only model. Rejected because a single numeric score would be less actionable than a labeled state with evidence.

4. **Treat provenance, eval, quality, and experience as evidence sources, not separate UX sections**

   The summary should show which facts drove the result and a brief reason string for each. This keeps the output explainable without forcing users to navigate each underlying file separately.

   Alternatives considered:
   - Expose raw file contents. Rejected because it would be noisy and redundant with existing commands.
   - Hide the evidence and show only a final label. Rejected because the next change depends on explainability.

5. **Preserve existing commands unchanged**

   This change adds lifecycle visibility without changing `show`, `list`, `diff`, or `upgrade`. The new command should be additive so it can ship without breaking current workflows.

   Alternatives considered:
   - Merge lifecycle fields into `show`. Rejected because it would overload an already dense command and make the first lifecycle step harder to isolate.

## Risks / Trade-offs

- [State drift] If lifecycle logic is duplicated between the service and later recommendation code, the two could diverge. → Keep the first change focused on a single service that future changes can reuse.
- [Too many labels] If the state taxonomy becomes too detailed, users will not know how to interpret it. → Limit the first change to a small set of states.
- [Evidence overload] If the summary includes every raw signal, the command becomes noisy. → Show concise reasons and only the most relevant facts.
- [Missing facts] Many packages will not have a full set of provenance, eval, or experience data. → Define a clear fallback state and treat missing facts as a valid input, not an error.

## Migration Plan

No data migration is required. The lifecycle index is derived from existing files under the generated Skill package and the local experience store. If the command is removed later, no persisted lifecycle state needs to be cleaned up.

## Open Questions

- Should the first lifecycle state taxonomy include `healthy_with_warnings`, or is that better reserved for the recommendation layer?
- Should `lifecycle show` also surface the installed target platform, or keep the first version focused on package-level health?
- Should the second change reuse the same state model verbatim, or derive recommendation labels from it?
