# Task Guidelines

A `tasks.md` file is the tracked checklist that the apply phase walks through. It is the lowest level of the artifact hierarchy: each task is a single, observable, verifiable unit of work.

This document collects the writing rules for tasks. The structural rules are in `artifact-rules.md`; the schema-enforced rules are in `openspec/schemas/skill-forge-governance/schema.yaml` and `openspec/schemas/skill-forge-governance/templates/tasks.md`.

## 1. What a Task Is

A task is a single checkbox `- [ ] N.M <description>` that the apply phase will mark complete. A task is:

- Bounded: it touches a small, named set of files.
- Verifiable: when the task is done, there is an observable signal.
- Independent: it does not depend on another in-flight task in a way that prevents marking it done.

A task is NOT:

- A multi-day epic.
- A refactor folded into a feature.
- A "while I'm here" cleanup.

## 2. The Checkbox Format

Tasks use the literal format `- [ ] N.M <description>`. The OpenSpec apply phase parses this. Anything else is ignored.

```markdown
- [ ] 1.1 Add `validate_session` to the auth module. Files: src/auth/session.py. Observation: `pytest tests/test_auth.py::test_validate_session` passes.
```

The description must include:

- The action (what to do).
- The files (which paths to touch).
- The observation (how to know the task is done).

The files and observation are not separate fields. They are part of the description text. The apply phase will read the whole line.

## 3. Group Headings

Tasks are grouped under numbered headings:

```markdown
## 1. <Group Name>

- [ ] 1.1 <task>
- [ ] 1.2 <task>

## 2. <Group Name>

- [ ] 2.1 <task>
- [ ] 2.2 <task>
```

Rules:

- Group names are short and describe the slice of work: "Schema", "Core implementation", "Tests", "Docs".
- Group related tasks together. A task that "also fixes a doc typo" is two tasks in two groups.
- Order groups by dependency. Group 1 must be completable before Group 2 starts. The apply phase walks in order.

## 4. Separation by Type

Tasks should be separated by type. A common grouping:

- **Schema / config**: changes to YAML, JSON, or TOML schemas.
- **Core implementation**: changes to `src/skill_forge/<module>/`.
- **Tests**: changes to `tests/test_<module>.py`.
- **Docs**: changes to `README.md`, `docs/`, or schema documentation.
- **Verification**: the final group with `openspec validate` and the verification report.

Mixing types in one task makes verification ambiguous. "Add the new blueprint AND update the test" is two tasks. "Update the doc AND fix the test" is two tasks.

## 5. Observable Completion Conditions

Every task has an observable completion condition. The condition is part of the description.

Examples of observable conditions:

- A file exists at `<path>`.
- A function `<name>` is exported from `<module>`.
- A test `<test path>::<test name>` passes.
- A command exits with code 0.
- A section in `<doc path>` is updated to include `<phrase>`.

Examples of NON-observable conditions (do not use these):

- "The implementation is clean."
- "The code is well-tested."
- "Everything works."
- "Looks good."

A task without an observable condition is not a task. It is a wish.

## 6. File Lists

Each task's description includes the files it touches. The file list must match the allowed-path list in `plan.md`. If a task's file list is not a subset of the plan's allowed paths, the apply phase will refuse the task.

When in doubt, write the file path explicitly:

```markdown
- [ ] 1.1 Add `validate_session` to `src/skill_forge/auth/session.py`. Observation: `pytest tests/test_auth.py::test_validate_session` passes.
```

Do not write "update the auth module" without naming the file. A weaker agent does not know which file you mean.

## 7. The Final Verification Group

The last group is `## N. Final Verification`. It contains three tasks:

```markdown
## N. Final Verification

- [ ] N.1 Run final verification commands from plan.md. Record exit codes in verification.md.
- [ ] N.2 Write verification.md (commands, results, skipped, risks, verdict).
- [ ] N.3 Run `openspec validate <change-id> --strict`. Must pass.
```

These three tasks must be the last tasks in the file. They are the closure of the change.

## 8. Forbidden Patterns in Tasks

The following patterns are explicitly forbidden in `tasks.md`:

- "Refactor X." Refactors are their own change. Do not embed them in a feature task.
- "Update docs as needed." Specify which doc, which section, which phrase.
- "Add tests for the new feature." Specify which test file, which test name, which assertion.
- "Tidy up." Specify what is untidy and how it should look.
- "Make sure everything works." Specify which command to run and what success looks like.

A task that an agent cannot complete without asking "what does this mean?" is not a task. Rewrite it.

## 9. Task Dependencies

Tasks in a later group may depend on tasks in an earlier group. The group order makes the dependency explicit. Within a group, tasks are usually independent and may be done in any order.

If a task in Group 2 cannot start until a specific task in Group 1 is done, that dependency is captured by the group order. The description does not need to say "depends on 1.3". A reviewer can see the order.

If a task has a non-obvious dependency (e.g., a task in Group 1 that must be skipped if an env var is missing), state the dependency in the task's description:

```markdown
- [ ] 2.1 Add corpus indexing. Skipped if `SKILL_FORGE_SKIP_INDEXING=1`. Observation: `pytest tests/test_indexer.py` passes.
```

## 10. Common Mistakes

- **A task bundles a refactor with a feature.** Split into two tasks in two changes.
- **A task uses vague language.** "Improve" is not a verb that produces a verifiable result.
- **A task's file list exceeds the plan's allowed paths.** Escalate to plan.
- **A task's completion condition is not observable.** Specify the file, the command, or the test.
- **The final verification group is missing or incomplete.** A change without the three closing tasks is not done.
- **The group order does not respect dependencies.** Reorder.

## 11. Reviewer Checklist

A reviewer should be able to answer "yes" to all of the following:

- Is every task a checkbox `- [ ] N.M <description>`?
- Does every task include the files it touches?
- Does every task include an observable completion condition?
- Are tasks grouped by type (schema, implementation, tests, docs, verification)?
- Are groups ordered by dependency?
- Is the file list of every task a subset of the plan's allowed paths?
- Is the final verification group present with all three tasks?

If any answer is "no", the tasks need another draft.
