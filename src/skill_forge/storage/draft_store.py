from pathlib import Path

from skill_forge.models.draft import SkillDraftState


class DraftNotFoundError(FileNotFoundError):
    def __init__(self, draft_id: str, path: Path) -> None:
        super().__init__(f"Draft not found: {draft_id}")
        self.draft_id = draft_id
        self.path = path


class DraftStore:
    def __init__(self, drafts_dir: Path) -> None:
        self._drafts_dir = drafts_dir

    def path_for(self, draft_id: str) -> Path:
        return self._drafts_dir / f"{draft_id}.json"

    def save(self, draft: SkillDraftState) -> Path:
        self._drafts_dir.mkdir(parents=True, exist_ok=True)
        draft.touch()
        path = self.path_for(draft.draft_id)
        path.write_text(draft.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load(self, draft_id: str) -> SkillDraftState:
        path = self.path_for(draft_id)
        if not path.is_file():
            raise DraftNotFoundError(draft_id, path)
        return SkillDraftState.model_validate_json(path.read_text(encoding="utf-8"))
