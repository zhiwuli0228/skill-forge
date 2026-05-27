import sqlite3
from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.models.source import FetchedDocument, ResearchSource
from skill_forge.research.github_discovery import (
    GitHubFileFetchError,
    GitHubSkillDiscoverer,
    extract_skill_metadata,
    parse_github_repository,
)
from skill_forge.research.updater import ResearchUpdater
from skill_forge.storage.paths import SkillForgePaths
from skill_forge.storage.sqlite_store import initialize_database


class FakeGitHubClient:
    def __init__(self, tree: list[dict], files: dict[str, str | Exception]) -> None:
        self.tree = tree
        self.files = files
        self.json_urls: list[str] = []
        self.text_urls: list[str] = []

    def get_json(self, url: str) -> dict:
        self.json_urls.append(url)
        return {"tree": self.tree}

    def get_text(self, url: str) -> str:
        self.text_urls.append(url)
        value = self.files[url]
        if isinstance(value, Exception):
            raise value
        return value


class FailIfCalledFetcher:
    def fetch(self, source: ResearchSource) -> FetchedDocument:
        raise AssertionError(f"single-document fetch should not be called for {source.name}")


class StaticFetcher:
    def __init__(self, content: str) -> None:
        self.content = content
        self.fetched: list[str] = []

    def fetch(self, source: ResearchSource) -> FetchedDocument:
        self.fetched.append(source.name)
        return FetchedDocument(source=source, content=self.content, content_type="text/markdown")


def write_sources(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def discovery_source_yaml() -> str:
    return """
sources:
  - name: Community Skills
    type: github
    url: https://github.com/example/skills
    authority_level: community
    enabled: true
    metadata:
      platform: codex
      tags: [skills, code-review]
      discovery:
        branch: main
        skill_file_patterns:
          - "skills/*/SKILL.md"
          - ".codex/skills/*/SKILL.md"
"""


def raw_url(path: str) -> str:
    return f"https://raw.githubusercontent.com/example/skills/main/{path}"


def skill_md(name: str = "code-review", description: str = "Review code changes for defects.") -> str:
    return f"""---
name: {name}
description: {description}
---

# Code Review

Use this skill for code review findings, test gaps, and risk analysis.
"""


def test_parse_github_repository_supports_https_urls() -> None:
    repository = parse_github_repository("https://github.com/example/skills.git")

    assert repository.owner == "example"
    assert repository.repo == "skills"


def test_discoverer_matches_patterns_and_fetches_raw_skill() -> None:
    client = FakeGitHubClient(
        tree=[
            {"path": "README.md", "type": "blob"},
            {"path": "skills/code-review/SKILL.md", "type": "blob"},
            {"path": ".codex/skills/bug/SKILL.md", "type": "blob"},
        ],
        files={
            raw_url("skills/code-review/SKILL.md"): skill_md(),
            raw_url(".codex/skills/bug/SKILL.md"): skill_md("bug-investigation", "Diagnose defects."),
        },
    )
    source = ResearchSource.model_validate(
        {
            "name": "Community Skills",
            "type": "github",
            "url": "https://github.com/example/skills",
            "authority_level": "community",
            "metadata": {
                "platform": "codex",
                "tags": ["skills"],
                "discovery": {"skill_file_patterns": ["skills/*/SKILL.md", ".codex/skills/*/SKILL.md"]},
            },
        }
    )
    discoverer = GitHubSkillDiscoverer(client)

    candidates = discoverer.discover(source, source.discovery_config)
    fetched = discoverer.fetch(candidates[0])

    assert [candidate.path for candidate in candidates] == [
        "skills/code-review/SKILL.md",
        ".codex/skills/bug/SKILL.md",
    ]
    assert fetched.document_url == raw_url("skills/code-review/SKILL.md")
    assert fetched.example_name == "code-review"
    assert fetched.example_description == "Review code changes for defects."
    assert fetched.platform == "codex"
    assert "discovered-skill" in (fetched.tags or [])


def test_extract_skill_metadata_uses_path_and_content_fallbacks() -> None:
    extracted = extract_skill_metadata("skills/review-helper/SKILL.md", "# Review Helper\n\nCode review workflow.")

    assert extracted.name == "review-helper"
    assert extracted.description == "Review Helper Code review workflow."
    assert extracted.quality_score == 0.45


def test_update_stores_each_discovered_skill_and_skips_unchanged_content(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    write_sources(paths.sources_file, discovery_source_yaml())
    client = FakeGitHubClient(
        tree=[{"path": "skills/code-review/SKILL.md", "type": "blob"}],
        files={raw_url("skills/code-review/SKILL.md"): skill_md()},
    )
    updater = ResearchUpdater(
        paths,
        fetcher=FailIfCalledFetcher(),
        github_discoverer=GitHubSkillDiscoverer(client),
    )

    first = updater.update()
    second = updater.update()

    assert first.updated_count == 1
    assert second.skipped_count == 1
    assert len(list(paths.corpus_raw_dir.glob("community-skills-*.raw"))) == 1
    assert len(list(paths.corpus_normalized_dir.glob("community-skills-*.md"))) == 1
    with sqlite3.connect(paths.database_file) as connection:
        rows = connection.execute(
            """
            SELECT documents.url, skill_examples.name, skill_examples.description, skill_examples.platform, skill_examples.tags
            FROM documents
            JOIN skill_examples ON skill_examples.document_id = documents.id
            """
        ).fetchall()
    assert rows == [
        (
            raw_url("skills/code-review/SKILL.md"),
            "code-review",
            "Review code changes for defects.",
            "codex",
            "skills,code-review,community,discovered-skill",
        )
    ]


def test_update_continues_when_one_discovered_skill_fetch_fails(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    write_sources(paths.sources_file, discovery_source_yaml())
    client = FakeGitHubClient(
        tree=[
            {"path": "skills/code-review/SKILL.md", "type": "blob"},
            {"path": "skills/broken/SKILL.md", "type": "blob"},
        ],
        files={
            raw_url("skills/code-review/SKILL.md"): skill_md(),
            raw_url("skills/broken/SKILL.md"): GitHubFileFetchError("not found"),
        },
    )

    result = ResearchUpdater(
        paths,
        fetcher=FailIfCalledFetcher(),
        github_discoverer=GitHubSkillDiscoverer(client),
    ).update()

    assert result.ok
    assert result.updated_count == 1
    assert result.failed_count == 1
    assert "skills/broken/SKILL.md" in result.outcomes[1].message


def test_github_source_without_discovery_uses_existing_single_fetch_path(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    write_sources(
        paths.sources_file,
        """
sources:
  - name: GitHub Page
    type: github
    url: https://github.com/example/repo
    authority_level: community
    enabled: true
""",
    )
    fetcher = StaticFetcher("# Repository page")

    result = ResearchUpdater(paths, fetcher=fetcher).update()

    assert result.updated_count == 1
    assert fetcher.fetched == ["GitHub Page"]


def test_search_returns_discovered_code_review_skill(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    write_sources(paths.sources_file, discovery_source_yaml())
    client = FakeGitHubClient(
        tree=[
            {"path": "skills/code-review/SKILL.md", "type": "blob"},
            {"path": "skills/test-generation/SKILL.md", "type": "blob"},
        ],
        files={
            raw_url("skills/code-review/SKILL.md"): skill_md(),
            raw_url("skills/test-generation/SKILL.md"): skill_md("test-generation", "Write regression tests."),
        },
    )
    ResearchUpdater(
        paths,
        fetcher=FailIfCalledFetcher(),
        github_discoverer=GitHubSkillDiscoverer(client),
    ).update()

    result = CliRunner().invoke(
        app,
        ["search", "code review skill", "--platform", "codex", "--top-k", "1", "--home", str(paths.home)],
    )

    assert result.exit_code == 0
    assert "code-review" in result.output
    assert "Community Skills" in result.output
    assert "codex" in result.output
    assert "test-generation" not in result.output
