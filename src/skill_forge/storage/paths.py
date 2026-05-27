import os
from dataclasses import dataclass
from pathlib import Path


HOME_ENV_VAR = "SKILL_FORGE_HOME"


@dataclass(frozen=True)
class SkillForgePaths:
    home: Path

    @classmethod
    def resolve(cls, home: Path | str | None = None) -> "SkillForgePaths":
        if home is None:
            home = os.environ.get(HOME_ENV_VAR)
        root = Path(home).expanduser() if home else Path.home() / ".skill-forge"
        return cls(home=root)

    @property
    def config_file(self) -> Path:
        return self.home / "config.yaml"

    @property
    def corpus_dir(self) -> Path:
        return self.home / "corpus"

    @property
    def corpus_raw_dir(self) -> Path:
        return self.corpus_dir / "raw"

    @property
    def corpus_normalized_dir(self) -> Path:
        return self.corpus_dir / "normalized"

    @property
    def sources_file(self) -> Path:
        return self.home / "sources.yaml"

    @property
    def drafts_dir(self) -> Path:
        return self.home / "drafts"

    @property
    def output_dir(self) -> Path:
        return self.home / "output"

    @property
    def blueprints_dir(self) -> Path:
        return self.home / "blueprints"

    @property
    def index_dir(self) -> Path:
        return self.home / "index"

    @property
    def logs_dir(self) -> Path:
        return self.home / "logs"

    @property
    def db_dir(self) -> Path:
        return self.home / "db"

    @property
    def database_file(self) -> Path:
        return self.db_dir / "skill_forge.sqlite"

    @property
    def workspace_directories(self) -> tuple[Path, ...]:
        return (
            self.home,
            self.corpus_dir,
            self.corpus_raw_dir,
            self.corpus_normalized_dir,
            self.drafts_dir,
            self.output_dir,
            self.blueprints_dir,
            self.index_dir,
            self.logs_dir,
            self.db_dir,
        )

    def ensure_directories(self) -> list[Path]:
        created_or_existing: list[Path] = []
        for directory in self.workspace_directories:
            directory.mkdir(parents=True, exist_ok=True)
            created_or_existing.append(directory)
        return created_or_existing
