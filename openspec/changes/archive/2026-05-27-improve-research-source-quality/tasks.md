## 1. Update Result Quality Reporting

- [x] 1.1 Add disabled and partial status helpers to `UpdateResult`.
- [x] 1.2 Add failed-source retry guidance formatting.
- [x] 1.3 Update `skill-forge update` summary output to include disabled and partial status.
- [x] 1.4 Preserve non-zero behavior when all enabled sources fail.

## 2. Search Explanation

- [x] 2.1 Add stable score explanation formatting to search result models or CLI rendering.
- [x] 2.2 Add `skill-forge search --explain`.
- [x] 2.3 Display relevance, authority, completeness, freshness, platform boost, and final score when explanation is enabled.
- [x] 2.4 Preserve compact default search output without explanation columns.

## 3. Tests and Documentation

- [x] 3.1 Add update tests for disabled counts, partial status, and retry guidance.
- [x] 3.2 Add search tests for `--explain`, platform boost visibility, and compact default output.
- [x] 3.3 Update README and README.zh-CN command documentation.
- [x] 3.4 Run focused tests and full `uv run pytest`.

## 4. OpenSpec Verification

- [x] 4.1 Run `openspec validate "improve-research-source-quality" --strict`.
- [x] 4.2 Run `openspec validate --all --strict`.
