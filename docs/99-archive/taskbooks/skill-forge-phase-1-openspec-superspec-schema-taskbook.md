# Skill Forge Phase 1 任务书：接入 OpenSpec + SuperSpec Governance Schema

> 适用仓库：`https://github.com/zhiwuli0228/skill-forge`  
> 前置阶段：Phase 0 已完成，commit `e541b3bee1eca8795b0258ae69be028f43070d9c`  
> 阶段目标：Introduce OpenSpec + SuperSpec Governance Schema  
> 执行对象：Codex 或 Claude Code  
> 变更类型：治理 schema 接入，不涉及业务代码实现

---

## 1. Phase 0 验收结论

Phase 0 已完成治理入口建设：

- 新增 `AGENTS.md`
- 新增 `CODEX.md`
- 新增 `OPENCODE.md`
- 新增 `SUPERPOWERS.md`
- 更新 `CLAUDE.md`
- 更新 `README.md`
- 更新 `README.zh-CN.md`
- 新增 `docs/00-project/governance-bootstrap-report.md`

验证结果：

- `uv run skill-forge --help` 通过
- `uv run pytest` 通过，265 tests passed
- 禁止路径未被 Phase 0 修改
- commit SHA: `e541b3bee1eca8795b0258ae69be028f43070d9c`

---

## 2. Phase 1 目标

Phase 1 的目标是接入 OpenSpec + SuperSpec 风格治理 schema。

本阶段要完成：

1. 建立项目专用 OpenSpec schema：`skill-forge-governance`
2. 将 `openspec/config.yaml` 切换到该 schema
3. 增加 SuperSpec 风格 artifact 模板
4. 建立 OpenSpec/SuperSpec 使用说明文档
5. 记录 schema 验证和 OpenSpec 验证结果

本阶段仍然是治理变更，不允许修改业务代码。

---

## 3. 关键原则

本项目的治理分层必须保持：

```text
OpenSpec owns lifecycle.
SuperSpec-style schema owns structured change artifacts.
Superpowers owns execution discipline.
Project Harness owns Skill Forge-specific constraints.
```

解释：

- OpenSpec 负责 change 生命周期和 `/opsx:*` 工作流入口；
- SuperSpec-style schema 负责 proposal/spec/design/tasks 等结构化资产；
- Superpowers 负责 brainstorm、planning、debugging、verification 等执行纪律；
- Skill Forge Harness 负责本项目技术栈、模块边界、CLI、模板、验证、provenance 等项目约束。

---

## 4. 本阶段允许修改的文件

Phase 1 只能创建或更新以下路径：

```text
openspec/config.yaml
openspec/schemas/skill-forge-governance/README.md
openspec/schemas/skill-forge-governance/schema.yaml
openspec/schemas/skill-forge-governance/templates/brainstorm.md
openspec/schemas/skill-forge-governance/templates/proposal.md
openspec/schemas/skill-forge-governance/templates/spec.md
openspec/schemas/skill-forge-governance/templates/design.md
openspec/schemas/skill-forge-governance/templates/review.md
openspec/schemas/skill-forge-governance/templates/plan.md
openspec/schemas/skill-forge-governance/templates/tasks.md
openspec/schemas/skill-forge-governance/templates/verification.md
docs/03-openspec/change-workflow.md
docs/03-openspec/artifact-rules.md
docs/03-openspec/schema-policy.md
docs/03-openspec/proposal-guidelines.md
docs/03-openspec/spec-guidelines.md
docs/03-openspec/design-guidelines.md
docs/03-openspec/task-guidelines.md
docs/00-project/governance-schema-verification-report.md
```

如 `docs/03-openspec/` 不存在，可以创建。

---

## 5. 本阶段禁止修改的文件或目录

禁止修改：

```text
src/**
tests/**
templates/**
configs/**
pyproject.toml
uv.lock
README.md
README.zh-CN.md
AGENTS.md
CODEX.md
CLAUDE.md
OPENCODE.md
SUPERPOWERS.md
docs/00-project/governance-bootstrap-report.md
```

特别说明：

- Phase 1 不处理 `AGENT.md` 单数残留；
- Phase 1 不处理 Phase 0 之前已经存在的脏工作树；
- Phase 1 不把预存修改混入提交；
- Phase 1 不修改业务代码；
- Phase 1 不调整依赖；
- Phase 1 不修改现有 Skill 生成模板。

---

## 6. 脏工作树控制要求

执行前必须先记录：

```bash
git status --short
git diff --name-only
```

如果工作树已有非 Phase 1 文件的预存修改：

1. 不得修改这些文件；
2. 不得 `git add .`；
3. 提交时只能显式 add Phase 1 允许路径；
4. 报告中必须列出“预存但未纳入本阶段”的文件数量和类别；
5. 不得为了清理工作树而删除或还原用户已有修改。

---

## 7. openspec/config.yaml 要求

将 `openspec/config.yaml` 更新为项目级治理配置。

必须设置：

```yaml
schema: skill-forge-governance
```

必须包含 `context`，覆盖以下信息：

- 项目名称：Skill Forge
- 定位：local-first Skill 生成、验证、搜索、升级、安装和治理工具
- 技术栈：
  - Python 3.11+
  - uv
  - Typer
  - Pydantic / pydantic-settings
  - Jinja2
  - Rich / Questionary
  - YAML
  - SQLite
  - pytest
- 核心约束：
  - local-first by default
  - deterministic generation by default
  - optional LLM refinement only when explicitly requested
  - generated Skill packages must include provenance
  - validation-first output quality
  - platform adapters must remain isolated
  - bounded and auditable project context ingestion
  - generated artifacts must not silently depend on chat history
  - backward compatibility for existing skill-forge workspaces

必须包含 `rules`，至少覆盖以下 artifact：

- brainstorm
- proposal
- spec
- design
- review
- plan
- tasks
- verification

---

## 8. schema 目录要求

创建：

```text
openspec/schemas/skill-forge-governance/
```

目录中必须包含：

```text
README.md
schema.yaml
templates/
  brainstorm.md
  proposal.md
  spec.md
  design.md
  review.md
  plan.md
  tasks.md
  verification.md
```

---

## 9. schema.yaml 要求

`schema.yaml` 必须定义 artifact 顺序：

```text
brainstorm -> proposal -> spec -> design -> review -> plan -> tasks -> verification
```

如果本地 OpenSpec schema 格式已有既定字段，必须优先遵循仓库现有 schema 格式或工具要求。

如果无法确认 schema.yaml 的精确格式：

1. 不得胡乱创造不可验证结构；
2. 应查看 `openspec/schemas/` 下已有 schema；
3. 参考已有 schema 的字段结构；
4. 在报告中记录判断依据；
5. 以能通过 `openspec schema validate` 为优先。

---

## 10. artifact 模板要求

### 10.1 brainstorm.md

必须包含：

- Problem
- Context
- Assumptions
- Options
- Risks
- Recommended Direction
- Non-goals
- Open Questions

要求：

- 不写代码；
- 至少列出两个方案，除非是纯文档小改；
- 明确假设。

---

### 10.2 proposal.md

必须包含：

- Problem
- Goal
- Scope
- Non-goals
- Affected Areas
- User-visible Impact
- Compatibility Impact
- Risks
- Rollback / Fallback
- Acceptance Criteria

要求：

- 必须区分治理变更、代码变更、模板变更、CLI 行为变更；
- 必须列出影响文件范围。

---

### 10.3 spec.md

必须包含：

- Requirements
- Scenarios
- Out of Scope
- Compatibility Notes
- Validation Expectations

要求：

- 使用 SHALL 风格；
- 至少一个场景；
- 区分 Skill Forge 内部行为与生成 Skill 包行为。

---

### 10.4 design.md

必须包含：

- Overview
- Module Boundaries
- Data Contracts
- CLI Impact
- Template Impact
- Validation Impact
- Provenance Impact
- Security / Filesystem Impact
- Compatibility
- Alternatives Considered

要求：

- 先讲边界，再讲实现；
- 涉及数据结构必须定义契约；
- 涉及文件系统必须说明安全影响。

---

### 10.5 review.md

必须包含：

- Readiness Checklist
- Scope Check
- Artifact Consistency Check
- Verification Plan Check
- Risk Check
- Decision

要求：

- 用于 implementation 前 gate；
- 发现范围不清必须阻断。

---

### 10.6 plan.md

必须包含：

- Execution Strategy
- Ordered Steps
- Expected File Changes
- Verification Steps
- Rollback Notes

要求：

- 必须适合比当前 Agent 弱很多的执行 Agent；
- 每一步必须小、清晰、可验证；
- 不允许一句话大任务。

---

### 10.7 tasks.md

必须包含：

- Task List
- Status
- Owner / Agent
- Files
- Completion Evidence
- Verification

要求：

- 文档、配置、测试、代码任务分离；
- 每个任务必须有完成证据。

---

### 10.8 verification.md

必须包含：

- Commands Executed
- Results
- Evidence Summary
- Skipped Checks
- Failure Analysis
- Remaining Risks
- Follow-up Changes

要求：

- 不允许只写“验证通过”；
- 必须记录命令和结果；
- 失败必须分类为环境问题、工具问题、代码问题或需求问题。

---

## 11. docs/03-openspec 文档要求

### 11.1 change-workflow.md

说明 Skill Forge 的变更流程：

```text
brainstorm -> proposal -> spec -> design -> review -> plan -> tasks -> implementation -> verification
```

必须说明什么情况下可以跳过 brainstorm，什么情况下不能跳过。

---

### 11.2 artifact-rules.md

说明每类 artifact 的作用、读者、必填内容和常见错误。

---

### 11.3 schema-policy.md

说明为什么使用 `skill-forge-governance` 自定义 schema，而不是直接依赖外部 schema。

必须包含：

- schema 本地版本化；
- artifact rules 与 config.yaml 对齐；
- 后续可吸收 SuperSpec/Superpowers 经验；
- 不把外部 schema 变化直接暴露给项目。

---

### 11.4 proposal-guidelines.md

说明 proposal 写法。

重点：

- scope / non-goals；
- affected areas；
- compatibility；
- rollback；
- acceptance criteria。

---

### 11.5 spec-guidelines.md

说明 spec 写法。

重点：

- SHALL；
- scenario；
- observable behavior；
- 区分内部行为和生成物行为。

---

### 11.6 design-guidelines.md

说明 design 写法。

重点：

- module boundary；
- data contract；
- CLI impact；
- template impact；
- validation impact；
- provenance impact；
- compatibility。

---

### 11.7 task-guidelines.md

说明 tasks 写法。

重点：

- 小任务；
- 可执行；
- 可验证；
- 证据；
- 禁止混合大任务。

---

## 12. 验证要求

必须执行可用命令：

```bash
git status --short
git diff --name-only
openspec schema validate
openspec validate --strict
uv run skill-forge --help
uv run pytest
```

如果 `openspec schema validate` 或 `openspec validate --strict` 因本地工具版本、命令不存在、schema 格式不支持而失败，必须在报告中记录：

- 命令；
- 退出码；
- 错误摘要；
- 是否阻塞 Phase 1；
- 需要的后续修复建议。

---

## 13. 报告要求

必须创建：

```text
docs/00-project/governance-schema-verification-report.md
```

报告必须包含：

- Phase 1 目标；
- 修改文件列表；
- 禁止路径检查；
- 脏工作树处理说明；
- schema 文件结构；
- config.yaml 更新摘要；
- 执行命令结果；
- OpenSpec schema validate 结果；
- OpenSpec strict validate 结果；
- pytest 结果；
- CLI smoke test 结果；
- skipped commands and reasons；
- remaining risks；
- Phase 2 推荐动作；
- 是否建议提交。

---

## 14. 提交要求

由于工作树存在 Phase 0 之前的预存修改，禁止使用：

```bash
git add .
```

只能显式添加 Phase 1 文件，例如：

```bash
git add openspec/config.yaml
git add openspec/schemas/skill-forge-governance
git add docs/03-openspec
git add docs/00-project/governance-schema-verification-report.md
```

建议 commit message：

```bash
git commit -m "docs: introduce openspec superspec governance schema"
```

---

# 15. 可直接复制给 Codex / Claude Code 的 Prompt

以下内容可直接复制给执行 Agent。

---

## Prompt 开始

Task: Phase 1 - Introduce OpenSpec + SuperSpec Governance Schema

Repository: https://github.com/zhiwuli0228/skill-forge

Precondition:
Phase 0 has been completed and committed as:

e541b3bee1eca8795b0258ae69be028f43070d9c

Goal:
Introduce a project-specific OpenSpec governance schema for Skill Forge with SuperSpec-style structured artifacts.

This is a governance-only change. Do not modify runtime code.

Governance model:

OpenSpec owns lifecycle.
SuperSpec-style schema owns structured change artifacts.
Superpowers owns execution discipline.
Project Harness owns Skill Forge-specific constraints.

Strict Scope:
You may create or update only:

- openspec/config.yaml
- openspec/schemas/skill-forge-governance/README.md
- openspec/schemas/skill-forge-governance/schema.yaml
- openspec/schemas/skill-forge-governance/templates/brainstorm.md
- openspec/schemas/skill-forge-governance/templates/proposal.md
- openspec/schemas/skill-forge-governance/templates/spec.md
- openspec/schemas/skill-forge-governance/templates/design.md
- openspec/schemas/skill-forge-governance/templates/review.md
- openspec/schemas/skill-forge-governance/templates/plan.md
- openspec/schemas/skill-forge-governance/templates/tasks.md
- openspec/schemas/skill-forge-governance/templates/verification.md
- docs/03-openspec/change-workflow.md
- docs/03-openspec/artifact-rules.md
- docs/03-openspec/schema-policy.md
- docs/03-openspec/proposal-guidelines.md
- docs/03-openspec/spec-guidelines.md
- docs/03-openspec/design-guidelines.md
- docs/03-openspec/task-guidelines.md
- docs/00-project/governance-schema-verification-report.md

You must not modify:

- src/**
- tests/**
- templates/**
- configs/**
- pyproject.toml
- uv.lock
- README.md
- README.zh-CN.md
- AGENTS.md
- CODEX.md
- CLAUDE.md
- OPENCODE.md
- SUPERPOWERS.md
- docs/00-project/governance-bootstrap-report.md

Important dirty worktree rule:
The repository may contain pre-existing modifications unrelated to this phase.
Do not reset them.
Do not include them in this phase.
Do not use `git add .`.
Only stage files explicitly allowed for Phase 1.

Required Work:

1. Update openspec/config.yaml.
   Set:
   schema: skill-forge-governance

   Add project context covering:
   - Skill Forge positioning
   - Python 3.11+, uv, Typer, Pydantic, Jinja2, Rich, Questionary, YAML, SQLite, pytest
   - local-first behavior
   - deterministic generation
   - optional LLM refinement only when explicitly requested
   - generated Skill provenance
   - validation-first quality
   - platform adapter boundaries
   - bounded project context ingestion
   - generated artifacts must not silently depend on chat history
   - backward compatibility for existing workspaces

   Add rules for:
   - brainstorm
   - proposal
   - spec
   - design
   - review
   - plan
   - tasks
   - verification

2. Create openspec/schemas/skill-forge-governance/.
   Include:
   - README.md
   - schema.yaml
   - templates/brainstorm.md
   - templates/proposal.md
   - templates/spec.md
   - templates/design.md
   - templates/review.md
   - templates/plan.md
   - templates/tasks.md
   - templates/verification.md

3. Define artifact order:
   brainstorm -> proposal -> spec -> design -> review -> plan -> tasks -> verification

4. Make templates operational and suitable for weaker agents.
   Avoid abstract theory.
   Each template must have clear headings and required sections.

5. Create docs/03-openspec/ documentation:
   - change-workflow.md
   - artifact-rules.md
   - schema-policy.md
   - proposal-guidelines.md
   - spec-guidelines.md
   - design-guidelines.md
   - task-guidelines.md

6. Create docs/00-project/governance-schema-verification-report.md.
   Include:
   - changed files
   - restricted path check
   - dirty worktree handling
   - schema structure
   - config update summary
   - commands executed
   - results
   - skipped checks and reasons
   - remaining risks
   - recommended Phase 2

Verification:
Run if available:

- git status --short
- git diff --name-only
- openspec schema validate
- openspec validate --strict
- uv run skill-forge --help
- uv run pytest

If a command fails, record exact command, exit code, error summary, and whether it blocks Phase 1.

Commit:
If validation passes or only documented environment/tooling checks fail, commit only Phase 1 files.

Do not use `git add .`.

Use explicit git add commands for allowed files only.

Suggested commit message:

docs: introduce openspec superspec governance schema

Return format:
After completion, return:

- changed files
- forbidden paths changed: yes/no
- dirty worktree handling summary
- schema validation result
- openspec validation result
- pytest result
- CLI smoke test result
- report file path
- commit SHA if committed
- blockers or risks

## Prompt 结束

---

# 16. 用户回传格式

执行完成后，请按下面格式回传：

```text
Phase 1 回传：

- 修改文件列表：
- 是否误改禁止路径：
- 脏工作树如何处理：
- schema validate 结果：
- openspec validate 结果：
- pytest 结果：
- CLI smoke test 结果：
- 报告文件：
- commit SHA：
- 遇到的问题：
```

---

# 17. Phase 2 预告

Phase 1 完成后，下一阶段是：

```text
Phase 2 - Integrate Superpowers Execution Discipline
```

Phase 2 将补齐：

```text
docs/04-superpowers/superpowers-overview.md
docs/04-superpowers/skill-usage-policy.md
docs/04-superpowers/execution-discipline.md
docs/04-superpowers/subagent-policy.md
.superpowers/project-profile.md
.superpowers/skill-usage-policy.md
.superpowers/execution-checklist.md
```

Phase 2 仍然不修改业务代码。
