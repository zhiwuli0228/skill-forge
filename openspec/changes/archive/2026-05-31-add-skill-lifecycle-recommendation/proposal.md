## Why

Skill Forge already exposes a lifecycle index, but users still have to interpret the status and decide the next action manually. A deterministic recommendation layer turns that status into a concrete next step without adding LLM dependence or file mutation.

## What Changes

- Add a read-only lifecycle recommendation layer that consumes lifecycle summaries and outputs a deterministic next best action with a reason.
- Add `skill-forge lifecycle recommend <skill-name>` to surface the recommended action for one generated Skill.
- Add `skill-forge lifecycle compare <skill-a> <skill-b>` to compare two lifecycle states and explain which package is healthier and why.
- Keep the recommendation logic local, deterministic, and explainable.
- Keep the change read-only: no promote, rollback, install, or file mutation.

## Capabilities

### New Capabilities
- `skill-lifecycle-recommendation`: Deterministic next best action and comparison views built on top of lifecycle summaries.

### Modified Capabilities
- None

## Impact

Affected code: a new `src/skill_forge/lifecycle/` recommendation module, CLI lifecycle recommendation commands, recommendation and compare tests, and reuse of the existing lifecycle index service and summary models.
