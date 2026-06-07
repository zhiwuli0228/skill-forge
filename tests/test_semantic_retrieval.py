import sqlite3
from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.retrieval.indexer import TfidfIndexer, TfidfIndexStore
from skill_forge.retrieval.semantic import SemanticIndexMetadata, SemanticRetriever
from skill_forge.storage.corpus_reader import CorpusReader
from skill_forge.storage.paths import SkillForgePaths
from skill_forge.storage.sqlite_store import initialize_database


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
        existing = connection.execute(
            "SELECT id FROM sources WHERE name = ?", (source_name,)
        ).fetchone()
        if existing is not None:
            source_id = existing[0]
        else:
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


def _make_retriever(paths: SkillForgePaths) -> SemanticRetriever:
    reader = CorpusReader(paths.database_file)
    return SemanticRetriever(TfidfIndexer(reader, TfidfIndexStore(paths.index_dir)))


def test_semantic_search_returns_results(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Bug Investigation",
        platform="codex",
        summary="Investigate bugs with logs.",
        content="bug investigation logs stacktrace root cause",
        content_hash="hash-1",
    )

    retriever = _make_retriever(paths)
    response = retriever.search("bug investigation", top_k=5)

    assert len(response.results) > 0
    assert response.retrieval_mode == "semantic-tfidf"
    assert response.index_metadata is not None
    assert response.index_metadata.document_count == 1


def test_semantic_search_falls_back_on_empty_corpus(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)

    retriever = _make_retriever(paths)
    response = retriever.search("test", top_k=5)

    assert response.results == []
    assert response.fallback_used is True
    assert response.fallback_reason == "empty-corpus"


def test_semantic_find_similar(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Docs",
        authority="official",
        title="Bug Investigation",
        platform="codex",
        summary="Investigate bugs.",
        content="bug investigation logs stacktrace root cause analysis debugging",
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Docs",
        authority="official",
        title="Debug Workflow",
        platform="codex",
        summary="Debug workflow.",
        content="debugging investigation logs stacktrace root cause analysis",
        content_hash="hash-2",
    )

    retriever = _make_retriever(paths)
    similar = retriever.find_similar("Bug Investigation", top_k=5)

    assert len(similar) > 0
    assert similar[0].target_title == "Debug Workflow"
    assert similar[0].similarity_score > 0.0


def test_semantic_find_similar_missing_title(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Docs",
        authority="official",
        title="Bug Investigation",
        platform="codex",
        summary="Investigate bugs.",
        content="bug investigation logs",
        content_hash="hash-1",
    )

    retriever = _make_retriever(paths)
    similar = retriever.find_similar("Nonexistent Title")

    assert similar == []


def test_semantic_detect_duplicates(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Docs",
        authority="official",
        title="Bug Investigation A",
        platform="codex",
        summary="Investigate bugs.",
        content="bug investigation logs stacktrace root cause analysis debugging workflow",
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Docs",
        authority="official",
        title="Bug Investigation B",
        platform="codex",
        summary="Investigate bugs.",
        content="bug investigation logs stacktrace root cause analysis debugging workflow",
        content_hash="hash-2",
    )

    retriever = _make_retriever(paths)
    duplicates = retriever.detect_duplicates(threshold=0.5)

    assert len(duplicates) > 0
    assert duplicates[0].similarity_score >= 0.5


def test_semantic_detect_duplicates_none_when_threshold_high(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Docs",
        authority="official",
        title="Bug Investigation",
        platform="codex",
        summary="Investigate bugs.",
        content="bug investigation logs",
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Docs",
        authority="official",
        title="Release Workflow",
        platform="codex",
        summary="Release workflow.",
        content="release deploy rollout production",
        content_hash="hash-2",
    )

    retriever = _make_retriever(paths)
    duplicates = retriever.detect_duplicates(threshold=0.99)

    assert duplicates == []


def test_semantic_get_metadata(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create skills.",
        content="skill creator workflow",
        content_hash="hash-1",
    )

    retriever = _make_retriever(paths)
    metadata = retriever.get_metadata()

    assert metadata is not None
    assert metadata.document_count == 1
    assert metadata.provider == "local-tfidf"
    assert metadata.index_version == "tfidf-semantic-v1"


def test_semantic_get_metadata_empty_corpus(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)

    retriever = _make_retriever(paths)
    metadata = retriever.get_metadata()

    assert metadata is None


def test_search_command_semantic_flag(tmp_path: Path) -> None:
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

    result = runner.invoke(app, ["search", "skill creator", "--semantic", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "Skill Creator" in result.output
    assert "semantic-tfidf" in result.output


def test_search_command_semantic_empty_corpus(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)

    result = runner.invoke(app, ["search", "test", "--semantic", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "empty-corpus" in result.output


def test_semantic_index_metadata_model() -> None:
    metadata = SemanticIndexMetadata()

    assert metadata.index_version == "tfidf-semantic-v1"
    assert metadata.provider == "local-tfidf"
    assert metadata.fallback_mode == "tfidf"
    assert metadata.document_count == 0
