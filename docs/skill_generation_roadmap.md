# Skill Forge 快速生成能力路线图与任务跟踪

本文档用于跟踪 Skill Forge 从“基础 Skill 生成框架”演进到“快速生成高质量 Skills”的整体需求、阶段拆分、OpenSpec change 规划和实施进展。

它不是某一个 change 的详细设计，而是后续创建 change 时的上游需求设计文档。每个 change 应从本文档中选择一个边界清晰、可独立验收的能力切片。

## 1. 背景

当前项目已经具备基础闭环：

```text
init
  ↓
create
  ↓
validate
  ↓
install
```

并已具备以下增强能力：

```text
interactive drafts
project context injection
research corpus update
local search/retrieval
```

但当前 `create` 本质上仍是：

```text
用户自然语言
  ↓
规则解析
  ↓
通用模板渲染
  ↓
生成 SKILL.md
```

这可以生成可用 Skill，但还不能稳定快速地产出“针对具体任务类型优化过”的高质量 Skill。

## 2. 总目标

将 Skill Forge 演进为一个快速生成高质量 Agent Skills 的本地工作台。

目标形态：

```text
用户需求 / 项目上下文 / 目标平台
  ↓
任务类型识别或显式蓝图选择
  ↓
Skill 蓝图装配
  ↓
生成 SKILL.md + 可选 references/assets/scripts
  ↓
校验与质量报告
  ↓
安装到目标 Agent 平台
```

## 3. 设计原则

1. 每个 OpenSpec change 必须小而可验收。
2. 优先稳定的确定性能力，再引入 LLM 增强。
3. `create` 必须保留无蓝图时的兼容回退路径。
4. 蓝图能力应先可加载、可校验、可展示，再接入生成流程。
5. 内置蓝图数量应逐步增加，不一次性追求覆盖所有场景。
6. 生成质量要通过 validator、quality report 和测试闭环保障。
7. 附加文件生成、质量评分、LLM 增强应作为独立阶段，不混入蓝图基础设施。

## 4. 能力分层

```text
Layer 5: LLM assisted refinement
Layer 4: quality report / repair suggestions
Layer 3: references / assets / scripts generation
Layer 2: blueprint-backed create
Layer 1: blueprint model / loader / validation
Layer 0: existing deterministic create / validate / install
```

当前项目位于 Layer 0，下一阶段应从 Layer 1 开始。

## 5. 推荐 Change 拆分

```text
add-blueprint-data-model
        ↓
add-blueprint-backed-generation
        ↓
add-built-in-blueprints
        ↓
add-blueprint-selection-cli
        ↓
add-blueprint-reference-assets
        ↓
add-generation-quality-report
        ↓
add-llm-assisted-generation
        ↓
add-skill-library-management
```

## 6. Change 总览

| 顺序 | Change ID | 状态 | 目标 | 不包含 |
|---:|---|---|---|---|
| 1 | `add-blueprint-data-model` | Archived | 定义 Skill 蓝图模型、文件格式、加载器、校验和展示命令 | 不改 `create` 生成逻辑 |
| 2 | `add-blueprint-backed-generation` | Archived | 让 `create` 能根据 task_type 使用蓝图填充结构化需求 | 不增加大量内置蓝图 |
| 3 | `add-built-in-blueprints` | Archived | 增加高价值内置蓝图并完善识别规则 | 不改蓝图基础架构 |
| 4 | `add-blueprint-selection-cli` | Archived | 支持用户显式选择蓝图 | 不做交互式蓝图编辑 |
| 5 | `add-blueprint-reference-assets` | Archived | 允许蓝图声明并生成 references/assets/scripts | 不做质量评分 |
| 6 | `add-generation-quality-report` | Archived | 生成后自动校验并输出质量报告 | 不做自动修复 |
| 7 | `add-llm-assisted-generation` | Archived | 可选 LLM 增强需求解析、润色和修复建议 | 不让基础生成依赖 LLM |
| 8 | `add-skill-library-management` | Archived | 管理生成过的 Skill，支持 list/show/diff 等 | 不改变生成质量逻辑 |

状态建议值：

- `Not started`
- `Proposed`
- `Implementing`
- `Implemented`
- `Verified`
- `Archived`
- `Blocked`

## 7. Change 详情模板

后续每创建一个 change，可复制本节结构补充到对应 change 小节。

```markdown
### N. `<change-id>`

状态：`Archived`

目标：

- ...

范围：

- ...

不包含：

- ...

用户可见行为：

```bash
skill-forge ...
```

验收标准：

1. ...
2. ...
3. ...

主要影响文件：

- `src/skill_forge/...`
- `tests/...`
- `openspec/specs/...`

风险：

- ...

进展记录：

- YYYY-MM-DD: Created proposal/design/spec/tasks.
- YYYY-MM-DD: Implemented ...
- YYYY-MM-DD: Verified with ...
- Remaining: ...
```

## 8. Change 详情

### 1. `add-blueprint-data-model`

状态：`Archived`

目标：

- 引入 `SkillBlueprint` 概念。
- 定义蓝图配置文件格式。
- 实现蓝图加载器。
- 实现蓝图静态校验。
- 提供 CLI 展示蓝图能力。

范围：

- 新增蓝图数据模型。
- 新增内置蓝图目录。
- 新增蓝图加载与校验逻辑。
- 新增 `skill-forge blueprints list`。
- 新增 `skill-forge blueprints show <blueprint-id>`。
- 为蓝图加载、校验、CLI 展示补充测试。

不包含：

- 不修改 `skill-forge create` 的生成逻辑。
- 不生成 references/assets/scripts。
- 不引入 LLM。
- 不做质量评分。
- 不一次性增加大量蓝图。

建议最小蓝图：

```yaml
id: bug-investigation
name: Bug Investigation
description: Generate skills for diagnosing bugs from symptoms, logs, stack traces, and source evidence.
task_type: bug-investigation
when_to_use:
  - The user needs to investigate a defect or runtime failure.
when_not_to_use:
  - The user is asking for new feature design.
required_inputs:
  - Symptoms, logs, stack traces, or reproduction steps.
workflow:
  - Collect symptoms and evidence.
  - Identify likely code paths.
  - Build an evidence-backed root-cause chain.
  - Propose a focused fix and test plan.
expected_outputs:
  - Symptom
  - Evidence
  - Root Cause
  - Fix Plan
  - Test Plan
  - Risks
quality_gates:
  - Root cause must be supported by evidence.
  - Fix plan must remain focused and testable.
```

用户可见行为：

```bash
skill-forge blueprints list
skill-forge blueprints show bug-investigation
```

验收标准：

1. 能列出内置蓝图。
2. 能展示指定蓝图详情。
3. 无效蓝图能被校验器拒绝，并给出清晰错误。
4. 不影响现有 `create`、`validate`、`install` 行为。
5. `uv run pytest` 通过。

主要影响文件：

- `src/skill_forge/blueprints/`
- `src/skill_forge/models/blueprint.py`
- `configs/blueprints/` 或 `templates/blueprints/`
- `src/skill_forge/cli.py`
- `tests/test_blueprints.py`

风险：

- 蓝图格式过早复杂化。
- CLI 命令层级设计过重。
- 蓝图模型和现有 `SkillRequirement` 字段重复但语义不清。

设计建议：

- 第一版蓝图字段尽量贴近 `SkillRequirement`。
- 不引入继承、组合、变量表达式等复杂能力。
- 蓝图 ID 使用稳定 slug，例如 `bug-investigation`。

进展记录：

- 2026-05-24: Created OpenSpec artifacts at `openspec/changes/add-blueprint-data-model/`: `proposal.md`, `design.md`, `specs/skill-blueprints/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented `SkillBlueprint`, built-in blueprint YAML loading, duplicate/validation/not-found errors, and `skill-forge blueprints list/show`.
- 2026-05-24: Verified with `uv run pytest`, `uv run skill-forge blueprints list`, `uv run skill-forge blueprints show bug-investigation`, and `openspec validate "add-blueprint-data-model" --strict`.
- 2026-05-24: Archived via `openspec archive "add-blueprint-data-model" --yes`; synced new `skill-blueprints` spec to `openspec/specs/skill-blueprints/spec.md`.
- Remaining: none.

### 2. `add-blueprint-backed-generation`

状态：`Archived`

目标：

- 将蓝图接入 `create`。
- 当 `RequirementAnalyzer` 识别出 `task_type` 时，优先使用匹配蓝图补齐 workflow、outputs、quality gates 等字段。
- 没有匹配蓝图时，回退到现有通用生成逻辑。

范围：

- 蓝图匹配服务。
- `SkillRequirement` 与 `SkillBlueprint` 合并策略。
- 生成流程接入。
- 保持现有 CLI 参数兼容。
- 测试自动匹配和回退路径。

不包含：

- 不增加大量新蓝图。
- 不增加 `--blueprint` 参数。
- 不生成附加文件。
- 不做质量评分。

用户可见行为：

```bash
skill-forge create "Java bug 定位 skill"
```

验收标准：

1. Java bug 类需求自动使用 `bug-investigation` 蓝图。
2. 未识别需求仍走当前通用生成逻辑。
3. 用户输入中显式约束优先于蓝图默认值。
4. 项目上下文约束仍能注入。
5. 现有测试全部通过。

主要影响文件：

- `src/skill_forge/requirement/analyzer.py`
- `src/skill_forge/generator/skill_generator.py`
- `src/skill_forge/blueprints/`
- `tests/test_skill_generator.py`
- `tests/test_cli.py`

风险：

- 蓝图默认值覆盖用户明确需求。
- 合并逻辑导致重复 constraints。
- 生成结果变动影响已有测试。

进展记录：

- 2026-05-24: Created OpenSpec artifacts at `openspec/changes/add-blueprint-backed-generation/`: `proposal.md`, `design.md`, `specs/local-skill-generation/spec.md`, `specs/skill-blueprints/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented blueprint task-type matching, `SkillRequirement` enrichment, non-duplicate list merging, and `create` integration before project context enrichment.
- 2026-05-24: Verified with `uv run pytest`, focused blueprint/create/project-context tests, and `openspec validate "add-blueprint-backed-generation" --strict`.
- 2026-05-24: Archived via `openspec archive "add-blueprint-backed-generation" --yes`; synced modified `local-skill-generation` and `skill-blueprints` specs.
- Remaining: none.

### 3. `add-built-in-blueprints`

状态：`Archived`

目标：

- 增加第一批高价值内置蓝图。
- 扩展确定性任务识别规则。

建议第一批蓝图：

- `bug-investigation`
- `code-review`
- `test-generation`
- `openspec-change`

范围：

- 新增蓝图文件。
- 增强关键词识别。
- 为每个蓝图补充 CLI 展示测试和生成测试。

不包含：

- 不修改蓝图文件格式。
- 不增加 references/assets/scripts。
- 不引入 LLM。

验收标准：

1. 每个蓝图都能 list/show。
2. 每个蓝图都有至少一个自然语言输入触发样例。
3. 每个蓝图生成的 Skill 有明确任务边界、workflow 和 quality gates。
4. 生成内容不是通用模板的简单换名。

风险：

- 蓝图内容泛化，无法体现任务差异。
- 关键词识别误判。

进展记录：

- 2026-05-24: Created OpenSpec artifacts at `openspec/changes/add-built-in-blueprints/`: `proposal.md`, `design.md`, `specs/skill-blueprints/spec.md`, `specs/local-skill-generation/spec.md`, and `tasks.md`.
- 2026-05-24: Added built-in `code-review`, `test-generation`, and `openspec-change` blueprint YAML files while preserving `bug-investigation`.
- 2026-05-24: Extended `RequirementAnalyzer` to classify code review, test generation, and OpenSpec change requests for blueprint-backed generation.
- 2026-05-24: Verified with `uv run pytest`, `uv run skill-forge blueprints list`, and `openspec validate "add-built-in-blueprints" --strict`.
- 2026-05-24: Archived via `openspec archive "add-built-in-blueprints" --yes`; synced modified `skill-blueprints` and `local-skill-generation` specs.
- Remaining: none.

### 4. `add-blueprint-selection-cli`

状态：`Archived`

目标：

- 支持用户显式指定蓝图，降低自动识别失败带来的不确定性。

范围：

- `skill-forge create "<requirement>" --blueprint <blueprint-id>`。
- 蓝图不存在时给出清晰错误。
- 显式蓝图优先于自动识别。
- 测试显式选择、错误处理和回退行为。

不包含：

- 不做交互式蓝图选择器。
- 不做蓝图编辑命令。
- 不生成附加文件。

用户可见行为：

```bash
skill-forge create "Python 服务 review" --blueprint code-review
```

验收标准：

1. 指定蓝图时使用该蓝图。
2. 指定不存在蓝图时返回非零退出码。
3. 未指定蓝图时保持自动匹配或回退逻辑。

进展记录：

- 2026-05-24: Created OpenSpec artifacts at `openspec/changes/add-blueprint-selection-cli/`: `proposal.md`, `design.md`, `specs/local-skill-generation/spec.md`, `specs/skill-blueprints/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented `skill-forge create --blueprint <blueprint-id>`, explicit blueprint enrichment, override behavior, and missing-blueprint CLI errors.
- 2026-05-24: Verified with `uv run pytest`, `uv run skill-forge create "Python 服务 review" --blueprint code-review --home <temp-home>`, and `openspec validate "add-blueprint-selection-cli" --strict`.
- 2026-05-24: Archived via `openspec archive "add-blueprint-selection-cli" --yes`; synced modified `local-skill-generation` and `skill-blueprints` specs.
- Remaining: none.

### 5. `add-blueprint-reference-assets`

状态：`Archived`

目标：

- 让蓝图可以声明生成附加文件。
- Skill 包从单文件逐步演进为结构化包。

范围：

- 蓝图新增 references/assets/scripts 声明。
- 渲染附加模板。
- 输出路径安全校验。
- Validator 识别附加文件存在性。

不包含：

- 不做质量评分。
- 不做 LLM 生成附加内容。

用户可见输出示例：

```text
bug-investigation/
├── SKILL.md
└── references/
    └── diagnosis-checklist.md
```

验收标准：

1. 蓝图可声明一个 reference 文件。
2. 生成器能输出该文件。
3. 输出路径不能逃逸 Skill 包目录。
4. 没有附加文件声明的蓝图仍只生成 `SKILL.md`。

进展记录：

- 2026-05-24: Created OpenSpec artifacts at `openspec/changes/add-blueprint-reference-assets/`: `proposal.md`, `design.md`, `specs/skill-blueprints/spec.md`, `specs/local-skill-generation/spec.md`, `specs/skill-validation/spec.md`, and `tasks.md`.
- 2026-05-24: Added blueprint generated-file declarations for references/assets/scripts with safe relative path validation.
- 2026-05-24: Implemented generator support for writing blueprint-declared files and package metadata, including `bug-investigation` reference checklist generation.
- 2026-05-24: Added optional validator checks for unsafe attachment path metadata.
- 2026-05-24: Verified with `uv run pytest`, `uv run skill-forge create "Java 存量代码 bug 定位 skill" --home <temp-home>`, generated reference inspection, and `openspec validate "add-blueprint-reference-assets" --strict`.
- 2026-05-24: Archived via `openspec archive "add-blueprint-reference-assets" --yes`; synced modified `skill-blueprints`, `local-skill-generation`, and `skill-validation` specs.
- Remaining: none.

### 6. `add-generation-quality-report`

状态：`Archived`

目标：

- 在生成后自动运行校验并输出质量报告。

范围：

- `create` 完成后调用 validator。
- 展示 errors、warnings 和建议动作。
- 增加确定性质量评分。

不包含：

- 不做自动修复。
- 不引入 LLM。

用户可见行为：

```text
Skill package generated
Quality: 86/100
Warnings:
- description could be more specific
Next:
- validate
- install
```

验收标准：

1. 生成后自动显示校验摘要。
2. 分数计算稳定可测。
3. 有 warning 时不影响生成成功。
4. 有 error 时返回清晰失败信息。

进展记录：

- 2026-05-24: Created OpenSpec artifacts at `openspec/changes/add-generation-quality-report/`: `proposal.md`, `design.md`, `specs/generation-quality-report/spec.md`, `specs/local-skill-generation/spec.md`, `specs/skill-validation/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented deterministic `GenerationQualityReport` scoring from validation results.
- 2026-05-24: Integrated post-generation validation into non-interactive `skill-forge create`, including generated attachment metadata, quality score output, warnings, errors, and next actions.
- 2026-05-24: Verified with `uv run pytest`, `uv run skill-forge create "Java 存量代码 bug 定位 skill" --home E:\tmp\skill-forge-quality-report-demo`, and `openspec validate "add-generation-quality-report" --strict`.
- 2026-05-24: Archived via `openspec archive "add-generation-quality-report" --yes`; synced new `generation-quality-report` spec and modified `local-skill-generation` and `skill-validation` specs.
- Remaining: none.

### 7. `add-llm-assisted-generation`

状态：`Archived`

目标：

- 在不破坏本地确定性生成的基础上，引入可选 LLM 增强。

范围：

- `--llm` 可选参数。
- LLM 辅助结构化需求解析。
- LLM 辅助润色 workflow、description、constraints。
- LLM 辅助修复 validator warning。

不包含：

- 不让默认 `create` 依赖网络或 LLM。
- 不绕过 validator。
- 不保存敏感项目上下文到远端。

验收标准：

1. 未传 `--llm` 时完全保持本地生成。
2. 传 `--llm` 时能增强生成内容。
3. LLM 输出必须经过 validator。
4. 网络或 LLM 失败时有清晰错误或回退策略。

进展记录：

- 2026-05-24: Created OpenSpec artifacts at `openspec/changes/add-llm-assisted-generation/`: `proposal.md`, `design.md`, `specs/llm-assisted-generation/spec.md`, `specs/local-skill-generation/spec.md`, `specs/generation-quality-report/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented optional `skill-forge create --llm` requirement refinement with an OpenAI-compatible provider boundary configured by `SKILL_FORGE_LLM_API_KEY`, `SKILL_FORGE_LLM_MODEL`, and optional `SKILL_FORGE_LLM_BASE_URL`.
- 2026-05-24: Added structured JSON response parsing, supported-field merging, unknown-field ignoring, malformed-response errors, and missing-configuration errors.
- 2026-05-24: Verified with `uv run pytest`, `uv run skill-forge create "整理团队发布流程 skill" --llm --home E:\tmp\skill-forge-llm-missing-config-demo`, `openspec validate "add-llm-assisted-generation" --strict`, and `openspec validate --all --strict`.
- 2026-05-24: Archived via `openspec archive "add-llm-assisted-generation" --yes`; synced new `llm-assisted-generation` spec and modified `local-skill-generation` and `generation-quality-report` specs.
- Remaining: none.

### 8. `add-skill-library-management`

状态：`Archived`

目标：

- 管理本地生成过的 Skill。

范围：

- `skill-forge list`
- `skill-forge show <skill-name>`
- `skill-forge diff <skill-a> <skill-b>`
- 可选：记录生成来源、蓝图、时间和质量分。

不包含：

- 不做远程市场。
- 不做自动升级。

验收标准：

1. 能列出本地 output 下的 Skill。
2. 能展示 Skill 元数据。
3. 能比较两个 Skill 的 `SKILL.md` 差异。

进展记录：

- 2026-05-24: Created OpenSpec artifacts at `openspec/changes/add-skill-library-management/`: `proposal.md`, `design.md`, `specs/skill-library-management/spec.md`, `specs/local-skill-generation/spec.md`, and `tasks.md`.
- 2026-05-24: Implemented filesystem-backed generated Skill library discovery, metadata extraction from `SKILL.md` frontmatter, attachment counts, and unified `SKILL.md` diffing.
- 2026-05-24: Added `skill-forge list`, `skill-forge show <skill-name>`, and `skill-forge diff <skill-a> <skill-b>` with `--home` support and missing-package errors.
- 2026-05-24: Verified with `uv run pytest`, `uv run skill-forge create "Java 存量代码 bug 定位 skill" --home E:\tmp\skill-forge-library-demo`, `uv run skill-forge list --home E:\tmp\skill-forge-library-demo`, `uv run skill-forge show java-bug-investigation --home E:\tmp\skill-forge-library-demo`, `openspec validate "add-skill-library-management" --strict`, and `openspec validate --all --strict`.
- 2026-05-24: Archived via `openspec archive "add-skill-library-management" --yes`; synced new `skill-library-management` spec and modified `local-skill-generation` spec.
- Remaining: none.

## 9. 后续使用方式

创建新 change 前：

1. 从本文档选择一个 `Not started` change。
2. 检查其范围和不包含项是否仍合理。
3. 创建 OpenSpec proposal/design/spec/tasks。
4. 如发现范围过大，先回到本文档拆分。

实现过程中：

1. 只完成当前 change 的范围。
2. 不把后续 change 的内容提前塞入当前实现。
3. 每完成一个关键节点，更新本文档中的状态和进展记录。

归档 change 后：

1. 将状态改为 `Archived`。
2. 补充验证命令。
3. 记录主要产物和遗留问题。

## 10. 当前推荐下一步

原路线图中的 8 个推荐 change 均已完成并归档：

```text
add-blueprint-data-model
add-blueprint-backed-generation
add-built-in-blueprints
add-blueprint-selection-cli
add-blueprint-reference-assets
add-generation-quality-report
add-llm-assisted-generation
add-skill-library-management
```

理由：

1. 路线图中推荐的 8 个 change 均已完成并归档。
2. 当前能力链路已覆盖蓝图、附加文件、质量报告、可选 LLM 增强和本地库管理。
3. 后续演进应从新的候选方向中选择边界清晰的能力切片，再创建 OpenSpec change。

## 11. 下一阶段候选方向

以下方向尚未进入具体 change，创建前应先确认范围和验收标准：

1. 生成后自动修复建议：基于 validator 和 quality report 给出确定性修复建议，必要时再接入 LLM。
2. 用户自定义蓝图目录：允许用户在配置目录中维护私有蓝图，并与内置蓝图统一 list/show/create。
3. Skill 生成元数据：记录生成时间、使用蓝图、是否启用 LLM、项目上下文路径、质量分和附件清单。
4. Skill 升级与版本迁移：在已有 `list/show/diff` 基础上增加 `upgrade` 或历史版本管理能力。
5. 资料库质量增强：补充 source freshness、失败重试、来源评分解释和更清晰的 update 报告。
6. 检索增强：在保持 TF-IDF 默认路径的前提下，探索可选向量检索或 rerank。
7. Web UI：在 CLI 能力稳定后，考虑为可视化编辑和比较 Skill 提供界面。

## 12. 文档维护说明

每个 OpenSpec change 归档后，应检查并按需更新：

1. `README.md` 和 `README.zh-CN.md`：用户可见命令、当前范围、配置和示例。
2. `docs/skill_generation_roadmap.md`：change 状态、验证命令、遗留问题和下一阶段建议。
3. `docs/skill_forge_design_doc.md`：长期设计文档中与当前能力冲突的命令或范围描述。
4. `openspec/specs/`：归档后的主规格 Purpose 和 requirement 是否仍可作为事实来源。

如果 README、roadmap、CLI help 或主规格之间出现冲突，以当前 CLI 行为和已归档主规格为优先事实源，再同步其他文档。

## 13. 下一阶段路线图

原路线图中的基础生成、蓝图生成、质量报告、LLM 增强、本地库管理和社区 Skill 发现能力已经完成。下一阶段不再继续在本文档中追加大段 change 详情，避免历史路线图过长。

后续“可定制、可追溯、可评估、可升级的 Skill 工厂”演进规划统一维护在：

```text
docs/skill_forge_next_evolution_plan.md
```

该文档包含：

1. 下一阶段目标架构。
2. 按模块依赖和重要性拆分的 change backlog。
3. 每个 change 的范围、不包含项、验收标准和风险。
4. process 跟踪规则和进展记录模板。

进展：

- 2026-05-26: 下一阶段第一个 change `add-user-custom-blueprints` 已完成并归档，详细进展记录见 `docs/skill_forge_next_evolution_plan.md`。
- 2026-05-26: 下一阶段第二个 change `add-generation-provenance-metadata` 已完成并归档，详细进展记录见 `docs/skill_forge_next_evolution_plan.md`。
- 2026-05-26: 下一阶段第三个 change `add-skill-authoring-lint-rules` 已完成并归档，详细进展记录见 `docs/skill_forge_next_evolution_plan.md`。
- 2026-05-26: 下一阶段第四个 change `add-deterministic-repair-suggestions` 已完成并归档，详细进展记录见 `docs/skill_forge_next_evolution_plan.md`。
- 2026-05-27: 下一阶段第五个 change `add-skill-eval-cases` 已完成并归档，详细进展记录见 `docs/skill_forge_next_evolution_plan.md`。
- 2026-05-27: 下一阶段第六个 change `add-skill-upgrade-workflow` 已完成并归档，详细进展记录见 `docs/skill_forge_next_evolution_plan.md`。
- 2026-05-27: 下一阶段第七个 change `improve-research-source-quality` 已完成并归档，详细进展记录见 `docs/skill_forge_next_evolution_plan.md`。
- 2026-05-27: 下一阶段第八个 change `add-optional-retrieval-rerank` 已完成并归档，详细进展记录见 `docs/skill_forge_next_evolution_plan.md`。
