# Execution Discipline

This document describes the **execution discipline** Superpowers requires in the Skill Forge project. It covers the four disciplines that apply at implementation time: TDD, systematic debugging, verification before completion, and the escalation rules.

The skill selection policy is in `skill-usage-policy.md`. This document assumes the Agent has already selected the right skill and now needs to execute it correctly.

## 1. Test-Driven Development (TDD)

### When TDD Applies

TDD applies to any change that alters **observable behavior**. Observable behavior is anything the user or another Agent can see:

- A CLI command's output (text, exit code, side effect on disk).
- A stored artifact's shape (`skill-forge.json`, `eval-report.json`, config schema, blueprint schema).
- A validation result's format or content.
- A function's return value or exception type.

TDD does NOT apply to:

- Pure documentation changes (no behavior change).
- Pure refactors (no observable change). Note: a refactor that accidentally changes behavior is not a refactor.
- Configuration-only changes (e.g., a new YAML field with no logic change). Note: a config change that influences behavior is observable and TDD applies.

### The TDD Cycle

1. **Write or extend the test first.** The test encodes the new behavior as a concrete assertion.
2. **Run the test. It must fail for the right reason.** A test that fails with `NameError` is failing for the wrong reason. A test that fails with `AssertionError: expected 5, got 4` is failing for the right reason.
3. **Make the minimum change to the implementation that turns the failing test green.** No opportunistic refactors. No "while I'm here" cleanups.
4. **Run the test again. It must pass.**
5. **Run the full test suite. No regression.** If another test fails, apply `systematic-debugging`.

### Pitfalls

- **Writing the test after the implementation.** This is not TDD; it is "test-alongside" at best. The order matters.
- **Modifying the test to match a broken implementation.** The test encodes the requirement. If the test is wrong, fix the requirement first, then the test, then the implementation.
- **Skipping TDD for "trivial" changes.** Trivial is a judgment call. When in doubt, TDD applies. The cost of one extra test is small; the cost of a regression is large.
- **TDD on a non-observable change.** If the change is not observable, TDD does not apply. Do not invent a test for the sake of the methodology.

## 2. Systematic Debugging

### When Debugging Applies

Debugging applies when a test fails, a verification command exits non-zero, or behavior regresses. The trigger is **observation of failure**, not suspicion of a bug.

### The Debugging Cycle

1. **Reproduce.** Make the failure happen on demand. If you cannot reproduce, you cannot debug.
2. **Locate.** Narrow the failure to a specific module, function, or line. Use logs, breakpoints, or simpler tests.
3. **Identify the root cause.** Ask "why" five times. The root cause is the most fundamental explanation that, if fixed, would prevent the failure.
4. **Write a regression test.** The regression test reproduces the failure. It should fail on the current code and pass on the fixed code.
5. **Fix the root cause.** Not the symptom. If the symptom is "output is wrong", the root cause might be "the function uses the wrong variable" or "the input was not validated".
6. **Run the regression test.** It must pass.
7. **Run the full test suite.** No new regressions.

### Pitfalls

- **Fixing the symptom.** If the test fails because the function returns `None` instead of `5`, do not add `return 5` blindly. Find out why the function returns `None`.
- **Skipping the reproducer.** A fix that is not preceded by a reproducer is a guess.
- **Multiple fixes at once.** One fix per debugging cycle. If a single change touches three modules, it is three changes.
- **Debugging without reading the code.** The root cause is in the code. Read the code.

## 3. Verification Before Completion

### When Verification Applies

Verification applies **always**, at the end of every change. There are no exceptions.

### The Verification Cycle

1. **Run the final verification commands from `plan.md`.** These are the commands the planning agent specified. They are the contract.
2. **Record the results in `verification.md`.** For each command: working directory, exit code, output summary.
3. **Run `openspec validate <change-id> --strict`.** Must return `valid`.
4. **State the verdict.** `done`, `done-with-risks`, or `not-done`.
5. **If verdict is `not-done`:** the change is not archiveable. The implementer reports the failure and waits for direction.

### Required Evidence

A `verification.md` without evidence is not a verification. The required evidence:

- **Executed commands**: exact commands, in order, with exit codes.
- **Test results**: pass/fail counts, pytest summary line.
- **OpenSpec validation**: output of `openspec validate --strict`.
- **Skipped commands**: any command that was not run, with the reason. The reason is required.
- **Deviations from plan**: any difference between the planned file list and the actual file list.
- **Remaining risks**: anything that could still break or surprise.
- **Verdict**: one of `done`, `done-with-risks`, `not-done`.

### Pitfalls

- **"It looks done."** Run the verification. Looks are not commands.
- **Skipping commands "to save time".** The verification is the contract. Skipping is breaking the contract.
- **Recording a verdict of `done` for a change with a failing test.** The verdict is `not-done`. The change is not archiveable.

## 4. Escalation Rules

The Agent must escalate (not improvise) when:

- A required Superpowers skill cannot be invoked (e.g., the required context is missing).
- A verification command cannot run for a non-environmental reason.
- A test fails and `systematic-debugging` does not converge in three cycles.
- A task would require touching a forbidden path.
- The plan and the actual repository state disagree in a way that affects the diff.

The escalation format:

- **What was attempted**: the action and the skill invoked.
- **What was blocked**: the specific blocker.
- **What is needed to unblock**: the user input or decision required.

A blocked Agent is not a failed Agent. Escalation is the correct response to an unresolvable blocker.

## 5. The Discipline of Not Implementing

The hardest discipline is **not implementing** when the situation calls for stopping.

- "I'll just clean this up while I'm here." Stop. Surface the cleanup as a follow-up change.
- "The plan is too narrow; I'll expand it." Stop. The plan is the contract. If the plan is too narrow, escalate.
- "I see another bug." Stop. A bug found during a change is a follow-up change, not part of the current diff.
- "Let me add a test for completeness." Stop. If the test is not required by `tasks.md`, it is scope drift.

The discipline of not implementing is what keeps the change small. A small change is reviewable. A large change is not.

## 6. Cross-References

- Skill selection: `skill-usage-policy.md`.
- Subagent and worktree rules: `subagent-policy.md`.
- Per-task execution: see the `Executing Plans` section in each change's `tasks.md`.
- Project configuration: `.superpowers/execution-checklist.md`.
