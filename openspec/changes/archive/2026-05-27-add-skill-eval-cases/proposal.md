## Why

Skill Forge can now generate, validate, lint, and explain repairs for Skill packages, but it still cannot check whether a Skill satisfies a concrete task standard beyond static authoring rules. Local eval cases provide a deterministic way to verify package content against expected sections, constraints, and forbidden patterns without executing a real Agent.

## What Changes

- Add a local `skill-forge eval <skill-name>` command.
- Support single eval case files with `--case <file>`.
- Support batch eval case directories with `--cases <dir>`.
- Define a YAML eval case format with stable assertions.
- Execute static assertions against generated Skill package content.
- Write an eval report into the Skill package for the latest run.
- Show the latest eval summary in `skill-forge show` when present.
- Do not execute code, call an Agent, or invoke an LLM.

## Capabilities

### New Capabilities

- `skill-evaluation`: Define and run local deterministic eval cases for generated Skill packages.

### Modified Capabilities

- `skill-library-management`: Generated Skill inspection can display the latest eval summary when one exists.

## Impact

- Affected CLI:
  - New `skill-forge eval <skill-name> --case <file>`
  - New `skill-forge eval <skill-name> --cases <dir>`
  - Existing `skill-forge show <skill-name>`
- Affected modules:
  - New `src/skill_forge/evals/`
  - New/updated models under `src/skill_forge/models/`
  - `src/skill_forge/library/manager.py`
  - `src/skill_forge/cli.py`
- Affected tests:
  - New `tests/test_skill_evals.py`
  - Updates to `tests/test_cli.py`
  - Updates to `tests/test_skill_library.py`
- No new third-party dependencies are expected because PyYAML is already available.
