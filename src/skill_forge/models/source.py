from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


SourceType = Literal["docs", "github"]
AuthorityLevel = Literal["official", "community", "reference"]


class ResearchSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    type: SourceType
    url: HttpUrl
    authority_level: AuthorityLevel = "reference"
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def url_text(self) -> str:
        return str(self.url)

    @property
    def discovery_config(self) -> "SkillDiscoveryConfig | None":
        discovery = self.metadata.get("discovery")
        if discovery is None:
            return None
        return SkillDiscoveryConfig.model_validate(discovery)


class SkillDiscoveryConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch: str = "main"
    skill_file_patterns: list[str] = Field(default_factory=lambda: ["*/SKILL.md", "skills/*/SKILL.md"])
    max_files: int = Field(default=100, ge=1)


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sources: list[ResearchSource] = Field(default_factory=list)


class FetchedDocument(BaseModel):
    source: ResearchSource
    content: str
    content_type: str = "text/plain"
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    document_url: str | None = None
    title: str | None = None
    example_name: str | None = None
    example_description: str | None = None
    platform: str | None = None
    tags: list[str] | None = None
    quality_score: float | None = None


class NormalizedDocument(BaseModel):
    source: ResearchSource
    raw_path: Path
    normalized_path: Path
    content_hash: str
    title: str
    summary: str
    fetched_at: datetime
