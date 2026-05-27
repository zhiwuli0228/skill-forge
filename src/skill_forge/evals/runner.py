from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from skill_forge.models.eval import (
    EVAL_REPORT_FILENAME,
    SkillEvalAssertionResult,
    SkillEvalCase,
    SkillEvalCaseResult,
    SkillEvalReport,
)


class EvalCaseError(RuntimeError):
    pass


class SkillEvaluator:
    def load_case(self, path: Path) -> SkillEvalCase:
        try:
            data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise EvalCaseError(f"Failed to read eval case {path}: {exc}") from exc
        except yaml.YAMLError as exc:
            raise EvalCaseError(f"Failed to parse eval case {path}: {exc}") from exc

        if not isinstance(data, dict):
            raise EvalCaseError(f"Eval case must contain a YAML mapping: {path}")

        try:
            case = SkillEvalCase.model_validate(data)
        except ValidationError as exc:
            raise EvalCaseError(f"Invalid eval case {path}: {_format_validation_error(exc)}") from exc
        case.path = path
        return case

    def load_cases_from_directory(self, path: Path) -> list[SkillEvalCase]:
        if not path.is_dir():
            raise EvalCaseError(f"Eval cases directory does not exist: {path}")
        cases: list[SkillEvalCase] = []
        for case_path in sorted([*path.glob("*.yaml"), *path.glob("*.yml")], key=lambda item: item.name.lower()):
            cases.append(self.load_case(case_path))
        if not cases:
            raise EvalCaseError(f"No eval case YAML files found: {path}")
        return cases

    def evaluate(self, skill_name: str, skill_path: Path, cases: list[SkillEvalCase]) -> SkillEvalReport:
        skill_md = skill_path / "SKILL.md"
        try:
            content = skill_md.read_text(encoding="utf-8")
        except OSError as exc:
            raise EvalCaseError(f"Failed to read SKILL.md: {skill_md}") from exc

        results = [_evaluate_case(skill_name, content, case) for case in cases]
        passed = sum(1 for result in results if result.passed)
        report = SkillEvalReport(
            skill_name=skill_name,
            total=len(results),
            passed=passed,
            failed=len(results) - passed,
            results=results,
        )
        (skill_path / EVAL_REPORT_FILENAME).write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return report


def _evaluate_case(skill_name: str, content: str, case: SkillEvalCase) -> SkillEvalCaseResult:
    assertions: list[SkillEvalAssertionResult] = []
    if case.skill != skill_name:
        assertions.append(
            SkillEvalAssertionResult(
                passed=False,
                assertion="skill",
                message=f"Eval case targets {case.skill}, not {skill_name}.",
            )
        )

    for section in case.assertions.required_sections:
        marker = f"## {section}"
        assertions.append(
            SkillEvalAssertionResult(
                passed=marker in content,
                assertion="required_sections",
                message=f"Required section present: {section}" if marker in content else f"Missing required section: {section}",
            )
        )

    folded = content.casefold()
    for constraint in case.assertions.required_constraints:
        present = constraint.casefold() in folded
        assertions.append(
            SkillEvalAssertionResult(
                passed=present,
                assertion="required_constraints",
                message=f"Required constraint present: {constraint}" if present else f"Missing required constraint: {constraint}",
            )
        )

    for phrase in case.assertions.forbidden_phrases:
        absent = phrase.casefold() not in folded
        assertions.append(
            SkillEvalAssertionResult(
                passed=absent,
                assertion="forbidden_phrases",
                message=f"Forbidden phrase absent: {phrase}" if absent else f"Forbidden phrase found: {phrase}",
            )
        )

    return SkillEvalCaseResult(
        case_id=case.id,
        case_path=str(case.path) if case.path is not None else None,
        passed=all(assertion.passed for assertion in assertions),
        assertions=assertions,
    )


def _format_validation_error(error: ValidationError) -> str:
    issues: list[str] = []
    for issue in error.errors():
        location = ".".join(str(part) for part in issue["loc"])
        issues.append(f"{location}: {issue['msg']}")
    return "; ".join(issues)
