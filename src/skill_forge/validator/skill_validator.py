from pathlib import Path
import re

import frontmatter

from skill_forge.models.validation import ValidationIssue, ValidationResult


ERROR_MISSING_DIRECTORY = "missing_directory"
ERROR_MISSING_SKILL_MD = "missing_skill_md"
ERROR_MISSING_FRONTMATTER = "missing_frontmatter"
ERROR_MISSING_NAME = "missing_name"
ERROR_MISSING_DESCRIPTION = "missing_description"
ERROR_EMPTY_DESCRIPTION = "empty_description"
WARNING_MISSING_SECTION = "missing_section"
ERROR_UNSAFE_ATTACHMENT_PATH = "unsafe_attachment_path"
WARNING_NAME_NOT_SLUG = "name_not_slug"
WARNING_PACKAGE_NAME_MISMATCH = "package_name_mismatch"
WARNING_DESCRIPTION_TOO_SHORT = "description_too_short"
WARNING_DESCRIPTION_MISSING_TRIGGER = "description_missing_trigger"
WARNING_DESCRIPTION_MISSING_EXCLUSION = "description_missing_exclusion"
WARNING_EMPTY_SECTION = "empty_section"
WARNING_WORKFLOW_TOO_SHORT = "workflow_too_short"
WARNING_QUALITY_GATES_TOO_FEW = "quality_gates_too_few"

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_TRIGGER_PATTERNS = (
    "use this skill",
    "when ",
    "用于",
    "使用",
    "适用于",
)
_EXCLUSION_PATTERNS = (
    "do not use",
    "don't use",
    "not use",
    "不要",
    "不适用",
    "不用于",
)

RECOMMENDED_SECTIONS = (
    "Purpose",
    "When to use",
    "When not to use",
    "Workflow",
    "Output format",
    "Quality gates",
)


class SkillValidator:
    def validate(self, skill_path: Path, attachment_paths: list[str] | None = None) -> ValidationResult:
        errors: list[ValidationIssue] = []
        warnings: list[ValidationIssue] = []

        for attachment_path in attachment_paths or []:
            if _is_unsafe_attachment_path(attachment_path):
                errors.append(
                    _error(
                        ERROR_UNSAFE_ATTACHMENT_PATH,
                        f"Attachment path must be relative and stay inside the Skill package: {attachment_path}",
                    )
                )

        if not skill_path.exists() or not skill_path.is_dir():
            errors.append(_error(ERROR_MISSING_DIRECTORY, f"Skill directory does not exist: {skill_path}"))
            return ValidationResult(ok=False, errors=errors, warnings=warnings)

        skill_md = skill_path / "SKILL.md"
        if not skill_md.is_file():
            errors.append(_error(ERROR_MISSING_SKILL_MD, f"Missing SKILL.md: {skill_md}"))
            return ValidationResult(ok=False, errors=errors, warnings=warnings)

        content = skill_md.read_text(encoding="utf-8")
        post = frontmatter.loads(content)
        if not _has_frontmatter(content):
            errors.append(_error(ERROR_MISSING_FRONTMATTER, "SKILL.md must include YAML frontmatter."))

        name = post.metadata.get("name")
        description = post.metadata.get("description")
        if not name:
            errors.append(_error(ERROR_MISSING_NAME, "SKILL.md frontmatter must include name."))
        else:
            name_text = str(name).strip()
            if not _SLUG_PATTERN.fullmatch(name_text):
                warnings.append(_warning(WARNING_NAME_NOT_SLUG, "SKILL.md frontmatter name should be a lowercase kebab-case slug."))
            if skill_path.name != name_text:
                warnings.append(
                    _warning(
                        WARNING_PACKAGE_NAME_MISMATCH,
                        f"Package directory name should match frontmatter name: {skill_path.name} != {name_text}",
                    )
                )
        if description is None:
            errors.append(_error(ERROR_MISSING_DESCRIPTION, "SKILL.md frontmatter must include description."))
        elif not str(description).strip():
            errors.append(_error(ERROR_EMPTY_DESCRIPTION, "SKILL.md frontmatter description must not be empty."))
        else:
            warnings.extend(_lint_description(str(description)))

        for section in RECOMMENDED_SECTIONS:
            if f"## {section}" not in content:
                warnings.append(_warning(WARNING_MISSING_SECTION, f"Recommended section is missing: {section}"))
            elif not _section_body(content, section):
                warnings.append(_warning(WARNING_EMPTY_SECTION, f"Recommended section has no meaningful content: {section}"))

        warnings.extend(_lint_section_density(content))

        return ValidationResult(ok=not errors, errors=errors, warnings=warnings)


def _has_frontmatter(content: str) -> bool:
    return content.startswith("---\n") or content.startswith("---\r\n")


def _is_unsafe_attachment_path(value: str) -> bool:
    path = Path(value)
    return path.is_absolute() or ".." in path.parts or not value.strip()


def _lint_description(description: str) -> list[ValidationIssue]:
    warnings: list[ValidationIssue] = []
    normalized = description.strip()
    folded = normalized.casefold()
    if len(normalized) < 40:
        warnings.append(_warning(WARNING_DESCRIPTION_TOO_SHORT, "SKILL.md frontmatter description should be specific enough to guide triggering."))
    if not any(pattern in folded for pattern in _TRIGGER_PATTERNS):
        warnings.append(_warning(WARNING_DESCRIPTION_MISSING_TRIGGER, "Description should explain when to use the Skill."))
    if not any(pattern in folded for pattern in _EXCLUSION_PATTERNS):
        warnings.append(_warning(WARNING_DESCRIPTION_MISSING_EXCLUSION, "Description should explain when not to use the Skill."))
    return warnings


def _lint_section_density(content: str) -> list[ValidationIssue]:
    warnings: list[ValidationIssue] = []
    workflow = _section_body(content, "Workflow")
    if workflow and _count_action_items(workflow) < 2:
        warnings.append(_warning(WARNING_WORKFLOW_TOO_SHORT, "Workflow should contain at least two actionable steps."))

    quality_gates = _section_body(content, "Quality gates")
    if quality_gates and _count_action_items(quality_gates) < 2:
        warnings.append(_warning(WARNING_QUALITY_GATES_TOO_FEW, "Quality gates should contain at least two checkable items."))
    return warnings


def _section_body(content: str, section: str) -> str:
    lines = content.splitlines()
    marker = f"## {section}"
    in_target = False
    in_fence = False
    body_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not in_target:
            if stripped == marker:
                in_target = True
            continue

        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and stripped.startswith("## "):
            break
        body_lines.append(line)

    meaningful = [line.strip() for line in body_lines if line.strip()]
    return "\n".join(meaningful).strip()


def _count_action_items(body: str) -> int:
    count = 0
    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^(\d+\.|-|\*)\s+\S", stripped):
            count += 1
    return count


def _error(code: str, message: str) -> ValidationIssue:
    return ValidationIssue(level="error", code=code, message=message)


def _warning(code: str, message: str) -> ValidationIssue:
    return ValidationIssue(level="warning", code=code, message=message)
