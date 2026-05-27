from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel
from pydantic import ValidationError

from skill_forge.models.blueprint import SkillBlueprint


BUILTIN_BLUEPRINTS_DIR = Path(__file__).parent / "builtins"
PROJECT_BLUEPRINTS_RELATIVE_DIR = Path(".skill-forge") / "blueprints"
BlueprintSource = Literal["builtin", "user", "project"]


class LoadedBlueprint(BaseModel):
    blueprint: SkillBlueprint
    source: BlueprintSource
    path: Path


class BlueprintError(RuntimeError):
    pass


class BlueprintLoadError(BlueprintError):
    def __init__(self, path: Path, message: str) -> None:
        super().__init__(f"Failed to load blueprint {path}: {message}")
        self.path = path
        self.message = message


class DuplicateBlueprintError(BlueprintError):
    def __init__(self, blueprint_id: str, paths: tuple[Path, ...] = ()) -> None:
        super().__init__(f"Duplicate blueprint id: {blueprint_id}")
        self.blueprint_id = blueprint_id
        self.paths = paths


class BlueprintNotFoundError(BlueprintError):
    def __init__(self, blueprint_id: str) -> None:
        super().__init__(f"Blueprint not found: {blueprint_id}")
        self.blueprint_id = blueprint_id


class BlueprintLoader:
    def __init__(
        self,
        blueprint_dir: Path | None = None,
        *,
        user_blueprint_dir: Path | None = None,
        project_blueprint_dir: Path | None = None,
    ) -> None:
        self._single_blueprint_dir = blueprint_dir
        self._user_blueprint_dir = user_blueprint_dir
        self._project_blueprint_dir = project_blueprint_dir

    def load_all(self) -> list[SkillBlueprint]:
        return [record.blueprint for record in self.load_records()]

    def load_records(self) -> list[LoadedBlueprint]:
        records_by_id: dict[str, LoadedBlueprint] = {}
        for source, directory in self._blueprint_roots():
            if not directory.exists():
                continue
            for path in sorted(directory.glob("*.yaml")):
                blueprint = self._load_file(path)
                if blueprint.id in records_by_id:
                    existing = records_by_id[blueprint.id]
                    raise DuplicateBlueprintError(blueprint.id, (existing.path, path))
                records_by_id[blueprint.id] = LoadedBlueprint(blueprint=blueprint, source=source, path=path)
        return [records_by_id[blueprint_id] for blueprint_id in sorted(records_by_id)]

    def get(self, blueprint_id: str) -> SkillBlueprint:
        return self.get_record(blueprint_id).blueprint

    def get_record(self, blueprint_id: str) -> LoadedBlueprint:
        for record in self.load_records():
            if record.blueprint.id == blueprint_id:
                return record
        raise BlueprintNotFoundError(blueprint_id)

    def find_by_task_type(self, task_type: str | None) -> SkillBlueprint | None:
        record = self.find_record_by_task_type(task_type)
        return record.blueprint if record is not None else None

    def find_record_by_task_type(self, task_type: str | None) -> LoadedBlueprint | None:
        if task_type is None:
            return None
        for record in self.load_records():
            if record.blueprint.task_type == task_type:
                return record
        return None

    def _blueprint_roots(self) -> tuple[tuple[BlueprintSource, Path], ...]:
        if self._single_blueprint_dir is not None:
            return (("user", self._single_blueprint_dir),)

        roots: list[tuple[BlueprintSource, Path]] = [("builtin", BUILTIN_BLUEPRINTS_DIR)]
        if self._user_blueprint_dir is not None:
            roots.append(("user", self._user_blueprint_dir))
        if self._project_blueprint_dir is not None:
            roots.append(("project", self._project_blueprint_dir))
        return tuple(roots)

    def _load_file(self, path: Path) -> SkillBlueprint:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise BlueprintLoadError(path, str(exc)) from exc
        except yaml.YAMLError as exc:
            raise BlueprintLoadError(path, str(exc)) from exc

        if not isinstance(data, dict):
            raise BlueprintLoadError(path, "Blueprint file must contain a YAML mapping.")

        try:
            return SkillBlueprint.model_validate(data)
        except ValidationError as exc:
            raise BlueprintLoadError(path, _format_validation_error(exc)) from exc


def _format_validation_error(error: ValidationError) -> str:
    issues: list[str] = []
    for issue in error.errors():
        location = ".".join(str(part) for part in issue["loc"])
        issues.append(f"{location}: {issue['msg']}")
    return "; ".join(issues)
