## 1. Configuration and Models

- [x] 1.1 Add retrieval config fields for rerank availability, default use, provider, and candidate multiplier.
- [x] 1.2 Add search result fields for retrieval mode and rerank score.
- [x] 1.3 Preserve existing config defaults and loading behavior.

## 2. Reranker Implementation

- [x] 2.1 Add a pluggable reranker interface.
- [x] 2.2 Implement an offline lexical reranker.
- [x] 2.3 Add rerank failure handling that falls back to TF-IDF.
- [x] 2.4 Keep default TF-IDF search order unchanged when rerank is disabled.

## 3. CLI Integration

- [x] 3.1 Add `skill-forge search --rerank`.
- [x] 3.2 Enable rerank automatically when config requests it.
- [x] 3.3 Display retrieval mode in search output.
- [x] 3.4 Display clear warnings for disabled or failed rerank fallback.

## 4. Tests and Documentation

- [x] 4.1 Add config tests for rerank defaults and overrides.
- [x] 4.2 Add retrieval tests for default order, reranked order, and fallback behavior.
- [x] 4.3 Add CLI tests for `--rerank`, config-enabled rerank, disabled rerank, and fallback warning.
- [x] 4.4 Update README and README.zh-CN command documentation.
- [x] 4.5 Run focused tests and full `uv run pytest`.

## 5. OpenSpec Verification

- [x] 5.1 Run `openspec validate "add-optional-retrieval-rerank" --strict`.
- [x] 5.2 Run `openspec validate --all --strict`.
