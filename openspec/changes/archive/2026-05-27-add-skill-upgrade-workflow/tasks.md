## 1. Upgrade Models and Service

- [x] 1.1 Add upgrade result and error types.
- [x] 1.2 Implement requirement reconstruction from provenance metadata.
- [x] 1.3 Implement candidate naming with `<skill-name>-upgraded` default and `--candidate-name` override.
- [x] 1.4 Implement candidate overwrite protection and `--force` replacement.

## 2. Candidate Generation and Quality

- [x] 2.1 Reapply the current recorded blueprint during upgrade.
- [x] 2.2 Generate the candidate package without modifying the source package.
- [x] 2.3 Validate the candidate package and build a quality report.
- [x] 2.4 Persist candidate provenance metadata.

## 3. CLI Integration

- [x] 3.1 Add `skill-forge upgrade <skill-name>`.
- [x] 3.2 Add `--candidate-name`, `--force`, `--home`, `--output-dir`, and `--project` options.
- [x] 3.3 Display source package, candidate package, old/new quality scores, and diff guidance.
- [x] 3.4 Report clear errors for missing provenance, invalid provenance, missing blueprint, existing candidate, and invalid candidate.

## 4. Tests and Documentation

- [x] 4.1 Add service tests for successful upgrade and source preservation.
- [x] 4.2 Add service tests for missing provenance, missing blueprint, and existing candidate behavior.
- [x] 4.3 Add CLI tests for success, custom candidate names, failure cases, and `--force`.
- [x] 4.4 Update README and README.zh-CN command documentation.
- [x] 4.5 Run focused tests and full `uv run pytest`.

## 5. OpenSpec Verification

- [x] 5.1 Run `openspec validate "add-skill-upgrade-workflow" --strict`.
- [x] 5.2 Run `openspec validate --all --strict`.
