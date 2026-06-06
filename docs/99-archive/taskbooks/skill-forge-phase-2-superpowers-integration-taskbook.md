# Skill Forge Phase 2 任务书：接入 Superpowers 执行纪律与端到端示例 Change

> 适用仓库：`https://github.com/zhiwuli0228/skill-forge`  
> 前置阶段：  
> - Phase 0 commit: `e541b3bee1eca8795b0258ae69be028f43070d9c`  
> - Phase 1 commit: `a14a4d449a81ac711497692d929b3bbf9835f87d`  
> 阶段目标：Integrate Superpowers Execution Discipline + Add Minimal End-to-End Example Change  
> 执行对象：Codex 或 Claude Code  
> 变更类型：治理执行纪律与示例资产接入，不涉及业务代码实现

---

## 1. Phase 1 验收结论

Phase 1 已完成 OpenSpec + SuperSpec 风格 schema 接入：

- `openspec/config.yaml` 已切换为 `schema: skill-forge-governance`
- 新增项目级 schema：`openspec/schemas/skill-forge-governance/`
- 8 个 artifact template 已存在：
  - brainstorm
  - proposal
  - spec
  - design
  - review
  - plan
  - tasks
  - verification
- `openspec schema validate` 通过
- `openspec validate --strict --all` 通过，23 items passed
- `uv run pytest` 通过，265 tests passed
- `uv run skill-forge --help` 通过
- Phase 1 commit: `a14a4d449a81ac711497692d929b3bbf9835f87d`

---

## 2. Phase 2 目标

Phase 2 的目标是补齐 Superpowers 执行纪律，并创建一个最小端到端示例 change，解决 Phase 1 遗留风险：

> schema、templates、docs 已存在，但还没有一个完整走完 8 个 artifact 的示例 change。

本阶段必须完成：

1. 新增 `docs/04-superpowers/` 执行纪律文档；
2. 新增 `.superpowers/` 项目级执行配置说明；
3. 创建一个最小端到端示例 change；
4. 示例 change 必须覆盖 8 个 artifact：
   - brainstorm
   - proposal
   - spec
   - design
   - review
   - plan
   - tasks
   - verification
5. 验证 OpenSpec、pytest、CLI smoke test 全部仍通过；
6. 记录 Phase 2 验证报告。

本阶段仍然是治理变更，不允许修改业务代码。

---

## 3. 核心原则

继续保持治理分层：

```text
OpenSpec owns lifecycle.
SuperSpec-style schema owns structured change artifacts.
Superpowers owns execution discipline.
Project Harness owns Skill Forge-specific constraints.
```

Phase 2 的重点不是介绍 Superpowers 是什么，而是定义：

- 在 Skill Forge 项目中什么时候使用哪类执行纪律；
- 哪些场景必须 brainstorm；
- 哪些场景必须先 plan；
- 什么时候允许 subagent；
- 什么时候允许 worktree；
- 验证失败时怎么处理；
- 弱 Agent 如何按清单执行。

---

## 4. 本阶段允许修改的文件

Phase 2 只能创建或更新以下路径：

```text
docs/04-superpowers/superpowers-overview.md
docs/04-superpowers/skill-usage-policy.md
docs/04-superpowers/execution-discipline.md
docs/04-superpowers/subagent-policy.md
.superpowers/project-profile.md
.superpowers/skill-usage-policy.md
.superpowers/execution-checklist.md
openspec/changes/example-governance-stack-walkthrough/brainstorm.md
openspec/changes/example-governance-stack-walkthrough/proposal.md
openspec/changes/example-governance-stack-walkthrough/spec.md
openspec/changes/example-governance-stack-walkthrough/design.md
openspec/changes/example-governance-stack-walkthrough/review.md
openspec/changes/example-governance-stack-walkthrough/plan.md
openspec/changes/example-governance-stack-walkthrough/tasks.md
openspec/changes/example-governance-stack-walkthrough/verification.md
docs/00-project/superpowers-integration-verification-report.md
```

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
openspec/config.yaml
openspec/schemas/**
docs/03-openspec/**
docs/00-project/governance-bootstrap-report.md
docs/00-project/governance-schema-verification-report.md
```

特别说明：

- Phase 2 不处理 `AGENT.md` 单数残留；
- Phase 2 不处理 Phase 0/1 之前存在的脏工作树；
- Phase 2 不修改 schema；
- Phase 2 不修改 config；
- Phase 2 不修改业务代码；
- Phase 2 不修改测试；
- Phase 2 不修改 README。

---

## 6. 脏工作树控制要求

执行前必须记录：

```bash
git status --short
git diff --name-only
```

如果工作树存在非 Phase 2 文件的预存修改：

1. 不得修改这些文件；
2. 不得还原这些文件；
3. 不得删除这些文件；
4. 不得把这些文件纳入提交；
5. 提交时禁止 `git add .`；
6. 必须显式 add Phase 2 允许路径；
7. 报告中必须记录预存修改的类别和处理方式。

---

## 7. docs/04-superpowers 文档要求

### 7.1 superpowers-overview.md

必须说明：

- Superpowers 在本项目中是执行纪律，不是项目权威来源；
- OpenSpec、SuperSpec-style schema、Superpowers、Project Harness 的边界；
- Agent 不应以 Superpowers 为理由绕过 OpenSpec；
- Superpowers 只增强工作方法，不改变项目技术约束。

必须包含：

```text
OpenSpec owns lifecycle.
SuperSpec-style schema owns structured change artifacts.
Superpowers owns execution discipline.
Project Harness owns Skill Forge-specific constraints.
```

---

### 7.2 skill-usage-policy.md

必须定义不同阶段的执行纪律映射。

至少包含：

| 阶段 | 推荐纪律 |
|---|---|
| unclear requirement | brainstorm |
| change planning | writing plans |
| implementation | executing plans |
| behavior change | test-driven development |
| bug fix | systematic debugging |
| large change | subagent-driven development |
| isolated risky work | using git worktrees |
| completion | verification before completion |

必须说明：

- 纯文档小改可以轻量处理；
- 涉及 CLI、template、validation、provenance、schema 的变更必须走完整流程；
- behavior change 必须优先考虑测试；
- debugging 必须先定位根因，不允许猜测式修复。

---

### 7.3 execution-discipline.md

必须定义 Agent 执行纪律。

必须包含：

- 开始前读取入口文件；
- 执行前确认 scope；
- 不允许 silent scope expansion；
- 不允许 opportunistic refactor；
- 不允许只依赖 chat history；
- 每个阶段都要留下可审计证据；
- 完成前必须验证；
- 验证失败必须分类：
  - environment issue
  - tooling issue
  - code issue
  - requirement issue
- 失败不得伪装成完成。

---

### 7.4 subagent-policy.md

必须定义 subagent 和 worktree 使用边界。

必须包含：

- 小任务禁止过度使用 subagent；
- 大任务可使用 subagent 拆分；
- subagent 必须有明确输入、输出、文件范围、验证要求；
- worktree 只用于隔离高风险或并行变更；
- 不允许 subagent 自动提交未验证代码；
- 不允许 subagent 修改 scope 外文件；
- 主 Agent 必须整合、审查并验证 subagent 结果。

---

## 8. .superpowers 项目配置说明要求

### 8.1 .superpowers/project-profile.md

必须说明 Skill Forge 项目画像：

- local-first CLI；
- Skill generation / validation / update / install / search / upgrade；
- Python 3.11+；
- uv；
- Typer；
- Pydantic；
- Jinja2；
- Rich / Questionary；
- YAML；
- SQLite；
- pytest；
- OpenSpec + SuperSpec-style schema + Superpowers + Harness governance stack。

必须说明：

- 默认不联网；
- 默认 deterministic；
- LLM refinement 必须显式启用；
- 生成物必须有 provenance；
- 上下文摄取必须 bounded and auditable。

---

### 8.2 .superpowers/skill-usage-policy.md

必须以更偏执行侧的方式复述文档政策。

要求适合弱 Agent 快速读取。

必须包含：

- When requirement is unclear: brainstorm first.
- When implementation is non-trivial: write plan first.
- When behavior changes: test first or update tests.
- When fixing bugs: reproduce and locate root cause first.
- Before completion: run verification.
- For large work: use subagents only with strict scopes.
- For risky parallel work: use worktrees only when explicitly authorized.

---

### 8.3 .superpowers/execution-checklist.md

必须是清单形式。

必须包含：

- Start checklist
- Scope checklist
- Implementation checklist
- Verification checklist
- Completion checklist
- Blocked checklist

要求每项简短、可执行。

---

## 9. 示例 change 要求

创建：

```text
openspec/changes/example-governance-stack-walkthrough/
```

这是一个文档型示例 change，用于展示 `skill-forge-governance` schema 如何被使用。

注意：

- 示例 change 不应修改业务代码；
- 示例 change 不应声明真实待实现功能；
- 示例 change 应明确自己是 example / walkthrough；
- 示例 change 应覆盖全部 8 个 artifact；
- 示例 change 必须能通过当前 OpenSpec validate；
- 如果 OpenSpec 对 change 目录结构有额外要求，必须遵循工具要求；
- 如果当前 OpenSpec 对 example change 的 spec delta 有要求，应创建最小合法结构；
- 如果不应创建可被误认为真实待实施的 change，应在 artifact 中明确标记 `Example Only`。

### 9.1 brainstorm.md

主题：`Example Only - Governance Stack Walkthrough`

必须包含：

- 这个示例解决的问题；
- 为什么需要一个端到端样例；
- 是否会改代码：不会；
- 方案选项：
  - 只写 docs；
  - 写完整 example change；
- 推荐方案：完整 example change；
- 风险：被误认为真实功能 change；
- 缓解：每个 artifact 标明 Example Only。

---

### 9.2 proposal.md

必须包含：

- Problem：缺少端到端治理样例；
- Goal：提供一个完整 8 artifact 示例；
- Scope：仅治理示例文档；
- Non-goals：不改代码、不改 CLI、不改模板、不改 schema；
- Affected Areas：openspec/changes/example-governance-stack-walkthrough；
- Acceptance Criteria：8 个 artifact 存在且 validate 通过。

---

### 9.3 spec.md

必须使用 SHALL 风格。

示例要求：

- The example change SHALL identify itself as example-only governance documentation.
- The example change SHALL include all eight governance artifacts.
- The example change SHALL not require runtime code changes.
- The example change SHALL document verification commands and results.

必须包含至少 2 个 scenario。

---

### 9.4 design.md

必须说明：

- 为什么示例 change 放在 `openspec/changes/`；
- 为什么不放在 docs；
- 为什么不修改 schema；
- 如何避免被误认为真实功能；
- 与 OpenSpec/SuperSpec/Superpowers/Harness 的关系。

---

### 9.5 review.md

必须作为 readiness gate。

必须检查：

- 是否 example-only；
- 是否不碰代码；
- 是否覆盖 8 artifacts；
- 是否 validate 通过；
- 是否文件范围清晰。

---

### 9.6 plan.md

必须是弱 Agent 可执行计划。

步骤：

1. 创建 docs/04-superpowers；
2. 创建 .superpowers；
3. 创建 example change；
4. 运行验证；
5. 写报告；
6. 显式 add 文件；
7. commit。

---

### 9.7 tasks.md

必须列出任务状态和证据。

建议任务：

- T1 docs/04-superpowers
- T2 .superpowers
- T3 example change
- T4 verification
- T5 report
- T6 commit

---

### 9.8 verification.md

必须记录本阶段验证命令和预期。

如果执行时已经有真实结果，应写真实结果。

必须包含：

- `openspec validate --strict --all`
- `uv run skill-forge --help`
- `uv run pytest`
- `git diff --name-only`
- skipped checks

---

## 10. 验证要求

必须执行可用命令：

```bash
git status --short
git diff --name-only
openspec validate --strict --all
uv run skill-forge --help
uv run pytest
```

可选执行：

```bash
openspec schema validate
```

如果命令失败，必须在报告中记录：

- 命令；
- 退出码；
- 错误摘要；
- 是否阻塞 Phase 2；
- 后续修复建议。

---

## 11. 报告要求

必须创建：

```text
docs/00-project/superpowers-integration-verification-report.md
```

报告必须包含：

- Phase 2 目标；
- 修改文件列表；
- 禁止路径检查；
- 脏工作树处理说明；
- docs/04-superpowers 摘要；
- .superpowers 摘要；
- example change 摘要；
- 执行命令结果；
- OpenSpec validate 结果；
- pytest 结果；
- CLI smoke test 结果；
- skipped commands and reasons；
- remaining risks；
- Phase 3 推荐动作；
- 是否建议提交。

---

## 12. 提交要求

由于工作树存在预存修改，禁止使用：

```bash
git add .
```

只能显式添加 Phase 2 文件，例如：

```bash
git add docs/04-superpowers
git add .superpowers
git add openspec/changes/example-governance-stack-walkthrough
git add docs/00-project/superpowers-integration-verification-report.md
```

建议 commit message：

```bash
git commit -m "docs: integrate superpowers execution discipline"
```

---

# 13. 可直接复制给 Codex / Claude Code 的 Prompt

以下内容可直接复制给执行 Agent。

---

## Prompt 开始

Task: Phase 2 - Integrate Superpowers Execution Discipline and Add End-to-End Example Change

Repository: https://github.com/zhiwuli0228/skill-forge

Preconditions:
Phase 0 completed: e541b3bee1eca8795b0258ae69be028f43070d9c
Phase 1 completed: a14a4d449a81ac711497692d929b3bbf9835f87d

Goal:
Integrate Superpowers execution discipline into the Skill Forge governance stack and add one minimal end-to-end example change that uses all eight governance artifacts.

This is a governance-only change. Do not modify runtime code.

Governance model:

OpenSpec owns lifecycle.
SuperSpec-style schema owns structured change artifacts.
Superpowers owns execution discipline.
Project Harness owns Skill Forge-specific constraints.

Strict Scope:
You may create or update only:

- docs/04-superpowers/superpowers-overview.md
- docs/04-superpowers/skill-usage-policy.md
- docs/04-superpowers/execution-discipline.md
- docs/04-superpowers/subagent-policy.md
- .superpowers/project-profile.md
- .superpowers/skill-usage-policy.md
- .superpowers/execution-checklist.md
- openspec/changes/example-governance-stack-walkthrough/brainstorm.md
- openspec/changes/example-governance-stack-walkthrough/proposal.md
- openspec/changes/example-governance-stack-walkthrough/spec.md
- openspec/changes/example-governance-stack-walkthrough/design.md
- openspec/changes/example-governance-stack-walkthrough/review.md
- openspec/changes/example-governance-stack-walkthrough/plan.md
- openspec/changes/example-governance-stack-walkthrough/tasks.md
- openspec/changes/example-governance-stack-walkthrough/verification.md
- docs/00-project/superpowers-integration-verification-report.md

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
- openspec/config.yaml
- openspec/schemas/**
- docs/03-openspec/**
- docs/00-project/governance-bootstrap-report.md
- docs/00-project/governance-schema-verification-report.md

Important dirty worktree rule:
The repository may contain pre-existing modifications unrelated to this phase.
Do not reset them.
Do not include them in this phase.
Do not use `git add .`.
Only stage files explicitly allowed for Phase 2.

Required Work:

1. Create docs/04-superpowers documentation:
   - superpowers-overview.md
   - skill-usage-policy.md
   - execution-discipline.md
   - subagent-policy.md

2. Create .superpowers project configuration notes:
   - project-profile.md
   - skill-usage-policy.md
   - execution-checklist.md

3. Create an example change:
   - openspec/changes/example-governance-stack-walkthrough/

   It must contain:
   - brainstorm.md
   - proposal.md
   - spec.md
   - design.md
   - review.md
   - plan.md
   - tasks.md
   - verification.md

   The example change must be clearly marked as Example Only.
   It must not require code changes.
   It must demonstrate the full governance flow.

4. Create docs/00-project/superpowers-integration-verification-report.md.
   Include:
   - changed files
   - restricted path check
   - dirty worktree handling
   - docs/04-superpowers summary
   - .superpowers summary
   - example change summary
   - commands executed
   - results
   - skipped checks and reasons
   - remaining risks
   - recommended Phase 3

Verification:
Run if available:

- git status --short
- git diff --name-only
- openspec validate --strict --all
- uv run skill-forge --help
- uv run pytest

Optional:

- openspec schema validate

If a command fails, record exact command, exit code, error summary, and whether it blocks Phase 2.

Commit:
If validation passes or only documented environment/tooling checks fail, commit only Phase 2 files.

Do not use `git add .`.

Use explicit git add commands for allowed files only.

Suggested commit message:

docs: integrate superpowers execution discipline

Return format:
After completion, return:

- changed files
- forbidden paths changed: yes/no
- dirty worktree handling summary
- openspec validation result
- pytest result
- CLI smoke test result
- report file path
- commit SHA if committed
- blockers or risks

## Prompt 结束

---

# 14. 用户回传格式

执行完成后，请按下面格式回传：

```text
Phase 2 回传：

- 修改文件列表：
- 是否误改禁止路径：
- 脏工作树如何处理：
- openspec validate 结果：
- pytest 结果：
- CLI smoke test 结果：
- 报告文件：
- commit SHA：
- 遇到的问题：
```

---

# 15. Phase 3 预告

Phase 2 完成后，下一阶段建议是：

```text
Phase 3 - Establish Project Harness Documentation Baseline
```

Phase 3 重点补齐：

```text
docs/00-project/project-overview.md
docs/00-project/current-state.md
docs/00-project/glossary.md
docs/00-project/roadmap.md
docs/01-architecture/architecture-overview.md
docs/01-architecture/module-boundaries.md
docs/01-architecture/data-flow.md
docs/01-architecture/storage-contracts.md
docs/02-harness/harness-overview.md
docs/02-harness/agent-workflow.md
docs/02-harness/coding-standards.md
docs/02-harness/verification-policy.md
docs/02-harness/context-ingestion-policy.md
docs/02-harness/checklist.md
```

Phase 3 仍然不修改业务代码。
