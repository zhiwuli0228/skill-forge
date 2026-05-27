import pytest

from skill_forge.llm.refiner import (
    LLMConfigurationError,
    LLMResponseError,
    OpenAICompatibleLLMClient,
    RequirementLLMRefiner,
)
from skill_forge.requirement.analyzer import RequirementAnalyzer


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def refine_requirement(self, requirement_text, requirement) -> str:
        self.calls += 1
        return self.response


def test_llm_refiner_merges_supported_fields() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient(
        """
        {
          "description": "Use this skill for release readiness checks.",
          "workflow": ["Confirm release scope", "Check rollout risks"],
          "constraints": ["Do not skip rollback planning"]
        }
        """
    )

    refined = RequirementLLMRefiner(client).refine("整理团队发布流程 skill", requirement)

    assert client.calls == 1
    assert refined.description == "Use this skill for release readiness checks."
    assert refined.workflow == ["Confirm release scope", "Check rollout risks"]
    assert refined.constraints == ["Do not skip rollback planning"]
    assert refined.name == requirement.name


def test_llm_refiner_ignores_unknown_fields() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient('{"description": "Refined description.", "unknown": "ignored"}')

    refined = RequirementLLMRefiner(client).refine("整理团队发布流程 skill", requirement)

    assert refined.description == "Refined description."
    assert not hasattr(refined, "unknown")


def test_llm_refiner_rejects_malformed_json() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient("not-json")

    with pytest.raises(LLMResponseError, match="not valid JSON"):
        RequirementLLMRefiner(client).refine("整理团队发布流程 skill", requirement)


def test_llm_refiner_rejects_invalid_list_field() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient('{"workflow": "not a list"}')

    with pytest.raises(LLMResponseError, match="workflow"):
        RequirementLLMRefiner(client).refine("整理团队发布流程 skill", requirement)


def test_openai_compatible_client_reports_missing_configuration(monkeypatch) -> None:
    monkeypatch.delenv("SKILL_FORGE_LLM_API_KEY", raising=False)
    monkeypatch.delenv("SKILL_FORGE_LLM_MODEL", raising=False)

    with pytest.raises(LLMConfigurationError) as exc:
        OpenAICompatibleLLMClient.from_env()

    assert "SKILL_FORGE_LLM_API_KEY" in str(exc.value)
    assert "SKILL_FORGE_LLM_MODEL" in str(exc.value)
