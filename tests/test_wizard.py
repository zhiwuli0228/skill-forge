from pathlib import Path

from skill_forge.interaction.wizard import SkillCreationWizard
from skill_forge.models.draft import DraftStatus, SkillDraftState
from skill_forge.requirement.analyzer import RequirementAnalyzer
from skill_forge.storage.draft_store import DraftStore


class FakePromptAdapter:
    def __init__(self) -> None:
        self.text_calls: list[str] = []
        self.multiline_calls: list[str] = []

    def text(self, message: str, default: str = "") -> str:
        self.text_calls.append(message)
        return default

    def multiline(self, message: str, default: list[str]) -> list[str]:
        self.multiline_calls.append(message)
        return default


def _wizard(tmp_path: Path, adapter: FakePromptAdapter) -> SkillCreationWizard:
    return SkillCreationWizard(
        draft_store=DraftStore(tmp_path / "drafts"),
        output_dir=tmp_path / "output",
        prompt_adapter=adapter,
    )


def test_wizard_progresses_steps_and_persists_draft(tmp_path: Path) -> None:
    adapter = FakePromptAdapter()
    wizard = _wizard(tmp_path, adapter)
    draft = wizard.create_draft(RequirementAnalyzer().analyze("Java bug 定位 skill"))

    result = wizard.run(draft)
    saved = DraftStore(tmp_path / "drafts").load(draft.draft_id)

    assert result.status == DraftStatus.GENERATED
    assert result.current_step == "generated"
    assert result.generated_package is not None
    assert saved.status == DraftStatus.GENERATED
    assert saved.generated_package is not None
    assert (tmp_path / "output" / "java-bug-investigation" / "SKILL.md").is_file()
    assert adapter.text_calls == ["Skill name"]
    assert "Workflow" in adapter.multiline_calls


def test_wizard_resume_skips_completed_steps(tmp_path: Path) -> None:
    adapter = FakePromptAdapter()
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")
    draft = SkillDraftState(
        draft_id="draft-1",
        requirement=requirement,
        current_step="workflow",
        status=DraftStatus.IN_PROGRESS,
    )
    store = DraftStore(tmp_path / "drafts")
    store.save(draft)

    result = SkillCreationWizard(draft_store=store, output_dir=tmp_path / "output", prompt_adapter=adapter).run(
        store.load("draft-1")
    )

    assert result.status == DraftStatus.GENERATED
    assert adapter.text_calls == []
    assert adapter.multiline_calls == ["Workflow", "Expected outputs", "Quality gates"]


def test_wizard_generates_ready_draft_without_reprompting(tmp_path: Path) -> None:
    adapter = FakePromptAdapter()
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")
    draft = SkillDraftState(
        draft_id="draft-1",
        requirement=requirement,
        current_step="generate",
        status=DraftStatus.READY_TO_GENERATE,
    )
    store = DraftStore(tmp_path / "drafts")
    store.save(draft)

    result = SkillCreationWizard(draft_store=store, output_dir=tmp_path / "output", prompt_adapter=adapter).run(
        store.load("draft-1")
    )

    assert result.status == DraftStatus.GENERATED
    assert adapter.text_calls == []
    assert adapter.multiline_calls == []
