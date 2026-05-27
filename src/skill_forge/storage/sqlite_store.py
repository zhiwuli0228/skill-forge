import sqlite3
from pathlib import Path


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        url TEXT NOT NULL,
        source_type TEXT NOT NULL,
        authority_level TEXT NOT NULL,
        enabled INTEGER DEFAULT 1,
        last_checked_at TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        title TEXT,
        raw_path TEXT,
        normalized_path TEXT,
        content_hash TEXT,
        fetched_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(source_id) REFERENCES sources(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS skill_examples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        name TEXT,
        description TEXT,
        platform TEXT,
        full_content_path TEXT,
        summary TEXT,
        tags TEXT,
        quality_score REAL DEFAULT 0,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(document_id) REFERENCES documents(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS skill_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT NOT NULL,
        title TEXT,
        content TEXT NOT NULL,
        source_example_id INTEGER,
        confidence REAL DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(source_example_id) REFERENCES skill_examples(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS drafts (
        id TEXT PRIMARY KEY,
        state_path TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT
    )
    """,
)


def initialize_database(database_file: Path) -> None:
    database_file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_file) as connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.commit()


def list_tables(database_file: Path) -> set[str]:
    with sqlite3.connect(database_file) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    return {row[0] for row in rows}
