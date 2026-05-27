## Context

The `create` pipeline currently analyzes user text deterministically, optionally applies blueprint defaults, optionally injects project context, renders the package, and validates the result. The roadmap calls for optional LLM enhancement without making base generation depend on a network service or bypassing validation.

## Goals / Non-Goals

**Goals:**

- Add `--llm` as an explicit opt-in for non-interactive `create`.
- Keep the default `create` path byte-for-byte deterministic in behavior and without network access.
- Refine structured `SkillRequirement` fields before rendering.
- Fail clearly when LLM configuration or response parsing fails.
- Ensure LLM-refined output is still validated and quality-reported.

**Non-Goals:**

- No automatic repair loop after validation.
- No provider-specific CLI sprawl.
- No persistence of prompts, responses, or project context.
- No interactive draft LLM mode in this slice.

## Decisions

1. Add a provider interface plus a default OpenAI-compatible HTTP implementation.

   Rationale: a small interface keeps tests deterministic and makes provider wiring replaceable. OpenAI-compatible chat completions require only endpoint, model, and API key configuration, which can be supplied from environment variables.

   Alternative considered: hard-code a specific SDK. That would add dependency weight and make tests more coupled to one vendor.

2. Use environment variables for first-version provider configuration.

   Rationale: this avoids expanding the persisted config schema before the shape of LLM usage stabilizes. The CLI can fail clearly if `--llm` is used without the required variables.

   Required variables: `SKILL_FORGE_LLM_API_KEY`, `SKILL_FORGE_LLM_MODEL`. Optional variable: `SKILL_FORGE_LLM_BASE_URL`.

3. Ask the LLM for structured JSON and merge only known fields into `SkillRequirement`.

   Rationale: the existing renderer and validator already expect structured fields. Ignoring unknown keys avoids accidental schema drift.

   Alternative considered: let the LLM generate full `SKILL.md`. That would bypass the deterministic template, blueprint-generated files, and existing validation assumptions.

4. Run LLM refinement before blueprint enrichment.

   Rationale: the LLM can improve the analyzed requirement while blueprints remain the authoritative deterministic defaults for recognized task types and generated files.

5. Fail clearly on LLM errors instead of silently falling back.

   Rationale: `--llm` is explicit. If a user asks for LLM assistance, hiding failures behind deterministic output makes results ambiguous.

## Risks / Trade-offs

- LLM output may be malformed -> parse only JSON objects and return a clear non-zero CLI error on parse failures.
- LLM output may remove important fields -> merge only non-empty recognized fields and preserve required baseline values.
- Provider configuration via env vars is minimal -> enough for this first opt-in slice, with config-file support left for a later change if needed.
- Network calls can be slow -> support a conservative timeout in the HTTP client and cover client failures in tests with fakes.
