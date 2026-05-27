from pathlib import Path

import yaml

from skill_forge.models.source import ResearchSource, SourceConfig


def default_sources_file() -> Path:
    project_file = Path(__file__).resolve().parents[3] / "configs" / "sources.yaml"
    if project_file.exists():
        return project_file
    return Path.cwd() / "configs" / "sources.yaml"


class SourceConfigError(ValueError):
    pass


class SourceLoader:
    def __init__(self, default_path: Path | None = None) -> None:
        self.default_path = default_path or default_sources_file()

    def load(self, user_override_path: Path | None = None) -> SourceConfig:
        source_path = user_override_path if user_override_path and user_override_path.exists() else self.default_path
        if not source_path.exists():
            raise SourceConfigError(f"Source config not found: {source_path}")

        data = yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
        try:
            return SourceConfig.model_validate(data)
        except Exception as exc:
            raise SourceConfigError(f"Invalid source config: {source_path}") from exc

    def enabled_sources(self, user_override_path: Path | None = None) -> list[ResearchSource]:
        return [source for source in self.load(user_override_path).sources if source.enabled]
