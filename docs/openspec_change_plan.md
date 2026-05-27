# Skill Forge OpenSpec Change 拆分与进展跟踪

本文档用于跟踪 `docs/skill_forge_design_doc.md` 中需求的 OpenSpec change 拆分、实现顺序、依赖关系和完成进展。

当前状态：

- 项目源码基本为空骨架：`src/skill_forge/__init__.py` 只有基础入口。
- `openspec list --json` 当前无 active change。
- 推荐按“可验收能力闭环”拆分 change，而不是按代码目录机械拆分。

## 拆分原则

1. 每个 change 都应该能形成明确的用户可见能力或工程基础能力。
2. 前 3 个 change 应优先完成最小 MVP 闭环。
3. 联网资料库、搜索、项目上下文读取可以在 MVP 闭环之后独立推进。
4. 不建议严格按设计文档的 10 个 Module 拆成 10 个 change，因为部分模块单独实现后不可验收。

## 总体依赖

```text
establish-cli-foundation
        |
        v
implement-local-skill-generation
        |
        v
add-validation-and-installation
        |
        +--------------> add-interactive-drafts
        |
        +--------------> add-research-corpus-update ---> add-search-retrieval
        |
        +--------------> add-project-context-generation
```

## Change 总览

| 顺序 | Change ID | 状态 | 目标 | 覆盖模块 |
|---:|---|---|---|---|
| 1 | `establish-cli-foundation` | Archived | 建立项目基础、CLI 框架、配置、路径、SQLite 初始化 | Module 1 + Module 2 基础 |
| 2 | `implement-local-skill-generation` | Archived | 实现无网络、无交互的 `create` 生成 Skill 包 | Module 3 + Module 5 |
| 3 | `add-validation-and-installation` | Archived | 实现 `validate` 和 `install`，完成本地 MVP 闭环 | Module 6 + Module 7 |
| 4 | `add-interactive-drafts` | Archived | 支持 `create --interactive` 和 `resume <draft-id>` | Module 4 |
| 5 | `add-research-corpus-update` | Archived | 支持 `update`，联网抓取、清洗、缓存、写库 | Module 8 |
| 6 | `add-search-retrieval` | Archived | 支持 `search`，基于本地资料库 TF-IDF 检索排序 | Module 9 |
| 7 | `add-project-context-generation` | Archived | 支持 `--project` 读取项目上下文并注入生成 | Module 10 |

状态建议值：

- `Not started`
- `Proposed`
- `Implementing`
- `Implemented`
- `Verified`
- `Archived`
- `Blocked`

## MVP 验收目标

前三个 change 完成后，应该跑通以下命令：

```bash
skill-forge init
skill-forge create "Java 存量代码 bug 定位 skill"
skill-forge validate ~/.skill-forge/output/java-bug-investigation
skill-forge install java-bug-investigation --target opencode --scope project
```

预期结果：

1. `init` 创建用户配置、SQLite 数据库和基础目录。
2. `create` 在本地输出一个包含 `SKILL.md` 的 Skill 包。
3. `validate` 能区分 error 和 warning。
4. `install` 能安装到目标平台目录，且默认不覆盖已有 Skill。

## Change 详情

### 1. `establish-cli-foundation`

状态：`Archived`

目标：

- 建立可运行的 Python CLI 基础。
- 实现 `skill-forge --help` 和 `skill-forge init`。
- 建立配置、路径和 SQLite 初始化基础。

建议范围：

- Typer CLI 应用入口。
- `init` 命令。
- 默认目录创建。
- 默认配置文件创建。
- SQLite 数据库文件和基础 schema 初始化。
- 基础 Pydantic 配置模型。
- 基础测试结构。

不包含：

- Skill 生成。
- Skill 校验。
- 安装逻辑。
- 网络更新。

验收命令：

```bash
skill-forge --help
skill-forge init
```

验收标准：

- 命令执行成功。
- 创建 `~/.skill-forge/config.yaml`。
- 创建 `~/.skill-forge/db/skill_forge.sqlite`。
- 创建 `~/.skill-forge/corpus/`、`drafts/`、`output/`。
- 单元测试覆盖配置默认值和 init 行为。

进展记录：

- 2026-05-24: Created OpenSpec change artifacts at `openspec/changes/establish-cli-foundation/`: `proposal.md`, `design.md`, `specs/cli-foundation/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented Typer CLI foundation, `init` workspace setup, default config handling, path helpers, and SQLite baseline schema.
- 2026-05-24: Verified with `uv run pytest`, `uv run skill-forge --help`, and `uv run skill-forge init --home E:\tmp\skill-forge-verify`.
- 2026-05-24: Archived via `openspec.cmd archive "establish-cli-foundation" --yes`; synced `cli-foundation` to main specs and archived change as `openspec/changes/archive/2026-05-23-establish-cli-foundation/`.
- Remaining: none.

### 2. `implement-local-skill-generation`

状态：`Archived`

目标：

- 实现无网络、无交互、模板驱动的 Skill 生成。
- 支持 `skill-forge create "<requirement>"`。

建议范围：

- `SkillRequirement` 等核心数据模型。
- 基于规则的 Requirement Analyzer。
- Jinja2 模板渲染。
- 生成 `~/.skill-forge/output/<skill-name>/SKILL.md`。
- 生成必要章节：Purpose、When to use、When not to use、Required inputs、Workflow、Constraints、Output format、Quality gates。

不包含：

- 交互式问答。
- 草稿保存。
- 校验器完整实现。
- 安装。
- 网络检索。

验收命令：

```bash
skill-forge create "Java 存量代码 bug 定位 skill"
```

验收标准：

- 生成 `~/.skill-forge/output/java-bug-investigation/SKILL.md`。
- `SKILL.md` 包含 frontmatter `name` 和 `description`。
- 对设计文档中的 Java bug 定位示例能生成合理结构化结果。
- 单元测试覆盖需求解析和模板渲染。

进展记录：

- 2026-05-24: Created OpenSpec change artifacts at `openspec/changes/implement-local-skill-generation/`: `proposal.md`, `design.md`, `specs/local-skill-generation/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented non-interactive local Skill generation with rule-based analysis, Jinja2 rendering, package writing, non-overwrite protection, and `skill-forge create`.
- 2026-05-24: Verified with `uv run pytest` and isolated `uv run skill-forge create "Java 存量代码 bug 定位 skill" --home <temp-home>`.
- 2026-05-24: Archived via `openspec.cmd archive "implement-local-skill-generation" --yes`; synced `local-skill-generation` to main specs and archived change as `openspec/changes/archive/2026-05-23-implement-local-skill-generation/`.
- Remaining: none.

### 3. `add-validation-and-installation`

状态：`Archived`

目标：

- 实现 Skill 静态校验。
- 实现安装到 opencode、Claude Code、Codex 目标路径。
- 完成本地 MVP 闭环。

建议范围：

- `validate <skill-path>` 命令。
- `install <skill-name> --target <codex|opencode|claude> --scope <project|user>` 命令。
- 校验目录、`SKILL.md`、frontmatter、必需字段和推荐章节。
- 安装路径计算。
- 默认不覆盖已有 Skill。
- `--force` 覆盖。

不包含：

- 交互式覆盖确认可以后续增强；MVP 可只支持 `--force`。
- 网络资料库。
- 项目上下文读取。

验收命令：

```bash
skill-forge validate ~/.skill-forge/output/java-bug-investigation
skill-forge install java-bug-investigation --target opencode --scope project
```

验收标准：

- `validate` 输出 error / warning。
- 合法 Skill 校验通过。
- 缺失 `SKILL.md` 或 frontmatter 时返回 error。
- 安装后生成 `./.opencode/skills/java-bug-investigation/SKILL.md`。
- 已存在目标目录时，未传 `--force` 不覆盖。
- 单元测试覆盖 validator 和 installer。

进展记录：

- 2026-05-24: Created OpenSpec change artifacts at `openspec/changes/add-validation-and-installation/`: `proposal.md`, `design.md`, `specs/skill-validation/spec.md`, `specs/skill-installation/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented static Skill validation, validation result models, platform installer, no-overwrite/force behavior, and `skill-forge validate` / `skill-forge install`.
- 2026-05-24: Verified with `uv run pytest`, isolated MVP `init/create/validate/install`, and `openspec.cmd validate "add-validation-and-installation" --strict`.
- 2026-05-24: Archived via `openspec.cmd archive "add-validation-and-installation" --yes`; synced `skill-validation` and `skill-installation` to main specs and archived change as `openspec/changes/archive/2026-05-23-add-validation-and-installation/`.
- Remaining: none.

### 4. `add-interactive-drafts`

状态：`Archived`

目标：

- 支持交互式 Skill 创建。
- 支持草稿保存和恢复。

建议范围：

- `create --interactive`。
- `resume <draft-id>`。
- `SkillDraftState`。
- 每一步回答后保存 draft JSON。
- 跳过已完成步骤。
- 支持从 draft 继续生成 Skill。

不包含：

- LLM 增强。
- 项目上下文读取。
- 网络资料更新。

验收命令：

```bash
skill-forge create "Java bug 定位 skill" --interactive
skill-forge resume <draft-id>
```

验收标准：

- 交互式流程能确认关键字段。
- 中断后可以恢复。
- 草稿 JSON 内容完整。
- 不重复追问已确认字段。
- 最终仍复用已有 generator 生成 Skill。

进展记录：

- 2026-05-24: Created OpenSpec change artifacts at `openspec/changes/add-interactive-drafts/`: `proposal.md`, `design.md`, `specs/interactive-drafts/spec.md`, `specs/local-skill-generation/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented interactive draft model/store, injectable wizard, `create --interactive`, `resume <draft-id>`, draft persistence, and resume-to-generation behavior.
- 2026-05-24: Verified with `uv run pytest`, CLI runner checks for interactive create/resume using fake prompts, and `openspec.cmd validate "add-interactive-drafts" --strict`.
- 2026-05-24: Archived via `openspec.cmd archive "add-interactive-drafts" --yes`; synced new `interactive-drafts` spec and modified `local-skill-generation` spec, archived change as `openspec/changes/archive/2026-05-23-add-interactive-drafts/`.
- Remaining: none.

### 5. `add-research-corpus-update`

状态：`Archived`

目标：

- 支持资料源配置、联网更新和本地分层缓存。

建议范围：

- `configs/sources.yaml`。
- `update` 命令。
- docs source 拉取。
- GitHub source 拉取的 MVP 版本。
- raw / normalized 文件保存。
- SQLite metadata 写入。
- content hash 去重。
- 单源失败不影响整体更新。

不包含：

- TF-IDF 搜索命令。
- 复杂 pattern 抽取。
- 自动定时更新。

验收命令：

```bash
skill-forge update
```

验收标准：

- 能读取资料源配置。
- 至少成功更新一个 docs source。
- 写入 raw 和 normalized 内容。
- 写入 SQLite documents / skill_examples 等元数据。
- 内容未变化时跳过重复解析。
- 所有源失败时返回非零退出码。

进展记录：

- 2026-05-24: Created OpenSpec change artifacts at `openspec/changes/add-research-corpus-update/`: `proposal.md`, `design.md`, `specs/research-corpus-update/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented source config loading, HTTP fetching, HTML/Markdown normalization, raw/normalized corpus cache writes, SQLite metadata persistence, hash-based skip behavior, partial failure handling, and `skill-forge update`.
- 2026-05-24: Verified with `uv run pytest`, `openspec.cmd validate "add-research-corpus-update" --strict`, and isolated `uv run skill-forge update --home E:\tmp\skill-forge-update-verify`.
- 2026-05-24: Verification review passed with no critical issues; change is ready to archive.
- 2026-05-24: Archived via `openspec.cmd archive "add-research-corpus-update" --yes`; synced `research-corpus-update` to main specs and archived change as `openspec/changes/archive/2026-05-24-add-research-corpus-update/`.
- Remaining: none.

### 6. `add-search-retrieval`

状态：`Archived`

目标：

- 支持基于本地资料库的搜索和排序。

依赖：

- `add-research-corpus-update`

建议范围：

- `search "<query>"` 命令。
- TF-IDF 索引构建。
- top-k 参数。
- 展示名称、来源、摘要、评分。
- 按权威性、文本相关性、完整度、更新时间、平台匹配等维度排序。

不包含：

- 向量数据库。
- LLM rerank。
- 自动联网刷新。

验收命令：

```bash
skill-forge search "bug investigation"
skill-forge search "skill creator" --top-k 5
```

验收标准：

- 能从本地资料库返回相关结果。
- 展示来源、摘要和评分。
- 无索引或无资料时给出清晰提示。
- 单元测试覆盖索引和检索排序。

进展记录：

- 2026-05-24: Created OpenSpec change artifacts at `openspec/changes/add-search-retrieval/`: `proposal.md`, `design.md`, `specs/search-retrieval/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented local corpus loading, TF-IDF index persistence, stale index rebuild, deterministic ranking boosts, and `skill-forge search` with `--top-k` and `--platform`.
- 2026-05-24: Verified with `uv run pytest`, `openspec.cmd validate "add-search-retrieval" --strict`, and isolated `uv run skill-forge search "skill creator" --home E:\tmp\skill-forge-update-verify --top-k 2`.
- 2026-05-24: Verification review passed with no critical issues; change is ready to archive.
- 2026-05-24: Archived via `openspec.cmd archive "add-search-retrieval" --yes`; synced `search-retrieval` to main specs and archived change as `openspec/changes/archive/2026-05-24-add-search-retrieval/`.
- Remaining: none.

### 7. `add-project-context-generation`

状态：`Archived`

目标：

- 支持读取项目上下文，并将项目约束注入生成流程。

建议范围：

- `create "<requirement>" --project <path>`。
- 扫描规则类文件：`AGENTS.md`、`CLAUDE.md`、`README.md`、`.opencode/`、`.claude/`、`.agents/`、`openspec/`、`config.yaml`、`project.md`。
- 跳过大文件、二进制文件和构建产物。
- 生成简单摘要。
- 将摘要转为 Skill constraints。

不包含：

- LLM 总结。
- 读取整个项目源码。
- 自动修改项目规则文件。

验收命令：

```bash
skill-forge create "OpenSpec change skill" --project . --interactive
```

验收标准：

- 能识别当前项目存在 OpenSpec。
- 生成的 Skill 包含项目约束，例如先提案后实现、保留测试要求、避免无关改动。
- 对大文件和二进制文件有明确跳过策略。
- 单元测试覆盖上下文扫描和约束注入。

进展记录：

- 2026-05-24: Created OpenSpec change artifacts at `openspec/changes/add-project-context-generation/`: `proposal.md`, `design.md`, `specs/project-context-generation/spec.md`, `specs/local-skill-generation/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented project context models, bounded project reader, deterministic summary/rule detection, constraint injection, `create --project`, and interactive draft project context persistence.
- 2026-05-24: Verified with `uv run pytest`, `openspec.cmd validate "add-project-context-generation" --strict`, and isolated `uv run skill-forge create "OpenSpec change skill" --project . --home <temp-home>`.
- 2026-05-24: Verification review passed with no critical issues; change is ready to archive.
- 2026-05-24: Archived via `openspec.cmd archive "add-project-context-generation" --yes`; synced new `project-context-generation` spec and modified `local-skill-generation` spec, archived change as `openspec/changes/archive/2026-05-24-add-project-context-generation/`.
- Remaining: none.

## 后续更新方式

每完成一个 OpenSpec change 后，建议更新以下位置：

1. 在“Change 总览”表中更新状态。
2. 在对应 change 的“进展记录”中补充：
   - 创建日期。
   - 实现完成日期。
   - 验证命令。
   - 主要产物。
   - 遗留问题。
3. 如果 change 被拆分或合并，更新“总体依赖”和对应说明。

进展记录模板：

```markdown
- 2026-xx-xx: Created proposal/design/spec/tasks.
- 2026-xx-xx: Implemented core behavior in ...
- 2026-xx-xx: Verified with `...`.
- Remaining: ...
```
