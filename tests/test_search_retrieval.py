import sqlite3
from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.models.search import SearchResult
from skill_forge.retrieval.indexer import TfidfIndexer, TfidfIndexStore
from skill_forge.retrieval.generation import GenerationRetrievalAugmenter
from skill_forge.retrieval.reranker import RerankError, SearchReranker
from skill_forge.retrieval.retriever import CorpusRetriever
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
    updated_at: str = "2026-05-24T00:00:00",
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


def make_retriever(paths: SkillForgePaths) -> CorpusRetriever:
    reader = CorpusReader(paths.database_file)
    return CorpusRetriever(TfidfIndexer(reader, TfidfIndexStore(paths.index_dir)))


def test_corpus_reader_loads_sqlite_metadata_and_normalized_text(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="Skill creator workflow with references and quality gates.",
        content_hash="hash-1",
    )

    documents = CorpusReader(paths.database_file).load_documents()

    assert len(documents) == 1
    assert documents[0].title == "Skill Creator"
    assert documents[0].source_name == "Official Docs"
    assert documents[0].source_url == "https://example.com/Official Docs"
    assert documents[0].document_url == "https://example.com/Skill Creator"
    assert documents[0].platform == "codex"
    assert "quality gates" in documents[0].content


def test_corpus_reader_loads_single_document_by_id_with_urls(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="Skill creator workflow.",
        content_hash="hash-1",
    )

    document = CorpusReader(paths.database_file).load_document(1)

    assert document is not None
    assert document.document_id == 1
    assert document.example_id == 1
    assert document.source_url == "https://example.com/Official Docs"
    assert document.document_url == "https://example.com/Skill Creator"
    assert CorpusReader(paths.database_file).load_document(999) is None


def test_corpus_reader_skips_missing_file_only_when_no_summary(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="content",
        content_hash="hash-1",
    )
    for path in paths.corpus_normalized_dir.glob("*.md"):
        path.unlink()

    documents = CorpusReader(paths.database_file).load_documents()

    assert len(documents) == 1
    assert documents[0].content == ""
    assert documents[0].summary == "Create reliable Skills."


def test_indexer_builds_and_loads_persisted_index(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="Skill creator references workflow.",
        content_hash="hash-1",
    )
    reader = CorpusReader(paths.database_file)
    store = TfidfIndexStore(paths.index_dir)
    indexer = TfidfIndexer(reader, store)

    first = indexer.load_or_build()
    second = indexer.load_or_build()

    assert first is not None
    assert second is not None
    assert store.index_file.is_file()
    assert store.metadata_file.is_file()
    assert second.signature == first.signature


def test_indexer_rebuilds_when_corpus_signature_changes(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Create reliable Skills.",
        content="Skill creator references workflow.",
        content_hash="hash-1",
    )
    reader = CorpusReader(paths.database_file)
    indexer = TfidfIndexer(reader, TfidfIndexStore(paths.index_dir))
    first = indexer.load_or_build()

    with sqlite3.connect(paths.database_file) as connection:
        connection.execute("UPDATE documents SET content_hash = ?, updated_at = ? WHERE id = 1", ("hash-2", "2026-05-24T01:00:00"))
        connection.commit()
    second = indexer.load_or_build()

    assert first is not None
    assert second is not None
    assert second.signature != first.signature


def test_retriever_returns_top_k_relevance_results(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Bug Investigation",
        platform="codex",
        summary="Investigate bugs with logs and root cause analysis.",
        content="bug investigation logs stacktrace root cause bug bug",
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Community Notes",
        authority="community",
        title="Skill Creator",
        platform="codex",
        summary="Create skills.",
        content="skill creator template references",
        content_hash="hash-2",
    )

    results = make_retriever(paths).search("bug investigation", top_k=1)

    assert len(results) == 1
    assert results[0].title == "Bug Investigation"
    assert results[0].document_id == 1
    assert results[0].example_id == 1


def test_retriever_reranks_candidates_without_changing_default_order(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="General Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow " * 50,
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Community Notes",
        authority="community",
        title="Specific Skill Creator",
        platform="codex",
        summary="Specific skill creator checklist.",
        content="skill creator workflow",
        content_hash="hash-2",
    )
    retriever = make_retriever(paths)

    default = retriever.search("skill creator workflow", top_k=1)
    reranked = retriever.search_with_metadata("skill creator workflow", top_k=1, reranker=PreferSpecificReranker())

    assert default[0].title == "General Skill Creator"
    assert reranked.retrieval_mode == "tfidf+rerank"
    assert reranked.results[0].title == "Specific Skill Creator"
    assert reranked.results[0].rerank_score == 1.0


def test_retriever_falls_back_when_reranker_fails(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-1",
    )

    response = make_retriever(paths).search_with_metadata("skill creator", top_k=1, reranker=FailingReranker())

    assert response.retrieval_mode == "tfidf"
    assert response.warning is not None
    assert "falling back to TF-IDF" in response.warning.message
    assert response.results[0].retrieval_mode == "tfidf"


def test_retriever_boosts_authority_and_completeness_when_relevance_is_similar(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Official Skill Creator",
        platform="codex",
        summary="Skill creator workflow with complete guidance.",
        content="skill creator workflow " * 40,
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Community Notes",
        authority="community",
        title="Community Skill Creator",
        platform="codex",
        summary="Skill creator.",
        content="skill creator workflow",
        content_hash="hash-2",
    )

    results = make_retriever(paths).search("skill creator workflow", top_k=2)

    assert [result.title for result in results] == ["Official Skill Creator", "Community Skill Creator"]


def test_retriever_boosts_platform_match(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Codex Docs",
        authority="official",
        title="Codex Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Claude Docs",
        authority="official",
        title="Claude Skill Creator",
        platform="claude",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-2",
    )

    results = make_retriever(paths).search("skill creator workflow", top_k=2, platform="claude")

    assert results[0].title == "Claude Skill Creator"
    assert results[0].platform_boost > 0


def test_retriever_returns_empty_for_empty_corpus(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    initialize_database(paths.database_file)

    results = make_retriever(paths).search("skill creator", top_k=5)

    assert results == []


def test_generation_retrieval_extracts_quality_gated_patterns(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Bug Investigation",
        platform="codex",
        summary="Investigate bugs with logs and root cause analysis.",
        content=(
            "# Bug Investigation\n\n"
            "## Workflow\n"
            "1. Inspect production logs before editing code\n"
            "2. Trace the failing Java path with stack evidence\n\n"
            "## Constraints\n"
            "- Do not change code before root cause evidence is documented\n\n"
            "## Quality gates\n"
            "- Pass when root cause evidence links logs to code\n"
        ),
        content_hash="hash-1",
    )
    augmenter = GenerationRetrievalAugmenter(make_retriever(paths), min_corpus_documents=1)

    context = augmenter.build_context("Java bug investigation logs", platform="codex")

    assert context.used is True
    assert context.skipped_reason is None
    assert context.source_names == ["Bug Investigation#1"]
    assert context.workflow_patterns == [
        "Inspect production logs before editing code",
        "Trace the failing Java path with stack evidence",
    ]
    assert context.constraint_patterns == ["Do not change code before root cause evidence is documented"]
    assert context.quality_gate_patterns == ["Pass when root cause evidence links logs to code"]


def test_generation_retrieval_skips_empty_insufficient_and_low_quality_corpus(tmp_path: Path) -> None:
    empty_paths = SkillForgePaths.resolve(tmp_path / "empty")
    empty_paths.ensure_directories()
    initialize_database(empty_paths.database_file)

    assert GenerationRetrievalAugmenter(make_retriever(empty_paths)).build_context("skill").skipped_reason == "empty-corpus"

    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Community Notes",
        authority="community",
        title="General Skill",
        platform="codex",
        summary="General skill guidance.",
        content="general skill notes",
        content_hash="hash-1",
    )

    assert (
        GenerationRetrievalAugmenter(make_retriever(paths), min_corpus_documents=2)
        .build_context("general skill")
        .skipped_reason
        == "insufficient-corpus"
    )
    assert (
        GenerationRetrievalAugmenter(make_retriever(paths), min_corpus_documents=1, min_quality_score=0.9)
        .build_context("general skill")
        .skipped_reason
        == "below-quality-threshold"
    )


def test_generation_retrieval_limits_and_deduplicates_patterns(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Release Skill",
        platform="codex",
        summary="Release workflow.",
        content=(
            "# Release Skill\n\n"
            "## Workflow\n"
            "- Confirm release scope\n"
            "- Confirm release scope\n"
            "- Check rollout risks\n\n"
            "## Constraints\n"
            "- Rollback evidence must be documented\n\n"
            "## Quality gates\n"
            "- Pass when release owner verifies rollback plan\n"
        ),
        content_hash="hash-1",
    )
    augmenter = GenerationRetrievalAugmenter(make_retriever(paths), min_corpus_documents=1, max_patterns_per_kind=1)

    context = augmenter.build_context("release workflow", platform="codex")

    assert context.used is True
    assert context.workflow_patterns == ["Confirm release scope"]


def test_search_command_displays_results(tmp_path: Path) -> None:
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
    assert "Search results" in result.output
    assert "Skill Creator" in result.output
    assert "Official Docs" in result.output
    assert "codex" in result.output
    assert "ID" in result.output
    assert "1" in result.output


def test_search_command_supports_top_k_and_platform(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Codex Docs",
        authority="official",
        title="Codex Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Claude Docs",
        authority="official",
        title="Claude Skill Creator",
        platform="claude",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-2",
    )

    result = runner.invoke(app, ["search", "skill creator", "--top-k", "1", "--platform", "claude", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "Claude Skill Creator" in result.output
    assert "Codex Skill Creator" not in result.output


def test_search_command_explain_displays_score_components(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Claude Docs",
        authority="official",
        title="Claude Skill Creator",
        platform="claude",
        summary="Skill creator workflow.",
        content="skill creator workflow " * 40,
        content_hash="hash-1",
    )

    result = runner.invoke(
        app,
        ["search", "skill creator", "--platform", "claude", "--explain", "--home", str(paths.home)],
    )

    assert result.exit_code == 0
    assert "score components" in result.output
    assert "relevance=" in result.output
    assert "authority=" in result.output
    assert "completeness=" in result.output
    assert "freshness=" in result.output
    assert "platform=0.080" in result.output
    assert "final=" in result.output


def test_search_command_rerank_displays_rerank_mode(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-1",
    )

    result = runner.invoke(app, ["search", "skill creator", "--rerank", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "tfidf+rerank" in result.output
    assert "Rerank" in result.output


def test_search_command_uses_config_enabled_rerank(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    paths.config_file.write_text("retrieval:\n  rerank_by_default: true\n", encoding="utf-8")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-1",
    )

    result = runner.invoke(app, ["search", "skill creator", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "tfidf+rerank" in result.output


def test_search_command_warns_when_rerank_disabled_by_config(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    paths.config_file.write_text("retrieval:\n  rerank_enabled: false\n", encoding="utf-8")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-1",
    )

    result = runner.invoke(app, ["search", "skill creator", "--rerank", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "Rerank is disabled by configuration" in result.output
    assert "tfidf" in result.output


def test_search_command_warns_when_rerank_provider_fails(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    paths.config_file.write_text("retrieval:\n  rerank_provider: missing-provider\n", encoding="utf-8")
    seed_document(
        paths,
        source_name="Official Docs",
        authority="official",
        title="Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-1",
    )

    result = runner.invoke(app, ["search", "skill creator", "--rerank", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert "Rerank unavailable" in result.output
    assert "Unsupported rerank provider" in result.output


def test_search_command_without_explain_stays_compact(tmp_path: Path) -> None:
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
    assert "Score explanation" not in result.output
    assert "relevance=" not in result.output


def test_search_command_uses_configured_default_top_k(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    paths.ensure_directories()
    paths.config_file.write_text("retrieval:\n  top_k: 1\n", encoding="utf-8")
    seed_document(
        paths,
        source_name="One",
        authority="official",
        title="First Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-1",
    )
    seed_document(
        paths,
        source_name="Two",
        authority="official",
        title="Second Skill Creator",
        platform="codex",
        summary="Skill creator workflow.",
        content="skill creator workflow",
        content_hash="hash-2",
    )

    result = runner.invoke(app, ["search", "skill creator", "--home", str(paths.home)])

    assert result.exit_code == 0
    assert result.output.count("Skill Creator") == 1


def test_search_command_displays_empty_corpus_message(tmp_path: Path) -> None:
    result = runner.invoke(app, ["search", "skill creator", "--home", str(tmp_path / "home")])

    assert result.exit_code == 0
    assert "Local research corpus is empty" in result.output
    assert "skill-forge update" in result.output


class PreferSpecificReranker:
    def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        return [
            result.model_copy(
                update={
                    "retrieval_mode": "tfidf+rerank",
                    "rerank_score": 1.0 if "Specific" in result.title else 0.0,
                }
            )
            for result in sorted(results, key=lambda item: "Specific" not in item.title)
        ]


class FailingReranker:
    def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        raise RerankError("boom")
