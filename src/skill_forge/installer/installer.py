import shutil
from dataclasses import dataclass
from pathlib import Path

from skill_forge.config import AppConfig, DEFAULT_OUTPUT_DIR


class SkillInstallError(RuntimeError):
    pass


class SourceSkillNotFoundError(SkillInstallError):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Generated Skill package not found: {path}")
        self.path = path


class DestinationExistsError(SkillInstallError):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Installed Skill already exists: {path}")
        self.path = path


@dataclass(frozen=True)
class InstalledSkill:
    name: str
    source_path: Path
    destination_path: Path
    target: str
    scope: str


class SkillInstaller:
    def __init__(self, config: AppConfig, *, home: Path, project_dir: Path | None = None) -> None:
        self._config = config
        self._home = home
        self._project_dir = project_dir or Path.cwd()

    def source_path(self, skill_name: str) -> Path:
        return _resolve_home_path(self._config.create.output_dir, self._home) / skill_name

    def destination_path(self, skill_name: str, *, target: str, scope: str) -> Path:
        if scope == "project":
            return self._project_destination(skill_name, target)
        if scope == "user":
            return self._user_destination(skill_name, target)
        raise ValueError(f"Unsupported install scope: {scope}")

    def install(self, skill_name: str, *, target: str, scope: str, force: bool = False) -> InstalledSkill:
        source = self.source_path(skill_name)
        if not source.is_dir():
            raise SourceSkillNotFoundError(source)

        destination = self.destination_path(skill_name, target=target, scope=scope)
        if destination.exists():
            if not force:
                raise DestinationExistsError(destination)
            shutil.rmtree(destination)

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)
        return InstalledSkill(
            name=skill_name,
            source_path=source,
            destination_path=destination,
            target=target,
            scope=scope,
        )

    def _project_destination(self, skill_name: str, target: str) -> Path:
        match target:
            case "opencode":
                return self._project_dir / ".opencode" / "skills" / skill_name
            case "claude":
                return self._project_dir / ".claude" / "skills" / skill_name
            case "codex":
                return self._project_dir / ".codex" / "skills" / skill_name
            case _:
                raise ValueError(f"Unsupported install target: {target}")

    def _user_destination(self, skill_name: str, target: str) -> Path:
        match target:
            case "opencode":
                root = self._config.platforms.opencode.user_skills_path
            case "claude":
                root = self._config.platforms.claude.user_skills_path
            case "codex":
                root = self._config.platforms.codex.user_skills_path
            case _:
                raise ValueError(f"Unsupported install target: {target}")
        return _resolve_home_path(root, self._home) / skill_name


def _resolve_home_path(value: str, home: Path) -> Path:
    if value == DEFAULT_OUTPUT_DIR and home != Path.home() / ".skill-forge":
        return home / "output"
    if value.startswith("~/.skill-forge"):
        return Path(value.replace("~/.skill-forge", str(home), 1))
    return Path(value).expanduser()
