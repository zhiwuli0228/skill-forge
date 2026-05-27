from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.interaction.wizard import QuestionaryPromptAdapter
from skill_forge.models.project_context import ProjectContextSettings
from skill_forge.models.requirement import SkillRequirement
from skill_forge.project_context.enricher import ProjectContextEnricher, merge_constraints
from skill_forge.project_context.reader import ProjectContextReader
from skill_forge.project_context.summarizer import ProjectContextSummarizer
from skill_forge.storage.draft_store import DraftStore


runner = CliRunner()


def write(path: Path, content: str | bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    return path


def test_project_context_settings_defaults_are_stable() -> None:
    settings = ProjectContextSettings()

    assert settings.supported_file_names[:3] == ("AGENTS.md", "CLAUDE.md", "README.md")
    assert ".opencode" in settings.supported_dir_names
    assert "node_modules" in settings.ignored_dir_names
    assert settings.max_file_bytes > 0
    assert settings.max_total_chars > 0


def test_reader_scans_supported_files_in_deterministic_order(tmp_path: Path) -> None:
    project = tmp_path / "project"
    write(project / "README.md", "Use pytest and keep changes focused.")
    write(project / "AGENTS.md", "Use OpenSpec proposals before implementation.")
    write(project / ".opencode" / "skills" / "README.md", "opencode skill rules")
    write(project / "src" / "ignored.py", "not included")

    context = ProjectContextReader().read(project)

    assert [file.relative_path for file in context.files] == [
        ".opencode/skills/README.md",
        "AGENTS.md",
        "README.md",
    ]


def test_reader_reports_binary_large_ignored_and_total_limit_skips(tmp_path: Path) -> None:
    project = tmp_path / "project"
    write(project / "README.md", "a" * 50)
    write(project / "CLAUDE.md", "b" * 50)
    write(project / "AGENTS.md", "too large")
    write(project / ".agents" / "binary.md", b"abc\x00def")
    write(project / ".agents" / "node_modules" / "ignored.md", "ignored")
    settings = ProjectContextSettings(max_file_bytes=8, max_total_chars=60)

    context = ProjectContextReader(settings).read(project)

    reasons = {skipped.relative_path: skipped.reason for skipped in context.skipped_files}
    assert reasons["AGENTS.md"] == "too_large"
    assert reasons[".agents/binary.md"] == "binary"
    assert reasons[".agents/node_modules/ignored.md"] == "ignored_directory"
    assert "node_modules" not in "\n".join(file.relative_path for file in context.files)
    assert len("".join(file.content for file in context.files)) <= 60


def test_summarizer_detects_tools_rules_and_constraints(tmp_path: Path) -> None:
    project = tmp_path / "project"
    write(project / "AGENTS.md", "Use OpenSpec proposal, design, spec, and change workflow. Run pytest tests.")
    write(project / ".opencode" / "skills" / "README.md", "opencode project skills")

    summary = ProjectContextSummarizer().summarize(ProjectContextReader().read(project))

    assert "openspec" in summary.detected_tools
    assert "opencode" in summary.detected_tools
    assert any("OpenSpec" in rule for rule in summary.detected_rules)
    assert any("tests" in rule.lower() for rule in summary.detected_rules)
    assert any("Project constraint:" in constraint for constraint in summary.derived_constraints)


def test_enricher_merges_project_constraints_without_duplicates(tmp_path: Path) -> None:
    project = tmp_path / "project"
    write(project / "README.md", "Run pytest tests and avoid unrelated modifications.")
    requirement = SkillRequirement(
        name="project-skill",
        description="Project skill",
        constraints=["Project constraint: Run or preserve relevant tests for implementation changes."],
    )

    summary = ProjectContextEnricher().enrich(requirement, project)

    assert summary.summary_text
    assert requirement.constraints.count(
        "Project constraint: Run or preserve relevant tests for implementation changes."
    ) == 1
    assert any("Avoid unrelated" in constraint for constraint in requirement.constraints)


def test_merge_constraints_deduplicates_case_insensitively() -> None:
    merged = merge_constraints(["Run tests"], ["run tests", "Keep scope focused"])

    assert merged == ["Run tests", "Keep scope focused"]


def test_create_with_project_injects_constraints_into_generated_skill(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    write(project / "AGENTS.md", "Use OpenSpec proposal and change workflow. Avoid unrelated modifications.")

    result = runner.invoke(app, ["create", "OpenSpec change skill", "--project", str(project), "--home", str(home)])

    generated = list((home / "output").glob("*/SKILL.md"))
    assert result.exit_code == 0
    assert len(generated) == 1
    content = generated[0].read_text(encoding="utf-8")
    assert "Project constraint: Use the OpenSpec change workflow" in content
    assert "Avoid unrelated modifications" in content


def test_interactive_create_with_project_persists_context_in_draft(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    write(project / "AGENTS.md", "Use OpenSpec proposal and change workflow. Run pytest tests.")
    monkeypatch.setattr(QuestionaryPromptAdapter, "text", lambda self, message, default="": default)
    monkeypatch.setattr(QuestionaryPromptAdapter, "multiline", lambda self, message, default: default)

    result = runner.invoke(
        app,
        ["create", "OpenSpec change skill", "--project", str(project), "--interactive", "--home", str(home)],
    )

    drafts = list((home / "drafts").glob("*.json"))
    assert result.exit_code == 0
    assert drafts
    draft = DraftStore(home / "drafts").load(drafts[0].stem)
    assert draft.project_path == str(project.resolve())
    assert draft.project_context_summary
    assert "OpenSpec" in draft.project_context_summary


def test_resume_keeps_stored_project_context_without_rescan(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    write(project / "AGENTS.md", "Use OpenSpec proposal and change workflow. Run pytest tests.")
    monkeypatch.setattr(QuestionaryPromptAdapter, "text", lambda self, message, default="": default)
    monkeypatch.setattr(QuestionaryPromptAdapter, "multiline", lambda self, message, default: default)
    create = runner.invoke(
        app,
        ["create", "OpenSpec change skill", "--project", str(project), "--interactive", "--home", str(home)],
    )
    draft_path = next((home / "drafts").glob("*.json"))
    draft = DraftStore(home / "drafts").load(draft_path.stem)
    original_summary = draft.project_context_summary
    write(project / "AGENTS.md", "changed project context after draft generation")

    resume = runner.invoke(app, ["resume", draft.draft_id, "--home", str(home)])
    reloaded = DraftStore(home / "drafts").load(draft.draft_id)

    assert create.exit_code == 0
    assert resume.exit_code == 0
    assert reloaded.project_context_summary == original_summary
