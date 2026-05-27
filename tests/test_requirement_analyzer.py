import pytest

from skill_forge.requirement.analyzer import RequirementAnalyzer


JAVA_BUG_REQUIREMENT = (
    "我需要一个用于 Java 存量代码 bug 定位的 skill，"
    "要求先分析日志，再读代码，不能直接修改代码，要输出根因、修复方案和测试建议。"
)


def test_analyzer_parses_java_bug_investigation_example() -> None:
    requirement = RequirementAnalyzer().analyze(JAVA_BUG_REQUIREMENT)

    assert requirement.name == "java-bug-investigation"
    assert requirement.domain == "software-engineering"
    assert requirement.task_type == "bug-investigation"
    assert "先分析日志和证据" in requirement.constraints
    assert "未定位根因前不要修改代码" in requirement.constraints
    assert "Root Cause" in requirement.expected_outputs
    assert "Fix Plan" in requirement.expected_outputs
    assert "Test Plan" in requirement.expected_outputs


def test_analyzer_provides_defaults_for_vague_requirement() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")

    assert requirement.name.endswith("-skill")
    assert requirement.description
    assert requirement.when_to_use
    assert requirement.when_not_to_use
    assert requirement.workflow
    assert requirement.expected_outputs
    assert requirement.quality_gates
    assert requirement.target_platform == "opencode"
    assert requirement.language == "zh-CN"


def test_analyzer_recognizes_code_review_requirement() -> None:
    requirement = RequirementAnalyzer().analyze("Python 代码审查 skill")

    assert requirement.name == "code-review"
    assert requirement.domain == "software-engineering"
    assert requirement.task_type == "code-review"


def test_analyzer_recognizes_test_generation_requirement() -> None:
    requirement = RequirementAnalyzer().analyze("为这个项目生成测试编写 skill")

    assert requirement.name == "test-generation"
    assert requirement.domain == "software-engineering"
    assert requirement.task_type == "test-generation"


def test_analyzer_recognizes_openspec_change_requirement() -> None:
    requirement = RequirementAnalyzer().analyze("OpenSpec change 分析 skill")

    assert requirement.name == "openspec-change"
    assert requirement.domain == "software-engineering"
    assert requirement.task_type == "openspec-change"


def test_analyzer_rejects_empty_requirement() -> None:
    with pytest.raises(ValueError, match="Requirement cannot be empty"):
        RequirementAnalyzer().analyze("  ")
