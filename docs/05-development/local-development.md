# Local Development

## Purpose

This document is the local development guide for Skill Forge. It states the environment assumptions, the common commands, the Windows PowerShell notes, and the read-only vs. mutating classification for the commands a developer runs day to day.

## Scope

- Applies to: setting up and running Skill Forge on a developer machine.
- Owns: environment prerequisites, common commands, command classification, and platform-specific notes.
- Does **not** own: testing strategy (see `testing-guide.md`), architecture (see `docs/01-architecture/`), or domain rules (see `docs/06-domain/`).

## Current Rules

### 1. Environment Assumptions

- Python 3.11 or newer is installed and on `PATH`.
- [uv](https://docs.astral.sh/uv/) is installed and on `PATH`. `uv` is the canonical tool for dependency management and command execution in this repository. Do not introduce `pip` workflows, `poetry`, or `conda` environments as alternatives.
- The default workspace path `~/.skill-forge/` is writable by the current user.
- Optional: an LLM provider is configured when `--llm` will be used. The required environment variables are `SKILL_FORGE_LLM_API_KEY`, `SKILL_FORGE_LLM_MODEL`, and `SKILL_FORGE_LLM_BASE_URL` (the last one only when the provider is not the default OpenAI endpoint).
- Optional: `git` is installed when the developer will use the harness's governance check, which shells out to git for diff inspection.
- The repository is checked out at a path without spaces in any directory name. The `uv` toolchain does not always handle spaces in `VIRTUAL_ENV` or in installed script paths reliably.

### 2. Common Commands

#### Install dependencies

```bash
uv sync
```

This installs the locked dependency set declared in `uv.lock` into the project's virtual environment. Run it once after cloning and after any change to `pyproject.toml` or `uv.lock`.

#### Run the CLI

```bash
uv run skill-forge --help
```

Lists the full command surface. The CLI is a Typer app; the help text is the canonical user-facing reference.

#### Run a single command

```bash
uv run skill-forge <command> [args...]
```

Examples: `uv run skill-forge init`, `uv run skill-forge create "..."`, `uv run skill-forge validate <path>`.

#### Run the test suite

```bash
uv run pytest
```

Runs the full pytest suite under the project's virtual environment.

#### Run the governance check (quick)

```bash
python scripts/governance_check.py --quick
```

Runs the two minimum checks: `openspec validate --strict --all` and `uv run skill-forge --help`. The quick mode is the floor for docs-only changes.

#### Run the governance check (full)

```bash
python scripts/governance_check.py
```

Adds `openspec schema validate`, the two example-change strict validations, and `uv run pytest`. The full mode is the floor for any code, schema, or governance change.

#### Editable install for local development

```bash
uv pip install -e .
```

Installs the package in editable mode so that local source changes are picked up without a reinstall. The `uv run` workflow already gives this behavior; use the explicit install when you need the `skill-forge` entry point on `PATH` outside `uv run`.

### 3. Windows PowerShell Notes

The Skill Forge CLI is cross-platform. The harness commands in `scripts/governance_check.py` are written to run on Windows PowerShell and on POSIX shells.

- Replace `/tmp/skill-forge-verify` examples with a Windows path such as `E:\tmp\skill-forge-verify`.
- Use forward slashes in `SKILL_FORGE_LLM_BASE_URL` and in URLs; PowerShell handles forward slashes in quoted strings.
- The default workspace path `~/.skill-forge/` resolves to `C:\Users\<user>\.skill-forge\` on Windows.
- The `uv run` syntax is identical on Windows PowerShell.
- `git` line endings: the repository is configured for `LF` in tracked files; on Windows, Git may warn about `LF will be replaced by CRLF`. The warning is benign for the workflow; do not "fix" it by committing CRLF.
- The `--home` flag on `init` accepts a Windows path. Quote the path to handle spaces.

### 4. Read-Only vs. Mutating Commands

A developer must know which commands change state and which only inspect it. Misclassifying a command leads to accidental data loss or to commits that touch the wrong paths.

**Read-only (safe to run at any time).**

| Command | Inspects |
|---|---|
| `uv run skill-forge --help` | CLI surface |
| `uv run skill-forge <command> --help` | Per-command help |
| `uv run skill-forge list` | Generated Skill packages in the configured output directory |
| `uv run skill-forge show <name>` | A specific package's metadata |
| `uv run skill-forge diff <a> <b>` | Two packages' `SKILL.md` |
| `uv run skill-forge search "<query>"` | The local research corpus |
| `uv run skill-forge validate <path>` | A Skill package's structure and frontmatter |
| `uv run skill-forge blueprints list` | Built-in, user, and project blueprints |
| `uv run skill-forge blueprints show <name>` | A specific blueprint |
| `uv run pytest` | The test suite |
| `python scripts/governance_check.py --quick` | The minimum governance checks |
| `python scripts/governance_check.py` | The full governance checks |
| `git status --short` | The current dirty state |
| `git diff --name-only` | The set of modified tracked files |
| `git diff --cached --stat` | The set of staged files |
| `openspec validate <change-id> --strict` | One change's validation status |
| `openspec validate --strict --all` | The full set of changes and specs |

**Mutating (change state — confirm before running in shared environments).**

| Command | Mutates |
|---|---|
| `uv sync` | The local virtual environment (adds / updates / removes packages per `uv.lock`) |
| `uv pip install -e .` | The active environment, registers the `skill-forge` entry point |
| `uv run skill-forge init` | Creates `~/.skill-forge/` (or the `--home` path) |
| `uv run skill-forge create "..."` | Writes a generated Skill package, `skill-forge.json`, and any blueprint-declared attachments |
| `uv run skill-forge update` | Refreshes the local research corpus, updates SQLite metadata |
| `uv run skill-forge install <name> --target <t> --scope <s>` | Copies a generated Skill into the target platform's skill directory |
| `uv run skill-forge upgrade <name>` | Writes a new upgrade candidate (does not modify the source package) |
| `uv run skill-forge eval <name> --case ...` | Writes `eval-report.json` into the package directory |
| `git add <path>` | The index |
| `git rm <path>` | The index and the working tree (for tracked files) |
| `git commit` | The local branch |
| `git push` | The remote |
| `openspec archive <change-id>` | Moves a change folder under `openspec/changes/archive/` and merges the spec deltas into `openspec/specs/` |
| `openspec new --change <id>` | Creates a new change folder under `openspec/changes/` |

When in doubt, treat a command as mutating. Read the help text, run with `--dry-run` when the command supports it, and never run a mutating command against a path that is not on the current change's allowed list.

### 5. Troubleshooting

- **`skill-forge: command not found` outside `uv run`.** Run `uv pip install -e .` to register the entry point, or use `uv run skill-forge ...` instead.
- **`ModuleNotFoundError` after a dependency change.** Run `uv sync` to re-resolve the lockfile.
- **`SKILL_FORGE_LLM_API_KEY` set but the LLM call fails.** Verify the base URL with `echo $SKILL_FORGE_LLM_BASE_URL` (or `echo $env:SKILL_FORGE_LLM_BASE_URL` on PowerShell). The default base URL points to the OpenAI-compatible endpoint; non-OpenAI providers require `SKILL_FORGE_LLM_BASE_URL`.
- **A test passes locally but fails in CI.** Check the line-ending warnings in the test file's git history; CRLF/LF mismatches in test fixtures can cause token-level diffs in JSON assertions.

## Related Files

- `docs/05-development/testing-guide.md` — testing strategy and how to interpret failures.
- `docs/01-architecture/architecture-overview.md` — layer model and CLI ownership.
- `docs/01-architecture/data-flow.md` — per-flow commands and verification.
- `README.md` — user-facing quick start and command reference.
- `pyproject.toml`, `uv.lock` — dependency manifests (forbidden by default; modify only with explicit authorization).

## What Not To Do

- Do not introduce a `pip install -r requirements.txt` workflow. The dependency surface is `pyproject.toml` + `uv.lock`, managed by `uv`.
- Do not run mutating commands against a path that is not on the current change's allowed list.
- Do not change `pyproject.toml` or `uv.lock` without an explicit authorization in the current task.
- Do not commit CRLF line endings to fix a Git warning.
- Do not run a mutating command in a shared environment without confirming the path and the scope.
- Do not skip `uv sync` after a dependency change. The lockfile must be consistent with the environment.
