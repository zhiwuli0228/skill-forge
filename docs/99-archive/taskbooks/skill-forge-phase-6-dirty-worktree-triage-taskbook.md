# Skill Forge Phase 6 任务书：Dirty Worktree Triage and Change Queue Normalization

> 适用仓库：`https://github.com/zhiwuli0228/skill-forge`  
> 前置阶段：  
> - Phase 0 commit: `e541b3bee1eca8795b0258ae69be028f43070d9c`  
> - Phase 1 commit: `a14a4d449a81ac711497692d929b3bbf9835f87d`  
> - Phase 2: Superpowers execution discipline and example change 已完成  
> - Phase 3 commits:
>   - `44f60fb` — `feat: add governed skill lifecycle recommendation slice`
>   - `1ace0e9` — `docs: record Phase 3 commit SHA in verification report`
> - Phase 4 commits:
>   - `0bcd73f` — `chore: add governance enforcement check`
>   - `39941f3` — `docs: record Phase 4 commit SHA in verification report`
> - Phase 5 commits:
>   - `2cb3912` — `refactor: reuse lifecycle recommendation rules in service`
>   - `e4992be` — `docs: record Phase 5 commit SHA in verification report`
>
> 阶段目标：清点、分类、归一化当前 pre-existing dirty worktree 和 change queue  
> 执行对象：Codex 负责审计与归类，Claude Code 负责必要的文档/索引落地  
> 变更类型：治理清理与队列归一化，不实现业务功能

---

## 1. Phase 5 验收结论

Phase 5 已完成 lifecycle recommendation service adapter：

- service-level `recommend` 已复用 Phase 3 的 pure function；
- 6 个 parity tests 新增；
- `tests/test_lifecycle_recommendation.py` 通过，15 passed；
- `tests/test_lifecycle_recommendation_rules.py` 通过，15 passed；
- 全量 `uv run pytest` 通过，310 passed；
- `openspec validate consolidate-lifecycle-recommendation-service --strict` 通过；
- `openspec validate --strict --all` 通过，26 items passed；
- quick/full `scripts/governance_check.py` 均通过；
- commit:
  - `2cb3912`
  - `e4992be`

当前主要剩余问题不再是 lifecycle adapter，而是：

> 工作树中仍有大量 Phase 0 之前或中途遗留的 pre-existing WIP、spec 修改、change 删除、未跟踪模块和测试。它们持续污染后续治理变更判断。

---

## 2. Phase 6 目标

Phase 6 不实现功能，只做一次**工作树与变更队列清点归一化**。

目标：

1. 盘点所有 dirty working tree entries；
2. 区分：
   - 已被 Phase 3/5 吸收的内容；
   - 应保留并拆成后续 change 的内容；
   - 应归档的旧 change；
   - 应丢弃的过时 WIP；
   - 需要用户确认的高风险项；
3. 创建一份可执行的 change queue；
4. 不直接删除用户 WIP；
5. 不直接提交业务代码；
6. 不修改 `src/**`、`tests/**` 等业务路径；
7. 生成 Phase 6 审计报告和后续队列。

---

## 3. 非目标

Phase 6 不做：

- 不实现新功能；
- 不修 bug；
- 不修改 Python 业务代码；
- 不修改测试；
- 不修改 templates；
- 不修改 configs；
- 不修改 pyproject/uv.lock；
- 不修改 OpenSpec schema；
- 不归档真实 change；
- 不删除 pre-existing WIP；
- 不恢复或 reset 工作树；
- 不运行 `git clean`；
- 不运行 `git checkout --` 或 `git restore` 清理用户改动；
- 不执行 `git add .` 或 `git add -A`；
- 不做 CI/pre-commit 接入；
- 不继续扩大 lifecycle/adoption/experience 功能。

---

## 4. 推荐产物

Phase 6 建议只新增治理审计文档和一个 OpenSpec change：

```text
openspec/changes/triage-dirty-worktree-change-queue/**
docs/00-project/dirty-worktree-triage-report.md
docs/00-project/change-queue.md
docs/00-project/wip-disposition-matrix.md
```

其中：

- `dirty-worktree-triage-report.md`：本次审计报告；
- `change-queue.md`：后续可执行 change 队列；
- `wip-disposition-matrix.md`：每个 WIP 文件/目录的处置建议；
- `openspec/changes/triage-dirty-worktree-change-queue/**`：本阶段治理 change artifact。

---

## 5. 允许修改路径

Phase 6 只允许创建或更新：

```text
openspec/changes/triage-dirty-worktree-change-queue/**
docs/00-project/dirty-worktree-triage-report.md
docs/00-project/change-queue.md
docs/00-project/wip-disposition-matrix.md
```

---

## 6. 禁止修改路径

Phase 6 禁止修改：

```text
src/**
tests/**
templates/**
configs/**
scripts/**
pyproject.toml
uv.lock
README.md
README.zh-CN.md
AGENTS.md
CODEX.md
CLAUDE.md
OPENCODE.md
SUPERPOWERS.md
docs/03-openspec/**
docs/04-superpowers/**
.superpowers/**
openspec/config.yaml
openspec/schemas/**
openspec/changes/example-governance-stack-walkthrough/**
openspec/changes/add-skill-lifecycle-recommendation/**
openspec/changes/add-governance-enforcement-hooks/**
openspec/changes/consolidate-lifecycle-recommendation-service/**
```

说明：

- Phase 6 可以读取这些路径；
- Phase 6 不能写入这些路径；
- Phase 6 不能 reset、delete、restore 这些路径；
- Phase 6 不能把这些路径纳入提交。

---

## 7. 审计命令

执行前必须运行并记录输出摘要：

```bash
git status --short
git diff --name-only
git ls-files --others --exclude-standard
git diff --stat
git log --oneline -10
openspec validate --strict --all
python scripts/governance_check.py --quick
```

可选：

```bash
python scripts/governance_check.py
```

如果 full governance check 耗时可接受，建议执行。

---

## 8. 分类规则

每个 dirty entry 必须分到以下类别之一：

### A. Absorbed by prior phases

已经被 Phase 3/5 的正式提交吸收，当前脏文件可能是重复或过时副本。

### B. Candidate for future governed change

有价值，但不应现在提交，应拆成后续 OpenSpec change。

### C. Existing change needs reshape

已有 OpenSpec change，但不符合新 `skill-forge-governance` 8-artifact 结构。

### D. Candidate for discard

看起来是过时、重复、临时产物或错误方向。

注意：Phase 6 只标记，不删除。

### E. Requires user decision

高风险或信息不足，不能判断。

---

## 9. wip-disposition-matrix.md 要求

创建：

```text
docs/00-project/wip-disposition-matrix.md
```

必须包含表格：

```text
Path | Status | Category | Observed Content | Recommended Action | Reason | Risk | Requires User Decision
```

要求：

- 每个 dirty tracked file 至少一行；
- 每个 untracked top-level directory 至少一行；
- 对大目录可按目录归并，但必须列出代表文件；
- 不允许只写“many files”；
- 不确定项必须标记 `Requires User Decision = yes`。

---

## 10. change-queue.md 要求

创建：

```text
docs/00-project/change-queue.md
```

必须将后续工作排成队列。

建议格式：

```text
Priority | Change Name | Type | Scope | Source WIP | Required Artifacts | Verification | Notes
```

建议至少包含这些候选项，如实际 WIP 支持：

1. `normalize-lifecycle-compare-service`
2. `introduce-skill-adoption-metrics`
3. `introduce-skill-experience-model`
4. `add-retrieval-generation-support`
5. `reshape-community-skill-discovery`
6. `normalize-existing-spec-drift`
7. `archive-or-rebuild-stale-changes`

要求：

- 每个 change 必须小；
- 每个 change 必须有明确 scope；
- 不允许一个 change 吞掉所有 WIP；
- 标记哪些 change 可以自动执行，哪些必须用户确认。

---

## 11. dirty-worktree-triage-report.md 要求

创建：

```text
docs/00-project/dirty-worktree-triage-report.md
```

必须包含：

- Phase 6 目标；
- 当前 HEAD / 最近 10 个 commit；
- dirty worktree 总览；
- tracked modified/deleted files 总览；
- untracked files/directories 总览；
- WIP 分类统计；
- absorbed by prior phases；
- future governed changes；
- changes needing reshape；
- discard candidates；
- user-decision items；
- 验证命令结果；
- remaining risks；
- Phase 7 推荐动作；
- 是否建议提交。

---

## 12. OpenSpec change 要求

创建：

```text
openspec/changes/triage-dirty-worktree-change-queue/
```

必须包含：

```text
.openspec.yaml
brainstorm.md
proposal.md
design.md
review.md
plan.md
tasks.md
verification.md
specs/dirty-worktree-change-queue/spec.md
```

### 12.1 brainstorm.md

必须说明：

- 当前问题：dirty worktree 长期存在，影响后续治理；
- 选项：
  - 继续忽略；
  - 直接 reset；
  - 审计并生成处置队列；
- 推荐：审计并生成处置队列；
- 风险：误判用户 WIP；
- 非目标：不删除、不 reset、不实现功能。

### 12.2 proposal.md

必须包含：

- Problem；
- Goal；
- Scope；
- Non-goals；
- Affected Areas；
- User-visible Impact；
- Compatibility Impact；
- Risks；
- Acceptance Criteria。

### 12.3 specs/dirty-worktree-change-queue/spec.md

必须使用 SHALL 风格。

建议 requirements：

- The triage report SHALL classify dirty worktree entries into explicit disposition categories.
- The disposition matrix SHALL include tracked and untracked WIP.
- The change queue SHALL break future work into small governed changes.
- The phase SHALL NOT modify runtime code.
- The phase SHALL NOT delete, reset, or restore user WIP.
- The phase SHALL mark uncertain or risky items as requiring user decision.

至少包含 3 个 scenario。

### 12.4 design.md

必须说明：

- 审计数据来源；
- 分类规则；
- 为什么不自动清理；
- 如何避免误删；
- 如何生成 change queue；
- 后续如何消费该队列。

### 12.5 review.md

必须作为 readiness gate。

检查：

- 是否只做审计文档；
- 是否禁止 reset/delete；
- 是否分类清晰；
- 是否不修改业务代码；
- 是否可以进入执行。

### 12.6 plan.md

步骤：

1. 采集 git 状态；
2. 分类 tracked dirty files；
3. 分类 untracked files；
4. 识别 absorbed / future / reshape / discard / decision；
5. 生成 disposition matrix；
6. 生成 change queue；
7. 写 triage report；
8. 运行验证；
9. 显式 add；
10. commit。

### 12.7 tasks.md

包含：

- T1 OpenSpec artifacts；
- T2 collect git state；
- T3 classify WIP；
- T4 write matrix；
- T5 write queue；
- T6 write report；
- T7 verification；
- T8 commit。

### 12.8 verification.md

记录真实验证结果。

---

## 13. 验证要求

必须执行：

```bash
openspec validate triage-dirty-worktree-change-queue --strict
openspec validate --strict --all
python scripts/governance_check.py --quick
```

建议执行：

```bash
python scripts/governance_check.py
uv run pytest
uv run skill-forge --help
```

如果 full check 因 dirty WIP 或耗时问题失败，必须记录失败，并判断是否与 Phase 6 新增文档有关。

---

## 14. 提交要求

禁止：

```bash
git add .
git add -A
```

只能显式 add：

```bash
git add openspec/changes/triage-dirty-worktree-change-queue
git add docs/00-project/dirty-worktree-triage-report.md
git add docs/00-project/change-queue.md
git add docs/00-project/wip-disposition-matrix.md
```

建议 commit message：

```bash
git commit -m "docs: triage dirty worktree change queue"
```

---

# 15. 可直接复制给 Codex / Claude Code 的 Prompt

以下内容可直接复制给执行 Agent。

---

## Prompt 开始

Task: Phase 6 - Dirty Worktree Triage and Change Queue Normalization

Repository: https://github.com/zhiwuli0228/skill-forge

Preconditions:
Phase 0 completed: e541b3bee1eca8795b0258ae69be028f43070d9c
Phase 1 completed: a14a4d449a81ac711497692d929b3bbf9835f87d
Phase 2 completed: Superpowers execution discipline and example change are in place
Phase 3 completed:
- 44f60fb feat: add governed skill lifecycle recommendation slice
- 1ace0e9 docs: record Phase 3 commit SHA in verification report
Phase 4 completed:
- 0bcd73f chore: add governance enforcement check
- 39941f3 docs: record Phase 4 commit SHA in verification report
Phase 5 completed:
- 2cb3912 refactor: reuse lifecycle recommendation rules in service
- e4992be docs: record Phase 5 commit SHA in verification report

Goal:
Audit and normalize the existing dirty working tree and future change queue. Do not implement features. Do not delete or reset user WIP.

Strict Scope:
You may create or update only:

- openspec/changes/triage-dirty-worktree-change-queue/**
- docs/00-project/dirty-worktree-triage-report.md
- docs/00-project/change-queue.md
- docs/00-project/wip-disposition-matrix.md

You must not modify:

- src/**
- tests/**
- templates/**
- configs/**
- scripts/**
- pyproject.toml
- uv.lock
- README.md
- README.zh-CN.md
- AGENTS.md
- CODEX.md
- CLAUDE.md
- OPENCODE.md
- SUPERPOWERS.md
- docs/03-openspec/**
- docs/04-superpowers/**
- .superpowers/**
- openspec/config.yaml
- openspec/schemas/**
- existing openspec/changes/** except openspec/changes/triage-dirty-worktree-change-queue/**

Dirty worktree rule:
Do not reset.
Do not delete.
Do not restore.
Do not clean.
Do not include unrelated files.
Do not use `git add .` or `git add -A`.

Required Work:

1. Collect git state:
   - git status --short
   - git diff --name-only
   - git ls-files --others --exclude-standard
   - git diff --stat
   - git log --oneline -10

2. Classify dirty entries into:
   - A. Absorbed by prior phases
   - B. Candidate for future governed change
   - C. Existing change needs reshape
   - D. Candidate for discard
   - E. Requires user decision

3. Create OpenSpec change:
   openspec/changes/triage-dirty-worktree-change-queue/

   It must include:
   - .openspec.yaml
   - brainstorm.md
   - proposal.md
   - design.md
   - review.md
   - plan.md
   - tasks.md
   - verification.md
   - specs/dirty-worktree-change-queue/spec.md

4. Create:
   - docs/00-project/wip-disposition-matrix.md
   - docs/00-project/change-queue.md
   - docs/00-project/dirty-worktree-triage-report.md

5. Do not modify runtime code or tests.

Verification:
Run:

- openspec validate triage-dirty-worktree-change-queue --strict
- openspec validate --strict --all
- python scripts/governance_check.py --quick

Recommended if practical:

- python scripts/governance_check.py
- uv run pytest
- uv run skill-forge --help

Commit:
If validation passes, commit only Phase 6 files.

Do not use `git add .`.
Do not use `git add -A`.

Suggested commit message:

docs: triage dirty worktree change queue

Return format:
After completion, return:

- changed files
- forbidden paths changed: yes/no
- dirty worktree handling summary
- WIP classification summary
- recommended change queue summary
- openspec validation result
- governance quick check result
- full governance check result if run
- report file paths
- commit SHA if committed
- blockers or risks

## Prompt 结束

---

# 16. 用户回传格式

执行完成后，请按下面格式回传：

```text
Phase 6 回传：

- 修改文件列表：
- 是否误改禁止路径：
- 脏工作树如何处理：
- WIP 分类摘要：
- 后续 change queue 摘要：
- openspec validate 结果：
- governance quick check 结果：
- full governance check 结果：
- 报告文件：
- commit SHA：
- 遇到的问题：
```

---

# 17. Phase 7 预告

Phase 6 完成后，Phase 7 应从 `docs/00-project/change-queue.md` 中选择一个最小且无需用户确认的 change 执行。

优先级建议：

1. reshaping existing OpenSpec changes；
2. 清理已被 Phase 3/5 吸收的重复 WIP；
3. lifecycle compare service 小切片；
4. adoption/experience/retrieval 等功能切片。

Phase 7 必须基于 Phase 6 队列，而不是凭感觉继续扩展。
