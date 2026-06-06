import hashlib
import sqlite3
from pathlib import Path

from skill_forge.models.search import CorpusDocument


class CorpusReader:
    def __init__(self, database_file: Path) -> None:
        self.database_file = database_file

    def load_documents(self) -> list[CorpusDocument]:
        if not self.database_file.exists():
            return []

        with sqlite3.connect(self.database_file) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT
                    documents.id AS document_id,
                    skill_examples.id AS example_id,
                    COALESCE(skill_examples.name, documents.title, sources.name) AS title,
                    sources.name AS source_name,
                    sources.url AS source_url,
                    documents.url AS document_url,
                    sources.authority_level AS authority_level,
                    skill_examples.platform AS platform,
                    COALESCE(skill_examples.summary, skill_examples.description, documents.title, '') AS summary,
                    skill_examples.quality_score AS quality_score,
                    documents.normalized_path AS normalized_path,
                    COALESCE(documents.content_hash, '') AS content_hash,
                    COALESCE(documents.updated_at, documents.fetched_at, skill_examples.updated_at) AS updated_at
                FROM documents
                JOIN sources ON sources.id = documents.source_id
                LEFT JOIN skill_examples ON skill_examples.document_id = documents.id
                WHERE documents.normalized_path IS NOT NULL
                ORDER BY documents.id ASC, skill_examples.id ASC
                """
            ).fetchall()

        documents: list[CorpusDocument] = []
        for row in rows:
            normalized_path = Path(row["normalized_path"])
            content = self._read_text(normalized_path)
            if not content and not row["summary"]:
                continue

            documents.append(
                CorpusDocument(
                    document_id=int(row["document_id"]),
                    example_id=int(row["example_id"]) if row["example_id"] is not None else None,
                    title=row["title"] or row["source_name"],
                    source_name=row["source_name"],
                    source_url=row["source_url"],
                    document_url=row["document_url"],
                    authority_level=row["authority_level"] or "reference",
                    platform=row["platform"],
                    summary=row["summary"] or "",
                    quality_score=float(row["quality_score"]) if row["quality_score"] is not None else None,
                    normalized_path=normalized_path,
                    content_hash=row["content_hash"] or "",
                    updated_at=row["updated_at"],
                    content=content,
                )
            )
        return documents

    def load_document(self, document_id: int) -> CorpusDocument | None:
        for document in self.load_documents():
            if document.document_id == document_id:
                return document
        return None

    def corpus_signature(self, documents: list[CorpusDocument] | None = None) -> str:
        documents = documents if documents is not None else self.load_documents()
        digest = hashlib.sha256()
        for document in documents:
            digest.update(
                "|".join(
                    (
                        str(document.document_id),
                        document.content_hash,
                        str(document.normalized_path),
                        document.updated_at or "",
                    )
                ).encode("utf-8")
            )
            digest.update(b"\n")
        return digest.hexdigest()

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""
