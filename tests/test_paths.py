from pathlib import Path

from skill_forge.storage.paths import HOME_ENV_VAR, SkillForgePaths


def test_resolve_uses_explicit_home(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path)

    assert paths.home == tmp_path
    assert paths.config_file == tmp_path / "config.yaml"
    assert paths.database_file == tmp_path / "db" / "skill_forge.sqlite"


def test_resolve_uses_environment_home(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(HOME_ENV_VAR, str(tmp_path))

    paths = SkillForgePaths.resolve()

    assert paths.home == tmp_path


def test_ensure_directories_creates_workspace(tmp_path: Path) -> None:
    paths = SkillForgePaths.resolve(tmp_path)

    paths.ensure_directories()

    for directory in paths.workspace_directories:
        assert directory.is_dir()
