from pathlib import Path

from skill_forge.storage.sqlite_store import initialize_database, list_tables


def test_initialize_database_creates_baseline_tables(tmp_path: Path) -> None:
    database = tmp_path / "db" / "skill_forge.sqlite"

    initialize_database(database)

    assert {
        "sources",
        "documents",
        "skill_examples",
        "skill_patterns",
        "drafts",
    }.issubset(list_tables(database))


def test_initialize_database_is_idempotent(tmp_path: Path) -> None:
    database = tmp_path / "db" / "skill_forge.sqlite"

    initialize_database(database)
    initialize_database(database)

    assert "sources" in list_tables(database)
