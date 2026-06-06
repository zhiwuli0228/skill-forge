# Skill Forge Phase 3 任务书：用治理栈承接第一个真实小切片变更

> 适用仓库：`https://github.com/zhiwuli0228/skill-forge`  
> 前置阶段：  
> - Phase 0 commit: `e541b3bee1eca8795b0258ae69be028f43070d9c`  
> - Phase 1 commit: `a14a4d449a81ac711497692d929b3bbf9835f87d`  
> - Phase 2: Superpowers execution discipline and example change 已完成  
> 阶段目标：First Real Governed Change Slice  
> 执行对象：Codex 负责规划，Claude Code 负责实现与验证  
> 变更类型：第一个真实小切片，必须严格走 OpenSpec + SuperSpec-style schema + Superpowers discipline

---

## 1. Phase 2 验收结论

Phase 2 已完成：

- `docs/04-superpowers/` 执行纪律文档；
- `.superpowers/` 项目级执行配置说明；
- `openspec/changes/example-governance-stack-walkthrough/` 端到端示例 change；
- 示例 change 覆盖 8 个 artifact；
- `openspec validate --strict --all` 通过，24 items passed；
- `uv run pytest` 通过，265 tests passed；
- `uv run skill-forge --help` 通过；
- `openspec schema validate` 通过。

Phase 2 遗留的关键风险：

1. 工作树中已有大量 Phase 2 之前的预存 WIP；
2. `src/skill_forge/{adoption,experience,lifecycle}/` 等模块存在未提交代码；
3. `openspec/changes/add-skill-lifecycle-recommendation/` 是真实 in-flight change，但不符合新的 8-artifact 治理结构；
4. `openspec/changes/example-governance-stack-walkthrough/` 是示例，不应作为真实功能实现依据。

---

## 2. Phase 3 目标

Phase 3 目标不是吞掉全部预存 WIP，而是选择一个**最小真实切片**，用新治理栈完整跑通一次真实变更。

推荐切片：

```text
skill lifecycle recommendation 的最小可验证切片
```

Phase 3 要完成：

1. 盘点现有 `add-skill-lifecycle-recommendation` 相关 WIP；
2. 将该真实变更重塑为新 schema 的 8-artifact 结构；
3. 只选择一个最小能力切片进入实现；
4. Codex 输出 plan，Claude Code 按 plan 实现；
5. 运行验证；
6. 记录 evidence；
7. 独立提交。

---

## 3. 本阶段核心约束

Phase 3 是第一个真实变更，因此必须遵守：

```text
OpenSpec owns lifecycle.
SuperSpec-style schema owns structured change artifacts.
Superpowers owns execution discipline.
Project Harness owns Skill Forge-specific constraints.
```

必须使用 Phase 1 的 `skill-forge-governance` schema。

必须使用 Phase 2 的 Superpowers 执行纪律。

不得跳过：

- brainstorm
- proposal
- spec
- design
- review
- plan
- tasks
- verification

---

## 4. 推荐变更名称

建议使用现有真实 change 名称，不新建重复 change：

```text
add-skill-lifecycle-recommendation
```

如果现有 change 内容过乱，不允许直接删除。

处理方式：

1. 先备份或保留原内容；
2. 在原 change 下补齐缺失 artifact；
3. 将实现范围压缩为最小切片；
4. 不把所有预存 WIP 一次性纳入。

---

## 5. 最小切片定义

Phase 3 只允许实现以下最小能力：

> 在不改变现有 CLI 主流程的前提下，为 skill lifecycle recommendation 建立一个最小、可测试、可验证的推荐数据模型和纯函数式推荐入口。

建议范围：

### 允许实现

```text
src/skill_forge/lifecycle/
tests/
openspec/changes/add-skill-lifecycle-recommendation/
docs/00-project/first-governed-change-verification-report.md
```

### 建议最小实现内容

可以包含：

- 一个生命周期状态枚举或数据模型；
- 一个 recommendation request / result 数据结构；
- 一个纯函数 recommendation entry；
- 单元测试覆盖基本场景；
- 不接入 CLI；
- 不接入数据库；
- 不接入网络；
- 不接入模板生成流程；
- 不接入安装流程；
- 不引入新依赖。

### 明确非目标

Phase 3 不做：

- CLI command；
- 交互式推荐；
- marketplace / community discovery；
- telemetry；
- LLM recommendation；
- SQLite persistence；
- generated skill template 修改；
- end-to-end install / upgrade pipeline；
- 大范围 adoption / experience / lifecycle 全量纳入。

---

## 6. 允许修改路径

Phase 3 允许修改：

```text
openspec/changes/add-skill-lifecycle-recommendation/**
src/skill_forge/lifecycle/**
tests/**
docs/00-project/first-governed-change-verification-report.md
```

如果现有测试目录中已经有相关 lifecycle tests，可在严格范围内更新。

如 `src/skill_forge/lifecycle/` 不存在，可以创建。

---

## 7. 禁止修改路径

Phase 3 禁止修改：

```text
AGENTS.md
CODEX.md
CLAUDE.md
OPENCODE.md
SUPERPOWERS.md
README.md
README.zh-CN.md
docs/03-openspec/**
docs/04-superpowers/**
.superpowers/**
openspec/config.yaml
openspec/schemas/**
openspec/changes/example-governance-stack-walkthrough/**
templates/**
configs/**
pyproject.toml
uv.lock
```

除非现有 `tests/` 中需要新增 lifecycle 单元测试，不得修改不相关测试。

---

## 8. 脏工作树处理规则

当前仓库已有大量 Phase 0/1/2 之前的预存修改。Phase 3 必须严格处理。

执行前运行：

```bash
git status --short
git diff --name-only
```

必须在报告中记录：

- 已存在的 modified 文件；
- 已存在的 untracked 文件；
- 哪些文件与 Phase 3 相关；
- 哪些文件不纳入 Phase 3。

禁止：

```bash
git add .
```

只允许显式 add Phase 3 文件。

如果发现 `src/skill_forge/lifecycle/**` 已有预存代码：

1. 先检查是否与最小切片相关；
2. 只选择必要文件；
3. 不相关文件不 stage；
4. 不直接删除用户已有 WIP；
5. 如需改写，必须在报告中说明覆盖原因。

---

## 9. OpenSpec artifact 要求

在 `openspec/changes/add-skill-lifecycle-recommendation/` 下必须补齐或更新：

```text
brainstorm.md
proposal.md
spec.md 或 specs/<capability>/spec.md
design.md
review.md
plan.md
tasks.md
verification.md
```

如果当前 OpenSpec 要求 spec 必须放在：

```text
openspec/changes/<change-name>/specs/<capability>/spec.md
```

则必须遵循该结构。

### 9.1 brainstorm.md

必须说明：

- 当前真实问题；
- 为什么不能一次性吞掉所有 lifecycle / adoption / experience WIP；
- 最小切片候选；
- 推荐切片；
- 风险；
- 非目标。

### 9.2 proposal.md

必须说明：

- Problem；
- Goal；
- Scope；
- Non-goals；
- Affected Areas；
- User-visible Impact；
- Compatibility Impact；
- Risks；
- Rollback / Fallback；
- Acceptance Criteria。

### 9.3 spec.md

必须包含 SHALL 风格要求。

建议 capability：

```text
skill-lifecycle-recommendation
```

建议 requirements：

- recommendation model SHALL represent lifecycle input and recommendation result；
- recommendation entry SHALL be deterministic；
- recommendation entry SHALL not require network, database, or LLM；
- recommendation logic SHALL be covered by unit tests；
- recommendation logic SHALL not alter existing CLI behavior in Phase 3。

必须包含至少 3 个 scenario。

### 9.4 design.md

必须说明：

- module boundary；
- data contracts；
- function boundary；
- why no CLI integration yet；
- why no persistence；
- compatibility；
- test strategy；
- risk and fallback。

### 9.5 review.md

必须作为 implementation gate。

必须检查：

- scope 是否足够小；
- artifact 是否齐全；
- 是否禁止 CLI / persistence / template 修改；
- 是否有测试计划；
- 是否允许进入实现。

### 9.6 plan.md

必须给 Claude Code 使用。

要求：

- 步骤小；
- 明确文件；
- 明确验证；
- 明确禁止项；
- 可由弱 Agent 执行。

### 9.7 tasks.md

必须分组：

- T1 artifact reshape；
- T2 minimal model；
- T3 pure recommendation function；
- T4 unit tests；
- T5 verification；
- T6 report / commit。

### 9.8 verification.md

必须记录真实命令结果：

- `openspec validate add-skill-lifecycle-recommendation --strict`
- `openspec validate --strict --all`
- `uv run pytest`
- `uv run skill-forge --help`
- `git diff --name-only`

---

## 10. 实现要求

### 10.1 技术要求

- Python 3.11+
- 不引入新依赖；
- 优先使用 dataclass 或 Pydantic，需与项目现有风格一致；
- 逻辑必须 deterministic；
- 不访问网络；
- 不访问数据库；
- 不读取写入用户文件；
- 不改变 CLI command；
- 不改变现有模板。

### 10.2 推荐接口形态

可参考以下边界，但需结合现有代码风格调整：

```text
src/skill_forge/lifecycle/
  __init__.py
  models.py
  recommendation.py
```

建议纯函数：

```text
recommend_lifecycle_action(request) -> result
```

建议测试：

```text
tests/test_lifecycle_recommendation.py
```

测试必须覆盖：

- 新 skill / unknown state 的推荐；
- existing skill with outdated provenance 的推荐；
- existing skill with valid current metadata 的推荐；
- invalid or incomplete input 的处理；
- deterministic behavior。

---

## 11. 验证要求

必须执行：

```bash
git status --short
git diff --name-only
openspec validate add-skill-lifecycle-recommendation --strict
openspec validate --strict --all
uv run pytest
uv run skill-forge --help
```

如果项目已有更细粒度测试命令，可额外执行：

```bash
uv run pytest tests/test_lifecycle_recommendation.py
```

如失败，必须记录：

- 命令；
- 退出码；
- 错误摘要；
- 失败分类：
  - environment issue
  - tooling issue
  - code issue
  - requirement issue
- 是否阻塞 Phase 3。

---

## 12. 报告要求

必须创建：

```text
docs/00-project/first-governed-change-verification-report.md
```

报告必须包含：

- Phase 3 目标；
- 选定最小切片；
- 为什么没有纳入全部 WIP；
- 修改文件列表；
- 禁止路径检查；
- 脏工作树处理；
- OpenSpec artifact 变更摘要；
- 代码变更摘要；
- 测试变更摘要；
- 验证命令结果；
- remaining risks；
- Phase 4 推荐动作；
- 是否建议提交。

---

## 13. 提交要求

禁止：

```bash
git add .
```

只能显式添加 Phase 3 文件，例如：

```bash
git add openspec/changes/add-skill-lifecycle-recommendation
git add src/skill_forge/lifecycle
git add tests/test_lifecycle_recommendation.py
git add docs/00-project/first-governed-change-verification-report.md
```

如果实际测试文件名不同，按实际文件名显式 add。

建议 commit message：

```bash
git commit -m "feat: add governed skill lifecycle recommendation slice"
```

---

# 14. 可直接复制给 Codex / Claude Code 的 Prompt

以下内容可直接复制给执行 Agent。

---

## Prompt 开始

Task: Phase 3 - First Real Governed Change Slice

Repository: https://github.com/zhiwuli0228/skill-forge

Preconditions:
Phase 0 completed: e541b3bee1eca8795b0258ae69be028f43070d9c
Phase 1 completed: a14a4d449a81ac711497692d929b3bbf9835f87d
Phase 2 completed: Superpowers execution discipline and end-to-end example change are in place.

Goal:
Use the new governance stack on the first real, small, code-bearing change.

Target change:
add-skill-lifecycle-recommendation

This phase must not consume all pre-existing WIP. It must select only one minimal, deterministic, testable slice.

Governance model:
OpenSpec owns lifecycle.
SuperSpec-style schema owns structured change artifacts.
Superpowers owns execution discipline.
Project Harness owns Skill Forge-specific constraints.

Strict Scope:
You may modify only:

- openspec/changes/add-skill-lifecycle-recommendation/**
- src/skill_forge/lifecycle/**
- tests/**
- docs/00-project/first-governed-change-verification-report.md

You must not modify:

- AGENTS.md
- CODEX.md
- CLAUDE.md
- OPENCODE.md
- SUPERPOWERS.md
- README.md
- README.zh-CN.md
- docs/03-openspec/**
- docs/04-superpowers/**
- .superpowers/**
- openspec/config.yaml
- openspec/schemas/**
- openspec/changes/example-governance-stack-walkthrough/**
- templates/**
- configs/**
- pyproject.toml
- uv.lock

Dirty worktree rule:
The repository may contain many pre-existing modifications.
Do not reset them.
Do not delete them.
Do not include unrelated files in this phase.
Do not use `git add .`.
Only explicitly stage Phase 3 files.

Required Work:

1. Inspect the existing add-skill-lifecycle-recommendation change and related lifecycle WIP.
2. Reshape the change into the new eight-artifact structure:
   - brainstorm
   - proposal
   - spec
   - design
   - review
   - plan
   - tasks
   - verification
3. Select one minimal implementation slice:
   - deterministic lifecycle recommendation model
   - pure recommendation function
   - unit tests
4. Do not add CLI integration.
5. Do not add persistence.
6. Do not modify templates.
7. Do not add dependencies.
8. Do not touch unrelated WIP.
9. Run verification.
10. Create docs/00-project/first-governed-change-verification-report.md.
11. Commit only Phase 3 files.

Minimum implementation expectations:
- A lifecycle recommendation input model.
- A lifecycle recommendation result model.
- A deterministic pure recommendation function.
- Unit tests covering at least:
  - new or unknown skill state
  - outdated provenance
  - current valid metadata
  - invalid or incomplete input
  - deterministic behavior

Verification:
Run:

- git status --short
- git diff --name-only
- openspec validate add-skill-lifecycle-recommendation --strict
- openspec validate --strict --all
- uv run pytest
- uv run skill-forge --help

If useful, also run:

- uv run pytest tests/test_lifecycle_recommendation.py

Report:
Create:

docs/00-project/first-governed-change-verification-report.md

Include:
- selected slice
- modified files
- forbidden path check
- dirty worktree handling
- OpenSpec artifact summary
- code summary
- test summary
- verification results
- remaining risks
- recommended Phase 4

Commit:
Do not use `git add .`.

Use explicit add commands only.

Suggested commit message:

feat: add governed skill lifecycle recommendation slice

Return format:
After completion, return:

- changed files
- forbidden paths changed: yes/no
- dirty worktree handling summary
- selected minimal slice
- openspec validation result
- pytest result
- CLI smoke test result
- report file path
- commit SHA if committed
- blockers or risks

## Prompt 结束

---

# 15. 用户回传格式

执行完成后，请按下面格式回传：

```text
Phase 3 回传：

- 修改文件列表：
- 是否误改禁止路径：
- 脏工作树如何处理：
- 选择的最小切片：
- openspec validate 结果：
- pytest 结果：
- CLI smoke test 结果：
- 报告文件：
- commit SHA：
- 遇到的问题：
```

---

# 16. Phase 4 预告

Phase 3 完成后，Phase 4 建议是：

```text
Phase 4 - Governance Enforcement Hooks
```

Phase 4 才考虑加入：

- pre-commit 或本地脚本；
- schema validate hook；
- openspec strict validate hook；
- example change validation check；
- artifact template consistency check；
- CI 规则。

Phase 4 不应继续扩大业务功能。
