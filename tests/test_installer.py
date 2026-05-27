from pathlib import Path

import pytest

from skill_forge.config import default_config
from skill_forge.generator.skill_generator import SkillGenerator
from skill_forge.installer.installer import DestinationExistsError, SkillInstaller, SourceSkillNotFoundError
from skill_forge.requirement.analyzer import RequirementAnalyzer


def _installer(home: Path, project: Path) -> SkillInstaller:
    return SkillInstaller(default_config(), home=home, project_dir=project)


def _generate_source(home: Path) -> Path:
    output = home / "output"
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")
    return SkillGenerator().generate(requirement, output).path


def test_installer_resolves_project_paths(tmp_path: Path) -> None:
    installer = _installer(tmp_path / "home", tmp_path / "project")

    assert installer.destination_path("demo", target="opencode", scope="project") == (
        tmp_path / "project" / ".opencode" / "skills" / "demo"
    )
    assert installer.destination_path("demo", target="claude", scope="project") == (
        tmp_path / "project" / ".claude" / "skills" / "demo"
    )
    assert installer.destination_path("demo", target="codex", scope="project") == (
        tmp_path / "project" / ".codex" / "skills" / "demo"
    )


def test_installer_resolves_user_paths(tmp_path: Path) -> None:
    installer = _installer(tmp_path / "home", tmp_path / "project")

    assert installer.destination_path("demo", target="opencode", scope="user").as_posix().endswith(
        ".config/opencode/skills/demo"
    )
    assert installer.destination_path("demo", target="claude", scope="user").as_posix().endswith(
        ".claude/skills/demo"
    )
    assert installer.destination_path("demo", target="codex", scope="user").as_posix().endswith(".codex/skills/demo")


def test_installer_copies_skill_package(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    _generate_source(home)

    installed = _installer(home, project).install("java-bug-investigation", target="opencode", scope="project")

    assert installed.destination_path == project / ".opencode" / "skills" / "java-bug-investigation"
    assert (installed.destination_path / "SKILL.md").is_file()


def test_installer_fails_for_missing_source(tmp_path: Path) -> None:
    with pytest.raises(SourceSkillNotFoundError):
        _installer(tmp_path / "home", tmp_path / "project").install("missing", target="opencode", scope="project")


def test_installer_does_not_overwrite_by_default(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    _generate_source(home)
    installer = _installer(home, project)
    installer.install("java-bug-investigation", target="opencode", scope="project")

    with pytest.raises(DestinationExistsError):
        installer.install("java-bug-investigation", target="opencode", scope="project")


def test_installer_force_overwrites_existing_destination(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    source = _generate_source(home)
    installer = _installer(home, project)
    installed = installer.install("java-bug-investigation", target="opencode", scope="project")
    (installed.destination_path / "extra.txt").write_text("old", encoding="utf-8")
    (source / "new.txt").write_text("new", encoding="utf-8")

    installed = installer.install("java-bug-investigation", target="opencode", scope="project", force=True)

    assert not (installed.destination_path / "extra.txt").exists()
    assert (installed.destination_path / "new.txt").read_text(encoding="utf-8") == "new"
