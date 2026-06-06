import json
import os
from typing import Any, Protocol

import httpx
from pydantic import BaseModel, Field

from skill_forge.models.requirement import SkillRequirement
from skill_forge.models.experience import AppliedExperienceRuleContext
from skill_forge.retrieval.generation import GenerationRetrievalContext


DEFAULT_LLM_BASE_URL = "https://api.openai.com/v1"
LLM_REQUIRED_ENV_VARS = ("SKILL_FORGE_LLM_API_KEY", "SKILL_FORGE_LLM_MODEL")
SUPPORTED_REFINEMENT_FIELDS = {
    "description",
    "domain",
    "task_type",
    "when_to_use",
    "when_not_to_use",
    "required_inputs",
    "workflow",
    "constraints",
    "expected_outputs",
    "quality_gates",
}
LIST_REFINEMENT_FIELDS = {
    "when_to_use",
    "when_not_to_use",
    "required_inputs",
    "workflow",
    "constraints",
    "expected_outputs",
    "quality_gates",
}
GENERATED_FIELDS = {"workflow", "constraints", "quality_gates"}
REFINED_FIELDS = SUPPORTED_REFINEMENT_FIELDS - GENERATED_FIELDS


class LLMConfigurationError(RuntimeError):
    pass


class LLMAvailabilityError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


class RequirementLLMClient(Protocol):
    def refine_requirement(
        self,
        requirement_text: str,
        requirement: SkillRequirement,
        retrieval_context: GenerationRetrievalContext | None = None,
        experience_context: AppliedExperienceRuleContext | None = None,
    ) -> str:
        """Return a JSON object string with supported requirement fields."""


class RequirementLLMRefinementResult(BaseModel):
    requirement: SkillRequirement
    generated_fields: list[str] = Field(default_factory=list)
    fallback_fields: list[str] = Field(default_factory=list)
    refined_fields: list[str] = Field(default_factory=list)
    fallback_reason: str | None = None
    retrieval_context: GenerationRetrievalContext | None = None


class OpenAICompatibleLLMClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = DEFAULT_LLM_BASE_URL,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    @classmethod
    def from_env(cls) -> "OpenAICompatibleLLMClient":
        missing = cls.missing_env_configuration()
        if missing:
            raise LLMConfigurationError(f"Missing LLM configuration: {', '.join(missing)}")

        return cls(
            api_key=os.environ["SKILL_FORGE_LLM_API_KEY"],
            model=os.environ["SKILL_FORGE_LLM_MODEL"],
            base_url=os.environ.get("SKILL_FORGE_LLM_BASE_URL", DEFAULT_LLM_BASE_URL),
        )

    @classmethod
    def missing_env_configuration(cls) -> list[str]:
        return [name for name in LLM_REQUIRED_ENV_VARS if not os.environ.get(name, "").strip()]

    @classmethod
    def has_required_env_configuration(cls) -> bool:
        return not cls.missing_env_configuration()

    def check_availability(self, *, timeout_seconds: float = 1.0) -> None:
        """Check provider availability.

        The initial intelligent fallback implementation uses env-only detection,
        so there is no network probe to perform here. The timeout argument keeps
        the availability boundary explicit and testable if a bounded probe is
        added later.
        """
        if timeout_seconds >= 2:
            raise LLMAvailabilityError("LLM availability probe timeout must be shorter than two seconds.")

    def refine_requirement(
        self,
        requirement_text: str,
        requirement: SkillRequirement,
        retrieval_context: GenerationRetrievalContext | None = None,
        experience_context: AppliedExperienceRuleContext | None = None,
    ) -> str:
        user_content = {
            "requirement_text": requirement_text,
            "analyzed_requirement": requirement.model_dump(
                exclude={"references", "assets", "scripts"}
            ),
        }
        if retrieval_context is not None and retrieval_context.used:
            user_content["retrieval_reference_patterns"] = {
                "source_names": retrieval_context.source_names,
                "workflow_patterns": retrieval_context.workflow_patterns,
                "constraint_patterns": retrieval_context.constraint_patterns,
                "quality_gate_patterns": retrieval_context.quality_gate_patterns,
                "instruction": (
                    "Use these as reference patterns for specificity and coverage. "
                    "Do not copy them verbatim unless they exactly match the user's task."
                ),
            }
        if experience_context is not None and experience_context.used:
            user_content["experience_rule_guidance"] = {
                "rule_ids": experience_context.rule_ids,
                "summaries": experience_context.rule_summaries,
                "instruction": (
                    "Use these rules as guidance for improving workflow, constraints, and quality gates. "
                    "Do not copy them verbatim unless they exactly match the user's task."
                ),
            }
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Generate task-specific Skill Forge requirement fields. "
                        "Use the analyzed requirement and any blueprint or project-context defaults as input. "
                        "Create concrete workflow, constraints, and quality_gates for this task when useful, "
                        "and refine descriptive fields only when you can make them more specific. "
                        "If retrieval reference patterns are provided, use them only as guidance for structure, "
                        "specificity, and checkability; do not copy unrelated examples. "
                        "If experience rule guidance is provided, use it only as guidance for improvement and not as copied output. "
                        "Return only a JSON object. Use only these keys when useful: "
                        + ", ".join(sorted(SUPPORTED_REFINEMENT_FIELDS))
                        + ". List fields must be arrays of strings. Do not wrap field values in Markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(user_content, ensure_ascii=False),
                },
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

        try:
            response = httpx.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise LLMResponseError(f"LLM request failed: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMResponseError("LLM response did not include message content.") from exc
        if not isinstance(content, str) or not content.strip():
            raise LLMResponseError("LLM response content was empty.")
        return content


class RequirementLLMRefiner:
    def __init__(self, client: RequirementLLMClient) -> None:
        self._client = client

    def refine(
        self,
        requirement_text: str,
        requirement: SkillRequirement,
        retrieval_context: GenerationRetrievalContext | None = None,
        experience_context: AppliedExperienceRuleContext | None = None,
    ) -> SkillRequirement:
        return self.refine_with_metadata(
            requirement_text,
            requirement,
            retrieval_context=retrieval_context,
            experience_context=experience_context,
        ).requirement

    def refine_with_metadata(
        self,
        requirement_text: str,
        requirement: SkillRequirement,
        retrieval_context: GenerationRetrievalContext | None = None,
        experience_context: AppliedExperienceRuleContext | None = None,
    ) -> RequirementLLMRefinementResult:
        baseline = requirement.model_copy(deep=True)
        try:
            raw_response = _call_refine_requirement(
                self._client,
                requirement_text,
                requirement,
                retrieval_context,
                experience_context,
            )
            data = _parse_json_object(raw_response)
        except LLMResponseError as exc:
            return RequirementLLMRefinementResult(
                requirement=baseline,
                fallback_fields=_fallback_fields_for_requirement(baseline),
                fallback_reason=str(exc),
                retrieval_context=retrieval_context,
            )

        updates, generated_fields, refined_fields, fallback_fields = _supported_updates(data)
        if not updates:
            return RequirementLLMRefinementResult(
                requirement=baseline,
                fallback_fields=fallback_fields,
                retrieval_context=retrieval_context,
            )
        return RequirementLLMRefinementResult(
            requirement=baseline.model_copy(update=updates, deep=True),
            generated_fields=generated_fields,
            refined_fields=refined_fields,
            fallback_fields=fallback_fields,
            retrieval_context=retrieval_context,
        )


def _call_refine_requirement(
    client: RequirementLLMClient,
    requirement_text: str,
    requirement: SkillRequirement,
    retrieval_context: GenerationRetrievalContext | None,
    experience_context: AppliedExperienceRuleContext | None,
) -> str:
    attempts: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    if retrieval_context is not None and experience_context is not None:
        attempts.extend(
            [
                ((requirement_text, requirement, retrieval_context), {"experience_context": experience_context}),
                ((requirement_text, requirement, retrieval_context), {}),
                ((requirement_text, requirement), {"experience_context": experience_context}),
            ]
        )
    elif retrieval_context is not None:
        attempts.extend(
            [
                ((requirement_text, requirement, retrieval_context), {}),
                ((requirement_text, requirement), {}),
            ]
        )
    elif experience_context is not None:
        attempts.extend(
            [
                ((requirement_text, requirement), {"experience_context": experience_context}),
                ((requirement_text, requirement), {}),
            ]
        )
    else:
        attempts.append(((requirement_text, requirement), {}))

    last_error: TypeError | None = None
    for args, kwargs in attempts:
        try:
            return client.refine_requirement(*args, **kwargs)
        except TypeError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    return client.refine_requirement(requirement_text, requirement)


def _parse_json_object(raw_response: str) -> dict[str, Any]:
    text = raw_response.strip()
    if not text:
        raise LLMResponseError("LLM response content was empty.")
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(f"LLM response was not valid JSON: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise LLMResponseError("LLM response must be a JSON object.")
    return data


def _supported_updates(data: dict[str, Any]) -> tuple[dict[str, str | list[str]], list[str], list[str], list[str]]:
    updates: dict[str, str | list[str]] = {}
    generated_fields: list[str] = []
    refined_fields: list[str] = []
    fallback_fields: list[str] = []
    for field, value in data.items():
        if field not in SUPPORTED_REFINEMENT_FIELDS:
            continue
        if field in LIST_REFINEMENT_FIELDS:
            if not isinstance(value, list):
                fallback_fields.append(field)
                continue
            items = [item.strip() for item in value if isinstance(item, str) and item.strip()]
            if items:
                updates[field] = items
                _append_field_kind(field, generated_fields, refined_fields)
            else:
                fallback_fields.append(field)
            continue
        if isinstance(value, str) and value.strip():
            updates[field] = value.strip()
            _append_field_kind(field, generated_fields, refined_fields)
        else:
            fallback_fields.append(field)
    return updates, generated_fields, refined_fields, fallback_fields


def _append_field_kind(field: str, generated_fields: list[str], refined_fields: list[str]) -> None:
    if field in GENERATED_FIELDS:
        generated_fields.append(field)
    elif field in REFINED_FIELDS:
        refined_fields.append(field)


def _fallback_fields_for_requirement(requirement: SkillRequirement) -> list[str]:
    fields = []
    for field in sorted(GENERATED_FIELDS):
        value = getattr(requirement, field)
        if value:
            fields.append(field)
    return fields
