from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


DEFAULT_OUTPUT_DIR = "E:/009workspace/skills"


class UpdateConfig(BaseModel):
    mode: str = "manual"
    stale_after_days: int = 7
    check_on_create: bool = True
    auto_update_on_create: bool = False


class CreateConfig(BaseModel):
    default_target: str = "opencode"
    default_language: str = "zh-CN"
    output_dir: str = DEFAULT_OUTPUT_DIR
    interactive_by_default: bool = False


class RetrievalConfig(BaseModel):
    top_k: int = 5
    use_tfidf: bool = True
    rerank_enabled: bool = True
    rerank_by_default: bool = False
    rerank_provider: str = "lexical"
    rerank_candidate_multiplier: int = 3
    generation_top_k: int = 3
    generation_min_corpus_documents: int = 10
    generation_min_relevance_score: float = 0.05
    generation_min_quality_score: float = 0.5


class PlatformConfig(BaseModel):
    user_skills_path: str


class PlatformsConfig(BaseModel):
    opencode: PlatformConfig = Field(
        default_factory=lambda: PlatformConfig(user_skills_path="~/.config/opencode/skills")
    )
    claude: PlatformConfig = Field(default_factory=lambda: PlatformConfig(user_skills_path="~/.claude/skills"))
    codex: PlatformConfig = Field(default_factory=lambda: PlatformConfig(user_skills_path="~/.codex/skills"))


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    update: UpdateConfig = Field(default_factory=UpdateConfig)
    create: CreateConfig = Field(default_factory=CreateConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    platforms: PlatformsConfig = Field(default_factory=PlatformsConfig)


def default_config() -> AppConfig:
    return AppConfig()


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        return default_config()

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(data)


def write_default_config(config_path: Path, *, overwrite: bool = False) -> bool:
    if config_path.exists() and not overwrite:
        return False

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = default_config().model_dump(mode="json")
    config_path.write_text(_dump_yaml(config), encoding="utf-8")
    return True


def _dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
