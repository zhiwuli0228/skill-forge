from pathlib import Path

from skill_forge.config import DEFAULT_OUTPUT_DIR, default_config, load_config, write_default_config


def test_default_config_values() -> None:
    config = default_config()

    assert config.update.mode == "manual"
    assert config.update.stale_after_days == 7
    assert config.create.default_target == "opencode"
    assert config.create.default_language == "zh-CN"
    assert config.create.output_dir == DEFAULT_OUTPUT_DIR
    assert config.retrieval.top_k == 5
    assert config.retrieval.rerank_enabled is True
    assert config.retrieval.rerank_by_default is False
    assert config.retrieval.rerank_provider == "lexical"
    assert config.retrieval.rerank_candidate_multiplier == 3
    assert config.platforms.opencode.user_skills_path == "~/.config/opencode/skills"
    assert config.platforms.claude.user_skills_path == "~/.claude/skills"
    assert config.platforms.codex.user_skills_path == "~/.codex/skills"


def test_load_config_uses_defaults_when_missing(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.yaml")

    assert config.create.default_target == "opencode"
    assert config.retrieval.use_tfidf is True
    assert config.retrieval.rerank_by_default is False


def test_load_config_accepts_retrieval_rerank_overrides(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(
        """
retrieval:
  top_k: 3
  use_tfidf: true
  rerank_enabled: false
  rerank_by_default: true
  rerank_provider: lexical
  rerank_candidate_multiplier: 5
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.retrieval.top_k == 3
    assert config.retrieval.rerank_enabled is False
    assert config.retrieval.rerank_by_default is True
    assert config.retrieval.rerank_candidate_multiplier == 5


def test_write_default_config_preserves_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("update:\n  mode: custom\n", encoding="utf-8")

    created = write_default_config(path)

    assert created is False
    assert path.read_text(encoding="utf-8") == "update:\n  mode: custom\n"


def test_write_default_config_creates_loadable_yaml(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"

    created = write_default_config(path)
    config = load_config(path)

    assert created is True
    assert config.update.mode == "manual"
    assert config.create.output_dir == DEFAULT_OUTPUT_DIR
