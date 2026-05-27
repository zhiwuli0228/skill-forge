# Skill Forge

[English README](README.md)

Skill Forge 是一个本地优先的 CLI 工作台，用于设计、生成、校验、更新、搜索和安装 AI Agent Skills。

它可以根据自然语言需求生成标准 `SKILL.md` 包，支持交互式草稿、项目上下文注入、本地资料库检索，并能将生成结果安装到 Codex、opencode 或 Claude 兼容目录。

默认生成路径采用确定性实现，不依赖 LLM 也可以生成 Skill。需要时可以通过 `--llm` 显式启用 LLM 辅助需求精炼。

## 功能

- 根据自然语言需求生成 Skill 包。
- 自动应用内置、用户级或项目级蓝图，或通过 `--blueprint` 显式选择蓝图。
- 可选通过 `--llm` 使用已配置的 LLM 精炼需求。
- 通过交互式向导补全和确认 Skill 需求。
- 保存并恢复交互式草稿。
- 生成后自动输出校验结果和质量报告。
- 以 validation warning 形式运行确定性的 Skill authoring lint 检查。
- 为 validation 和质量报告中的问题输出确定性的 suggested fixes。
- 将生成来源和质量信息写入 `skill-forge.json`。
- 运行确定性的本地 eval cases，并保存最近一次 `eval-report.json`。
- 基于 provenance 和当前蓝图标准生成升级候选 Skill。
- 校验 Skill 包结构和 `SKILL.md` frontmatter。
- 将生成的 Skill 安装到 Codex、opencode 或 Claude 目录。
- 从配置的文档源更新本地研究资料库。
- 使用 TF-IDF 和平台匹配加权搜索本地资料库。
- 读取 `AGENTS.md`、`CLAUDE.md`、`README.md`、`.opencode/`、`.claude/`、`.agents/`、`openspec/` 等项目规则，并转成生成约束。
- 查看内置和自定义蓝图，并通过 `list`、`show`、`diff` 管理已生成的 Skill 包。

## 环境要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 用于依赖管理和本地命令执行

## 安装

在仓库根目录执行：

```bash
uv sync
```

不全局安装，直接运行 CLI：

```bash
uv run skill-forge --help
```

本地开发可使用 editable 安装：

```bash
uv pip install -e .
```

## 快速开始

初始化本地 Skill Forge 工作区：

```bash
uv run skill-forge init
```

生成一个 Skill：

```bash
uv run skill-forge create "Java 存量代码 bug 定位 skill"
```

生成完成后会自动运行校验，并输出确定性的质量报告。

校验生成结果：

```bash
uv run skill-forge validate E:/009workspace/skills/java-bug-investigation
```

安装到当前项目的 opencode Skill 目录：

```bash
uv run skill-forge install java-bug-investigation --target opencode --scope project
```

显式指定项目目录：

```bash
uv run skill-forge install java-bug-investigation --target opencode --scope project --project /path/to/project
```

## 命令说明

### `init`

创建本地工作区、默认配置和 SQLite 数据库。

```bash
uv run skill-forge init
```

默认工作区是 `~/.skill-forge`。测试或隔离运行时可以指定：

```bash
uv run skill-forge init --home /tmp/skill-forge-home
```

也可以使用环境变量：

```bash
export SKILL_FORGE_HOME=/tmp/skill-forge-home
```

### `create`

在配置的输出目录下生成 Skill 包，默认输出到 `E:/009workspace/skills`。

```bash
uv run skill-forge create "git commit workflow skill"
```

也可以为单次命令覆盖输出目录：

```bash
uv run skill-forge create "git commit workflow skill" --output-dir E:/tmp/skills
```

当需求解析器识别出受支持的任务类型时，Skill Forge 会在渲染前应用匹配的内置蓝图。也可以显式指定内置或自定义蓝图：

```bash
uv run skill-forge create "Python 服务 review skill" --blueprint code-review
```

交互式模式会保存可恢复草稿：

```bash
uv run skill-forge create "OpenSpec change analysis skill" --interactive
```

项目上下文模式会读取项目规则文件，并把推导出的约束写入 Skill：

```bash
uv run skill-forge create "OpenSpec change skill" --project .
```

也可以同时使用交互式模式和项目上下文：

```bash
uv run skill-forge create "OpenSpec change skill" --project . --interactive
```

非交互式生成可以显式启用 LLM 辅助需求精炼。需要配置 `SKILL_FORGE_LLM_API_KEY` 和 `SKILL_FORGE_LLM_MODEL`，也可以用 `SKILL_FORGE_LLM_BASE_URL` 指向 OpenAI 兼容接口。

```bash
uv run skill-forge create "release process skill" --llm
```

LLM 返回内容只会合并到受支持的结构化需求字段中，生成结果仍会经过校验和质量报告。

### `blueprints`

查看内置、用户级和项目级生成蓝图。

```bash
uv run skill-forge blueprints list
uv run skill-forge blueprints show bug-investigation
```

当前内置蓝图覆盖 bug 定位、代码审查、OpenSpec change 工作流和测试生成。

用户级自定义蓝图可以放在：

```text
~/.skill-forge/blueprints
```

传入 `--project` 时会同时加载项目级自定义蓝图，默认目录为：

```text
<project>/.skill-forge/blueprints
```

```bash
uv run skill-forge blueprints list --project .
uv run skill-forge create "team review skill" --blueprint team-code-review --project .
```

### `resume`

从 `~/.skill-forge/drafts` 恢复交互式草稿。

```bash
uv run skill-forge resume <draft-id>
```

### `validate`

校验一个 Skill 包目录。

```bash
uv run skill-forge validate E:/009workspace/skills/java-bug-investigation
```

校验内容包括：

- Skill 目录是否存在。
- `SKILL.md` 是否存在。
- frontmatter 是否存在。
- `name` 和 `description` 是否存在。
- Purpose、Workflow、Output format、Quality gates 等推荐章节是否存在。
- authoring lint warning，例如 name 格式、包名不一致、description 太弱、章节为空、workflow 或 quality gates 太薄。

当 validation 输出 error 或 warning 时，CLI 也会显示确定性的 suggested fixes。这些建议只做提示，不会自动修改文件。

### `eval`

对已生成的 Skill 包运行确定性的本地 eval cases。Eval case 使用 YAML 描述目标 Skill 和静态断言。

```bash
uv run skill-forge eval java-bug-investigation --case evals/java-bug-basic.yaml
uv run skill-forge eval java-bug-investigation --cases evals/
```

支持的断言：

- `required_sections`：每个章节都必须出现在 `SKILL.md` 中。
- `required_constraints`：每个约束短语都必须出现在 `SKILL.md` 中。
- `forbidden_phrases`：每个禁用短语都不能出现在 `SKILL.md` 中。

命令会把最近一次结果写入被评估 Skill 包的 `eval-report.json`。任意断言失败时命令返回非零退出码。

### `install`

将生成的 Skill 包安装到目标平台。

```bash
uv run skill-forge install <skill-name> --target <codex|opencode|claude> --scope <project|user>
```

项目级安装路径：

| 目标 | 路径 |
|---|---|
| `codex` | `<project>/.codex/skills/<skill-name>` |
| `opencode` | `<project>/.opencode/skills/<skill-name>` |
| `claude` | `<project>/.claude/skills/<skill-name>` |

用户级安装路径可配置，默认值为：

| 目标 | 路径 |
|---|---|
| `codex` | `~/.codex/skills/<skill-name>` |
| `opencode` | `~/.config/opencode/skills/<skill-name>` |
| `claude` | `~/.claude/skills/<skill-name>` |

默认不会覆盖已有安装。需要覆盖时传入 `--force`：

```bash
uv run skill-forge install java-bug-investigation --target opencode --scope project --force
```

### `update`

从配置的资料源刷新本地研究资料库。

```bash
uv run skill-forge update
```

Skill Forge 会保存 raw 和 normalized 内容，更新 SQLite 元数据，根据内容 hash 跳过未变化内容，并允许部分资料源失败。如果所有启用的资料源都失败，命令会以非零状态退出。

摘要会显示 `ok`、`partial` 或 `failed` 状态，并列出 updated、skipped、failed、disabled 数量。失败的 source 行会给出修复 source 问题后重新运行 update 的提示。

默认资料源配置位于：

```text
configs/sources.yaml
```

用户覆盖配置可以放在：

```text
~/.skill-forge/sources.yaml
```

### `search`

搜索本地研究资料库。

```bash
uv run skill-forge search "skill creator"
```

限制结果数量：

```bash
uv run skill-forge search "bug investigation" --top-k 3
```

优先匹配目标平台：

```bash
uv run skill-forge search "skill creator" --platform codex
```

解释确定性的排序分数组成：

```bash
uv run skill-forge search "skill creator" --platform codex --explain
```

解释输出包含 relevance、authority、completeness、freshness、platform boost 和 final score。

也可以使用内置的离线 lexical reranker 对 TF-IDF 候选结果做可选重排：

```bash
uv run skill-forge search "skill creator" --rerank
```

Search 输出会标识检索模式，例如 `tfidf` 或 `tfidf+rerank`。如果 rerank 被配置禁用或不可用，search 会回退到 TF-IDF 并打印 warning。

如果本地资料库为空，先运行 `skill-forge update`。

### `list`

列出配置输出目录下已生成的 Skill 包。

```bash
uv run skill-forge list
```

### `show`

展示某个已生成 Skill 包的元数据，包括 frontmatter、包路径、附件数量、生成来源，以及存在时的最近 eval 摘要。

```bash
uv run skill-forge show java-bug-investigation
```

### `diff`

比较两个已生成 Skill 包的 `SKILL.md`。

```bash
uv run skill-forge diff skill-a skill-b
```

### `upgrade`

基于已有 Skill 包中的 `skill-forge.json` provenance 和当前记录的蓝图，生成一个新的升级候选包。

```bash
uv run skill-forge upgrade java-bug-investigation
```

默认候选名是 `<skill-name>-upgraded`。也可以显式指定：

```bash
uv run skill-forge upgrade java-bug-investigation --candidate-name java-bug-v2
```

默认不会覆盖已有候选包。需要替换候选包时传入 `--force`：

```bash
uv run skill-forge upgrade java-bug-investigation --force
```

源 Skill 包不会被修改。升级后可比较源包和候选包：

```bash
uv run skill-forge diff java-bug-investigation java-bug-investigation-upgraded
```

没有 `skill-forge.json` 的旧包不能升级，因为 Skill Forge 无法可靠还原原始需求和蓝图来源。

## 配置

默认配置写入：

```text
~/.skill-forge/config.yaml
```

默认内容：

```yaml
update:
  mode: manual
  stale_after_days: 7
  check_on_create: true
  auto_update_on_create: false
create:
  default_target: opencode
  default_language: zh-CN
  output_dir: E:/009workspace/skills
  interactive_by_default: false
retrieval:
  top_k: 5
  use_tfidf: true
  rerank_enabled: true
  rerank_by_default: false
  rerank_provider: lexical
  rerank_candidate_multiplier: 3
platforms:
  opencode:
    user_skills_path: ~/.config/opencode/skills
  claude:
    user_skills_path: ~/.claude/skills
  codex:
    user_skills_path: ~/.codex/skills
```

## 本地数据目录

默认工作区结构：

```text
~/.skill-forge/
├── config.yaml
├── sources.yaml
├── corpus/
│   ├── raw/
│   └── normalized/
├── db/
│   └── skill_forge.sqlite
├── blueprints/
├── drafts/
├── index/
├── logs/
└── output/
```

## 生成结果结构

生成的 Skill 包至少包含：

```text
<skill-name>/
└── SKILL.md
```

基于蓝图生成的 Skill 包也可能包含蓝图声明的 references、assets 或 scripts，例如：

```text
<skill-name>/
├── SKILL.md
├── skill-forge.json
├── eval-report.json
└── references/
    └── diagnosis-checklist.md
```

生成的 `SKILL.md` 包含：

- 带 `name` 和 `description` 的 frontmatter。
- Purpose。
- When to use。
- When not to use。
- Required inputs。
- Workflow。
- Constraints。
- Output format。
- Quality gates。

`skill-forge.json` 会记录有限的生成来源信息，例如 schema version、生成时间、原始需求、目标平台、语言、应用的蓝图、是否启用 LLM、项目路径、质量分和生成附件路径。

`eval-report.json` 会记录最近一次确定性 eval 的汇总和 case 级断言结果。

## 开发

运行完整测试：

```bash
uv run pytest
```

运行单个测试文件：

```bash
uv run pytest tests/test_cli.py
```

常用本地验证流程：

```bash
uv run skill-forge init --home /tmp/skill-forge-verify
uv run skill-forge create "Java 存量代码 bug 定位 skill" --home /tmp/skill-forge-verify
uv run skill-forge validate /tmp/skill-forge-verify/output/java-bug-investigation
uv run skill-forge list --home /tmp/skill-forge-verify
uv run skill-forge blueprints list
uv run skill-forge search "skill creator" --home /tmp/skill-forge-verify
```

Windows PowerShell 下可将 `/tmp/skill-forge-verify` 替换为类似 `E:\tmp\skill-forge-verify` 的路径。

## 项目结构

```text
src/skill_forge/
├── cli.py
├── config.py
├── evals/
├── generator/
├── installer/
├── interaction/
├── models/
├── project_context/
├── requirement/
├── research/
├── retrieval/
├── storage/
└── validator/
```

辅助文件：

- `templates/common/SKILL.md.j2`：默认 Skill 模板。
- `configs/sources.yaml`：默认研究资料源。
- `docs/skill_forge_design_doc.md`：产品和架构设计文档。
- `docs/openspec_change_plan.md`：OpenSpec 实现阶段跟踪文档。
- `openspec/specs/`：已归档的能力规格。

## 当前范围

已实现：

- 本地确定性 Skill 生成。
- 内置、用户级和项目级蓝图驱动生成，以及显式蓝图选择。
- 蓝图声明的 reference、asset、script 文件生成。
- `skill-forge.json` 生成来源 metadata。
- 确定性本地 eval cases 和持久化的 `eval-report.json`。
- 交互式草稿与恢复。
- Skill 校验与安装。
- 生成后质量报告。
- validation 和质量报告中的 authoring lint warning。
- validation 和质量报告问题对应的确定性 suggested fixes。
- 研究资料库更新。
- 本地搜索与排序。
- 项目上下文注入。
- 可选 LLM 辅助需求精炼。
- 已生成 Skill 包管理命令：`list`、`show`、`diff`，以及 eval 摘要展示。
- 使用 `upgrade` 生成升级候选 Skill。

暂未实现：

- Web UI。
- 后台定时更新。
- 向量数据库检索。
- 自动原地替换 Skill 或远程迁移。
