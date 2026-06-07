from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.table import Table

from skill_forge.adoption.service import (
    AdoptedSkillExistsError,
    CorpusDocumentNotFoundError,
    EmptyCorpusDocumentError,
    SkillAdoptionService,
)
from skill_forge.experience.service import ExperienceService, ExperienceStore
from skill_forge.blueprints.enricher import BlueprintRequirementEnricher
from skill_forge.lifecycle.scoring import (
    ScoringConfig,
    ScoringInputs,
    compute_scores,
    suggested_state,
)
from skill_forge.models.collection import CollectionState, build_collection_record
from skill_forge.storage.collection_store import CollectionStore
from skill_forge.blueprints.loader import (
    BlueprintError,
    BlueprintLoader,
    BlueprintNotFoundError,
    DuplicateBlueprintError,
    PROJECT_BLUEPRINTS_RELATIVE_DIR,
)
from skill_forge.lifecycle.service import LifecycleService
from skill_forge.config import AppConfig, DEFAULT_OUTPUT_DIR, load_config, write_default_config
from skill_forge.generator.skill_generator import SkillGenerator, SkillPackageExistsError
from skill_forge.evals.runner import EvalCaseError, SkillEvaluator
from skill_forge.interaction.wizard import SkillCreationWizard
from skill_forge.installer.installer import DestinationExistsError, SkillInstaller, SourceSkillNotFoundError
from skill_forge.library.manager import (
    GeneratedSkillMissingSkillMdError,
    GeneratedSkillNotFoundError,
    SkillLibraryManager,
)
from skill_forge.lifecycle.promotion import (
    InvalidPromotionTargetError,
    PromotionSnapshotNotFoundError,
    SkillPromotionService,
)
from skill_forge.lifecycle.recommendation import LifecycleRecommendationService
from skill_forge.llm.refiner import (
    LLMAvailabilityError,
    LLMConfigurationError,
    LLMResponseError,
    OpenAICompatibleLLMClient,
    RequirementLLMRefiner,
    RequirementLLMRefinementResult,
)
from skill_forge.models.quality import GenerationQualityReport, RepairSuggestion, build_generation_quality_report, build_repair_suggestions
from skill_forge.models.generated import PROVENANCE_METADATA_FILENAME, GenerationProvenanceMetadata
from skill_forge.project_context.enricher import ProjectContextEnricher
from skill_forge.research.fetcher import HttpSourceFetcher
from skill_forge.research.sources import SourceConfigError
from skill_forge.research.updater import ResearchUpdater, UpdateResult
from skill_forge.retrieval.indexer import TfidfIndexer, TfidfIndexStore
from skill_forge.retrieval.generation import GenerationRetrievalAugmenter, GenerationRetrievalContext
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
experience_app = typer.Typer(help="Manage local experience rules.")
lifecycle_app = typer.Typer(help="Inspect generated Skill lifecycle state.")
collection_app = typer.Typer(help="Manage Skill collection governance.")
app.add_typer(blueprints_app, name="blueprints")
app.add_typer(experience_app, name="experience")
app.add_typer(lifecycle_app, name="lifecycle")
app.add_typer(collection_app, name="collection")
console = Console()


class CreateLLMMode(str, Enum):
    AUTO = "auto"
    FORCE = "force"
    DISABLED = "disabled"


class CreateLLMSelection(str, Enum):
    AUTO_SELECTED = "auto-selected"
    AUTO_FALLBACK = "auto-fallback"
    FORCED = "forced"
    DISABLED = "disabled"


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
    collection: Annotated[
        str | None,
        typer.Option("--collection", help="Filter results by collection state (candidate, curated, promoted, rejected)."),
    ] = None,
    promoted_boost: Annotated[
        bool,
        typer.Option("--promoted-boost", help="Boost promoted Skills in ranking."),
    ] = False,
    semantic: Annotated[
        bool,
        typer.Option("--semantic", help="Use semantic retrieval mode (local TF-IDF similarity). Falls back to default if unavailable."),
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

    collection_filter = None
    if collection is not None:
        try:
            collection_filter = CollectionState(collection)
        except ValueError:
            console.print(f"[red]Invalid collection state:[/red] {collection}")
            console.print(f"Valid states: {', '.join(s.value for s in CollectionState)}")
            raise typer.Exit(code=1)

    limit = top_k if top_k is not None else config.retrieval.top_k
    reader = CorpusReader(paths.database_file)
    indexer = TfidfIndexer(reader, TfidfIndexStore(paths.index_dir))

    if semantic:
        from skill_forge.retrieval.semantic import SemanticRetriever
        semantic_retriever = SemanticRetriever(indexer)
        semantic_response = semantic_retriever.search(query, top_k=limit, platform=platform)
        results = semantic_response.results
        retrieval_mode = semantic_response.retrieval_mode
        warning = semantic_response.fallback_reason if semantic_response.fallback_used else None
    else:
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
        results = response.results
        retrieval_mode = response.retrieval_mode
        warning = rerank_warning

    collection_warning = None
    if collection_filter is not None or promoted_boost:
        from skill_forge.retrieval.collection_integration import CollectionSearchFilter
        collection_store = CollectionStore(paths.collections_dir)
        collection_filter_obj = CollectionSearchFilter(collection_store)
        results = collection_filter_obj.apply(
            results,
            collection_filter=collection_filter,
            promoted_boost=0.10 if promoted_boost else 0.0,
        )
        if collection_filter is not None and not results:
            collection_warning = f"No results match collection state '{collection_filter.value}'."

    warning = warning or collection_warning
    _print_search_result(results, explain=explain, retrieval_mode=retrieval_mode, warning=warning)


@app.command()
def adopt(
    document_id: Annotated[int, typer.Option("--document-id", help="Local corpus document ID to adopt.")],
    name: Annotated[
        str | None,
        typer.Option("--name", help="Output package name. Does not rewrite adopted SKILL.md content."),
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
    """Adopt a cached corpus Skill document into the local Skill library."""
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    initialize_database(paths.database_file)
    config = load_config(paths.config_file)
    output_path = _resolve_output_dir(
        str(output_dir) if output_dir is not None else config.create.output_dir,
        paths.home,
        isolate_default=home is not None and output_dir is None,
    )
    service = SkillAdoptionService(
        output_dir=output_path,
        corpus_reader=CorpusReader(paths.database_file),
    )

    try:
        result = service.adopt(document_id=document_id, name=name)
    except CorpusDocumentNotFoundError as exc:
        console.print(f"[red]Cached corpus document not found:[/red] {exc.document_id}")
        raise typer.Exit(code=1) from exc
    except EmptyCorpusDocumentError as exc:
        console.print(f"[red]Cached corpus document has no adoptable Skill content:[/red] {exc.document_id}")
        raise typer.Exit(code=1) from exc
    except AdoptedSkillExistsError as exc:
        console.print(f"[red]Adopted Skill package already exists:[/red] {exc.path}")
        console.print("Use --name to adopt into a different package name.")
        raise typer.Exit(code=1) from exc

    table = Table(title="Skill package adopted")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Name", result.package.name)
    table.add_row("Package", str(result.package.path))
    table.add_row("SKILL.md", str(result.package.skill_md_path))
    table.add_row("Source", result.source_document.source_name)
    table.add_row("Document ID", str(result.source_document.document_id))
    table.add_row("Source URL", result.source_document.document_url or result.source_document.source_url or "-")
    console.print(table)
    _print_generation_quality_report(result.quality_report)

    if not result.quality_report.ok:
        console.print(f"[red]Adopted Skill package is invalid:[/red] {result.package.path}")
        raise typer.Exit(code=1)


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
    table.add_column("Collection", no_wrap=True)
    table.add_column("Path")
    for entry in entries:
        collection_label = "-"
        if entry.collection_record is not None:
            collection_label = entry.collection_record.collection_state.value
            if entry.collection_record.is_promoted:
                collection_label = f"[bold green]{collection_label}[/bold green]"
            elif entry.collection_record.is_curated_or_better:
                collection_label = f"[cyan]{collection_label}[/cyan]"
        table.add_row(entry.name, entry.description or "-", collection_label, str(entry.path))
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
        table.add_row("Origin", provenance.origin_type)
        if provenance.origin_type == "community-adopted":
            table.add_row("Adopted at", provenance.adopted_at or "-")
            table.add_row("Source", provenance.source_name or "-")
            table.add_row("Source URL", provenance.document_url or provenance.source_url or "-")
            table.add_row("Document ID", str(provenance.document_id) if provenance.document_id is not None else "-")
            table.add_row("Example ID", str(provenance.example_id) if provenance.example_id is not None else "-")
            table.add_row("Source platform", provenance.source_platform or "-")
        table.add_row("Generated at", provenance.generated_at)
        table.add_row("Blueprint", provenance.blueprint_id or "-")
        table.add_row("Blueprint source", provenance.blueprint_source or "-")
        table.add_row("LLM enabled", str(provenance.llm_enabled))
        table.add_row("LLM mode", provenance.llm_mode)
        table.add_row("LLM selection", provenance.llm_selection)
        if provenance.llm_fallback_reason:
            table.add_row("LLM fallback reason", provenance.llm_fallback_reason)
        if provenance.llm_enabled:
            table.add_row("LLM generated fields", ", ".join(provenance.llm_generated_fields) or "-")
            table.add_row("LLM fallback fields", ", ".join(provenance.llm_fallback_fields) or "-")
            table.add_row("LLM refined fields", ", ".join(provenance.llm_refined_fields) or "-")
            table.add_row("Retrieval augmented", str(provenance.retrieval_augmented))
            if provenance.retrieval_augmentation_reason:
                table.add_row("Retrieval augmentation reason", provenance.retrieval_augmentation_reason)
            if provenance.retrieval_reference_names:
                table.add_row("Retrieval references", ", ".join(provenance.retrieval_reference_names))
        table.add_row("Applied experience rules", ", ".join(provenance.applied_experience_rule_ids) or "-")
        table.add_row("Quality", f"{provenance.quality_score}/100 ({provenance.quality_status})")
        if provenance.content_quality is not None:
            table.add_row(
                "Content quality",
                (
                    f"workflow={provenance.content_quality.workflow_specificity:.2f}, "
                    f"constraints={provenance.content_quality.constraint_verifiability:.2f}, "
                    f"gates={provenance.content_quality.quality_gate_clarity:.2f}"
                ),
            )
        table.add_row("Project context", provenance.project_context_path or "-")
    else:
        table.add_row("Provenance", "missing")
    if entry.eval_report is not None:
        table.add_row(
            "Eval summary",
            f"{entry.eval_report.passed}/{entry.eval_report.total} passed, {entry.eval_report.failed} failed",
        )
    if entry.collection_record is not None:
        cr = entry.collection_record
        table.add_row("Collection state", cr.collection_state.value)
        table.add_row("Collection score", f"{cr.collection_score:.4f}")
        table.add_row("Promotion score", f"{cr.promotion_score:.4f}")
        table.add_row("Score version", cr.score_version)
        if cr.rationale:
            table.add_row("Collection rationale", cr.rationale)
        table.add_row("Manual override", str(cr.manual_override))
    else:
        table.add_row("Collection state", "not tracked")
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


@app.command("promote")
def promote_generated_skill(
    candidate_name: Annotated[str, typer.Argument(help="Generated Skill package name to promote.")],
    target_name: Annotated[
        str | None,
        typer.Option("--as", help="Active package name to replace. Defaults to removing the -upgraded suffix."),
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
    """Promote a generated candidate Skill package into an active package."""
    service = _promotion_service(home, output_dir)
    try:
        result = service.promote(candidate_name, target_name=target_name)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Generated Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except InvalidPromotionTargetError as exc:
        console.print(f"[red]Invalid promotion target:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Skill promoted")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Candidate", result.candidate_name)
    table.add_row("Target", result.target_name)
    table.add_row("Active version", result.active_version_name)
    table.add_row("Candidate path", str(result.candidate_path))
    table.add_row("Target path", str(result.target_path))
    table.add_row("Previous version", result.previous_version_name or "-")
    table.add_row("Snapshot", str(result.snapshot_path) if result.snapshot_path is not None else "-")
    table.add_row("Registry", str(result.registry_path))
    table.add_row("Promoted at", result.promoted_at)
    console.print(table)


@app.command("rollback")
def rollback_generated_skill(
    skill_name: Annotated[str, typer.Argument(help="Active Skill package name to restore.")],
    version_name: Annotated[str, typer.Option("--to", help="Recorded version label to restore.")],
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
    """Rollback an active Skill package to a previously recorded version."""
    service = _promotion_service(home, output_dir)
    try:
        result = service.rollback(skill_name, version_name=version_name)
    except PromotionSnapshotNotFoundError as exc:
        console.print(f"[red]Rollback history not found:[/red] {exc.skill_name} -> {exc.version_name}")
        console.print(f"Registry: {exc.registry_path}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Skill rolled back")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Skill", result.skill_name)
    table.add_row("Restored version", result.restored_version_name)
    table.add_row("Active version", result.active_version_name)
    table.add_row("Target path", str(result.target_path))
    table.add_row("Previous version", result.previous_version_name or "-")
    table.add_row("Snapshot", str(result.snapshot_path) if result.snapshot_path is not None else "-")
    table.add_row("Registry", str(result.registry_path))
    table.add_row("Rolled back at", result.rolled_back_at)
    console.print(table)


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
    llm: Annotated[bool, typer.Option("--llm", help="Force LLM-assisted generation.")] = False,
    no_llm: Annotated[
        bool,
        typer.Option("--no-llm", help="Disable automatic LLM detection and use deterministic generation."),
    ] = False,
) -> None:
    """Generate a local Skill package from a requirement string."""
    if llm and no_llm:
        console.print("[red]Conflicting options:[/red] use either --llm or --no-llm, not both.")
        raise typer.Exit(code=1)

    llm_mode = _create_llm_mode(llm=llm, no_llm=no_llm)
    if llm_mode == CreateLLMMode.FORCE and interactive:
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
    experience_service = ExperienceService(ExperienceStore(paths.experience_dir))
    llm_result: RequirementLLMRefinementResult | None = None
    retrieval_context: GenerationRetrievalContext | None = None
    experience_context = None
    llm_enabled = False
    llm_selection = CreateLLMSelection.DISABLED if llm_mode == CreateLLMMode.DISABLED else CreateLLMSelection.AUTO_FALLBACK
    llm_selection_fallback_reason: str | None = None

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

    skill_requirement, experience_context = experience_service.apply_to_requirement(skill_requirement)

    if not interactive:
        llm_client = None
        if llm_mode == CreateLLMMode.DISABLED:
            llm_selection = CreateLLMSelection.DISABLED
        elif llm_mode == CreateLLMMode.AUTO and not OpenAICompatibleLLMClient.has_required_env_configuration():
            llm_selection = CreateLLMSelection.AUTO_FALLBACK
            missing = ", ".join(OpenAICompatibleLLMClient.missing_env_configuration())
            llm_selection_fallback_reason = f"Missing LLM configuration: {missing}"
        else:
            try:
                llm_client = OpenAICompatibleLLMClient.from_env()
                llm_client.check_availability(timeout_seconds=1.0)
                llm_enabled = True
                llm_selection = (
                    CreateLLMSelection.FORCED
                    if llm_mode == CreateLLMMode.FORCE
                    else CreateLLMSelection.AUTO_SELECTED
                )
            except LLMConfigurationError as exc:
                if llm_mode == CreateLLMMode.FORCE:
                    console.print(f"[red]LLM configuration error:[/red] {exc}")
                    raise typer.Exit(code=1) from exc
                llm_selection = CreateLLMSelection.AUTO_FALLBACK
                llm_selection_fallback_reason = str(exc)
            except LLMAvailabilityError as exc:
                if llm_mode == CreateLLMMode.FORCE:
                    console.print(f"[red]LLM availability error:[/red] {exc}")
                    raise typer.Exit(code=1) from exc
                llm_selection = CreateLLMSelection.AUTO_FALLBACK
                llm_selection_fallback_reason = str(exc)

        if llm_client is not None:
            retrieval_context = _build_generation_retrieval_context(
                paths=paths,
                config=config,
                requirement_text=requirement,
                skill_requirement=skill_requirement,
            )
            try:
                llm_result = RequirementLLMRefiner(llm_client).refine_with_metadata(
                    requirement,
                    skill_requirement,
                    retrieval_context=retrieval_context,
                    experience_context=experience_context,
                )
            except LLMResponseError as exc:
                console.print(f"[yellow]LLM response error; using deterministic fallback:[/yellow] {exc}")
                llm_result = RequirementLLMRefinementResult(requirement=skill_requirement)
            skill_requirement = llm_result.requirement

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
    quality_report = build_generation_quality_report(validation_result, requirement=skill_requirement)

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
        llm_enabled=llm_enabled,
        llm_mode=llm_mode,
        llm_selection=llm_selection,
        llm_selection_fallback_reason=llm_selection_fallback_reason,
        project=project,
        quality_report=quality_report,
        llm_result=llm_result,
        retrieval_context=retrieval_context,
        experience_context=experience_context,
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


# --- Collection subcommands ---


def _collection_store(home: Path | None) -> tuple[SkillForgePaths, CollectionStore]:
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    return paths, CollectionStore(paths.collections_dir)


def _collection_library_manager(home: Path | None, output_dir: Path | None = None) -> tuple[SkillForgePaths, SkillLibraryManager, AppConfig]:
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    config = load_config(paths.config_file)
    output_path = _resolve_output_dir(
        str(output_dir) if output_dir is not None else config.create.output_dir,
        paths.home,
        isolate_default=home is not None and output_dir is None,
    )
    collection_store = CollectionStore(paths.collections_dir)
    return paths, SkillLibraryManager(output_path, collection_store=collection_store), config


@collection_app.command("list")
def collection_list(
    state: Annotated[
        str | None,
        typer.Option("--state", help="Filter by collection state (candidate, curated, promoted, rejected)."),
    ] = None,
    home: Annotated[
        Path | None,
        typer.Option("--home", help="Override the Skill Forge home directory."),
    ] = None,
) -> None:
    """List Skills in the collection."""
    _, store = _collection_store(home)
    if state is not None:
        try:
            filter_state = CollectionState(state)
        except ValueError:
            console.print(f"[red]Invalid collection state:[/red] {state}")
            console.print(f"Valid states: {', '.join(s.value for s in CollectionState)}")
            raise typer.Exit(code=1)
        records = store.list_by_state(filter_state)
    else:
        records = store.list_records()

    if not records:
        console.print("[yellow]No collection records found.[/yellow]")
        return

    table = Table(title="Skill Collection")
    table.add_column("Skill ID", no_wrap=True)
    table.add_column("Package", no_wrap=True)
    table.add_column("State", no_wrap=True)
    table.add_column("Collection Score", justify="right")
    table.add_column("Promotion Score", justify="right")
    table.add_column("Origin", no_wrap=True)
    for record in records:
        table.add_row(
            record.skill_id,
            record.package_name,
            record.collection_state.value,
            f"{record.collection_score:.4f}",
            f"{record.promotion_score:.4f}",
            record.origin_type,
        )
    console.print(table)


@collection_app.command("show")
def collection_show(
    skill_id: Annotated[str, typer.Argument(help="Skill identifier to inspect.")],
    home: Annotated[
        Path | None,
        typer.Option("--home", help="Override the Skill Forge home directory."),
    ] = None,
) -> None:
    """Show collection details for a Skill."""
    _, store = _collection_store(home)
    record = store.read_record(skill_id)
    if record is None:
        console.print(f"[red]Collection record not found:[/red] {skill_id}")
        raise typer.Exit(code=1)

    table = Table(title=f"Collection: {record.skill_id}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Skill ID", record.skill_id)
    table.add_row("Package", record.package_name)
    table.add_row("Origin", record.origin_type)
    table.add_row("Origin reference", record.origin_reference or "-")
    table.add_row("State", record.collection_state.value)
    table.add_row("Collection score", f"{record.collection_score:.4f}")
    table.add_row("Promotion score", f"{record.promotion_score:.4f}")
    table.add_row("Score version", record.score_version)
    table.add_row("Tags", ", ".join(record.tags) or "-")
    table.add_row("Rationale", record.rationale or "-")
    table.add_row("Manual override", str(record.manual_override))
    table.add_row("Last verified", record.last_verified_at or "-")
    table.add_row("Created", record.created_at)
    table.add_row("Updated", record.updated_at)
    console.print(table)

    snapshot = store.read_snapshot(skill_id)
    if snapshot is not None:
        snap_table = Table(title="Score Snapshot")
        snap_table.add_column("Dimension")
        snap_table.add_column("Score", justify="right")
        snap_table.add_column("Evidence")
        for dim in snapshot.dimensions:
            snap_table.add_row(dim.name, f"{dim.score:.4f}", dim.evidence or "-")
        snap_table.add_row("Collection (final)", f"{snapshot.final_collection_score:.4f}", "")
        snap_table.add_row("Promotion (final)", f"{snapshot.final_promotion_score:.4f}", "")
        console.print(snap_table)


@collection_app.command("update")
def collection_update(
    skill_id: Annotated[str, typer.Argument(help="Skill identifier to update.")],
    state: Annotated[str, typer.Option("--state", help="New collection state.")],
    rationale: Annotated[
        str | None,
        typer.Option("--rationale", help="Reason for the state change."),
    ] = None,
    home: Annotated[
        Path | None,
        typer.Option("--home", help="Override the Skill Forge home directory."),
    ] = None,
) -> None:
    """Update the collection state of a Skill."""
    try:
        new_state = CollectionState(state)
    except ValueError:
        console.print(f"[red]Invalid collection state:[/red] {state}")
        console.print(f"Valid states: {', '.join(s.value for s in CollectionState)}")
        raise typer.Exit(code=1)

    _, store = _collection_store(home)
    record = store.update_state(skill_id, state=new_state, rationale=rationale, manual=True)
    if record is None:
        console.print(f"[red]Collection record not found:[/red] {skill_id}")
        console.print("Run `skill-forge collection score <skill-id>` to create a record first.")
        raise typer.Exit(code=1)

    table = Table(title="Collection updated")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Skill ID", record.skill_id)
    table.add_row("New state", record.collection_state.value)
    table.add_row("Rationale", record.rationale or "-")
    table.add_row("Updated", record.updated_at)
    console.print(table)


@collection_app.command("score")
def collection_score(
    skill_name: Annotated[str, typer.Argument(help="Generated Skill package name to score.")],
    home: Annotated[
        Path | None,
        typer.Option("--home", help="Override the Skill Forge home directory."),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Override the generated Skill package directory."),
    ] = None,
) -> None:
    """Compute collection and promotion scores for a Skill."""
    paths, manager, app_config = _collection_library_manager(home, output_dir)
    store = CollectionStore(paths.collections_dir)
    scoring_config = ScoringConfig(
        collection_weights=app_config.collection_scoring.collection_weights.model_dump(),
        promotion_weights=app_config.collection_scoring.promotion_weights.model_dump(),
        promotion_threshold=app_config.collection_scoring.promotion_threshold,
        curated_threshold=app_config.collection_scoring.curated_threshold,
    )

    try:
        entry = manager.show(skill_name)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    inputs = ScoringInputs()
    inputs.has_skill_md = entry.skill_md_path.is_file()
    if entry.provenance is not None:
        inputs.has_frontmatter = True
        inputs.has_required_sections = True
    if entry.provenance is not None:
        inputs.quality_score = entry.provenance.quality_score
        inputs.quality_status = entry.provenance.quality_status
        inputs.content_quality_workflow = entry.provenance.content_quality.workflow_specificity if entry.provenance.content_quality else None
        inputs.content_quality_constraint = entry.provenance.content_quality.constraint_verifiability if entry.provenance.content_quality else None
        inputs.content_quality_gate = entry.provenance.content_quality.quality_gate_clarity if entry.provenance.content_quality else None
        inputs.has_provenance = True
        inputs.origin_type = entry.provenance.origin_type
        inputs.has_applied_experience = bool(entry.provenance.applied_experience_rule_ids)
    if entry.eval_report is not None:
        inputs.eval_total = entry.eval_report.total
        inputs.eval_passed = entry.eval_report.passed
        inputs.eval_failed = entry.eval_report.failed

    snapshot = compute_scores(inputs, config=scoring_config)
    snapshot.skill_id = skill_name
    store.write_snapshot(snapshot)

    origin_type = entry.provenance.origin_type if entry.provenance else "unknown"
    existing = store.read_record(skill_name)
    if existing is None:
        record = build_collection_record(
            skill_id=skill_name,
            package_name=skill_name,
            origin_type=origin_type,
            collection_state=CollectionState(suggested_state(snapshot.final_collection_score, snapshot.final_promotion_score, config=scoring_config)),
            rationale="Auto-scored",
        )
        record.collection_score = snapshot.final_collection_score
        record.promotion_score = snapshot.final_promotion_score
        record.score_version = snapshot.score_version
        store.write_record(record)
    else:
        existing.collection_score = snapshot.final_collection_score
        existing.promotion_score = snapshot.final_promotion_score
        existing.score_version = snapshot.score_version
        store.write_record(existing)

    table = Table(title="Collection score")
    table.add_column("Dimension")
    table.add_column("Score", justify="right")
    table.add_column("Evidence")
    for dim in snapshot.dimensions:
        table.add_row(dim.name, f"{dim.score:.4f}", dim.evidence or "-")
    table.add_row("Collection (final)", f"{snapshot.final_collection_score:.4f}", "")
    table.add_row("Promotion (final)", f"{snapshot.final_promotion_score:.4f}", "")
    table.add_row("Suggested state", suggested_state(snapshot.final_collection_score, snapshot.final_promotion_score, config=scoring_config), "")
    console.print(table)


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
    collection_store = CollectionStore(paths.collections_dir)
    return SkillLibraryManager(output_path, collection_store=collection_store)


def _experience_service(home: Path | None) -> ExperienceService:
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    return ExperienceService(ExperienceStore(paths.experience_dir))


def _lifecycle_service(home: Path | None, output_dir: Path | None = None) -> LifecycleService:
    paths = SkillForgePaths.resolve(home)
    config = load_config(paths.config_file)
    output_path = _resolve_output_dir(
        str(output_dir) if output_dir is not None else config.create.output_dir,
        paths.home,
        isolate_default=home is not None and output_dir is None,
    )
    return LifecycleService(
        SkillLibraryManager(output_path),
        ExperienceStore(paths.experience_dir),
    )


def _lifecycle_recommendation_service(home: Path | None, output_dir: Path | None = None) -> LifecycleRecommendationService:
    return LifecycleRecommendationService(_lifecycle_service(home, output_dir))


def _promotion_service(home: Path | None, output_dir: Path | None = None) -> SkillPromotionService:
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    config = load_config(paths.config_file)
    output_path = _resolve_output_dir(
        str(output_dir) if output_dir is not None else config.create.output_dir,
        paths.home,
        isolate_default=home is not None and output_dir is None,
    )
    return SkillPromotionService(
        SkillLibraryManager(output_path),
        paths.promotions_dir,
    )


def _blueprint_loader(home: Path | None = None, project: Path | None = None) -> BlueprintLoader:
    paths = SkillForgePaths.resolve(home)
    project_blueprint_dir = None
    if project is not None:
        project_blueprint_dir = project.expanduser().resolve() / PROJECT_BLUEPRINTS_RELATIVE_DIR
    return BlueprintLoader(
        user_blueprint_dir=paths.blueprints_dir,
        project_blueprint_dir=project_blueprint_dir,
    )


def _create_llm_mode(*, llm: bool, no_llm: bool) -> CreateLLMMode:
    if no_llm:
        return CreateLLMMode.DISABLED
    if llm:
        return CreateLLMMode.FORCE
    return CreateLLMMode.AUTO


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
    llm_mode: CreateLLMMode,
    llm_selection: CreateLLMSelection,
    llm_selection_fallback_reason: str | None,
    project: Path | None,
    quality_report: GenerationQualityReport,
    llm_result: RequirementLLMRefinementResult | None = None,
    retrieval_context: GenerationRetrievalContext | None = None,
    experience_context=None,
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
        llm_mode=llm_mode.value,
        llm_selection=llm_selection.value,
        llm_fallback_reason=(
            llm_selection_fallback_reason
            if llm_selection_fallback_reason is not None
            else (llm_result.fallback_reason if llm_result is not None else None)
        ),
        llm_generated_fields=sorted(llm_result.generated_fields) if llm_result is not None else [],
        llm_fallback_fields=sorted(llm_result.fallback_fields) if llm_result is not None else [],
        llm_refined_fields=sorted(llm_result.refined_fields) if llm_result is not None else [],
        retrieval_augmented=retrieval_context.used if retrieval_context is not None else False,
        retrieval_augmentation_reason=retrieval_context.skipped_reason if retrieval_context is not None else None,
        retrieval_reference_names=sorted(retrieval_context.source_names) if retrieval_context is not None else [],
        applied_experience_rule_ids=sorted(experience_context.rule_ids) if experience_context is not None and experience_context.used else [],
        project_context_path=str(project.expanduser().resolve()) if project is not None else None,
        quality_score=quality_report.score,
        quality_status=quality_report.status,
        content_quality=quality_report.content_quality,
        references=sorted(package.references),
        assets=sorted(package.assets),
        scripts=sorted(package.scripts),
    )
    metadata_path = package.path / PROVENANCE_METADATA_FILENAME
    metadata_path.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")


def _build_generation_retrieval_context(
    *,
    paths: SkillForgePaths,
    config,
    requirement_text: str,
    skill_requirement,
) -> GenerationRetrievalContext:
    try:
        reader = CorpusReader(paths.database_file)
        indexer = TfidfIndexer(reader, TfidfIndexStore(paths.index_dir))
        retriever = CorpusRetriever(indexer)
        return GenerationRetrievalAugmenter(
            retriever,
            top_k=config.retrieval.generation_top_k,
            min_corpus_documents=config.retrieval.generation_min_corpus_documents,
            min_relevance_score=config.retrieval.generation_min_relevance_score,
            min_quality_score=config.retrieval.generation_min_quality_score,
        ).build_context(requirement_text, platform=skill_requirement.target_platform)
    except Exception as exc:
        return GenerationRetrievalContext(skipped_reason=f"retrieval-failed: {exc}")


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

    if report.content_quality is not None:
        metrics_table = Table(title="Content quality")
        metrics_table.add_column("Metric")
        metrics_table.add_column("Score")
        metrics_table.add_row("Workflow specificity", f"{report.content_quality.workflow_specificity:.2f}")
        metrics_table.add_row("Constraint verifiability", f"{report.content_quality.constraint_verifiability:.2f}")
        metrics_table.add_row("Quality gate clarity", f"{report.content_quality.quality_gate_clarity:.2f}")
        console.print(metrics_table)

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


@lifecycle_app.command("show")
def show_skill_lifecycle(
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
    """Show lifecycle state for a generated Skill package."""
    service = _lifecycle_service(home, output_dir)
    try:
        summary = service.show(skill_name)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Generated Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Skill lifecycle: {summary.skill_name}")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Skill", summary.skill_name)
    table.add_row("Package", str(summary.package_path))
    table.add_row("State", summary.state)
    table.add_row("Reason", summary.reason)
    table.add_row("Quality", f"{summary.quality_score}/100 ({summary.quality_status})" if summary.quality_score is not None else "-")
    table.add_row(
        "Eval",
        f"{summary.eval_passed}/{summary.eval_total} passed, {summary.eval_failed} failed"
        if summary.eval_total is not None
        else "-",
    )
    table.add_row("Applied experience rules", ", ".join(summary.applied_experience_rule_ids) or "-")
    table.add_row("Resolved experience rules", ", ".join(summary.resolved_experience_rules) or "-")
    console.print(table)

    if summary.evidence:
        evidence_table = Table(title="Lifecycle evidence")
        evidence_table.add_column("Source", no_wrap=True)
        evidence_table.add_column("Summary")
        evidence_table.add_column("Details")
        for item in summary.evidence:
            evidence_table.add_row(item.source, item.summary, _format_list(item.details))
        console.print(evidence_table)

    if summary.missing_facts:
        missing_table = Table(title="Missing facts")
        missing_table.add_column("Fact")
        for fact in summary.missing_facts:
            missing_table.add_row(fact)
        console.print(missing_table)


@lifecycle_app.command("recommend")
def recommend_skill_lifecycle(
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
    """Recommend the next lifecycle action for a generated Skill package."""
    service = _lifecycle_recommendation_service(home, output_dir)
    try:
        recommendation = service.recommend(skill_name)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Generated Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Lifecycle recommendation: {recommendation.skill_name}")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Skill", recommendation.skill_name)
    table.add_row("State", recommendation.state)
    table.add_row("Action", recommendation.action)
    table.add_row("Reason", recommendation.reason)
    table.add_row("Signals", _format_list(recommendation.signals))
    table.add_row("Missing facts", _format_list(recommendation.missing_facts))
    console.print(table)


@lifecycle_app.command("compare")
def compare_skill_lifecycle(
    left_skill_name: Annotated[str, typer.Argument(help="First generated Skill package name to compare.")],
    right_skill_name: Annotated[str, typer.Argument(help="Second generated Skill package name to compare.")],
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
    """Compare two generated Skill lifecycle summaries."""
    service = _lifecycle_recommendation_service(home, output_dir)
    try:
        comparison = service.compare(left_skill_name, right_skill_name)
    except GeneratedSkillNotFoundError as exc:
        console.print(f"[red]Generated Skill package not found:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc
    except GeneratedSkillMissingSkillMdError as exc:
        console.print(f"[red]Generated Skill package is missing SKILL.md:[/red] {exc.path}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Lifecycle comparison: {comparison.left_skill_name} vs {comparison.right_skill_name}")
    table.add_column("Item")
    table.add_column("Left")
    table.add_column("Right")
    table.add_column("Preferred")
    table.add_row("State", comparison.left_summary.state, comparison.right_summary.state, comparison.preferred_skill_name)
    table.add_row(
        "Quality",
        f"{comparison.left_summary.quality_score}/100" if comparison.left_summary.quality_score is not None else "-",
        f"{comparison.right_summary.quality_score}/100" if comparison.right_summary.quality_score is not None else "-",
        "-",
    )
    table.add_row(
        "Eval",
        (
            f"{comparison.left_summary.eval_passed}/{comparison.left_summary.eval_total} passed"
            if comparison.left_summary.eval_total is not None
            else "-"
        ),
        (
            f"{comparison.right_summary.eval_passed}/{comparison.right_summary.eval_total} passed"
            if comparison.right_summary.eval_total is not None
            else "-"
        ),
        "-",
    )
    table.add_row("Missing facts", _format_list(comparison.left_summary.missing_facts), _format_list(comparison.right_summary.missing_facts), "-")
    table.add_row("Reason", comparison.reason, "", "")
    table.add_row("Tie-breaker", comparison.tie_breaker, "", "")
    console.print(table)


@experience_app.command("list")
def list_experience_rules(
    home: Annotated[
        Path | None,
        typer.Option(
            "--home",
            help="Override the Skill Forge home directory. Primarily useful for tests and isolated runs.",
        ),
    ] = None,
) -> None:
    """List local experience rules."""
    service = _experience_service(home)
    rules = service.list_rules()
    if not rules:
        console.print(f"[yellow]No local experience rules found:[/yellow] {service.store.experience_dir}")
        return

    table = Table(title="Local experience rules")
    table.add_column("ID", no_wrap=True)
    table.add_column("Task type", no_wrap=True)
    table.add_column("Priority", justify="right", no_wrap=True)
    table.add_column("Scope", no_wrap=True)
    table.add_column("Rule")
    for rule in rules:
        scope = ", ".join(
            part
            for part in [
                f"language={rule.language}" if rule.language else None,
                f"platform={rule.target_platform}" if rule.target_platform else None,
            ]
            if part is not None
        ) or "-"
        table.add_row(rule.id, rule.task_type, str(rule.priority), scope, rule.rule_text)
    console.print(table)


@experience_app.command("derive")
def derive_experience_rules(
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
    """Derive local experience rules from generated Skill packages."""
    paths = SkillForgePaths.resolve(home)
    paths.ensure_directories()
    write_default_config(paths.config_file)
    config = load_config(paths.config_file)
    output_path = _resolve_output_dir(
        str(output_dir) if output_dir is not None else config.create.output_dir,
        paths.home,
        isolate_default=home is not None and output_dir is None,
    )
    service = _experience_service(home)
    result = service.derive_from_output_dir(output_path, rebuild=True)

    table = Table(title="Experience derivation")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Scanned packages", str(result.scanned_packages))
    table.add_row("Evidence count", str(result.evidence_count))
    table.add_row("Skipped packages", ", ".join(result.skipped_packages) or "-")
    table.add_row("Derived rules", str(len(result.rules)))
    console.print(table)

    if result.rules:
        rules_table = Table(title="Derived rules")
        rules_table.add_column("ID", no_wrap=True)
        rules_table.add_column("Task type", no_wrap=True)
        rules_table.add_column("Priority", justify="right", no_wrap=True)
        rules_table.add_column("Rule")
        for rule in result.rules:
            rules_table.add_row(rule.id, rule.task_type, str(rule.priority), rule.rule_text)
        console.print(rules_table)


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
    table.add_column("ID", justify="right", no_wrap=True)
    table.add_column("Name / Title", no_wrap=True)
    table.add_column("Source", no_wrap=True)
    table.add_column("Platform", no_wrap=True)
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
            str(result.document_id),
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
