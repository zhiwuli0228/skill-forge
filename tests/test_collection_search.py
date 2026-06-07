import sqlite3
from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.models.collection import CollectionState, build_collection_record
from skill_forge.retrieval.collection_integration import CollectionSearchFilter
from skill_forge.retrieval.indexer import TfidfIndexer, TfidfIndexStore
from skill_forge.retrieval.retriever import CorpusRetriever
from skill_forge.storage.collection_store import CollectionStore
from skill_forge.storage.corpus_reader import CorpusReader
from skill_forge.storage.paths import SkillForgePaths
from skill_forge.storage.sqlite_store import initialize_database
from skill_forge.models.search import SearchResult


runner = CliRunner()


def seed_document(
    paths: SkillForgePaths,
    *,
    source_name: str,
    authority: str,
    title: str,
    platform: str,
    summary: str,
    content: str,
    content_hash: str,
    updated_at: str = "2026-06-07T00:00:00",
) -> None:
    paths.ensure_directories()
    initialize_database(paths.database_file)
    normalized_path = paths.corpus_normalized_dir / f"{title.lower().replace(' ', '-')}.md"
    normalized_path.write_text(content, encoding="utf-8")

    with sqlite3.connect(paths.database_file) as connection:
        source_id = connection.execute(
            """
            INSERT INTO sources (name, url, source_type, authority_level, enabled, last_checked_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, ?, ?, ?)
            """,
            (source_name, f"https://example.com/{source_name}", "docs", authority, updated_at, updated_at, updated_at),
        ).lastrowid
        document_id = connection.execute(
            """
            INSERT INTO documents (source_id, url, title, raw_path, normalized_path, content_hash, fetched_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                f"https://example.com/{title}",
                title,
                str(paths.corpus_raw_dir / f"{title}.raw"),
                str(normalized_path),
                content_hash,
                updated_at,
                updated_at,
            ),
        ).lastrowid
        connection.execute(
            """
            INSERT INTO skill_examples (document_id, name, description, platform, full_content_path, summary, tags, quality_score, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0.5, ?, ?)
            """,
            (
                document_id,
                title,
                summary,
                platform,
                str(normalized_path),
                summary,
                "skills",
                updated_at,
                updated_at,
            ),
        )
        connection.commit()


def _make_search_result(title: str, score: float = 0.5) -> SearchResult:
    return SearchResult(
        document_id=1,
        title=title,
        source_name="test",
        summary="test summary",
        score=score,
        relevance_score=score,
        authority_boost=0.0,
        completeness_boost=0.0,
        freshness_boost=0.0,
        platform_boost=0.0,
        normalized_path=Path("/test"),
    )


def test_collection_filter_enriches_results_with_state(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Skill A", package_name="Skill A", origin_type="generated", collection_state=CollectionState.PROMOTED))
    store.write_record(build_collection_record(skill_id="Skill B", package_name="Skill B", origin_type="generated", collection_state=CollectionState.CURATED))

    filter_obj = CollectionSearchFilter(store)
    results = [_make_search_result("Skill A"), _make_search_result("Skill B"), _make_search_result("Skill C")]

    enriched = filter_obj.apply(results)

    states = {r.title: r.collection_state for r in enriched}
    assert states["Skill A"] == "promoted"
    assert states["Skill B"] == "curated"
    assert states.get("Skill C") is None


def test_collection_filter_filters_by_state(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Skill A", package_name="Skill A", origin_type="generated", collection_state=CollectionState.PROMOTED))
    store.write_record(build_collection_record(skill_id="Skill B", package_name="Skill B", origin_type="generated", collection_state=CollectionState.CURATED))

    filter_obj = CollectionSearchFilter(store)
    results = [_make_search_result("Skill A"), _make_search_result("Skill B")]

    promoted = filter_obj.apply(results, collection_filter=CollectionState.PROMOTED)
    assert len(promoted) == 1
    assert promoted[0].title == "Skill A"


def test_collection_filter_applies_promoted_boost(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Skill A", package_name="Skill A", origin_type="generated", collection_state=CollectionState.PROMOTED))

    filter_obj = CollectionSearchFilter(store)
    results = [_make_search_result("Skill A", score=0.5), _make_search_result("Skill B", score=0.5)]

    boosted = filter_obj.apply(results, promoted_boost=0.10, curated_boost=0.0)

    scores = {r.title: r.score for r in boosted}
    assert scores["Skill A"] > scores["Skill B"]
    assert boosted[0].title == "Skill A"


def test_collection_filter_no_boost_when_disabled(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Skill A", package_name="Skill A", origin_type="generated", collection_state=CollectionState.PROMOTED))

    filter_obj = CollectionSearchFilter(store)
    results = [_make_search_result("Skill A", score=0.5), _make_search_result("Skill B", score=0.6)]

    no_boost = filter_obj.apply(results, promoted_boost=0.0, curated_boost=0.0)

    assert no_boost[0].title == "Skill B"


def test_search_command_default_unchanged(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="skill creator workflow references",
        content_hash="hash-1",
    )

    result = runner.invoke(app, ["search", "skill creator", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "Skill Creator" in result.output
    assert "tfidf" in result.output


def test_search_command_collection_filter(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="skill creator workflow references",
        content_hash="hash-1",
    )
    store = CollectionStore(paths.collections_dir)
    store.write_record(build_collection_record(skill_id="Skill Creator", package_name="Skill Creator", origin_type="generated", collection_state=CollectionState.PROMOTED))

    result = runner.invoke(app, ["search", "skill creator", "--collection", "promoted", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "Skill Creator" in result.output


def test_search_command_collection_filter_empty_result(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="skill creator workflow references",
        content_hash="hash-1",
    )

    result = runner.invoke(app, ["search", "skill creator", "--collection", "promoted", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "No results match collection state" in result.output


def test_search_command_invalid_collection_state(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()

    result = runner.invoke(app, ["search", "test", "--collection", "invalid", "--home", str(paths.home)])

    assert result.exit_code == 1
    assert "Invalid collection state" in result.output


def test_search_command_promoted_boost(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="skill creator workflow references",
        content_hash="hash-1",
    )
    store = CollectionStore(paths.collections_dir)
    store.write_record(build_collection_record(skill_id="Skill Creator", package_name="Skill Creator", origin_type="generated", collection_state=CollectionState.PROMOTED))

    result = runner.invoke(app, ["search", "skill creator", "--promoted-boost", "--explain", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "Skill Creator" in result.output
