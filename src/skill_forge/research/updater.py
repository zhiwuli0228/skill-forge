from dataclasses import dataclass, field
from pathlib import Path

from skill_forge.research.github_discovery import GitHubDiscoveryError, GitHubFileFetchError, GitHubSkillDiscoverer
from skill_forge.research.fetcher import FetchError, SourceFetcher
from skill_forge.research.sources import SourceLoader
from skill_forge.storage.corpus_store import CorpusStore
from skill_forge.storage.paths import SkillForgePaths


@dataclass(frozen=True)
class SourceUpdateOutcome:
    source_name: str
    status: str
    message: str = ""


@dataclass
class UpdateResult:
    outcomes: list[SourceUpdateOutcome] = field(default_factory=list)

    @property
    def updated_count(self) -> int:
        return self._count("updated")

    @property
    def skipped_count(self) -> int:
        return self._count("skipped")

    @property
    def failed_count(self) -> int:
        return self._count("failed")

    @property
    def disabled_count(self) -> int:
        return self._count("disabled")

    @property
    def partial_failure(self) -> bool:
        processed = [outcome for outcome in self.outcomes if outcome.status in {"updated", "skipped", "failed"}]
        return any(outcome.status in {"updated", "skipped"} for outcome in processed) and any(
            outcome.status == "failed" for outcome in processed
        )

    @property
    def status_label(self) -> str:
        if self.partial_failure:
            return "partial"
        if self.ok:
            return "ok"
        return "failed"

    @property
    def ok(self) -> bool:
        processed = [outcome for outcome in self.outcomes if outcome.status in {"updated", "skipped", "failed"}]
        return bool(processed) and any(outcome.status in {"updated", "skipped"} for outcome in processed)

    def _count(self, status: str) -> int:
        return sum(1 for outcome in self.outcomes if outcome.status == status)


class ResearchUpdater:
    def __init__(
        self,
        paths: SkillForgePaths,
        fetcher: SourceFetcher,
        loader: SourceLoader | None = None,
        store: CorpusStore | None = None,
        github_discoverer: GitHubSkillDiscoverer | None = None,
    ) -> None:
        self.paths = paths
        self.fetcher = fetcher
        self.loader = loader or SourceLoader()
        self.store = store or CorpusStore(paths.database_file, paths.corpus_raw_dir, paths.corpus_normalized_dir)
        self.github_discoverer = github_discoverer or GitHubSkillDiscoverer()

    def update(self, user_sources_file: Path | None = None) -> UpdateResult:
        config = self.loader.load(user_sources_file or self.paths.sources_file)
        result = UpdateResult()

        for source in config.sources:
            if not source.enabled:
                result.outcomes.append(SourceUpdateOutcome(source.name, "disabled", "disabled"))
                continue

            try:
                discovery_config = source.discovery_config
            except ValueError as exc:
                result.outcomes.append(SourceUpdateOutcome(source.name, "failed", str(exc)))
                continue

            if source.type == "github" and discovery_config is not None:
                self._update_discovered_skills(source, discovery_config, result)
                continue

            try:
                fetched = self.fetcher.fetch(source)
                stored = self.store.store(fetched)
            except (FetchError, OSError, ValueError) as exc:
                result.outcomes.append(SourceUpdateOutcome(source.name, "failed", str(exc)))
                continue

            result.outcomes.append(SourceUpdateOutcome(source.name, stored.status, str(stored.document.normalized_path)))

        return result

    def _update_discovered_skills(self, source, discovery_config, result: UpdateResult) -> None:
        try:
            candidates = self.github_discoverer.discover(source, discovery_config)
        except (GitHubDiscoveryError, ValueError) as exc:
            result.outcomes.append(SourceUpdateOutcome(source.name, "failed", str(exc)))
            return

        if not candidates:
            result.outcomes.append(SourceUpdateOutcome(source.name, "failed", "no matching SKILL.md files discovered"))
            return

        success_count = 0
        for candidate in candidates:
            try:
                fetched = self.github_discoverer.fetch(candidate)
                stored = self.store.store(fetched)
            except (GitHubFileFetchError, OSError, ValueError) as exc:
                result.outcomes.append(SourceUpdateOutcome(source.name, "failed", f"{candidate.path}: {exc}"))
                continue

            success_count += 1
            result.outcomes.append(SourceUpdateOutcome(source.name, stored.status, f"{candidate.path}: {stored.document.normalized_path}"))

        if success_count == 0:
            result.outcomes.append(SourceUpdateOutcome(source.name, "failed", "no discovered Skills could be stored"))
