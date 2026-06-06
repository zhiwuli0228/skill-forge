## Context

The lifecycle index and recommendation layers already answer whether a Skill is healthy and what action should happen next. What remains is the irreversible-looking part of the workflow: promoting a candidate into an active package and, if needed, rolling back to a previous known-good version.

This change must stay local, deterministic, and reversible. It should not introduce a remote release system, and it should not overwrite the only copy of a previous package version.

## Goals / Non-Goals

**Goals:**

- Promote a candidate package into an active target package while preserving rollback history.
- Restore a previous version snapshot with a deterministic rollback command.
- Keep promotion provenance and history local and inspectable.
- Preserve the source candidate package during promotion and rollback.

**Non-Goals:**

- No remote publishing or marketplace sync.
- No install flow changes beyond what users may do after promotion.
- No LLM involvement.
- No attempt to re-derive or rewrite lifecycle recommendations.

## Decisions

1. **Use a local promotion registry and package snapshots**

   The service will store promotion history under the Skill Forge home directory and keep rollback snapshots as copied package directories. This avoids rewriting source packages in place and gives rollback a concrete target to restore from.

   Alternatives considered:
   - Overwrite the active package without history. Rejected because rollback would have no reliable source.
   - Encode the history only inside package files. Rejected because it would mutate package content and blur the boundary between the package and its operational history.

2. **Treat promotion as a copy operation, not a move**

   Promotion will copy the candidate package into the active target path and preserve the candidate package as-is. This makes the candidate reusable for future comparisons or promotions and avoids destroying the source evidence.

   Alternatives considered:
   - Move the candidate into place. Rejected because the candidate then disappears as a separate artifact.
   - Symlink the active package to the candidate. Rejected because the workspace needs to remain portable and predictable across platforms.

3. **Keep rollback deterministic by naming snapshots explicitly**

   Each promote or rollback operation will create a named snapshot that can be selected later with `--to <version-name>`. The registry will record both the snapshot path and the version label so rollback can restore a specific package state deterministically.

   Alternatives considered:
   - Roll back only to the latest snapshot. Rejected because users need a stable version target.
   - Roll back by timestamp alone. Rejected because a version label is easier to reason about than a raw timestamp.

4. **Keep promote/rollback separate from install**

   The new commands operate on generated Skill packages and their history in the local workspace. Installing into agent-specific destinations remains a separate concern and can continue to use the existing installer after promotion.

   Alternatives considered:
   - Make promotion automatically install into platform destinations. Rejected because it would couple release control to platform deployment and make rollback harder to scope.

5. **Expose a small explicit CLI surface**

   The first release should provide one promote command and one rollback command. The command interface should be explicit about the target package or version being restored so the user can tell exactly what state is being changed.

   Alternatives considered:
   - Add a large set of subcommands for listing and inspecting promotion history. Rejected for the first increment because it would inflate the surface area before the core motion works.

## Risks / Trade-offs

- [Workspace churn] Promotion and rollback will create additional snapshot directories and registry files. → Keep snapshots under a dedicated hidden directory and make the registry compact.
- [Version naming ambiguity] Users may not know which version label to choose for rollback. → Record the source name, target name, and promoted-at timestamp in the registry and surface them in CLI output.
- [Cross-platform filesystem behavior] Copying directories can fail if package contents are malformed or partially missing. → Validate source and target paths before copying and fail with clear messages.
- [Overwriting active state] Promotion intentionally replaces the active target package. → Always snapshot the previous active version before overwriting it.

## Migration Plan

No migration is required. The promotion registry and snapshot directories are created on demand. Existing generated packages continue to work unchanged, and promotion history starts only when the user first promotes a candidate.

## Open Questions

- Should the first promote command infer the target name from the candidate name, or should it require an explicit `--as` target?
- Should rollback restore from a named version label only, or also support selecting by promotion timestamp?
- Should the registry store a compact JSON ledger only, or also persist a small human-readable summary file for each target?
