from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from skill_forge.library.manager import (
    GeneratedSkillMissingSkillMdError,
    GeneratedSkillNotFoundError,
    SkillLibraryManager,
)


PROMOTION_REGISTRY_FILENAME = "promotion-registry.json"
PROMOTION_VERSION_SUFFIX = "-upgraded"
PACKAGE_NAME_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class PromotionHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["promote", "rollback"]
    timestamp: str
    active_version_name: str
    previous_version_name: str | None = None
    source_version_name: str | None = None
    snapshot_version_name: str | None = None
    snapshot_path: str | None = None
    source_path: str | None = None
    target_path: str | None = None


class PromotionRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_name: str
    active_version_name: str | None = None
    history: list[PromotionHistoryEntry] = Field(default_factory=list)


class PromotionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_name: str
    target_name: str
    active_version_name: str
    candidate_path: Path
    target_path: Path
    registry_path: Path
    snapshot_path: Path | None = None
    previous_version_name: str | None = None
    promoted_at: str


class RollbackResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_name: str
    restored_version_name: str
    active_version_name: str
    target_path: Path
    registry_path: Path
    snapshot_path: Path | None = None
    previous_version_name: str | None = None
    rolled_back_at: str


class InvalidPromotionTargetError(RuntimeError):
    def __init__(self, candidate_name: str, message: str) -> None:
        super().__init__(message)
        self.candidate_name = candidate_name


class PromotionSnapshotNotFoundError(RuntimeError):
    def __init__(self, skill_name: str, version_name: str, registry_path: Path) -> None:
        super().__init__(f"Recorded version snapshot not found: {skill_name} -> {version_name}")
        self.skill_name = skill_name
        self.version_name = version_name
        self.registry_path = registry_path


class SkillPromotionService:
    def __init__(self, library_manager: SkillLibraryManager, promotions_dir: Path) -> None:
        self._library_manager = library_manager
        self._promotions_dir = promotions_dir.expanduser()

    @property
    def library_manager(self) -> SkillLibraryManager:
        return self._library_manager

    @property
    def promotions_dir(self) -> Path:
        return self._promotions_dir

    def promote(self, candidate_name: str, *, target_name: str | None = None) -> PromotionResult:
        try:
            candidate = self._library_manager.show(candidate_name)
        except GeneratedSkillNotFoundError:
            raise
        except GeneratedSkillMissingSkillMdError:
            raise

        resolved_target_name = self._resolve_target_name(candidate_name, target_name)
        if resolved_target_name == candidate_name:
            raise InvalidPromotionTargetError(
                candidate_name,
                "Target name must differ from the candidate name. Use --as to choose the active package name.",
            )

        target_path = self._library_manager.output_dir / resolved_target_name
        registry = self._load_registry(resolved_target_name)
        previous_version_name = registry.active_version_name or (resolved_target_name if target_path.exists() else None)
        snapshot_path = None
        if target_path.exists():
            snapshot_path = self._create_snapshot(resolved_target_name, target_path, previous_version_name or resolved_target_name)
        if target_path.exists():
            shutil.rmtree(target_path)
        shutil.copytree(candidate.path, target_path)

        promoted_at = _timestamp()
        registry.active_version_name = candidate_name
        registry.history.append(
            PromotionHistoryEntry(
                operation="promote",
                timestamp=promoted_at,
                active_version_name=candidate_name,
                previous_version_name=previous_version_name,
                source_version_name=candidate_name,
                snapshot_version_name=previous_version_name,
                snapshot_path=str(snapshot_path) if snapshot_path is not None else None,
                source_path=str(candidate.path),
                target_path=str(target_path),
            )
        )
        registry_path = self._write_registry(resolved_target_name, registry)

        return PromotionResult(
            candidate_name=candidate_name,
            target_name=resolved_target_name,
            active_version_name=candidate_name,
            candidate_path=candidate.path,
            target_path=target_path,
            registry_path=registry_path,
            snapshot_path=snapshot_path,
            previous_version_name=previous_version_name,
            promoted_at=promoted_at,
        )

    def rollback(self, skill_name: str, *, version_name: str) -> RollbackResult:
        registry = self._load_registry(skill_name)
        registry_path = self._registry_path(skill_name)
        snapshot_entry = self._find_snapshot_entry(registry, version_name)
        if snapshot_entry is None or snapshot_entry.snapshot_path is None:
            raise PromotionSnapshotNotFoundError(skill_name, version_name, registry_path)

        snapshot_path = Path(snapshot_entry.snapshot_path)
        if not snapshot_path.is_dir():
            raise PromotionSnapshotNotFoundError(skill_name, version_name, registry_path)

        target_path = self._library_manager.output_dir / skill_name
        previous_version_name = registry.active_version_name or skill_name
        current_snapshot_path = None
        if target_path.exists():
            current_snapshot_path = self._create_snapshot(skill_name, target_path, previous_version_name)
            shutil.rmtree(target_path)
        shutil.copytree(snapshot_path, target_path)

        rolled_back_at = _timestamp()
        registry.active_version_name = version_name
        registry.history.append(
            PromotionHistoryEntry(
                operation="rollback",
                timestamp=rolled_back_at,
                active_version_name=version_name,
                previous_version_name=previous_version_name,
                source_version_name=version_name,
                snapshot_version_name=previous_version_name,
                snapshot_path=str(current_snapshot_path) if current_snapshot_path is not None else None,
                source_path=str(snapshot_path),
                target_path=str(target_path),
            )
        )
        registry_path = self._write_registry(skill_name, registry)

        return RollbackResult(
            skill_name=skill_name,
            restored_version_name=version_name,
            active_version_name=version_name,
            target_path=target_path,
            registry_path=registry_path,
            snapshot_path=current_snapshot_path,
            previous_version_name=previous_version_name,
            rolled_back_at=rolled_back_at,
        )

    def _resolve_target_name(self, candidate_name: str, target_name: str | None) -> str:
        if target_name is not None:
            self._validate_package_name(target_name)
            return target_name
        if candidate_name.endswith(PROMOTION_VERSION_SUFFIX):
            target = candidate_name[: -len(PROMOTION_VERSION_SUFFIX)]
            self._validate_package_name(target)
            return target
        raise InvalidPromotionTargetError(
            candidate_name,
            "Use --as <skill-name> when the candidate name does not end with -upgraded.",
        )

    def _validate_package_name(self, name: str) -> None:
        if not name or not _package_name_pattern_match(name):
            raise InvalidPromotionTargetError(name, "Package names must be lowercase kebab-case.")

    def _registry_path(self, skill_name: str) -> Path:
        return self._promotions_dir / skill_name / PROMOTION_REGISTRY_FILENAME

    def _snapshot_root(self, skill_name: str) -> Path:
        return self._promotions_dir / skill_name / "snapshots"

    def _create_snapshot(self, skill_name: str, source_path: Path, version_name: str) -> Path:
        snapshot_root = self._snapshot_root(skill_name)
        snapshot_root.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshot_root / f"{_timestamp()}__{version_name}"
        shutil.copytree(source_path, snapshot_path)
        return snapshot_path

    def _load_registry(self, skill_name: str) -> PromotionRegistry:
        path = self._registry_path(skill_name)
        if not path.is_file():
            return PromotionRegistry(target_name=skill_name)
        return PromotionRegistry.model_validate_json(path.read_text(encoding="utf-8"))

    def _write_registry(self, skill_name: str, registry: PromotionRegistry) -> Path:
        path = self._registry_path(skill_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(registry.model_dump_json(indent=2), encoding="utf-8")
        return path

    def _find_snapshot_entry(self, registry: PromotionRegistry, version_name: str) -> PromotionHistoryEntry | None:
        for entry in reversed(registry.history):
            if entry.snapshot_version_name == version_name and entry.snapshot_path is not None:
                return entry
        return None


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _package_name_pattern_match(value: str) -> bool:
    import re

    return re.fullmatch(PACKAGE_NAME_PATTERN, value) is not None
