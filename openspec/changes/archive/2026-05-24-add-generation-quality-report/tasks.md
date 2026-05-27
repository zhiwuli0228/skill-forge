## 1. Quality Report Model

- [x] 1.1 Add a deterministic generation quality report model/helper derived from `ValidationResult`.
- [x] 1.2 Add unit tests for clean, warning-only, and error score calculation.

## 2. Create Command Integration

- [x] 2.1 Run post-generation validation for non-interactive `create`, including generated attachment metadata.
- [x] 2.2 Print quality score, validation status, errors, warnings, and next actions after successful generation.
- [x] 2.3 Exit non-zero with a clear invalid generated package message when post-generation validation has errors.

## 3. Verification

- [x] 3.1 Add CLI tests covering quality report output and warning-only success behavior.
- [x] 3.2 Run automated tests and strict OpenSpec validation.
