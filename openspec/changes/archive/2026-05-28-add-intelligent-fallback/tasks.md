## 1. LLM Selection Model

- [x] 1.1 Add an internal create LLM mode representation for automatic, force-enabled, and disabled generation.
- [x] 1.2 Add `--no-llm` to the create command and fail clearly when it is combined with `--llm`.
- [x] 1.3 Preserve the existing interactive create restriction for LLM-assisted generation.

## 2. Availability Detection

- [x] 2.1 Add a helper that detects required LLM environment configuration without constructing a full client.
- [x] 2.2 Add an optional bounded availability probe with a timeout shorter than two seconds, or explicitly implement env-only availability detection for the first iteration.
- [x] 2.3 Ensure auto mode skips network probing when required configuration is missing.

## 3. Create Flow Behavior

- [x] 3.1 Update default non-interactive create to use LLM generation when auto detection reports availability.
- [x] 3.2 Update default non-interactive create to fall back to deterministic generation when LLM configuration or availability is missing.
- [x] 3.3 Keep `--llm` strict: missing configuration or failed availability checks exit non-zero with clear errors.
- [x] 3.4 Keep `--no-llm` deterministic: no LLM configuration lookup, availability check, or LLM field generation.
- [x] 3.5 Preserve existing field-level fallback behavior after an LLM request is made.

## 4. Provenance And Display

- [x] 4.1 Extend generated provenance metadata with LLM selection mode and fallback reason while keeping existing LLM fields.
- [x] 4.2 Update any `show` or metadata display paths to present the new LLM selection fields when available.
- [x] 4.3 Ensure older provenance files remain readable when the new fields are absent.

## 5. Documentation

- [x] 5.1 Update `README.md` with automatic default behavior, `--llm`, `--no-llm`, and configuration details.
- [x] 5.2 Update `README.zh-CN.md` with the same behavior change.
- [x] 5.3 Add or update release notes describing the default behavior change.
- [x] 5.4 Update `docs/intelligent-generation-roadmap.md` implementation progress after this change is implemented and verified.

## 6. Tests And Validation

- [x] 6.1 Add CLI tests for default no-config deterministic fallback.
- [x] 6.2 Add CLI tests for default configured LLM generation.
- [x] 6.3 Add CLI tests for `--llm` missing configuration and unavailable provider errors.
- [x] 6.4 Add CLI tests for `--no-llm` bypassing LLM detection.
- [x] 6.5 Add CLI tests for conflicting `--llm` and `--no-llm` flags.
- [x] 6.6 Add provenance tests for automatic LLM selection, automatic deterministic fallback, and explicit no-LLM.
- [x] 6.7 Run focused tests for CLI and LLM refiner behavior.
- [x] 6.8 Run `openspec validate "add-intelligent-fallback" --strict` and `openspec validate --all --strict`.
