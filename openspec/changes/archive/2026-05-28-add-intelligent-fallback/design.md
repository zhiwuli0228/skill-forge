## Context

`add-llm-field-generation` moved LLM generation after blueprint and project-context enrichment, added field-level fallback, and records deterministic content quality metrics. The remaining usability gap is selection: users must still know to pass `--llm`, while the roadmap calls for a zero-configuration default that uses LLM only when it is locally available.

Current LLM configuration is environment-based: `SKILL_FORGE_LLM_API_KEY`, `SKILL_FORGE_LLM_MODEL`, and optional `SKILL_FORGE_LLM_BASE_URL`. The implementation should preserve that provider boundary and avoid introducing model routing, provider registries, or a `--strategy` option.

## Goals / Non-Goals

**Goals:**

- Make `skill-forge create "<requirement>"` automatically use LLM generation when LLM configuration is present and available.
- Keep unconfigured users on the deterministic generation path without errors or noticeable delay.
- Preserve `--llm` as force-enable mode and add `--no-llm` as force-disable mode.
- Make availability detection bounded, testable, and independent from full generation requests.
- Record selection mode and fallback information in provenance metadata.

**Non-Goals:**

- No `--strategy`, model priority list, model registry, or `OllamaClient`.
- No change to the field-level LLM merge and fallback rules from `add-llm-field-generation`.
- No LLM requirement for interactive create.
- No automatic repair of low content-quality scores.

## Decisions

1. Use a three-state CLI selection model.

   The create command should resolve LLM mode as `auto`, `force`, or `disabled`: default is `auto`, `--llm` is `force`, and `--no-llm` is `disabled`. If both explicit flags are supplied, the command should fail before generation with a clear message.

   Alternative considered: keep a boolean `llm` flag and infer `--no-llm` after parsing. A named selection state is clearer for tests, provenance, and future extension without exposing a strategy concept to users.

2. Split configuration detection from request execution.

   Auto mode should first check whether required environment variables are present. If they are missing, the command should skip client construction and use deterministic generation. Force mode should keep the current strict behavior and report missing configuration as an error.

   Alternative considered: always call `OpenAICompatibleLLMClient.from_env()` and catch configuration errors. That works, but it makes a common non-error path look exceptional and makes it easier to accidentally emit warnings for normal deterministic fallback.

3. Make network probing optional and bounded.

   The first implementation may treat complete environment configuration as available, but if a network probe is added it must use a short timeout below two seconds and must be skipped when required configuration is missing. Probe failure in auto mode should fall back deterministically; probe failure in force mode should fail clearly.

   Alternative considered: send a small chat completion request as the probe. That proves the full path but adds cost, latency, and possible side effects before the real generation call.

4. Preserve existing LLM response fallback semantics.

   Once auto mode chooses LLM, field-level malformed output should still fall back to pre-LLM values and overall malformed responses should still produce a package. Provider configuration or availability failures are selection failures: auto falls back to deterministic generation, force errors.

   Alternative considered: make auto mode fail on provider request failures after selection. That would violate the roadmap principle that default generation should not block users when LLM is unavailable.

5. Extend provenance with selection metadata.

   Existing `llm_enabled`, generated/refined/fallback fields, and content quality metadata should remain. Add metadata sufficient to distinguish explicit LLM, auto-selected LLM, auto deterministic fallback, and explicit no-LLM. A compact shape such as `llm_mode`, `llm_selection`, and `llm_fallback_reason` is enough; exact field names can follow existing model style during implementation.

   Alternative considered: infer everything from `llm_enabled`. That cannot distinguish "user disabled LLM" from "auto checked and fell back because unavailable".

## Risks / Trade-offs

- Default behavior now may call a remote-compatible endpoint when users have LLM env vars configured -> Document the behavior change in README, README.zh-CN, and release notes, and provide `--no-llm`.
- Probe latency could slow create -> Skip probing when env vars are absent and enforce a timeout below two seconds when probing is enabled.
- Complete env vars do not guarantee a healthy provider -> Auto mode must fall back on bounded availability failure; force mode must surface the error.
- Provenance schema churn could affect existing readers -> Keep existing provenance fields and only add optional fields with defaults.

## Migration Plan

1. Implement selection helpers and CLI flag handling.
2. Add tests for default no-config fallback, default configured LLM usage, force-enable errors, explicit disable, and conflicting flags.
3. Extend provenance metadata without removing existing fields.
4. Update README, README.zh-CN, release notes, and the intelligent generation roadmap.
5. Roll back by restoring default selection to deterministic while leaving `--no-llm` harmlessly available.

## Open Questions

- Should the first implementation perform an HTTP availability probe or only require complete environment configuration? The roadmap allows the probe to be optional, so implementation can start with env-only detection if latency/cost concerns dominate.
