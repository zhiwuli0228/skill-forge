from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from skill_forge.models.collection import (
    CollectionRecord,
    CollectionState,
    ScoreSnapshot,
)


class CollectionStore:
    def __init__(self, collections_dir: Path) -> None:
        self._collections_dir = collections_dir.expanduser()

    @property
    def collections_dir(self) -> Path:
        return self._collections_dir

    @property
    def manifests_dir(self) -> Path:
        return self._collections_dir / "manifests"

    @property
    def snapshots_dir(self) -> Path:
        return self._collections_dir / "snapshots"

    @property
    def indexes_dir(self) -> Path:
        return self._collections_dir / "indexes"

    def ensure_directories(self) -> None:
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.indexes_dir.mkdir(parents=True, exist_ok=True)

    def list_records(self) -> list[CollectionRecord]:
        if not self.manifests_dir.exists():
            return []
        records: list[CollectionRecord] = []
        for path in sorted(self.manifests_dir.glob("*.json"), key=lambda p: p.name.lower()):
            record = self._read_record(path)
            if record is not None:
                records.append(record)
        return records

    def read_record(self, skill_id: str) -> CollectionRecord | None:
        return self._read_record(self._record_path(skill_id))

    def write_record(self, record: CollectionRecord) -> Path:
        self.ensure_directories()
        path = self._record_path(record.skill_id)
        path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
        return path

    def update_state(
        self,
        skill_id: str,
        *,
        state: CollectionState,
        rationale: str | None = None,
        manual: bool = True,
    ) -> CollectionRecord | None:
        record = self.read_record(skill_id)
        if record is None:
            return None
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        record.collection_state = state
        record.manual_override = manual
        record.updated_at = now
        record.last_verified_at = now
        if rationale is not None:
            record.rationale = rationale
        self.write_record(record)
        return record

    def delete_record(self, skill_id: str) -> bool:
        path = self._record_path(skill_id)
        if not path.is_file():
            return False
        path.unlink()
        return True

    def write_snapshot(self, snapshot: ScoreSnapshot) -> Path:
        self.ensure_directories()
        path = self.snapshots_dir / f"{snapshot.skill_id}.json"
        path.write_text(snapshot.model_dump_json(indent=2), encoding="utf-8")
        return path

    def read_snapshot(self, skill_id: str) -> ScoreSnapshot | None:
        path = self.snapshots_dir / f"{skill_id}.json"
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ScoreSnapshot.model_validate(data)
        except (OSError, json.JSONDecodeError, ValidationError):
            return None

    def list_by_state(self, state: CollectionState) -> list[CollectionRecord]:
        return [r for r in self.list_records() if r.collection_state == state]

    def exists(self, skill_id: str) -> bool:
        return self._record_path(skill_id).is_file()

    def _record_path(self, skill_id: str) -> Path:
        return self.manifests_dir / f"{skill_id}.json"

    def _read_record(self, path: Path) -> CollectionRecord | None:
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return CollectionRecord.model_validate(data)
        except (OSError, json.JSONDecodeError, ValidationError):
            return None
