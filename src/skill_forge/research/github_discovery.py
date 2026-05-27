import fnmatch
import re
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import quote

import frontmatter
import httpx

from skill_forge.models.source import FetchedDocument, ResearchSource, SkillDiscoveryConfig


class GitHubDiscoveryError(RuntimeError):
    pass


class GitHubFileFetchError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitHubRepository:
    owner: str
    repo: str


@dataclass(frozen=True)
class DiscoveredSkillCandidate:
    source: ResearchSource
    repository: GitHubRepository
    branch: str
    path: str

    @property
    def raw_url(self) -> str:
        return (
            f"https://raw.githubusercontent.com/{self.repository.owner}/{self.repository.repo}/"
            f"{self.branch}/{quote(self.path, safe='/')}"
        )


class GitHubHttpClient(Protocol):
    def get_json(self, url: str) -> dict:
        ...

    def get_text(self, url: str) -> str:
        ...


class HttpGitHubClient:
    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def get_json(self, url: str) -> dict:
        try:
            response = httpx.get(url, timeout=self.timeout, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GitHubDiscoveryError(str(exc)) from exc
        return response.json()

    def get_text(self, url: str) -> str:
        try:
            response = httpx.get(url, timeout=self.timeout, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GitHubFileFetchError(str(exc)) from exc
        return response.text


class GitHubSkillDiscoverer:
    def __init__(self, client: GitHubHttpClient | None = None) -> None:
        self.client = client or HttpGitHubClient()

    def discover(self, source: ResearchSource, config: SkillDiscoveryConfig) -> list[DiscoveredSkillCandidate]:
        repository = parse_github_repository(source.url_text)
        tree_url = (
            f"https://api.github.com/repos/{repository.owner}/{repository.repo}/"
            f"git/trees/{config.branch}?recursive=1"
        )
        data = self.client.get_json(tree_url)
        tree = data.get("tree")
        if not isinstance(tree, list):
            raise GitHubDiscoveryError("GitHub tree response did not contain a tree list")

        candidates: list[DiscoveredSkillCandidate] = []
        for item in tree:
            if not isinstance(item, dict) or item.get("type") != "blob":
                continue
            path = item.get("path")
            if not isinstance(path, str):
                continue
            if not _matches_any(path, config.skill_file_patterns):
                continue
            candidates.append(DiscoveredSkillCandidate(source, repository, config.branch, path))
            if len(candidates) >= config.max_files:
                break
        return candidates

    def fetch(self, candidate: DiscoveredSkillCandidate) -> FetchedDocument:
        content = self.client.get_text(candidate.raw_url)
        extracted = extract_skill_metadata(candidate.path, content)
        source_tags = candidate.source.metadata.get("tags", [])
        tags = [str(tag) for tag in source_tags] + ["community", "discovered-skill"]
        return FetchedDocument(
            source=candidate.source,
            content=content,
            content_type="text/markdown",
            document_url=candidate.raw_url,
            title=extracted.name,
            example_name=extracted.name,
            example_description=extracted.description,
            platform=candidate.source.metadata.get("platform"),
            tags=_dedupe(tags),
            quality_score=extracted.quality_score,
        )


@dataclass(frozen=True)
class ExtractedSkillMetadata:
    name: str
    description: str | None
    quality_score: float


def parse_github_repository(url: str) -> GitHubRepository:
    match = re.match(r"^https://github\.com/([^/\s]+)/([^/\s#?]+?)(?:\.git)?/?(?:[?#].*)?$", url)
    if not match:
        raise GitHubDiscoveryError(f"Unsupported GitHub repository URL: {url}")
    return GitHubRepository(owner=match.group(1), repo=match.group(2))


def extract_skill_metadata(path: str, content: str) -> ExtractedSkillMetadata:
    try:
        parsed = frontmatter.loads(content)
        metadata = parsed.metadata
        body = parsed.content
    except Exception:
        metadata = {}
        body = content

    name = _metadata_string(metadata.get("name")) or _name_from_path(path)
    description = _metadata_string(metadata.get("description")) or _summary_from_content(body)
    quality_score = 0.75 if metadata.get("name") and metadata.get("description") else 0.45
    return ExtractedSkillMetadata(name=name, description=description, quality_score=quality_score)


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def _metadata_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _name_from_path(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 2 and parts[-1].lower() == "skill.md":
        return parts[-2]
    return "community-skill"


def _summary_from_content(content: str) -> str | None:
    compact = " ".join(line.strip(" #\t") for line in content.splitlines() if line.strip())
    return compact[:280] or None


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
