from pathlib import Path
from typing import Protocol
from uuid import uuid4

import questionary

from skill_forge.generator.skill_generator import SkillGenerator
from skill_forge.models.draft import DraftStatus, SkillDraftState
from skill_forge.models.requirement import SkillRequirement
from skill_forge.storage.draft_store import DraftStore


class PromptAdapter(Protocol):
    def text(self, message: str, default: str = "") -> str: ...

    def multiline(self, message: str, default: list[str]) -> list[str]: ...


class QuestionaryPromptAdapter:
    def text(self, message: str, default: str = "") -> str:
        answer = questionary.text(message, default=default).ask()
        return default if answer is None else answer

    def multiline(self, message: str, default: list[str]) -> list[str]:
        default_text = "\n".join(default)
        answer = questionary.text(message, default=default_text).ask()
        if answer is None:
            answer = default_text
        return _parse_lines(answer)


class SkillCreationWizard:
    STEPS = (
        "name",
        "when_to_use",
        "when_not_to_use",
        "workflow",
        "expected_outputs",
        "quality_gates",
    )

    def __init__(
        self,
        *,
        draft_store: DraftStore,
        output_dir: Path,
        prompt_adapter: PromptAdapter | None = None,
        generator: SkillGenerator | None = None,
    ) -> None:
        self._draft_store = draft_store
        self._output_dir = output_dir
        self._prompt_adapter = prompt_adapter or QuestionaryPromptAdapter()
        self._generator = generator or SkillGenerator()

    def create_draft(self, requirement: SkillRequirement) -> SkillDraftState:
        draft = SkillDraftState(
            draft_id=uuid4().hex,
            requirement=requirement,
            status=DraftStatus.IN_PROGRESS,
            current_step=self.STEPS[0],
        )
        self._draft_store.save(draft)
        return draft

    def run(self, draft: SkillDraftState) -> SkillDraftState:
        if draft.status not in {DraftStatus.IN_PROGRESS, DraftStatus.DRAFT}:
            return self._generate_if_ready(draft)

        draft.status = DraftStatus.IN_PROGRESS
        start_index = self._step_index(draft.current_step)
        for step in self.STEPS[start_index:]:
            draft.current_step = step
            self._apply_step(draft, step)
            next_index = self._step_index(step) + 1
            draft.current_step = self.STEPS[next_index] if next_index < len(self.STEPS) else "generate"
            self._draft_store.save(draft)

        draft.status = DraftStatus.READY_TO_GENERATE
        draft.current_step = "generate"
        self._draft_store.save(draft)
        return self._generate_if_ready(draft)

    def _generate_if_ready(self, draft: SkillDraftState) -> SkillDraftState:
        if draft.status == DraftStatus.READY_TO_GENERATE:
            package = self._generator.generate(draft.requirement, self._output_dir)
            draft.generated_package = package
            draft.status = DraftStatus.GENERATED
            draft.current_step = "generated"
            self._draft_store.save(draft)
        return draft

    def _apply_step(self, draft: SkillDraftState, step: str) -> None:
        requirement = draft.requirement
        match step:
            case "name":
                requirement.name = self._prompt_adapter.text("Skill name", requirement.name).strip() or requirement.name
            case "when_to_use":
                requirement.when_to_use = self._prompt_adapter.multiline("When to use", requirement.when_to_use)
            case "when_not_to_use":
                requirement.when_not_to_use = self._prompt_adapter.multiline(
                    "When not to use", requirement.when_not_to_use
                )
            case "workflow":
                requirement.workflow = self._prompt_adapter.multiline("Workflow", requirement.workflow)
            case "expected_outputs":
                requirement.expected_outputs = self._prompt_adapter.multiline(
                    "Expected outputs", requirement.expected_outputs
                )
            case "quality_gates":
                requirement.quality_gates = self._prompt_adapter.multiline("Quality gates", requirement.quality_gates)
            case _:
                raise ValueError(f"Unknown wizard step: {step}")

    def _step_index(self, step: str) -> int:
        if step == "generate":
            return len(self.STEPS)
        if step not in self.STEPS:
            return 0
        return self.STEPS.index(step)


def _parse_lines(value: str) -> list[str]:
    return [line.strip(" -\t") for line in value.splitlines() if line.strip(" -\t")]
