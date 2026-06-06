# Skill Forge 下一阶段演进设计与进展跟踪

本文档用于规划 Skill Forge 从“可生成高质量 Skill 包”继续演进到“可定制、可追溯、可评估、可升级的 Skill 工厂”的下一阶段能力。

它不是某一个 OpenSpec change 的详细 proposal，而是后续创建多个 change 的上游设计和 process 跟踪文档。每个 change 应从本文档选择一个边界清晰、可独立验收的能力切片，再创建 `proposal.md`、`design.md`、`specs/` 和 `tasks.md`。

## 1. 当前基线

当前项目已经完成基础闭环和第一轮增强：

```text
用户需求
  ↓
RequirementAnalyzer
  ↓
可选 LLM refinement
  ↓
BlueprintRequirementEnricher
  ↓
ProjectContextEnricher
  ↓
SkillGenerator + Jinja2
  ↓
SkillValidator
  ↓
GenerationQualityReport
  ↓
install / list / show / diff
```

已具备的关键能力：

1. 本地确定性 Skill 生成。
2. 内置蓝图和显式 `--blueprint` 选择。
3. 蓝图声明 references、assets、scripts。
4. 生成后校验和质量报告。
5. 可选 LLM 辅助需求精炼。
6. 项目上下文注入。
7. 本地资料库更新、社区 Skill 发现和搜索。
8. 已生成 Skill 的 `list`、`show`、`diff` 管理。

当前主要缺口：

1. 蓝图还以 built-in 为主，团队无法自然沉淀私有标准。
2. 生成产物缺少 provenance metadata，难以复现、升级和治理。
3. Validator 仍偏结构校验，缺少面向 Skill authoring 的 lint 规则。
4. 质量报告能指出问题，但不能给出稳定的修复建议。
5. 没有 eval case 机制验证一个 Skill 在典型任务中是否真的有效。
6. `diff` 只能比较内容，尚不能基于生成来源和蓝图版本做升级。

## 2. 下一阶段目标

目标形态：

```text
团队标准 / 用户蓝图 / 官方最佳实践 / 项目上下文
  ↓
可配置蓝图解析与优先级
  ↓
可追溯 Skill 生成
  ↓
结构校验 + authoring lint + 修复建议
  ↓
eval cases 验证
  ↓
版本升级 / 迁移 / 对比
```

一句话目标：

> 让 Skill Forge 成为团队可以持续沉淀标准、批量生成、评估和升级 Agent Skills 的本地工作台。

## 3. 设计原则

1. 优先增强确定性能力，再考虑 LLM 或向量检索。
2. 每个 change 都要有用户可见行为或明确工程基础价值。
3. 先让团队能定制标准，再做自动升级和 UI。
4. 生成产物必须可追溯，后续质量治理都以 metadata 为基础。
5. Lint 和 eval 要分层：lint 检查静态质量，eval 检查任务行为。
6. 不把 marketplace、Web UI、远程同步提前混入核心链路。

## 4. 能力分层

```text
Layer 9: Web UI / remote collaboration
Layer 8: optional semantic retrieval / rerank
Layer 7: skill upgrade and migration
Layer 6: skill eval cases and batch reports
Layer 5: deterministic repair suggestions
Layer 4: authoring lint rules
Layer 3: generation provenance metadata
Layer 2: user and project custom blueprints
Layer 1: existing built-in blueprint generation
Layer 0: existing deterministic create / validate / install
```

下一阶段应优先完成 Layer 2 到 Layer 6。

## 5. 总体依赖

```text
add-user-custom-blueprints
        |
        v
add-generation-provenance-metadata
        |
        +--------------------------+
        |                          |
        v                          v
add-skill-authoring-lint-rules     add-skill-eval-cases
        |
        v
add-deterministic-repair-suggestions
        |
        v
add-skill-upgrade-workflow

improve-research-source-quality
        |
        v
add-optional-retrieval-rerank
```

说明：

1. 自定义蓝图是最高优先级，因为它直接服务“定制标准 Skill 输出”。
2. 生成 metadata 是后续升级、评估和治理的公共基础。
3. Lint 可以独立增强 validator，但记录 lint 结果最好依赖 metadata。
4. Eval 可以在 metadata 后并行推进，不必等待 repair suggestions。
5. Upgrade 依赖自定义蓝图、metadata 和 lint，否则无法判断如何迁移。
6. 检索增强和资料库质量增强是旁路能力，优先级低于生成质量主链路。

## 6. Change 总览

| 顺序 | Change ID | 优先级 | 状态 | 依赖 | 目标 | 不包含 |
|---:|---|---|---|---|---|---|
| 1 | `add-user-custom-blueprints` | P0 | Archived | 已有蓝图能力 | 支持用户级和项目级私有蓝图目录 | 不做远程 marketplace |
| 2 | `add-generation-provenance-metadata` | P0 | Archived | 可独立；建议在 1 后 | 为每次生成写入可追溯 metadata | 不做升级逻辑 |
| 3 | `add-skill-authoring-lint-rules` | P0 | Archived | 2 推荐 | 扩展 validator 为 Skill authoring lint | 不做自动修复 |
| 4 | `add-deterministic-repair-suggestions` | P1 | Archived | 3 | 根据 lint 结果给出确定性修复建议 | 不直接改写用户 Skill |
| 5 | `add-skill-eval-cases` | P1 | Archived | 2 推荐 | 支持 eval case 定义和本地执行报告 | 不接入真实 Agent 自动执行 |
| 6 | `add-skill-upgrade-workflow` | P2 | Archived | 1,2,3 | 支持基于蓝图和 metadata 的升级/迁移 | 不做远程同步 |
| 7 | `improve-research-source-quality` | P2 | Archived | 已有 update/search | 增强资料源新鲜度、失败重试和评分解释 | 不改变 create 主链路 |
| 8 | `add-optional-retrieval-rerank` | P3 | Archived | 7 推荐 | 可选语义检索或 rerank | 不替换默认 TF-IDF |

状态建议值：

- `Not started`
- `Proposed`
- `Implementing`
- `Implemented`
- `Verified`
- `Archived`
- `Blocked`

## 7. Process 跟踪规则

每个 change 进入实现前，应执行：

```bash
openspec list --json
openspec validate --all --strict
```

每个 change 的生命周期：

```text
Not started
  ↓
Proposed: 已创建 proposal/design/spec/tasks
  ↓
Implementing: 已开始代码或文档实现
  ↓
Implemented: 功能完成，测试尚未最终确认
  ↓
Verified: 测试和 openspec validate 通过
  ↓
Archived: openspec archive 完成，主 specs 已同步
```

每个 change 的进展记录必须至少包含：

1. 创建 OpenSpec artifacts 的日期。
2. 主要实现文件。
3. 验证命令。
4. 是否更新 README、roadmap、主规格。
5. Remaining 项。

进展记录模板：

```markdown
进展记录：

- YYYY-MM-DD: Created OpenSpec artifacts at `openspec/changes/<change-id>/`.
- YYYY-MM-DD: Implemented core behavior in `src/skill_forge/...`.
- YYYY-MM-DD: Verified with `uv run pytest ...` and `openspec validate "<change-id>" --strict`.
- YYYY-MM-DD: Archived via `openspec archive "<change-id>" --yes`.
- Remaining: ...
```

## 8. Change 详情

### 1. `add-user-custom-blueprints`

状态：`Archived`

目标：

- 支持用户级和项目级自定义蓝图目录。
- 让团队可以沉淀私有 Skill 标准，并与内置蓝图统一 `list`、`show`、`create`。

建议范围：

- 配置项：用户蓝图目录，例如 `~/.skill-forge/blueprints`。
- 项目级蓝图目录，例如 `<project>/.skill-forge/blueprints`。
- `BlueprintLoader` 支持多个 roots。
- 蓝图来源 metadata：`builtin`、`user`、`project`。
- 处理重复 blueprint id：第一版建议明确报错，避免优先级误解。
- CLI 展示蓝图来源。
- `create --blueprint <id>` 能使用自定义蓝图。

不包含：

- 不做远程 marketplace。
- 不做蓝图编辑器。
- 不做 Web UI。
- 不做蓝图版本升级。

用户可见行为：

```bash
skill-forge blueprints list
skill-forge blueprints show team-code-review
skill-forge create "团队代码审查 skill" --blueprint team-code-review
```

验收标准：

1. 用户目录中的合法蓝图能被加载、展示和用于生成。
2. 项目目录中的合法蓝图能在传入 `--project` 时被加载。
3. 重复 blueprint id 返回清晰错误。
4. 无自定义蓝图时保持现有内置蓝图行为。
5. 测试覆盖用户级、项目级、重复 id 和非法 YAML。

主要影响文件：

- `src/skill_forge/blueprints/loader.py`
- `src/skill_forge/models/blueprint.py`
- `src/skill_forge/config.py`
- `src/skill_forge/cli.py`
- `tests/test_blueprints.py`
- `openspec/specs/skill-blueprints/spec.md`

风险：

- 蓝图优先级不清会导致生成结果不可预测。
- 项目级蓝图如果默认扫描过宽，可能带来性能和安全问题。

进展记录：

- 2026-05-26: Created OpenSpec artifacts at `openspec/changes/add-user-custom-blueprints/`: `proposal.md`, `design.md`, delta specs for `skill-blueprints` and `local-skill-generation`, and `tasks.md`.
- 2026-05-26: Implemented user and project custom blueprint roots, loaded blueprint source metadata, duplicate ID diagnostics, CLI source/path display, `--project` support for blueprint inspection, and custom blueprint generation integration.
- 2026-05-26: Added tests for custom user/project blueprint loading, missing custom roots, duplicate IDs, blueprint list/show output, and `create --blueprint` with user/project custom blueprints.
- 2026-05-26: Verified with `uv run pytest tests/test_blueprints.py`, `uv run pytest tests/test_cli.py::test_init_creates_workspace`, `uv run pytest`, `openspec validate "add-user-custom-blueprints" --strict`, and `openspec validate --all --strict`.
- 2026-05-26: Archived via `openspec archive "add-user-custom-blueprints" --yes`; synced `skill-blueprints` and `local-skill-generation` specs and archived the change as `openspec/changes/archive/2026-05-25-add-user-custom-blueprints/`.
- Remaining: none.

### 2. `add-generation-provenance-metadata`

状态：`Archived`

目标：

- 为每次生成的 Skill 包写入 `skill-forge.json`，记录生成来源、配置、质量和附件清单。
- 为后续 `show`、`diff`、`upgrade`、eval 报告提供事实来源。

建议 metadata：

```json
{
  "schema_version": 1,
  "generated_at": "2026-05-26T00:00:00Z",
  "skill_name": "team-code-review",
  "requirement_text": "团队代码审查 skill",
  "target_platform": "opencode",
  "language": "zh-CN",
  "blueprint_id": "team-code-review",
  "blueprint_source": "project",
  "llm_enabled": false,
  "project_context_path": ".",
  "quality_score": 95,
  "quality_status": "valid",
  "references": [],
  "assets": [],
  "scripts": []
}
```

不包含：

- 不做历史版本管理。
- 不做升级命令。
- 不把敏感项目上下文全文写入 metadata。

用户可见行为：

```bash
skill-forge show team-code-review
```

验收标准：

1. `create` 生成 `skill-forge.json`。
2. `show` 展示 metadata 摘要。
3. `diff` 可以在内容差异之外提示 metadata 差异。
4. 未带 metadata 的旧 Skill 仍可被 `list/show/diff` 管理。
5. 测试覆盖 metadata 写入、读取和向后兼容。

主要影响文件：

- `src/skill_forge/models/generated.py`
- `src/skill_forge/generator/skill_generator.py`
- `src/skill_forge/library/manager.py`
- `src/skill_forge/cli.py`
- `tests/test_skill_generator.py`
- `tests/test_skill_library.py`

风险：

- metadata 记录过多会泄漏项目路径或需求细节。
- schema 后续变化需要版本字段。

进展记录：

- 2026-05-26: Created OpenSpec artifacts at `openspec/changes/add-generation-provenance-metadata/`: `proposal.md`, `design.md`, delta specs for `local-skill-generation` and `skill-library-management`, and `tasks.md`.
- 2026-05-26: Implemented `skill-forge.json` provenance metadata for successful non-interactive generation, applied blueprint ID/source tracking, quality and attachment manifests, optional library provenance loading, `show` provenance display, and metadata-aware `diff`.
- 2026-05-26: Added tests for provenance metadata writing, library show with and without provenance, metadata diff output, and legacy package compatibility.
- 2026-05-26: Verified with focused provenance/library tests, `uv run pytest`, `openspec validate "add-generation-provenance-metadata" --strict`, and `openspec validate --all --strict`.
- 2026-05-26: Archived via `openspec archive "add-generation-provenance-metadata" --yes`; synced `local-skill-generation` and `skill-library-management` specs and archived the change as `openspec/changes/archive/2026-05-25-add-generation-provenance-metadata/`.
- Remaining: none.

### 3. `add-skill-authoring-lint-rules`

状态：`Archived`

目标：

- 将 validator 从结构校验扩展为 Skill authoring lint。
- 用确定性规则检查 Skill 是否清晰、边界明确、平台兼容。

建议 lint 维度：

- `name` 是否符合 slug 规则。
- package 目录名是否与 frontmatter `name` 一致。
- `description` 是否包含明确触发条件。
- `description` 是否过短、过长或过宽。
- 是否存在 `When not to use`。
- workflow 是否为空、过短或不可执行。
- output format 是否稳定。
- quality gates 是否能验证输出。
- 附件路径和声明是否一致。
- 目标平台特定约束是否满足。

不包含：

- 不做自动修复。
- 不调用 LLM。
- 不执行 eval case。

用户可见行为：

```bash
skill-forge validate path/to/skill
skill-forge create "..." 
```

验收标准：

1. validator 输出新增 lint warning code。
2. quality report 分数反映 lint 结果。
3. `create` 后质量报告包含 authoring warnings。
4. 现有合法 Skill 不因为新增 lint 被错误判为 invalid。
5. 测试覆盖每类 lint 规则。

主要影响文件：

- `src/skill_forge/validator/skill_validator.py`
- `src/skill_forge/models/quality.py`
- `src/skill_forge/cli.py`
- `tests/test_skill_validator.py`
- `tests/test_generation_quality_report.py`

风险：

- 规则过严会让可用 Skill 产生大量噪声。
- 平台差异规则需要清晰归属，避免混用。

进展记录：

- 2026-05-26: Created OpenSpec artifacts at `openspec/changes/add-skill-authoring-lint-rules/`: `proposal.md`, `design.md`, delta specs for `skill-validation` and `generation-quality-report`, and `tasks.md`.
- 2026-05-26: Implemented deterministic warning-only authoring lint rules for name slug format, package/name mismatch, description strength, empty recommended sections, workflow density, and quality gate density.
- 2026-05-26: Preserved existing error semantics so lint warnings do not invalidate packages, while quality reports include and score the warnings through the existing warning penalty model.
- 2026-05-26: Added validator and create/quality regression tests for the new lint behavior.
- 2026-05-26: Verified with focused validator/quality/create tests, `uv run pytest`, `openspec validate "add-skill-authoring-lint-rules" --strict`, and `openspec validate --all --strict`.
- 2026-05-26: Archived via `openspec archive "add-skill-authoring-lint-rules" --yes`; synced `skill-validation` and `generation-quality-report` specs and archived the change as `openspec/changes/archive/2026-05-25-add-skill-authoring-lint-rules/`.
- Remaining: none.

### 4. `add-deterministic-repair-suggestions`

状态：`Archived`

目标：

- 基于 validator/lint issues 输出可执行修复建议。
- 先提供建议，不自动改写 Skill 文件。

建议范围：

- 新增 `RepairSuggestion` 模型。
- 将 issue code 映射为修复建议。
- `validate` 和 `create` 输出建议。
- 支持机器可读结构，后续可接入 `repair` 命令。

不包含：

- 不自动修改文件。
- 不调用 LLM 生成建议。
- 不处理复杂语义重写。

用户可见行为：

```text
Warnings:
- description is too broad

Suggested fixes:
- Narrow the description to one trigger condition and one excluded scenario.
```

验收标准：

1. 每个新增 lint issue 至少有一个建议。
2. error 和 warning 的建议分开展示。
3. 建议文本稳定可测。
4. 无 issue 时不展示空建议区块。

主要影响文件：

- `src/skill_forge/models/quality.py`
- `src/skill_forge/validator/`
- `src/skill_forge/cli.py`
- `tests/test_generation_quality_report.py`

风险：

- 建议如果太泛，会降低可信度。
- 后续自动修复前需要更严格的可逆设计。

进展记录：

- 2026-05-26: Created OpenSpec artifacts at `openspec/changes/add-deterministic-repair-suggestions/`: `proposal.md`, `design.md`, delta specs for `skill-validation` and `generation-quality-report`, and `tasks.md`.
- 2026-05-26: Implemented structured `RepairSuggestion` output, deterministic issue-code mappings for current validation errors and lint warnings, fallback suggestions for unknown codes, and suggestions on `GenerationQualityReport`.
- 2026-05-26: Updated `validate` and non-interactive `create` output to display suggested fixes only when validation issues exist.
- 2026-05-26: Added quality report and CLI tests for warning suggestions, error suggestions, clean omission, deduplication, and fallback behavior.
- 2026-05-26: Verified with focused quality/CLI tests, `uv run pytest`, `openspec validate "add-deterministic-repair-suggestions" --strict`, and `openspec validate --all --strict`.
- 2026-05-26: Archived via `openspec archive "add-deterministic-repair-suggestions" --yes`; synced `skill-validation` and `generation-quality-report` specs and archived the change as `openspec/changes/archive/2026-05-25-add-deterministic-repair-suggestions/`.
- Remaining: none.

### 5. `add-skill-eval-cases`

状态：`Archived`

目标：

- 引入本地 eval case，用样例任务验证 Skill 的静态输出约束和预期行为。
- 第一版不执行真实 Agent，只做确定性 case 检查。

建议 eval case 格式：

```yaml
id: code-review-basic
skill: team-code-review
input:
  request: "Review this Python diff for correctness and tests."
assertions:
  required_sections:
    - Findings
    - Tests
  forbidden_phrases:
    - "looks good"
  required_constraints:
    - "Findings first"
```

建议范围：

- `skill-forge eval <skill-name> --case <file>`。
- 读取 eval YAML。
- 检查 Skill 是否包含必要章节、约束、输出格式和禁用模式。
- 输出 eval report。
- 支持批量 case 目录。

不包含：

- 不调用真实 Agent。
- 不执行代码。
- 不做远程 eval 服务。

用户可见行为：

```bash
skill-forge eval team-code-review --case evals/code-review-basic.yaml
skill-forge eval team-code-review --cases evals/
```

验收标准：

1. 单个 eval case 可以执行并输出 pass/fail。
2. 批量 eval 可以输出汇总。
3. eval failure 有具体 assertion message。
4. `show` 可展示最近 eval 摘要，前提是 metadata 已存在。
5. 测试覆盖 pass、fail、非法 case 和缺失 Skill。

主要影响文件：

- `src/skill_forge/evals/`
- `src/skill_forge/models/`
- `src/skill_forge/cli.py`
- `tests/test_skill_evals.py`
- `openspec/specs/skill-evaluation/spec.md`

风险：

- 静态 eval 不能完全代表 Agent 执行效果。
- case 语法过复杂会增加维护成本。

进展记录：

- 2026-05-27: Created OpenSpec artifacts at `openspec/changes/add-skill-eval-cases/`: `proposal.md`, `design.md`, delta specs for `skill-evaluation` and `skill-library-management`, and `tasks.md`.
- 2026-05-27: Implemented deterministic YAML eval case models, single-case and batch loading, static section/constraint/forbidden-phrase assertions, latest `eval-report.json` persistence, `skill-forge eval`, and `show` eval summary display.
- 2026-05-27: Added eval loader/evaluator tests, CLI tests for single-case, batch, failed eval, and missing Skill behavior, plus library/show eval summary tests.
- 2026-05-27: Verified with `uv run pytest tests/test_skill_evals.py tests/test_skill_library.py tests/test_cli.py`, `uv run pytest`, `openspec validate "add-skill-eval-cases" --strict`, and `openspec validate --all --strict`.
- 2026-05-27: Archived via `openspec archive "add-skill-eval-cases" --yes`; synced new `skill-evaluation` spec and modified `skill-library-management` spec, archived as `openspec/changes/archive/2026-05-27-add-skill-eval-cases/`.
- Remaining: none.

### 6. `add-skill-upgrade-workflow`

状态：`Archived`

目标：

- 基于蓝图、metadata 和 lint 结果升级已有 Skill。
- 支持生成新版本并与旧版本比较。

建议范围：

- `skill-forge upgrade <skill-name>`。
- 根据 metadata 找到原 blueprint。
- 使用最新 blueprint 重新合并 requirement。
- 输出新 Skill 到独立目录或生成 candidate。
- 自动运行 validate/lint。
- 展示 old/new diff 和质量分变化。

不包含：

- 不自动覆盖旧 Skill。
- 不做远程同步。
- 不处理没有 metadata 的复杂迁移；可给出 fallback 提示。

用户可见行为：

```bash
skill-forge upgrade team-code-review
skill-forge diff team-code-review team-code-review-upgraded
```

验收标准：

1. 有 metadata 的 Skill 可以生成 upgrade candidate。
2. 无 metadata 的旧 Skill 给出清晰错误或降级提示。
3. candidate 不覆盖原 Skill。
4. 输出 old/new quality score。
5. 测试覆盖成功升级、缺失 blueprint、缺失 metadata 和已有 candidate。

主要影响文件：

- `src/skill_forge/library/manager.py`
- `src/skill_forge/generator/`
- `src/skill_forge/cli.py`
- `tests/test_skill_upgrade.py`

风险：

- 蓝图变化可能改变用户手工编辑内容。
- 需要明确哪些字段来自用户、蓝图、项目上下文。

进展记录：

- 2026-05-27: Created OpenSpec artifacts at `openspec/changes/add-skill-upgrade-workflow/`: `proposal.md`, `design.md`, delta specs for `skill-upgrade-workflow` and `skill-library-management`, and `tasks.md`.
- 2026-05-27: Implemented `SkillUpgradeService`, provenance-backed requirement reconstruction, current recorded blueprint reapplication, candidate package naming, overwrite protection with `--force`, candidate validation, candidate provenance persistence, and `skill-forge upgrade`.
- 2026-05-27: Added service and CLI tests for successful upgrades, source preservation, custom candidate names, missing provenance, missing blueprint, existing candidate failures, `--force`, and library list/show/diff behavior for candidates.
- 2026-05-27: Updated README and README.zh-CN with the new `upgrade` command and candidate comparison flow.
- 2026-05-27: Verified with `uv run pytest tests/test_skill_upgrade.py tests/test_cli.py tests/test_skill_library.py`, `uv run pytest`, `openspec validate "add-skill-upgrade-workflow" --strict`, and `openspec validate --all --strict`.
- 2026-05-27: Archived via `openspec archive "add-skill-upgrade-workflow" --yes`; synced new `skill-upgrade-workflow` spec and modified `skill-library-management` spec, archived as `openspec/changes/archive/2026-05-27-add-skill-upgrade-workflow/`.
- Remaining: none.

### 7. `improve-research-source-quality`

状态：`Archived`

目标：

- 增强 `update` 和 `search` 的资料源质量解释能力。
- 让用户知道结果为什么被推荐、资料是否新鲜、失败是否可重试。

建议范围：

- source freshness 状态。
- 单源失败重试建议。
- search score breakdown 展示。
- update 报告区分 updated/skipped/failed/disabled/partial。
- 可选 `--explain` 展示评分分解。

不包含：

- 不引入向量数据库。
- 不改变生成主链路。
- 不自动启用社区源。

用户可见行为：

```bash
skill-forge update
skill-forge search "code review" --explain
```

验收标准：

1. search 结果能解释 authority、relevance、freshness、platform boost。
2. update 对 partial failure 有清晰摘要。
3. 空资料库提示下一步动作。
4. 测试覆盖评分解释和失败报告。

主要影响文件：

- `src/skill_forge/research/updater.py`
- `src/skill_forge/retrieval/ranker.py`
- `src/skill_forge/cli.py`
- `tests/test_research_update.py`
- `tests/test_search_retrieval.py`

风险：

- 解释过多会让 CLI 输出变噪。
- 评分分解需要和实际排序保持一致。

进展记录：

- 2026-05-27: Created OpenSpec artifacts at `openspec/changes/improve-research-source-quality/`: `proposal.md`, `design.md`, delta specs for `research-corpus-update` and `search-retrieval`, and `tasks.md`.
- 2026-05-27: Implemented update result status helpers for disabled counts and partial failures, retry guidance for failed source rows, enhanced `skill-forge update` summaries, `skill-forge search --explain`, and stable score component explanations.
- 2026-05-27: Added update tests for disabled counts, partial status, and retry guidance; added search tests for explain output, platform boost visibility, and compact default output.
- 2026-05-27: Updated README and README.zh-CN with update summary behavior and `search --explain` examples.
- 2026-05-27: Verified with `uv run pytest tests/test_research_update.py tests/test_search_retrieval.py`, `uv run pytest`, `openspec validate "improve-research-source-quality" --strict`, and `openspec validate --all --strict`.
- 2026-05-27: Archived via `openspec archive "improve-research-source-quality" --yes`; synced modified `research-corpus-update` and `search-retrieval` specs, archived as `openspec/changes/archive/2026-05-27-improve-research-source-quality/`.
- Remaining: none.

### 8. `add-optional-retrieval-rerank`

状态：`Archived`

目标：

- 在保持 TF-IDF 默认路径的前提下，增加可选语义检索或 rerank。

建议范围：

- 配置项控制是否启用。
- 保留当前 TF-IDF 作为默认和 fallback。
- 可插拔 reranker 接口。
- search 输出标识检索模式。

不包含：

- 不强制下载 embedding 模型。
- 不默认联网。
- 不让 create 依赖 rerank。

用户可见行为：

```bash
skill-forge search "skill creator" --rerank
```

验收标准：

1. 默认 search 行为不变。
2. 启用 rerank 后结果仍可离线或有清晰配置错误。
3. rerank 失败能回退或清晰退出。
4. 测试覆盖默认路径、启用路径和失败路径。

主要影响文件：

- `src/skill_forge/retrieval/`
- `src/skill_forge/config.py`
- `src/skill_forge/cli.py`
- `tests/test_search_retrieval.py`

风险：

- 依赖过重会破坏本地优先原则。
- 语义检索如果没有解释能力，会降低可调试性。

进展记录：

- 2026-05-27: Created OpenSpec artifacts at `openspec/changes/add-optional-retrieval-rerank/`: `proposal.md`, `design.md`, delta specs for `search-retrieval` and `cli-foundation`, and `tasks.md`.
- 2026-05-27: Implemented retrieval rerank config controls, search result rerank metadata, a pluggable reranker interface, the offline lexical reranker, bounded rerank candidate fetching, fallback to TF-IDF on disabled or failed rerank, `skill-forge search --rerank`, and retrieval mode display.
- 2026-05-27: Added config tests for rerank defaults and overrides, retrieval tests for default order, reranked order, and fallback behavior, plus CLI tests for explicit rerank, config-enabled rerank, disabled rerank, and unsupported provider fallback.
- 2026-05-27: Updated README and README.zh-CN with `search --rerank` examples and rerank configuration fields.
- 2026-05-27: Verified with `uv run pytest tests/test_config.py tests/test_search_retrieval.py`, `uv run pytest`, `openspec validate "add-optional-retrieval-rerank" --strict`, and `openspec validate --all --strict`.
- 2026-05-27: Archived via `openspec archive "add-optional-retrieval-rerank" --yes`; synced modified `search-retrieval` and `cli-foundation` specs, archived as `openspec/changes/archive/2026-05-27-add-optional-retrieval-rerank/`.
- Remaining: none.

## 9. 推荐实施顺序

第一批应连续完成：

```text
add-user-custom-blueprints
  -> add-generation-provenance-metadata
  -> add-skill-authoring-lint-rules
```

理由：

1. 自定义蓝图解决定制标准输出。
2. metadata 解决可追溯和后续升级基础。
3. lint 解决标准质量可检查。

第二批：

```text
add-deterministic-repair-suggestions
  -> add-skill-eval-cases
```

理由：

1. 修复建议提升生成质量闭环。
2. eval case 开始验证 Skill 是否满足典型任务。

第三批：

```text
add-skill-upgrade-workflow
  -> improve-research-source-quality
  -> add-optional-retrieval-rerank
```

理由：

1. upgrade 依赖前面的定制、metadata 和 lint。
2. 资料库质量和 rerank 是增强参考资料质量，不应阻塞核心 Skill 工厂能力。

## 10. 文档维护要求

每完成一个 change 后，应检查并更新：

1. 本文档的 Change 总览状态和对应进展记录。
2. `docs/skill_generation_roadmap.md` 的下一阶段入口。
3. `README.md` 和 `README.zh-CN.md` 的用户可见命令。
4. 对应 `openspec/specs/` 主规格。
5. 如有命令变化，补充 CLI 示例和测试命令。

如果文档冲突，以当前 CLI 行为、已归档 OpenSpec specs 和测试为优先事实源。
