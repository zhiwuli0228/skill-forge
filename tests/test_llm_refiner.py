import pytest

from skill_forge.llm.refiner import (
    LLMConfigurationError,
    LLMResponseError,
    OpenAICompatibleLLMClient,
    RequirementLLMRefiner,
)
from skill_forge.models.experience import AppliedExperienceRuleContext
from skill_forge.retrieval.generation import GenerationRetrievalContext
from skill_forge.requirement.analyzer import RequirementAnalyzer


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def refine_requirement(self, requirement_text, requirement) -> str:
        self.calls += 1
        return self.response


class ContextAwareFakeLLMClient(FakeLLMClient):
    def __init__(self, response: str) -> None:
        super().__init__(response)
        self.seen_contexts = []
        self.seen_experience_contexts = []

    def refine_requirement(
        self,
        requirement_text,
        requirement,
        retrieval_context=None,
        experience_context=None,
    ) -> str:
        self.calls += 1
        self.seen_contexts.append(retrieval_context)
        self.seen_experience_contexts.append(experience_context)
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

    result = RequirementLLMRefiner(client).refine_with_metadata("整理团队发布流程 skill", requirement)
    refined = result.requirement

    assert client.calls == 1
    assert refined.description == "Use this skill for release readiness checks."
    assert refined.workflow == ["Confirm release scope", "Check rollout risks"]
    assert refined.constraints == ["Do not skip rollback planning"]
    assert refined.name == requirement.name
    assert result.generated_fields == ["workflow", "constraints"]
    assert result.refined_fields == ["description"]
    assert result.fallback_fields == []


def test_llm_refiner_generates_core_quality_fields() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient(
        """
        {
          "workflow": ["Confirm release scope", "Check rollout risks"],
          "constraints": ["Rollback evidence must be documented"],
          "quality_gates": ["Pass when rollback owner and release window are verified"]
        }
        """
    )

    result = RequirementLLMRefiner(client).refine_with_metadata("整理团队发布流程 skill", requirement)

    assert result.requirement.workflow == ["Confirm release scope", "Check rollout risks"]
    assert result.requirement.constraints == ["Rollback evidence must be documented"]
    assert result.requirement.quality_gates == ["Pass when rollback owner and release window are verified"]
    assert result.generated_fields == ["workflow", "constraints", "quality_gates"]


def test_llm_refiner_ignores_unknown_fields() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient('{"description": "Refined description.", "unknown": "ignored"}')

    refined = RequirementLLMRefiner(client).refine("整理团队发布流程 skill", requirement)

    assert refined.description == "Refined description."
    assert not hasattr(refined, "unknown")


def test_llm_refiner_falls_back_on_malformed_json() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient("not-json")

    result = RequirementLLMRefiner(client).refine_with_metadata("整理团队发布流程 skill", requirement)

    assert result.requirement == requirement
    assert result.fallback_reason
    assert "not valid JSON" in result.fallback_reason


def test_llm_refiner_falls_back_on_invalid_list_field() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    requirement.workflow = ["Keep existing workflow"]
    client = FakeLLMClient('{"workflow": "not a list"}')

    result = RequirementLLMRefiner(client).refine_with_metadata("整理团队发布流程 skill", requirement)

    assert result.requirement.workflow == ["Keep existing workflow"]
    assert result.fallback_fields == ["workflow"]


def test_llm_refiner_passes_retrieval_context_to_client() -> None:
    requirement = RequirementAnalyzer().analyze("Java bug investigation skill")
    client = ContextAwareFakeLLMClient('{"workflow": ["Inspect logs before code changes"]}')
    retrieval_context = GenerationRetrievalContext(
        used=True,
        source_names=["Bug Investigation#1"],
        workflow_patterns=["Inspect logs before editing code"],
        constraint_patterns=["Do not change code before evidence is documented"],
        quality_gate_patterns=["Pass when evidence links logs to code"],
    )

    result = RequirementLLMRefiner(client).refine_with_metadata(
        "Java bug investigation skill",
        requirement,
        retrieval_context=retrieval_context,
    )

    assert client.seen_contexts == [retrieval_context]
    assert result.retrieval_context == retrieval_context
    assert result.requirement.workflow == ["Inspect logs before code changes"]


def test_llm_refiner_passes_experience_context_to_client() -> None:
    requirement = RequirementAnalyzer().analyze("Java bug investigation skill")
    client = ContextAwareFakeLLMClient('{"workflow": ["Inspect logs before code changes"]}')
    experience_context = AppliedExperienceRuleContext(
        used=True,
        task_type="bug-investigation",
        rule_ids=["experience-123"],
        rule_summaries=["For bug-investigation, confirm logs before code changes."],
    )

    result = RequirementLLMRefiner(client).refine_with_metadata(
        "Java bug investigation skill",
        requirement,
        experience_context=experience_context,
    )

    assert client.seen_experience_contexts == [experience_context]
    assert result.requirement.workflow == ["Inspect logs before code changes"]


def test_llm_refiner_preserves_field_fallback_with_retrieval_context() -> None:
    requirement = RequirementAnalyzer().analyze("Java bug investigation skill")
    requirement.workflow = ["Keep existing workflow"]
    client = ContextAwareFakeLLMClient('{"workflow": "not a list", "unknown": "ignored"}')
    retrieval_context = GenerationRetrievalContext(used=True, source_names=["Bug Investigation#1"])

    result = RequirementLLMRefiner(client).refine_with_metadata(
        "Java bug investigation skill",
        requirement,
        retrieval_context=retrieval_context,
    )

    assert result.requirement.workflow == ["Keep existing workflow"]
    assert result.fallback_fields == ["workflow"]
    assert result.retrieval_context == retrieval_context


def test_llm_refiner_falls_back_on_empty_response() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient("")

    result = RequirementLLMRefiner(client).refine_with_metadata("整理团队发布流程 skill", requirement)

    assert result.requirement == requirement
    assert result.fallback_reason == "LLM response content was empty."


def test_llm_refiner_falls_back_on_non_object_json() -> None:
    requirement = RequirementAnalyzer().analyze("整理团队发布流程 skill")
    client = FakeLLMClient("[]")

    result = RequirementLLMRefiner(client).refine_with_metadata("整理团队发布流程 skill", requirement)

    assert result.requirement == requirement
    assert result.fallback_reason == "LLM response must be a JSON object."


def test_openai_compatible_client_reports_missing_configuration(monkeypatch) -> None:
    monkeypatch.delenv("SKILL_FORGE_LLM_API_KEY", raising=False)
    monkeypatch.delenv("SKILL_FORGE_LLM_MODEL", raising=False)

    with pytest.raises(LLMConfigurationError) as exc:
        OpenAICompatibleLLMClient.from_env()

    assert "SKILL_FORGE_LLM_API_KEY" in str(exc.value)
    assert "SKILL_FORGE_LLM_MODEL" in str(exc.value)


def test_openai_compatible_client_detects_env_configuration(monkeypatch) -> None:
    monkeypatch.delenv("SKILL_FORGE_LLM_API_KEY", raising=False)
    monkeypatch.delenv("SKILL_FORGE_LLM_MODEL", raising=False)

    assert OpenAICompatibleLLMClient.has_required_env_configuration() is False
    assert OpenAICompatibleLLMClient.missing_env_configuration() == [
        "SKILL_FORGE_LLM_API_KEY",
        "SKILL_FORGE_LLM_MODEL",
    ]

    monkeypatch.setenv("SKILL_FORGE_LLM_API_KEY", "test-key")
    monkeypatch.setenv("SKILL_FORGE_LLM_MODEL", "test-model")

    assert OpenAICompatibleLLMClient.has_required_env_configuration() is True
    assert OpenAICompatibleLLMClient.missing_env_configuration() == []
