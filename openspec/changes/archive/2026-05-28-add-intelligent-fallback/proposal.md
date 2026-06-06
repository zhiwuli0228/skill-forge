## Why

LLM field generation is now available after blueprint and project-context enrichment, but users still need to know when to pass `--llm`. This change makes high-quality generation the default when an LLM is configured while preserving deterministic generation as the fallback for unconfigured or explicitly disabled environments.

## What Changes

- Change `skill-forge create "<requirement>"` from always-deterministic generation to automatic LLM selection when the local LLM configuration is available.
- Keep `--llm` as explicit LLM mode; when selected and LLM configuration or availability checks fail, the command exits with a clear error instead of silently falling back.
- Add `--no-llm` as explicit deterministic mode; it bypasses LLM detection and guarantees the existing pure-rule generation path.
- Add a short, bounded LLM availability check that can determine configured/unconfigured states without slowing unconfigured users.
- Record whether automatic selection used LLM or fell back to deterministic generation in provenance metadata.
- Update README, README.zh-CN, and release notes to explain the default behavior change.

## Capabilities

### New Capabilities
- `intelligent-generation-fallback`: Automatic LLM availability detection and fallback semantics for Skill generation.

### Modified Capabilities
- `llm-assisted-generation`: LLM assistance changes from opt-in only to automatic by default when available, with explicit force-enable and force-disable modes.
- `local-skill-generation`: `create` default generation behavior changes to automatic LLM selection with deterministic fallback.

## Impact

- CLI: `src/skill_forge/cli.py` create option handling and user-facing error messages.
- LLM integration: `src/skill_forge/llm/refiner.py` or adjacent helper for configuration/availability detection.
- Models/provenance: generated metadata may need to distinguish auto-selected LLM, explicit LLM, disabled LLM, and fallback reason.
- Tests: CLI default behavior, explicit `--llm`, explicit `--no-llm`, missing config, configured available LLM, and bounded probe behavior.
- Documentation: `README.md`, `README.zh-CN.md`, release notes, and roadmap progress.
