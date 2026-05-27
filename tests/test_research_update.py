import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.models.source import FetchedDocument, ResearchSource
from skill_forge.research.fetcher import FetchError
from skill_forge.research.normalizer import ContentNormalizer
from skill_forge.research.sources import SourceConfigError, SourceLoader
from skill_forge.research.updater import ResearchUpdater, SourceUpdateOutcome, UpdateResult
from skill_forge.storage.paths import SkillForgePaths
from skill_forge.storage.sqlite_store import initialize_database


class FakeFetcher:
    def __init__(self, responses: dict[str, str | Exception]) -> None:
        self.responses = responses
        self.fetched: list[str] = []

    def fetch(self, source: ResearchSource) -> FetchedDocument:
        self.fetched.append(source.name)
        response = self.responses[source.name]
        if isinstance(response, Exception):
            raise response
        return FetchedDocument(source=source, content=response, content_type="text/html")


def write_sources(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_source_loader_uses_default_file(tmp_path: Path) -> None:
    default = write_sources(
        tmp_path / "configs" / "sources.yaml",
        """
sources:
  - name: Default Docs
    type: docs
    url: https://example.com/docs
    authority_level: official
    enabled: true
""",
    )

    config = SourceLoader(default).load()

    assert [source.name for source in config.sources] == ["Default Docs"]


def test_source_loader_uses_user_override_when_present(tmp_path: Path) -> None:
    default = write_sources(
        tmp_path / "configs" / "sources.yaml",
        """
sources:
  - name: Default Docs
    type: docs
    url: https://example.com/default
    authority_level: official
    enabled: true
""",
    )
    override = write_sources(
        tmp_path / "home" / "sources.yaml",
        """
sources:
  - name: User Docs
    type: github
    url: https://example.com/user
    authority_level: community
    enabled: true
""",
    )

    config = SourceLoader(default).load(override)

    assert [source.name for source in config.sources] == ["User Docs"]


def test_source_loader_rejects_invalid_config(tmp_path: Path) -> None:
    default = write_sources(tmp_path / "sources.yaml", "sources:\n  - name: Missing fields\n")

    with pytest.raises(SourceConfigError):
        SourceLoader(default).load()


def test_normalizer_extracts_readable_html_text() -> None:
    normalized = ContentNormalizer().normalize(
        "<html><body><h1>Skill Guide</h1><p>Use this when creating Skills.</p></body></html>",
        "text/html",
    )

    assert "Skill Guide" in normalized
    assert "creating Skills" in normalized
    assert "<html>" not in normalized


def test_updater_skips_disabled_sources_without_fetching(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    sources_file = write_sources(
        paths.sources_file,
        """
sources:
  - name: Disabled Docs
    type: docs
    url: https://example.com/disabled
    authority_level: official
    enabled: false
""",
    )
    fetcher = FakeFetcher({})

    result = ResearchUpdater(paths, fetcher=fetcher).update(sources_file)

    assert result.outcomes[0].status == "disabled"
    assert result.disabled_count == 1
    assert fetcher.fetched == []


def test_updater_writes_cache_and_sqlite_metadata(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    write_sources(
        paths.sources_file,
        """
sources:
  - name: Skill Docs
    type: docs
    url: https://example.com/docs
    authority_level: official
    enabled: true
    metadata:
      platform: codex
      tags: [skills]
""",
    )

    result = ResearchUpdater(
        paths,
        fetcher=FakeFetcher({"Skill Docs": "<h1>Skill Docs</h1><p>Build better Skills.</p>"}),
    ).update()

    assert result.updated_count == 1
    assert list(paths.corpus_raw_dir.glob("skill-docs-*.raw"))
    assert list(paths.corpus_normalized_dir.glob("skill-docs-*.md"))
    with sqlite3.connect(paths.database_file) as connection:
        assert connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM skill_examples").fetchone()[0] == 1


def test_updater_skips_repeated_unchanged_content(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    write_sources(
        paths.sources_file,
        """
sources:
  - name: Skill Docs
    type: docs
    url: https://example.com/docs
    authority_level: official
    enabled: true
""",
    )
    updater = ResearchUpdater(paths, fetcher=FakeFetcher({"Skill Docs": "# Same content"}))

    first = updater.update()
    second = updater.update()

    assert first.updated_count == 1
    assert second.skipped_count == 1
    assert len(list(paths.corpus_normalized_dir.glob("skill-docs-*.md"))) == 1


def test_updater_succeeds_when_one_source_fails_and_another_updates(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    write_sources(
        paths.sources_file,
        """
sources:
  - name: Failing Docs
    type: docs
    url: https://example.com/fail
    authority_level: official
    enabled: true
  - name: Working Docs
    type: docs
    url: https://example.com/work
    authority_level: official
    enabled: true
""",
    )

    result = ResearchUpdater(
        paths,
        fetcher=FakeFetcher({"Failing Docs": FetchError("offline"), "Working Docs": "# Working"}),
    ).update()

    assert result.ok
    assert result.partial_failure
    assert result.status_label == "partial"
    assert result.failed_count == 1
    assert result.updated_count == 1


def test_updater_reports_not_ok_when_all_sources_fail(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)
    write_sources(
        paths.sources_file,
        """
sources:
  - name: Failing Docs
    type: docs
    url: https://example.com/fail
    authority_level: official
    enabled: true
""",
    )

    result = ResearchUpdater(paths, fetcher=FakeFetcher({"Failing Docs": FetchError("offline")})).update()

    assert not result.ok
    assert result.status_label == "failed"
    assert result.failed_count == 1


def test_update_command_prints_summary(tmp_path: Path, monkeypatch) -> None:
    class FakeUpdater:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def update(self) -> UpdateResult:
            return UpdateResult([SourceUpdateOutcome("Skill Docs", "updated", "ok")])

    monkeypatch.setattr("skill_forge.cli.ResearchUpdater", FakeUpdater)

    result = CliRunner().invoke(app, ["update", "--home", str(tmp_path / "home")])

    assert result.exit_code == 0
    assert "Status: ok | Updated: 1 | Skipped: 0 | Failed: 0 | Disabled: 0" in result.output
    assert "Research corpus update" in result.output


def test_update_command_prints_partial_status_disabled_count_and_retry_guidance(tmp_path: Path, monkeypatch) -> None:
    class FakeUpdater:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def update(self) -> UpdateResult:
            return UpdateResult(
                [
                    SourceUpdateOutcome("Working Docs", "updated", "ok"),
                    SourceUpdateOutcome("Failing Docs", "failed", "offline"),
                    SourceUpdateOutcome("Disabled Docs", "disabled", "disabled"),
                ]
            )

    monkeypatch.setattr("skill_forge.cli.ResearchUpdater", FakeUpdater)

    result = CliRunner().invoke(app, ["update", "--home", str(tmp_path / "home")])

    assert result.exit_code == 0
    assert "Status: partial" in result.output
    assert "Disabled: 1" in result.output
    assert "Fix the source issue" in result.output
    assert "skill-forge update" in result.output


def test_update_command_returns_nonzero_when_all_sources_fail(tmp_path: Path, monkeypatch) -> None:
    class FakeUpdater:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def update(self) -> UpdateResult:
            return UpdateResult([SourceUpdateOutcome("Skill Docs", "failed", "offline")])

    monkeypatch.setattr("skill_forge.cli.ResearchUpdater", FakeUpdater)

    result = CliRunner().invoke(app, ["update", "--home", str(tmp_path / "home")])

    assert result.exit_code == 1
    assert "Failed: 1" in result.output
    assert "Fix the source issue" in result.output
