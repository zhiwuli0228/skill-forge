import json
from pathlib import Path

import pytest

from skill_forge.evals.runner import EvalCaseError, SkillEvaluator


def _write_skill(output_dir: Path, name: str, content: str | None = None) -> Path:
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        content
        or """---
name: sample-skill
description: Use this skill for code review. Do not use it for unrelated work.
---

# sample-skill

## Findings

Findings first, with concrete defects and evidence.

## Tests

Always mention tests reviewed.
""",
        encoding="utf-8",
    )
    return skill_dir


def _write_case(path: Path, *, case_id: str = "review-basic", skill: str = "sample-skill") -> Path:
    path.write_text(
        f"""id: {case_id}
skill: {skill}
input:
  request: Review this pull request.
assertions:
  required_sections:
    - Findings
    - Tests
  required_constraints:
    - Findings first
  forbidden_phrases:
    - looks good
""",
        encoding="utf-8",
    )
    return path


def test_eval_loader_reads_valid_case(tmp_path: Path) -> None:
    case_path = _write_case(tmp_path / "case.yaml")

    case = SkillEvaluator().load_case(case_path)

    assert case.id == "review-basic"
    assert case.skill == "sample-skill"
    assert case.input.request == "Review this pull request."
    assert case.assertions.required_sections == ["Findings", "Tests"]
    assert case.path == case_path


def test_eval_loader_rejects_invalid_case(tmp_path: Path) -> None:
    case_path = tmp_path / "case.yaml"
    case_path.write_text("id: missing-assertions\nskill: sample-skill\n", encoding="utf-8")

    with pytest.raises(EvalCaseError, match="Invalid eval case"):
        SkillEvaluator().load_case(case_path)


def test_eval_loader_discovers_yaml_and_yml_in_deterministic_order(tmp_path: Path) -> None:
    _write_case(tmp_path / "b.yml", case_id="b")
    _write_case(tmp_path / "a.yaml", case_id="a")
    (tmp_path / "ignored.txt").write_text("ignored", encoding="utf-8")

    cases = SkillEvaluator().load_cases_from_directory(tmp_path)

    assert [case.id for case in cases] == ["a", "b"]


def test_evaluator_passes_and_persists_report(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "sample-skill")
    case = SkillEvaluator().load_case(_write_case(tmp_path / "case.yaml"))

    report = SkillEvaluator().evaluate("sample-skill", skill_dir, [case])

    report_path = skill_dir / "eval-report.json"
    assert report.total == 1
    assert report.passed == 1
    assert report.failed == 0
    assert report_path.is_file()
    assert json.loads(report_path.read_text(encoding="utf-8"))["passed"] == 1


def test_evaluator_reports_failed_assertions(tmp_path: Path) -> None:
    skill_dir = _write_skill(
        tmp_path,
        "sample-skill",
        """---
name: sample-skill
description: Use this skill for code review.
---

# sample-skill

## Notes

Looks good.
""",
    )
    case = SkillEvaluator().load_case(_write_case(tmp_path / "case.yaml"))

    report = SkillEvaluator().evaluate("sample-skill", skill_dir, [case])

    assert report.passed == 0
    assert report.failed == 1
    messages = [assertion.message for assertion in report.results[0].assertions]
    assert "Missing required section: Findings" in messages
    assert "Forbidden phrase found: looks good" in messages
