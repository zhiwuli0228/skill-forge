# Release Notes

## Unreleased

- Changed `skill-forge create "<requirement>"` to automatically use configured LLM generation when `SKILL_FORGE_LLM_API_KEY` and `SKILL_FORGE_LLM_MODEL` are present.
- Added `--no-llm` to force deterministic generation and keep LLM detection disabled for a create run.
- Kept `--llm` as force-enabled LLM mode; missing configuration now remains a clear error in this explicit mode.
- Extended `skill-forge.json` provenance with LLM mode, selection result, and fallback reason fields.
