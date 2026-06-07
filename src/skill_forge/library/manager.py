from __future__ import annotations

import difflib
import json
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from skill_forge.models.eval import EVAL_REPORT_FILENAME, SkillEvalReport
from skill_forge.models.generated import PROVENANCE_METADATA_FILENAME, GenerationProvenanceMetadata
from skill_forge.models.library import SkillLibraryEntry
from skill_forge.storage.collection_store import CollectionStore


class GeneratedSkillNotFoundError(RuntimeError):
    def __init__(self, name: str, path: Path) -> None:
        super().__init__(f"Generated Skill not found: {name}")
        self.name = name
        self.path = path


class GeneratedSkillMissingSkillMdError(RuntimeError):
    def __init__(self, name: str, path: Path) -> None:
        super().__init__(f"Generated Skill is missing SKILL.md: {name}")
        self.name = name
        self.path = path


class SkillLibraryManager:
    def __init__(self, output_dir: Path, collection_store: CollectionStore | None = None) -> None:
        self._output_dir = output_dir.expanduser()
        self._collection_store = collection_store

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    def list(self) -> list[SkillLibraryEntry]:
        if not self._output_dir.exists():
            return []

        entries: list[SkillLibraryEntry] = []
        for path in sorted(self._output_dir.iterdir(), key=lambda item: item.name.lower()):
            if path.is_dir() and (path / "SKILL.md").is_file():
                entries.append(self._entry_from_path(path))
        return entries

    def show(self, name: str) -> SkillLibraryEntry:
        path = self._package_path(name)
        if not path.is_dir():
            raise GeneratedSkillNotFoundError(name, path)
        if not (path / "SKILL.md").is_file():
            raise GeneratedSkillMissingSkillMdError(name, path / "SKILL.md")
        return self._entry_from_path(path)

    def diff(self, left_name: str, right_name: str) -> list[str]:
        left = self.show(left_name)
        right = self.show(right_name)
        left_lines = left.skill_md_path.read_text(encoding="utf-8").splitlines(keepends=True)
        right_lines = right.skill_md_path.read_text(encoding="utf-8").splitlines(keepends=True)
        diff_lines = list(
            difflib.unified_diff(
                left_lines,
                right_lines,
                fromfile=f"{left.name}/SKILL.md",
                tofile=f"{right.name}/SKILL.md",
            )
        )
        diff_lines.extend(_metadata_diff(left.path, right.path))
        return diff_lines

    def _package_path(self, name: str) -> Path:
        return self._output_dir / name

    def _entry_from_path(self, path: Path) -> SkillLibraryEntry:
        skill_md_path = path / "SKILL.md"
        post = frontmatter.loads(skill_md_path.read_text(encoding="utf-8"))
        collection_record = None
        if self._collection_store is not None:
            collection_record = self._collection_store.read_record(path.name)
        return SkillLibraryEntry(
            name=path.name,
            frontmatter_name=_metadata_string(post.metadata.get("name")),
            description=_metadata_string(post.metadata.get("description")),
            path=path,
            skill_md_path=skill_md_path,
            reference_count=_count_files(path / "references"),
            asset_count=_count_files(path / "assets"),
            script_count=_count_files(path / "scripts"),
            provenance=_read_provenance(path),
            eval_report=_read_eval_report(path),
            collection_record=collection_record,
        )


def _metadata_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _count_files(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def _read_provenance(path: Path) -> GenerationProvenanceMetadata | None:
    metadata_path = path / PROVENANCE_METADATA_FILENAME
    if not metadata_path.is_file():
        return None
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        return GenerationProvenanceMetadata.model_validate(data)
    except (OSError, json.JSONDecodeError, ValidationError):
        return None


def _read_eval_report(path: Path) -> SkillEvalReport | None:
    report_path = path / EVAL_REPORT_FILENAME
    if not report_path.is_file():
        return None
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        return SkillEvalReport.model_validate(data)
    except (OSError, json.JSONDecodeError, ValidationError):
        return None


def _metadata_diff(left_path: Path, right_path: Path) -> list[str]:
    left_metadata = left_path / PROVENANCE_METADATA_FILENAME
    right_metadata = right_path / PROVENANCE_METADATA_FILENAME
    left_lines = _read_optional_lines(left_metadata)
    right_lines = _read_optional_lines(right_metadata)
    if left_lines == right_lines:
        return []
    return list(
        difflib.unified_diff(
            left_lines,
            right_lines,
            fromfile=f"{left_path.name}/{PROVENANCE_METADATA_FILENAME}",
            tofile=f"{right_path.name}/{PROVENANCE_METADATA_FILENAME}",
        )
    )


def _read_optional_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8").splitlines(keepends=True)
