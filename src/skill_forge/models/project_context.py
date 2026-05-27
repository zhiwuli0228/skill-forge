from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


SUPPORTED_FILE_NAMES = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "README.txt",
    "config.yaml",
    "project.md",
)
SUPPORTED_DIR_NAMES = (
    ".opencode",
    ".claude",
    ".agents",
    "openspec",
)
IGNORED_DIR_NAMES = (
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
)
DEFAULT_MAX_FILE_BYTES = 64 * 1024
DEFAULT_MAX_TOTAL_CHARS = 60_000


class ProjectContextSettings(BaseModel):
    supported_file_names: tuple[str, ...] = SUPPORTED_FILE_NAMES
    supported_dir_names: tuple[str, ...] = SUPPORTED_DIR_NAMES
    ignored_dir_names: tuple[str, ...] = IGNORED_DIR_NAMES
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES
    max_total_chars: int = DEFAULT_MAX_TOTAL_CHARS


class ProjectContextFile(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: Path
    relative_path: str
    content: str


class SkippedProjectFile(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: Path
    relative_path: str
    reason: str


class ProjectContextInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    project_path: Path
    files: list[ProjectContextFile] = Field(default_factory=list)
    skipped_files: list[SkippedProjectFile] = Field(default_factory=list)


class ProjectContextSummary(BaseModel):
    project_path: Path
    detected_tools: list[str] = Field(default_factory=list)
    detected_rules: list[str] = Field(default_factory=list)
    summary_text: str = ""
    derived_constraints: list[str] = Field(default_factory=list)
