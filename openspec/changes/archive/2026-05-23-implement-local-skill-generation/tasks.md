## 1. Models and Module Structure

- [x] 1.1 Add generation model modules for `SkillRequirement` and `GeneratedSkillPackage`.
- [x] 1.2 Add package structure for requirement analysis and Skill generation.
- [x] 1.3 Ensure generation models provide stable defaults for target platform, language, lists, and optional asset flags.

## 2. Requirement Analyzer

- [x] 2.1 Implement a rule-based analyzer that accepts a natural language requirement string.
- [x] 2.2 Derive a stable kebab-case skill name, including `java-bug-investigation` for the documented Java bug example.
- [x] 2.3 Detect software engineering and bug investigation signals from Java/log/bug/root-cause requirements.
- [x] 2.4 Extract or infer constraints and expected outputs from phrases such as "要求", "不能", and "输出".
- [x] 2.5 Provide useful fallback usage boundaries, workflow, output format, and quality gates for vague requirements.

## 3. Template Rendering and Generation

- [x] 3.1 Add a Jinja2 `SKILL.md` template with frontmatter and all standard sections.
- [x] 3.2 Implement a template renderer that renders `SkillRequirement` into Markdown.
- [x] 3.3 Implement a Skill generator that writes `SKILL.md` under the configured output directory.
- [x] 3.4 Ensure generated package directories are not silently overwritten.
- [x] 3.5 Return generated package metadata including package path and `SKILL.md` path.

## 4. CLI Integration

- [x] 4.1 Add `skill-forge create "<requirement>"` to the Typer CLI.
- [x] 4.2 Load configuration and resolve the output directory for create.
- [x] 4.3 Ensure create can prepare the minimum workspace paths needed for generation.
- [x] 4.4 Print a clear success message including the generated package path.
- [x] 4.5 Print a clear error and non-zero exit when the target package already exists.

## 5. Tests

- [x] 5.1 Add analyzer tests for the documented Java bug investigation example.
- [x] 5.2 Add analyzer tests for vague requirements and default fields.
- [x] 5.3 Add renderer tests for frontmatter and standard sections.
- [x] 5.4 Add generator tests for output path creation and non-overwrite behavior.
- [x] 5.5 Add CLI tests for `create` success and existing-package failure using isolated test paths.
- [x] 5.6 Run the test suite and fix failures for this change.

## 6. Documentation and Verification

- [x] 6.1 Confirm `uv run skill-forge create "Java 存量代码 bug 定位 skill"` creates `java-bug-investigation/SKILL.md` in an isolated home.
- [x] 6.2 Confirm generated `SKILL.md` contains frontmatter and all standard sections.
- [x] 6.3 Update `docs/openspec_change_plan.md` to mark `implement-local-skill-generation` progress after proposal creation.
