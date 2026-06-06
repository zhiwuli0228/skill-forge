import json
import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from skill_forge.adoption.service import AdoptedSkillExistsError, CorpusDocumentNotFoundError, SkillAdoptionService
from skill_forge.cli import app
from skill_forge.storage.corpus_reader import CorpusReader
from skill_forge.storage.paths import SkillForgePaths
from skill_forge.storage.sqlite_store import initialize_database


runner = CliRunner()


VALID_SKILL = """---
name: adopted-review
description: Use this skill when adopting community review workflows. Do not use it for unrelated planning.
---

# Purpose

Review adopted code changes with clear findings.

## When to use

- Use when reviewing a cached community workflow.

## When not to use

- Do not use for release planning.

## Workflow

1. Inspect the change.
2. Identify correctness risks.
3. Check test coverage.

## Output format

- Findings
- Tests

## Quality gates

- Findings must cite evidence.
- Tests must be explicit.
"""


def seed_corpus_skill(paths: SkillForgePaths, *, title: str = "Adopted Review", content: str = VALID_SKILL) -> None:
    paths.ensure_directories()
    initialize_database(paths.database_file)
    normalized_path = paths.corpus_normalized_dir / f"{title.lower().replace(' ', '-')}.md"
    normalized_path.write_text(content, encoding="utf-8")
    with sqlite3.connect(paths.database_file) as connection:
        source_id = connection.execute(
            """
            INSERT INTO sources (name, url, source_type, authority_level, enabled, last_checked_at, created_at, updated_at)
            VALUES (?, ?, 'github', 'community', 1, '2026-05-28T00:00:00', '2026-05-28T00:00:00', '2026-05-28T00:00:00')
            """,
            ("Community Repo", "https://github.com/example/skills"),
        ).lastrowid
        document_id = connection.execute(
            """
            INSERT INTO documents (source_id, url, title, raw_path, normalized_path, content_hash, fetched_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, '2026-05-28T00:00:00', '2026-05-28T00:00:00')
            """,
            (
                source_id,
                "https://raw.githubusercontent.com/example/skills/main/review/SKILL.md",
                title,
                str(paths.corpus_raw_dir / "review.raw"),
                str(normalized_path),
                "hash-1",
            ),
        ).lastrowid
        connection.execute(
            """
            INSERT INTO skill_examples (document_id, name, description, platform, full_content_path, summary, tags, quality_score, created_at, updated_at)
            VALUES (?, ?, 'Review skill.', 'codex', ?, 'Review skill.', 'community', 0.8, '2026-05-28T00:00:00', '2026-05-28T00:00:00')
            """,
            (document_id, title, str(normalized_path)),
        )
        connection.commit()


def test_adoption_service_creates_package_and_provenance(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_corpus_skill(paths)

    result = SkillAdoptionService(output_dir=tmp_path / "output", corpus_reader=CorpusReader(paths.database_file)).adopt(document_id=1)

    metadata = json.loads(result.package.path.joinpath("skill-forge.json").read_text(encoding="utf-8"))
    assert result.package.name == "adopted-review"
    assert result.package.skill_md_path.read_text(encoding="utf-8") == VALID_SKILL
    assert result.quality_report.ok is True
    assert metadata["origin_type"] == "community-adopted"
    assert metadata["source_name"] == "Community Repo"
    assert metadata["document_id"] == 1
    assert metadata["example_id"] == 1
    assert metadata["source_platform"] == "codex"
    assert metadata["document_url"].endswith("/review/SKILL.md")


def test_adoption_service_uses_title_fallback_and_name_override_without_rewrite(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    content = "# Purpose\n\nNo frontmatter here."
    seed_corpus_skill(paths, title="Team Review Skill", content=content)
    service = SkillAdoptionService(output_dir=tmp_path / "output", corpus_reader=CorpusReader(paths.database_file))

    fallback = service.adopt(document_id=1)
    other_paths = SkillForgePaths.resolve(tmp_path / "other-home")
    seed_corpus_skill(other_paths, title="Team Review Skill", content=content)
    override = SkillAdoptionService(
        output_dir=tmp_path / "other-output",
        corpus_reader=CorpusReader(other_paths.database_file),
    ).adopt(document_id=1, name="custom-adopted")

    assert fallback.package.name == "team-review-skill"
    assert override.package.name == "custom-adopted"
    assert override.package.skill_md_path.read_text(encoding="utf-8") == content


def test_adoption_service_rejects_missing_document_and_conflict(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_corpus_skill(paths)
    service = SkillAdoptionService(output_dir=tmp_path / "output", corpus_reader=CorpusReader(paths.database_file))
    service.adopt(document_id=1)

    with pytest.raises(CorpusDocumentNotFoundError):
        service.adopt(document_id=999)
    with pytest.raises(AdoptedSkillExistsError):
        service.adopt(document_id=1)


def test_adoption_cli_success_and_show_provenance(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_corpus_skill(paths)

    adopted = runner.invoke(app, ["adopt", "--document-id", "1", "--home", str(paths.home)])
    shown = runner.invoke(app, ["show", "adopted-review", "--home", str(paths.home)])

    assert adopted.exit_code == 0
    assert "Skill package adopted" in adopted.output
    assert "Quality:" in adopted.output
    assert (paths.home / "output" / "adopted-review" / "SKILL.md").is_file()
    assert shown.exit_code == 0
    assert "community-adopted" in shown.output
    assert "Community Repo" in shown.output
    assert "Document ID" in shown.output


def test_adoption_cli_name_override_warning_and_conflict(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_corpus_skill(paths)

    first = runner.invoke(app, ["adopt", "--document-id", "1", "--name", "custom-adopted", "--home", str(paths.home)])
    second = runner.invoke(app, ["adopt", "--document-id", "1", "--name", "custom-adopted", "--home", str(paths.home)])

    assert first.exit_code == 0
    assert "package_name_mismatch" in first.output
    assert "Suggested fixes" in first.output
    assert second.exit_code == 1
    assert "already exists" in second.output


def test_adoption_cli_missing_document_and_invalid_skill(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path / "home")
    seed_corpus_skill(paths, content="not a valid skill")

    missing = runner.invoke(app, ["adopt", "--document-id", "999", "--home", str(paths.home)])
    invalid = runner.invoke(app, ["adopt", "--document-id", "1", "--home", str(paths.home)])

    assert missing.exit_code == 1
    assert "Cached corpus document not found" in missing.output
    assert invalid.exit_code == 1
    assert "Adopted Skill package is invalid" in invalid.output
    assert "Suggested fixes" in invalid.output
