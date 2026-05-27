from pathlib import Path

from skill_forge.models.project_context import (
    ProjectContextFile,
    ProjectContextInput,
    ProjectContextSettings,
    SkippedProjectFile,
)


class ProjectContextReader:
    def __init__(self, settings: ProjectContextSettings | None = None) -> None:
        self.settings = settings or ProjectContextSettings()

    def read(self, project_path: Path) -> ProjectContextInput:
        root = project_path.expanduser().resolve()
        result = ProjectContextInput(project_path=root)
        if not root.exists() or not root.is_dir():
            result.skipped_files.append(SkippedProjectFile(path=root, relative_path=".", reason="missing_project"))
            return result

        total_chars = 0
        for path in self._candidate_paths(root):
            relative_path = path.relative_to(root).as_posix()
            skip_reason = "ignored_directory" if self._is_ignored_path(path, root) else self._skip_reason(path)
            if skip_reason:
                result.skipped_files.append(SkippedProjectFile(path=path, relative_path=relative_path, reason=skip_reason))
                continue

            text = path.read_text(encoding="utf-8", errors="replace")
            remaining = self.settings.max_total_chars - total_chars
            if remaining <= 0:
                result.skipped_files.append(SkippedProjectFile(path=path, relative_path=relative_path, reason="total_limit"))
                continue
            if len(text) > remaining:
                text = text[:remaining]
            total_chars += len(text)
            result.files.append(ProjectContextFile(path=path, relative_path=relative_path, content=text))

        return result

    def _candidate_paths(self, root: Path) -> list[Path]:
        candidates: list[Path] = []
        for name in self.settings.supported_file_names:
            path = root / name
            if path.is_file():
                candidates.append(path)

        for directory_name in self.settings.supported_dir_names:
            directory = root / directory_name
            if not directory.exists():
                continue
            if directory.is_file():
                candidates.append(directory)
                continue
            for path in directory.rglob("*"):
                if path.is_file():
                    candidates.append(path)

        return sorted(set(candidates), key=lambda path: path.relative_to(root).as_posix().lower())

    def _skip_reason(self, path: Path) -> str | None:
        try:
            if path.stat().st_size > self.settings.max_file_bytes:
                return "too_large"
            sample = path.read_bytes()[:2048]
        except OSError:
            return "unreadable"
        if b"\x00" in sample:
            return "binary"
        return None

    def _is_ignored_path(self, path: Path, root: Path) -> bool:
        return any(part in self.settings.ignored_dir_names for part in path.relative_to(root).parts[:-1])
