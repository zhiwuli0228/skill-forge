from pathlib import Path

import pytest

from skill_forge.models.draft import DraftStatus, SkillDraftState
from skill_forge.requirement.analyzer import RequirementAnalyzer
from skill_forge.storage.draft_store import DraftNotFoundError, DraftStore


def test_draft_state_defaults_and_serialization() -> None:
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")

    draft = SkillDraftState(draft_id="draft-1", requirement=requirement)
    reloaded = SkillDraftState.model_validate_json(draft.model_dump_json())

    assert draft.status == DraftStatus.DRAFT
    assert draft.current_step == "name"
    assert draft.selected_examples == []
    assert reloaded.draft_id == "draft-1"
    assert reloaded.requirement.name == "java-bug-investigation"
    assert reloaded.created_at.tzinfo is not None


def test_draft_store_saves_and_loads_by_id(tmp_path: Path) -> None:
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")
    draft = SkillDraftState(draft_id="draft-1", requirement=requirement)
    store = DraftStore(tmp_path)

    path = store.save(draft)
    loaded = store.load("draft-1")

    assert path == tmp_path / "draft-1.json"
    assert loaded.draft_id == "draft-1"
    assert loaded.requirement.name == "java-bug-investigation"
    assert "updated_at" in path.read_text(encoding="utf-8")


def test_draft_store_raises_for_missing_draft(tmp_path: Path) -> None:
    with pytest.raises(DraftNotFoundError):
        DraftStore(tmp_path).load("missing")
