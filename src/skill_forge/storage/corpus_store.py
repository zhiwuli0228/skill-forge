import hashlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from skill_forge.models.source import FetchedDocument, NormalizedDocument, ResearchSource
from skill_forge.research.normalizer import ContentNormalizer


@dataclass(frozen=True)
class StoredDocument:
    status: str
    document: NormalizedDocument


class CorpusStore:
    def __init__(
        self,
        database_file: Path,
        raw_dir: Path,
        normalized_dir: Path,
        normalizer: ContentNormalizer | None = None,
    ) -> None:
        self.database_file = database_file
        self.raw_dir = raw_dir
        self.normalized_dir = normalized_dir
        self.normalizer = normalizer or ContentNormalizer()

    def store(self, fetched: FetchedDocument) -> StoredDocument:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.normalized_dir.mkdir(parents=True, exist_ok=True)

        document_url = fetched.document_url or fetched.source.url_text
        content_hash = hashlib.sha256(fetched.content.encode("utf-8")).hexdigest()
        slug = _slugify(fetched.source.name)
        raw_path = self.raw_dir / f"{slug}-{content_hash[:12]}.raw"
        normalized_path = self.normalized_dir / f"{slug}-{content_hash[:12]}.md"

        existing = self._find_document(document_url, content_hash)
        normalized_content = self.normalizer.normalize(fetched.content, fetched.content_type)
        title = fetched.title or self.normalizer.title_for(fetched.source.name, normalized_content)
        summary = self.normalizer.summary_for(normalized_content)
        document = NormalizedDocument(
            source=fetched.source,
            raw_path=raw_path,
            normalized_path=normalized_path,
            content_hash=content_hash,
            title=title,
            summary=summary,
            fetched_at=fetched.fetched_at,
        )

        if existing is not None and normalized_path.exists():
            self._touch_source(fetched.source)
            return StoredDocument(status="skipped", document=document)

        raw_path.write_text(fetched.content, encoding="utf-8")
        normalized_path.write_text(normalized_content, encoding="utf-8")
        self._upsert_metadata(fetched.source, document, document_url=document_url, fetched=fetched)
        return StoredDocument(status="updated", document=document)

    def _find_document(self, url: str, content_hash: str) -> int | None:
        with sqlite3.connect(self.database_file) as connection:
            row = connection.execute(
                "SELECT id FROM documents WHERE url = ? AND content_hash = ?",
                (url, content_hash),
            ).fetchone()
        return int(row[0]) if row else None

    def _touch_source(self, source: ResearchSource) -> None:
        now = _utcnow()
        with sqlite3.connect(self.database_file) as connection:
            source_id = self._upsert_source(connection, source, now)
            connection.execute("UPDATE sources SET last_checked_at = ?, updated_at = ? WHERE id = ?", (now, now, source_id))
            connection.commit()

    def _upsert_metadata(
        self,
        source: ResearchSource,
        document: NormalizedDocument,
        *,
        document_url: str,
        fetched: FetchedDocument,
    ) -> None:
        now = _utcnow()
        with sqlite3.connect(self.database_file) as connection:
            source_id = self._upsert_source(connection, source, now)
            row = connection.execute(
                "SELECT id FROM documents WHERE url = ?",
                (document_url,),
            ).fetchone()
            if row:
                document_id = int(row[0])
                connection.execute(
                    """
                    UPDATE documents
                    SET source_id = ?, title = ?, raw_path = ?, normalized_path = ?, content_hash = ?, fetched_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        source_id,
                        document.title,
                        str(document.raw_path),
                        str(document.normalized_path),
                        document.content_hash,
                        document.fetched_at.isoformat(),
                        now,
                        document_id,
                    ),
                )
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO documents (source_id, url, title, raw_path, normalized_path, content_hash, fetched_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source_id,
                        document_url,
                        document.title,
                        str(document.raw_path),
                        str(document.normalized_path),
                        document.content_hash,
                        document.fetched_at.isoformat(),
                        now,
                    ),
                )
                document_id = int(cursor.lastrowid)

            connection.execute("DELETE FROM skill_examples WHERE document_id = ?", (document_id,))
            platform = fetched.platform or source.metadata.get("platform", "unknown")
            tags = fetched.tags if fetched.tags is not None else source.metadata.get("tags", [])
            quality_score = fetched.quality_score if fetched.quality_score is not None else 0.5
            connection.execute(
                """
                INSERT INTO skill_examples (document_id, name, description, platform, full_content_path, summary, tags, quality_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    fetched.example_name or document.title,
                    fetched.example_description or document.summary,
                    platform,
                    str(document.normalized_path),
                    document.summary,
                    ",".join(str(tag) for tag in tags),
                    quality_score,
                    now,
                    now,
                ),
            )
            connection.commit()

    def _upsert_source(self, connection: sqlite3.Connection, source: ResearchSource, now: str) -> int:
        row = connection.execute("SELECT id FROM sources WHERE name = ?", (source.name,)).fetchone()
        if row:
            source_id = int(row[0])
            connection.execute(
                """
                UPDATE sources
                SET url = ?, source_type = ?, authority_level = ?, enabled = ?, last_checked_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (source.url_text, source.type, source.authority_level, int(source.enabled), now, now, source_id),
            )
            return source_id

        cursor = connection.execute(
            """
            INSERT INTO sources (name, url, source_type, authority_level, enabled, last_checked_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (source.name, source.url_text, source.type, source.authority_level, int(source.enabled), now, now, now),
        )
        return int(cursor.lastrowid)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "source"


def _utcnow() -> str:
    return datetime.utcnow().isoformat()
