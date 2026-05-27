import json
import os
from typing import Any, Protocol

import httpx

from skill_forge.models.requirement import SkillRequirement


DEFAULT_LLM_BASE_URL = "https://api.openai.com/v1"
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


class LLMConfigurationError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


class RequirementLLMClient(Protocol):
    def refine_requirement(self, requirement_text: str, requirement: SkillRequirement) -> str:
        """Return a JSON object string with supported requirement fields."""


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
        missing = [
            name
            for name in ("SKILL_FORGE_LLM_API_KEY", "SKILL_FORGE_LLM_MODEL")
            if not os.environ.get(name, "").strip()
        ]
        if missing:
            raise LLMConfigurationError(f"Missing LLM configuration: {', '.join(missing)}")

        return cls(
            api_key=os.environ["SKILL_FORGE_LLM_API_KEY"],
            model=os.environ["SKILL_FORGE_LLM_MODEL"],
            base_url=os.environ.get("SKILL_FORGE_LLM_BASE_URL", DEFAULT_LLM_BASE_URL),
        )

    def refine_requirement(self, requirement_text: str, requirement: SkillRequirement) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You refine Skill Forge generation requirements. "
                        "Return only a JSON object. Use only these keys when useful: "
                        + ", ".join(sorted(SUPPORTED_REFINEMENT_FIELDS))
                        + ". List fields must be arrays of strings."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "requirement_text": requirement_text,
                            "analyzed_requirement": requirement.model_dump(
                                exclude={"references", "assets", "scripts"}
                            ),
                        },
                        ensure_ascii=False,
                    ),
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

    def refine(self, requirement_text: str, requirement: SkillRequirement) -> SkillRequirement:
        raw_response = self._client.refine_requirement(requirement_text, requirement)
        data = _parse_json_object(raw_response)
        updates = _supported_updates(data)
        if not updates:
            return requirement.model_copy(deep=True)
        return requirement.model_copy(update=updates, deep=True)


def _parse_json_object(raw_response: str) -> dict[str, Any]:
    text = raw_response.strip()
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


def _supported_updates(data: dict[str, Any]) -> dict[str, str | list[str]]:
    updates: dict[str, str | list[str]] = {}
    for field, value in data.items():
        if field not in SUPPORTED_REFINEMENT_FIELDS:
            continue
        if field in LIST_REFINEMENT_FIELDS:
            if not isinstance(value, list):
                raise LLMResponseError(f"LLM field `{field}` must be a list of strings.")
            items = [item.strip() for item in value if isinstance(item, str) and item.strip()]
            if items:
                updates[field] = items
            continue
        if isinstance(value, str) and value.strip():
            updates[field] = value.strip()
    return updates
