from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.table import Table

from skill_forge.blueprints.enricher import BlueprintRequirementEnricher
from skill_forge.blueprints.loader import (
    BlueprintError,
    BlueprintLoader,
    BlueprintNotFoundError,
    DuplicateBlueprintError,
    PROJECT_BLUEPRINTS_RELATIVE_DIR,
)
from skill_forge.config import DEFAULT_OUTPUT_DIR, load_config, write_default_config
from skill_forge.generator.skill_generator import SkillGenerator, SkillPackageExistsError
from skill_forge.evals.runner import EvalCaseError, SkillEvaluator
from skill_forge.interaction.wizard import SkillCreationWizard
from skill_forge.installer.installer import DestinationExistsError, SkillInstaller, SourceSkillNotFoundError
from skill_forge.library.manager import (
    GeneratedSkillMissingSkillMdError,
    GeneratedSkillNotFoundError,
    SkillLibraryManager,
)
from skill_forge.llm.refiner import (
    LLMConfigurationError,
    LLMResponseError,
    OpenAICompatibleLLMClient,
    RequirementLLMRefiner,
)
from skill_forge.models.quality import GenerationQualityReport, RepairSuggestion, build_generation_quality_report, build_repair_suggestions
from skill_forge.models.generated import PROVENANCE_METADATA_FILENAME, GenerationProvenanceMetadata
from skill_forge.project_context.enricher import ProjectContextEnricher
from skill_forge.research.fetcher import HttpSourceFetcher
from skill_forge.research.sources import SourceConfigError
from skill_forge.research.updater import ResearchUpdater, UpdateResult
from skill_forge.retrieval.indexer import TfidfIndexer, TfidfIndexStore
from skill_forge.retrieval.reranker import RerankError, build_reranker
from skill_forge.retrieval.retriever import CorpusRetriever
from skill_forge.requirement.analyzer import RequirementAnalyzer
from skill_forge.models.search import SearchResult
from skill_forge.storage.corpus_reader import CorpusReader
from skill_forge.storage.draft_store import DraftNotFoundError, DraftStore
from skill_forge.storage.paths import SkillForgePaths
from skill_forge.storage.sqlite_store import initialize_database
from skill_forge.upgrade.service import (
    CandidateExistsError,
    InvalidCandidateNameError,
    InvalidUpgradeCandidateError,
    InvalidUpgradeProvenanceError,
    MissingUpgradeBlueprintError,
    MissingUpgradeProvenanceError,
    SkillUpgradeResult,
    SkillUpgradeService,
)
from skill_forge.validator.skill_validator import SkillValidator

app = typer.Typer(help="Skill Forge CLI.")
blueprints_app = typer.Typer(help="Inspect built-in Skill blueprints.")
app.add_typer(blueprints_app, name="blueprints")
console = Console()


@app.callback()
def root() -> None:
    """Skill Forge command line interface."""


@blueprints_app.command("list")
def list_blueprints(
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    project: Annotated[
        Path | None,
        typer.Option("--project", help="Include project custom blueprints from this project directory."),
    ] = None,
) -> None:
    """List built-in Skill blueprints."""
    try:
        records = _blueprint_loader(home, project).load_records()
    except DuplicateBlueprintError as exc:
        _print_duplicate_blueprint_error(exc)
        raise typer.Exit(code=1) from exc
    except BlueprintError as exc:
        console.print(f"[red]Blueprint error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Skill blueprints")
    table.add_column("ID", no_wrap=True)
    table.add_column("Name", no_wrap=True)
    table.add_column("Task type", no_wrap=True)
    table.add_column("Source", no_wrap=True)
    table.add_column("Description")
    for record in records:
        blueprint = record.blueprint
        table.add_row(blueprint.id, blueprint.name, blueprint.task_type, record.source, blueprint.description)
    console.print(table)


@blueprints_app.command("show")
def show_blueprint(
    blueprint_id: Annotated[str, typer.Argument(help="Built-in blueprint id to inspect.")],
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    project: Annotated[
        Path | None,
        typer.Option("--project", help="Include project custom blueprints from this project directory."),
    ] = None,
) -> None:
    """Show a built-in Skill blueprint."""
    try:
        record = _blueprint_loader(home, project).get_record(blueprint_id)
        blueprint = record.blueprint
    except BlueprintNotFoundError as exc:
        console.print(f"[red]Blueprint not found:[/red] {exc.blueprint_id}")
        raise typer.Exit(code=1) from exc
    except DuplicateBlueprintError as exc:
        _print_duplicate_blueprint_error(exc)
        raise typer.Exit(code=1) from exc
    except BlueprintError as exc:
        console.print(f"[red]Blueprint error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Blueprint: {blueprint.id}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Name", blueprint.name)
    table.add_row("Description", blueprint.description)
    table.add_row("Task type", blueprint.task_type)
    table.add_row("Source", record.source)
    table.add_row("Path", str(record.path))
    table.add_row("When to use", _format_list(blueprint.when_to_use))
    table.add_row("When not to use", _format_list(blueprint.when_not_to_use))
    table.add_row("Required inputs", _format_list(blueprint.required_inputs))
    table.add_row("Workflow", _format_numbered_list(blueprint.workflow))
    table.add_row("Constraints", _format_list(blueprint.constraints))
    table.add_row("Expected outputs", _format_list(blueprint.expected_outputs))
    table.add_row("Quality gates", _format_list(blueprint.quality_gates))
    console.print(table)


@app.command()
def init(
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
) -> None:
    """Initialize the local Skill Forge workspace."""
    paths = SkillForgePaths.resolve(home)
    created_dirs = paths.ensure_directories()
    config_created = write_default_config(paths.config_file)
    initialize_database(paths.database_file)

    table = Table(title="Skill Forge initialized")
    table.add_column("Item")
    table.add_column("Path")
    table.add_column("Status")

    table.add_row("Home", str(paths.home), "ready")
    table.add_row("Config", str(paths.config_file), "created" if config_created else "preserved")
    table.add_row("Database", str(paths.database_file), "ready")
    for directory in created_dirs:
        table.add_row("Directory", str(directory), "ready")

    console.print(table)


@app.command()
def validate(
    skill_path: Annotated[Path, typer.Argument(help="Path to a Skill package directory.")],
) -> None:
    """Validate a Skill package."""
    result = SkillValidator().validate(skill_path)
    _print_validation_result(result)
    if not result.ok:
        raise typer.Exit(code=1)


@app.command()
def install(
    skill_name: Annotated[str, typer.Argument(help="Generated Skill package name to install.")],
    target: Annotated[
        Literal["codex", "opencode", "claude"],
        typer.Option("--target", help="Target agent platform."),
    ],
    scope: Annotated[
        Literal["project", "user"],
        typer.Option("--scope", help="Install scope."),
    ],
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
    project: Annotated[
        Path | None,
        typer.Option("--project", help="Project directory for project-scope installs."),
    ] = None,
    force: Annotated[bool, typer.Option("--force", help="Overwrite an existing installed Skill.")] = False,
) -> None:
    """Install a generated Skill package into an agent platform."""
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    config = load_config(paths.config_file)
    if output_dir is not None:
        config.create.output_dir = str(output_dir)
    elif home is not None and config.create.output_dir == DEFAULT_OUTPUT_DIR:
        config.create.output_dir = str(paths.output_dir)
    installer = SkillInstaller(config, home=paths.home, project_dir=project)

    try:
        installed = installer.install(skill_name, target=target, scope=scope, force=force)
    except SourceSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except DestinationExistsError as exc:
        console.print(f"[red]Installed Skill already exists:[/red] {exc.path}")
        console.print("Use --force to overwrite it.")
        raise typer.Exit(code=1) from exc

    table = Table(title="Skill installed")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Name", installed.name)
    table.add_row("Target", installed.target)
    table.add_row("Scope", installed.scope)
    table.add_row("Destination", str(installed.destination_path))
    console.print(table)


@app.command()
def update(
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
) -> None:
    """Refresh the local research corpus from configured sources."""
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    initialize_database(paths.database_file)

    updater = ResearchUpdater(paths=paths, fetcher=HttpSourceFetcher())
    try:
        result = updater.update()
    except SourceConfigError as exc:
        console.print(f"[red]Source configuration error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    _print_update_result(result)
    if not result.ok:
        raise typer.Exit(code=1)


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query for local Skill research references.")],
    top_k: Annotated[
        int | None,
        typer.Option("--top-k", min=1, help="Maximum number of results to display."),
    ] = None,
    platform: Annotated[
        Literal["codex", "opencode", "claude"] | None,
        typer.Option("--platform", help="Prefer results matching a target platform."),
    ] = None,
    explain: Annotated[
        bool,
        typer.Option("--explain", help="Show deterministic score component explanations."),
    ] = False,
    rerank: Annotated[
        bool,
        typer.Option("--rerank", help="Rerank TF-IDF candidates with the configured local reranker."),
    ] = False,
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
) -> None:
    """Search the local research corpus."""
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    initialize_database(paths.database_file)
    config = load_config(paths.config_file)

    limit = top_k if top_k is not None else config.retrieval.top_k
    reader = CorpusReader(paths.database_file)
    indexer = TfidfIndexer(reader, TfidfIndexStore(paths.index_dir))
    use_rerank = rerank or config.retrieval.rerank_by_default
    reranker = None
    rerank_warning = None
    if use_rerank:
        if not config.retrieval.rerank_enabled:
            rerank_warning = "Rerank is disabled by configuration; using TF-IDF results."
        else:
            try:
                reranker = build_reranker(config.retrieval.rerank_provider)
            except RerankError as exc:
                rerank_warning = f"Rerank unavailable; using TF-IDF results: {exc}"
    response = CorpusRetriever(indexer).search_with_metadata(
        query,
        top_k=limit,
        platform=platform,
        reranker=reranker,
        rerank_candidate_multiplier=config.retrieval.rerank_candidate_multiplier,
    )
    if response.warning is not None:
        rerank_warning = response.warning.message
    _print_search_result(response.results, explain=explain, retrieval_mode=response.retrieval_mode, warning=rerank_warning)


@app.command("list")
def list_generated_skills(
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
) -> None:
    """List generated Skill packages."""
    manager = _library_manager(home, output_dir)
    entries = manager.list()
    if not entries:
        console.print(f"[yellow]No generated Skill packages found:[/yellow] {manager.output_dir}")
        return

    table = Table(title="Generated Skills")
    table.add_column("Name", no_wrap=True)
    table.add_column("Description")
    table.add_column("Path")
    for entry in entries:
        table.add_row(entry.name, entry.description or "-", str(entry.path))
    console.print(table)


@app.command("show")
def show_generated_skill(
    skill_name: Annotated[str, typer.Argument(help="Generated Skill package name to inspect.")],
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
) -> None:
    """Show generated Skill package metadata."""
    manager = _library_manager(home, output_dir)
    try:
        entry = manager.show(skill_name)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Generated Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Generated Skill: {entry.name}")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Name", entry.name)
    table.add_row("Frontmatter name", entry.frontmatter_name or "-")
    table.add_row("Description", entry.description or "-")
    table.add_row("Package", str(entry.path))
    table.add_row("SKILL.md", str(entry.skill_md_path))
    table.add_row("References", str(entry.reference_count))
    table.add_row("Assets", str(entry.asset_count))
    table.add_row("Scripts", str(entry.script_count))
    if entry.provenance is not None:
        provenance = entry.provenance
        table.add_row("Generated at", provenance.generated_at)
        table.add_row("Blueprint", provenance.blueprint_id or "-")
        table.add_row("Blueprint source", provenance.blueprint_source or "-")
        table.add_row("LLM enabled", str(provenance.llm_enabled))
        table.add_row("Quality", f"{provenance.quality_score}/100 ({provenance.quality_status})")
        table.add_row("Project context", provenance.project_context_path or "-")
    else:
        table.add_row("Provenance", "missing")
    if entry.eval_report is not None:
        table.add_row(
            "Eval summary",
            f"{entry.eval_report.passed}/{entry.eval_report.total} passed, {entry.eval_report.failed} failed",
        )
    console.print(table)


@app.command("eval")
def eval_generated_skill(
    skill_name: Annotated[str, typer.Argument(help="Generated Skill package name to evaluate.")],
    case: Annotated[
        Path | None,
        typer.Option("--case", help="Run one eval case YAML file."),
    ] = None,
    cases: Annotated[
        Path | None,
        typer.Option("--cases", help="Run all eval case YAML files from a directory."),
    ] = None,
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
) -> None:
    """Run deterministic local eval cases against a generated Skill package."""
    if (case is None and cases is None) or (case is not None and cases is not None):
        console.print("[red]Specify exactly one of --case or --cases.[/red]")
        raise typer.Exit(code=1)

    manager = _library_manager(home, output_dir)
    try:
        entry = manager.show(skill_name)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Generated Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    evaluator = SkillEvaluator()
    try:
        eval_cases = [evaluator.load_case(case)] if case is not None else evaluator.load_cases_from_directory(cases)
        report = evaluator.evaluate(skill_name, entry.path, eval_cases)
    except EvalCaseError as exc:
        console.print(f"[red]Eval error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    _print_eval_report(report)
    if report.failed:
        raise typer.Exit(code=1)


@app.command("upgrade")
def upgrade_generated_skill(
    skill_name: Annotated[str, typer.Argument(help="Generated Skill package name to upgrade.")],
    candidate_name: Annotated[
        str | None,
        typer.Option("--candidate-name", help="Candidate package name. Defaults to <skill-name>-upgraded."),
    ] = None,
    force: Annotated[bool, typer.Option("--force", help="Replace an existing candidate package.")] = False,
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
    project: Annotated[
        Path | None,
        typer.Option("--project", help="Include project custom blueprints from this project directory."),
    ] = None,
) -> None:
    """Generate an upgrade candidate for an existing generated Skill package."""
    manager = _library_manager(home, output_dir)
    try:
        entry = manager.show(skill_name)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Generated Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    service = SkillUpgradeService(output_dir=manager.output_dir, blueprint_loader=_blueprint_loader(home, project))
    try:
        result = service.upgrade(entry.path, candidate_name=candidate_name, force=force)
    except MissingUpgradeProvenanceError as exc:
        console.print(f"[red]Upgrade requires provenance metadata:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except InvalidUpgradeProvenanceError as exc:
        console.print(f"[red]Invalid provenance metadata:[/red] {exc.path}")
        console.print(exc.message)
        raise typer.Exit(code=1) from exc
    except MissingUpgradeBlueprintError as exc:
        console.print(f"[red]Upgrade blueprint not found:[/red] {exc.blueprint_id}")
        raise typer.Exit(code=1) from exc
    except CandidateExistsError as exc:
        console.print(f"[red]Upgrade candidate already exists:[/red] {exc.path}")
        console.print("Use --force to replace the candidate package.")
        raise typer.Exit(code=1) from exc
    except InvalidCandidateNameError as exc:
        console.print(f"[red]Invalid candidate name:[/red] {exc.name}")
        console.print("Use lowercase kebab-case, such as java-bug-investigation-upgraded.")
        raise typer.Exit(code=1) from exc
    except DuplicateBlueprintError as exc:
        _print_duplicate_blueprint_error(exc)
        raise typer.Exit(code=1) from exc
    except BlueprintError as exc:
        console.print(f"[red]Blueprint error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    except InvalidUpgradeCandidateError as exc:
        console.print(f"[red]Upgrade candidate is invalid:[/red] {exc.package.path}")
        _print_generation_quality_report(exc.quality_report)
        raise typer.Exit(code=1) from exc
    except SkillPackageExistsError as exc:
        console.print(f"[red]Upgrade candidate already exists:[/red] {exc.path}")
        console.print("Use --force to replace the candidate package.")
        raise typer.Exit(code=1) from exc

    _print_upgrade_result(result)


@app.command("diff")
def diff_generated_skills(
    left: Annotated[str, typer.Argument(help="First generated Skill package name.")],
    right: Annotated[str, typer.Argument(help="Second generated Skill package name.")],
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
) -> None:
    """Diff generated Skill package SKILL.md files."""
    manager = _library_manager(home, output_dir)
    try:
        diff_lines = manager.diff(left, right)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Generated Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    if not diff_lines:
        console.print("[green]No differences found.[/green]")
        return
    console.print("".join(diff_lines), end="")


@app.command()
def create(
    requirement: Annotated[str, typer.Argument(help="Natural language description of the Skill to generate.")],
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    interactive: Annotated[bool, typer.Option("--interactive", help="Refine the requirement through prompts.")] = False,
    project: Annotated[
        Path | None,
        typer.Option("--project", help="Read project context and inject project constraints."),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
    blueprint: Annotated[
        str | None,
        typer.Option("--blueprint", help="Built-in blueprint id to apply before generation."),
    ] = None,
    llm: Annotated[bool, typer.Option("--llm", help="Refine the requirement with a configured LLM before generation.")] = False,
) -> None:
    """Generate a local Skill package from a requirement string."""
    if llm and interactive:
        console.print("[red]LLM-assisted generation is only supported for non-interactive create.[/red]")
        raise typer.Exit(code=1)

    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    config = load_config(paths.config_file)

    analyzer = RequirementAnalyzer()
    skill_requirement = analyzer.analyze(
        requirement,
        target_platform=config.create.default_target,
        language=config.create.default_language,
    )
    if llm:
        try:
            skill_requirement = RequirementLLMRefiner(OpenAICompatibleLLMClient.from_env()).refine(
                requirement,
                skill_requirement,
            )
        except LLMConfigurationError as exc:
            console.print(f"[red]LLM configuration error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        except LLMResponseError as exc:
            console.print(f"[red]LLM response error:[/red] {exc}")
            raise typer.Exit(code=1) from exc

    try:
        skill_requirement = BlueprintRequirementEnricher(_blueprint_loader(home, project)).enrich(
            skill_requirement,
            blueprint_id=blueprint,
        )
    except BlueprintNotFoundError as exc:
        console.print(f"[red]Blueprint not found:[/red] {exc.blueprint_id}")
        raise typer.Exit(code=1) from exc
    except DuplicateBlueprintError as exc:
        _print_duplicate_blueprint_error(exc)
        raise typer.Exit(code=1) from exc
    except BlueprintError as exc:
        console.print(f"[red]Blueprint error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    project_summary = None
    if project is not None:
        project_summary = ProjectContextEnricher().enrich(skill_requirement, project)
    output_path = _resolve_output_dir(
        str(output_dir) if output_dir is not None else config.create.output_dir,
        paths.home,
        isolate_default=home is not None and output_dir is None,
    )

    if interactive:
        draft_store = DraftStore(paths.drafts_dir)
        wizard = SkillCreationWizard(draft_store=draft_store, output_dir=output_path)
        draft = wizard.create_draft(skill_requirement)
        if project_summary is not None:
            draft.project_path = str(project.expanduser().resolve())
            draft.project_context_summary = project_summary.summary_text
            draft_store.save(draft)
        try:
            draft = wizard.run(draft)
        except SkillPackageExistsError as exc:
            console.print(f"[red]Skill package already exists:[/red] {exc.path}")
            console.print(f"Draft saved: {draft.draft_id}")
            raise typer.Exit(code=1) from exc
        _print_draft_result(draft)
        return

    try:
        package = SkillGenerator().generate(skill_requirement, output_path)
    except SkillPackageExistsError as exc:
        console.print(f"[red]Skill package already exists:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    attachment_paths = [*package.references, *package.assets, *package.scripts]
    validation_result = SkillValidator().validate(package.path, attachment_paths=attachment_paths)
    quality_report = build_generation_quality_report(validation_result)

    table = Table(title="Skill package generated")
    table.add_column("Item")
    table.add_column("Path")
    table.add_row("Name", package.name)
    table.add_row("Package", str(package.path))
    table.add_row("SKILL.md", str(package.skill_md_path))
    console.print(table)
    _print_generation_quality_report(quality_report)

    if not quality_report.ok:
        console.print(f"[red]Generated Skill package is invalid:[/red] {package.path}")
        raise typer.Exit(code=1)

    _write_generation_provenance(
        package=package,
        skill_requirement=skill_requirement,
        requirement_text=requirement,
        llm_enabled=llm,
        project=project,
        quality_report=quality_report,
    )


@app.command()
def resume(
    draft_id: Annotated[str, typer.Argument(help="Draft id to resume.")],
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
) -> None:
    """Resume an interactive Skill draft."""
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    config = load_config(paths.config_file)
    output_path = _resolve_output_dir(
        str(output_dir) if output_dir is not None else config.create.output_dir,
        paths.home,
        isolate_default=home is not None and output_dir is None,
    )
    draft_store = DraftStore(paths.drafts_dir)

    try:
        draft = draft_store.load(draft_id)
    except DraftNotFoundError as exc:
        console.print(f"[red]Draft not found:[/red] {exc.draft_id}")
        raise typer.Exit(code=1) from exc

    try:
        draft = SkillCreationWizard(draft_store=draft_store, output_dir=output_path).run(draft)
    except SkillPackageExistsError as exc:
        console.print(f"[red]Skill package already exists:[/red] {exc.path}")
        console.print(f"Draft saved: {draft.draft_id}")
        raise typer.Exit(code=1) from exc

    _print_draft_result(draft)


def _resolve_output_dir(value: str, home: Path, *, isolate_default: bool = False) -> Path:
    if isolate_default and value == DEFAULT_OUTPUT_DIR:
        return home / "output"
    if value.startswith("~/.skill-forge"):
        return Path(value.replace("~/.skill-forge", str(home), 1))
    return Path(value).expanduser()


def _library_manager(home: Path | None, output_dir: Path | None = None) -> SkillLibraryManager:
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    config = load_config(paths.config_file)
    output_path = _resolve_output_dir(
        str(output_dir) if output_dir is not None else config.create.output_dir,
        paths.home,
        isolate_default=home is not None and output_dir is None,
    )
    return SkillLibraryManager(output_path)


def _blueprint_loader(home: Path | None = None, project: Path | None = None) -> BlueprintLoader:
    paths = SkillForgePaths.resolve(home)
    project_blueprint_dir = None
    if project is not None:
        project_blueprint_dir = project.expanduser().resolve() / PROJECT_BLUEPRINTS_RELATIVE_DIR
    return BlueprintLoader(
        user_blueprint_dir=paths.blueprints_dir,
        project_blueprint_dir=project_blueprint_dir,
    )


def _print_duplicate_blueprint_error(exc: DuplicateBlueprintError) -> None:
    console.print(f"[red]Duplicate blueprint id:[/red] {exc.blueprint_id}")
    for path in exc.paths:
        console.print(f"- {path}")


def _write_generation_provenance(
    *,
    package,
    skill_requirement,
    requirement_text: str,
    llm_enabled: bool,
    project: Path | None,
    quality_report: GenerationQualityReport,
) -> None:
    metadata = GenerationProvenanceMetadata(
        generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        skill_name=package.name,
        requirement_text=requirement_text,
        target_platform=package.target_platform,
        language=skill_requirement.language,
        task_type=skill_requirement.task_type,
        blueprint_id=skill_requirement.applied_blueprint_id,
        blueprint_source=skill_requirement.applied_blueprint_source,
        llm_enabled=llm_enabled,
        project_context_path=str(project.expanduser().resolve()) if project is not None else None,
        quality_score=quality_report.score,
        quality_status=quality_report.status,
        references=sorted(package.references),
        assets=sorted(package.assets),
        scripts=sorted(package.scripts),
    )
    metadata_path = package.path / PROVENANCE_METADATA_FILENAME
    metadata_path.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")


def _format_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "-"


def _format_numbered_list(items: list[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1)) if items else "-"


def _print_validation_result(result) -> None:
    table = Table(title="Skill validation")
    table.add_column("Level")
    table.add_column("Code")
    table.add_column("Message")

    for issue in result.errors:
        table.add_row("error", issue.code, issue.message)
    for issue in result.warnings:
        table.add_row("warning", issue.code, issue.message)

    if result.ok:
        if result.warnings:
            console.print("[yellow]Skill package is valid with warnings.[/yellow]")
        else:
            console.print("[green]Skill package is valid.[/green]")
    else:
        console.print("[red]Skill package is invalid.[/red]")

    if result.errors or result.warnings:
        console.print(table)
        _print_repair_suggestions(build_repair_suggestions(result))


def _print_generation_quality_report(report: GenerationQualityReport) -> None:
    if report.status == "valid":
        console.print(f"[green]Quality: {report.score}/100 ({report.status})[/green]")
    elif report.ok:
        console.print(f"[yellow]Quality: {report.score}/100 ({report.status})[/yellow]")
    else:
        console.print(f"[red]Quality: {report.score}/100 ({report.status})[/red]")

    if report.errors or report.warnings:
        table = Table(title="Generation quality report")
        table.add_column("Level")
        table.add_column("Code")
        table.add_column("Message")
        for issue in report.errors:
            table.add_row("error", issue.code, issue.message)
        for issue in report.warnings:
            table.add_row("warning", issue.code, issue.message)
        console.print(table)
        _print_repair_suggestions(report.repair_suggestions)

    next_table = Table(title="Next")
    next_table.add_column("Action")
    for action in report.next_actions:
        next_table.add_row(action)
    console.print(next_table)


def _print_repair_suggestions(suggestions: list[RepairSuggestion]) -> None:
    if not suggestions:
        return
    table = Table(title="Suggested fixes")
    table.add_column("Level")
    table.add_column("Code")
    table.add_column("Suggestion")
    for suggestion in suggestions:
        table.add_row(suggestion.level, suggestion.code, suggestion.suggestion)
    console.print(table)


def _print_draft_result(draft) -> None:
    table = Table(title="Interactive draft")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Draft ID", draft.draft_id)
    table.add_row("Status", str(draft.status))
    table.add_row("Current step", draft.current_step)
    if draft.generated_package:
        table.add_row("Package", str(draft.generated_package.path))
        table.add_row("SKILL.md", str(draft.generated_package.skill_md_path))
    console.print(table)


def _print_update_result(result: UpdateResult) -> None:
    table = Table(title="Research corpus update")
    table.add_column("Source")
    table.add_column("Status")
    table.add_column("Message")
    table.add_column("Next")

    for outcome in result.outcomes:
        table.add_row(outcome.source_name, outcome.status, outcome.message, _update_next_action(outcome))

    status = f"Status: {result.status_label}"
    console.print(
        f"{status} | Updated: {result.updated_count} | Skipped: {result.skipped_count} | "
        f"Failed: {result.failed_count} | Disabled: {result.disabled_count}"
    )
    console.print(table)


def _update_next_action(outcome) -> str:
    if outcome.status == "failed":
        return "Fix the source issue, then run `skill-forge update` again."
    if outcome.status == "disabled":
        return "Enable the source in sources.yaml to include it."
    return "-"


def _print_search_result(
    results: list[SearchResult],
    *,
    explain: bool = False,
    retrieval_mode: str = "tfidf",
    warning: str | None = None,
) -> None:
    if warning:
        console.print(f"[yellow]{warning}[/yellow]")
    if not results:
        console.print("[yellow]Local research corpus is empty or has no matches.[/yellow]")
        console.print("Run `skill-forge update` to refresh local references.")
        return

    table = Table(title=f"Search results ({retrieval_mode})")
    table.add_column("Name / Title")
    table.add_column("Source")
    table.add_column("Platform")
    table.add_column("Score", justify="right")
    if retrieval_mode == "tfidf+rerank":
        table.add_column("Rerank", justify="right")
    if explain:
        table.add_column("Relevance", justify="right")
        table.add_column("Authority", justify="right")
        table.add_column("Completeness", justify="right")
        table.add_column("Freshness", justify="right")
        table.add_column("Platform boost", justify="right")
    table.add_column("Summary")

    for result in results:
        row = [
            result.title,
            result.source_name,
            result.platform or "unknown",
            f"{result.score:.3f}",
        ]
        if retrieval_mode == "tfidf+rerank":
            row.append(f"{result.rerank_score:.3f}" if result.rerank_score is not None else "-")
        if explain:
            row.extend(
                [
                    f"{result.relevance_score:.3f}",
                    f"{result.authority_boost:.3f}",
                    f"{result.completeness_boost:.3f}",
                    f"{result.freshness_boost:.3f}",
                    f"{result.platform_boost:.3f}",
                ]
            )
        row.append(result.summary)
        table.add_row(*row)
    console.print(table)
    if explain:
        for result in results:
            console.print(f"{result.title} score components: {result.score_explanation}")


def _print_eval_report(report) -> None:
    if report.failed:
        console.print(f"[red]Eval: {report.passed}/{report.total} passed, {report.failed} failed[/red]")
    else:
        console.print(f"[green]Eval: {report.passed}/{report.total} passed[/green]")

    table = Table(title="Eval results")
    table.add_column("Case")
    table.add_column("Status")
    table.add_column("Assertion")
    table.add_column("Message")
    for result in report.results:
        status = "pass" if result.passed else "fail"
        if not result.assertions:
            table.add_row(result.case_id, status, "-", "No assertions")
            continue
        for assertion in result.assertions:
            table.add_row(result.case_id, status, assertion.assertion, assertion.message)
    console.print(table)


def _print_upgrade_result(result: SkillUpgradeResult) -> None:
    table = Table(title="Skill upgrade candidate")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Source", result.source_name)
    table.add_row("Candidate", result.candidate_name)
    table.add_row("Source package", str(result.source_path))
    table.add_row("Candidate package", str(result.candidate_package.path))
    table.add_row("Blueprint", result.blueprint_id or "-")
    table.add_row("Blueprint source", result.blueprint_source or "-")
    table.add_row("Previous quality", f"{result.previous_quality_score}/100 ({result.previous_quality_status})")
    table.add_row(
        "Candidate quality",
        f"{result.candidate_quality_report.score}/100 ({result.candidate_quality_report.status})",
    )
    table.add_row("Compare", f"skill-forge diff {result.source_name} {result.candidate_name}")
    console.print(table)
