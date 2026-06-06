# Skill Forge Phase 5 任务书：Lifecycle Recommendation Service Adapter

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
>
> 阶段目标：Consolidate lifecycle recommendation service with pure recommendation rules  
> 执行对象：Codex 负责方案收敛，Claude Code 负责实现与验证  
> 变更类型：内部收敛，不扩大用户可见功能

---

## 1. Phase 4 验收结论

Phase 4 已完成治理门禁工具化：

- 新增 `scripts/governance_check.py`
- 新增 `tests/test_governance_check.py`
- 新增 `openspec/changes/add-governance-enforcement-hooks/**`
- 新增 `docs/00-project/governance-enforcement-verification-report.md`
- `openspec validate add-governance-enforcement-hooks --strict` 通过
- `openspec validate --strict --all` 通过，25 items passed
- `uv run pytest` 通过，304 tests passed
- `uv run skill-forge --help` 通过
- `python scripts/governance_check.py --quick` 通过
- `python scripts/governance_check.py` 通过

Phase 4 后，治理栈已经从“文档约束”升级为“本地可执行检查”。

---

## 2. Phase 5 目标

Phase 5 只解决 Phase 3 遗留的一个明确问题：

> `src/skill_forge/lifecycle/recommendation_rules.py` 中的 pure recommendation rule 与预存 service-level `recommendation.py` 之间存在规则重复。

本阶段目标：

1. 让 service-level recommendation 调用 Phase 3 的 pure function；
2. 增加 parity tests，证明 service 层行为与 pure function 对齐；
3. 保持 CLI 行为不变；
4. 不新增用户可见功能；
5. 不接数据库；
6. 不接网络；
7. 不改模板；
8. 不引入依赖；
9. 继续使用 governance stack 和 Phase 4 governance check。

---

## 3. 非目标

Phase 5 不做：

- 不新增 CLI command；
- 不修改现有 CLI 参数；
- 不新增 persistence；
- 不新增 telemetry；
- 不新增 LLM recommendation；
- 不修改 templates；
- 不修改 configs；
- 不修改 OpenSpec schema；
- 不修改 governance docs；
- 不处理全部 pre-existing WIP；
- 不清理 unrelated dirty worktree；
- 不做 adoption / experience / lifecycle 全量合并；
- 不归档任何 existing change；
- 不接 CI/pre-commit。

---

## 4. 推荐 change 名称

建议新建小 change，而不是继续扩大 Phase 3 的 change：

```text
consolidate-lifecycle-recommendation-service
```

原因：

- Phase 3 是 pure function 最小切片；
- Phase 5 是 adapter/internal convergence；
- 两者目标不同，分开更可审计。

---

## 5. 允许修改路径

Phase 5 只允许修改：

```text
openspec/changes/consolidate-lifecycle-recommendation-service/**
src/skill_forge/lifecycle/recommendation.py
src/skill_forge/lifecycle/recommendation_rules.py
tests/test_lifecycle_recommendation.py
tests/test_lifecycle_recommendation_rules.py
docs/00-project/lifecycle-service-adapter-verification-report.md
```

说明：

- 如果 `src/skill_forge/lifecycle/recommendation.py` 是预存 WIP，必须先审查其现有行为，不得直接重写；
- 如果 `tests/test_lifecycle_recommendation.py` 是预存 WIP，必须只做与 adapter parity 相关的最小修改；
- `recommendation_rules.py` 只允许做兼容 service adapter 所需的最小调整；
- 可以新增小型 helper，但必须仍在上述文件范围内。

---

## 6. 禁止修改路径

Phase 5 禁止修改：

```text
scripts/governance_check.py
tests/test_governance_check.py
src/skill_forge/cli.py
src/skill_forge/**/*
```

例外：只允许修改 `src/skill_forge/lifecycle/recommendation.py` 和 `src/skill_forge/lifecycle/recommendation_rules.py`。

同时禁止修改：

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
openspec/changes/add-skill-lifecycle-recommendation/**
openspec/changes/add-governance-enforcement-hooks/**
templates/**
configs/**
pyproject.toml
uv.lock
```

---

## 7. 脏工作树控制规则

当前仓库仍有 pre-existing dirty WIP。

执行前必须运行：

```bash
git status --short
git diff --name-only
```

必须记录：

- 哪些 dirty 文件与 Phase 5 相关；
- 哪些 dirty 文件不纳入；
- 是否有 pre-existing edits in allowed files；
- 对 allowed files 的修改是否为最小 adapter 修改。

禁止：

```bash
git add .
git add -A
```

只能显式 add Phase 5 文件。

---

## 8. OpenSpec artifact 要求

创建：

```text
openspec/changes/consolidate-lifecycle-recommendation-service/
```

必须使用 `skill-forge-governance` 结构，包含：

```text
.openspec.yaml
brainstorm.md
proposal.md
design.md
review.md
plan.md
tasks.md
verification.md
specs/lifecycle-recommendation-service-adapter/spec.md
```

### 8.1 brainstorm.md

必须说明：

- 当前问题：pure function 与 service-level rule 可能重复；
- 为什么需要 adapter；
- 为什么不扩大 CLI 或 persistence；
- 可选方案：
  - 保持重复；
  - service 调用 pure function；
  - 重写全部 service；
- 推荐方案：service 调用 pure function；
- 风险；
- 非目标。

### 8.2 proposal.md

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

### 8.3 specs/lifecycle-recommendation-service-adapter/spec.md

必须使用 SHALL 风格。

建议 requirements：

- Service-level lifecycle recommendation SHALL reuse the deterministic pure recommendation rule where applicable.
- Service adapter SHALL preserve existing public service behavior.
- Service adapter SHALL not add CLI behavior.
- Service adapter SHALL not require network, persistence, or LLM.
- Parity tests SHALL compare service-level outputs with pure function outputs for representative inputs.
- Existing pure recommendation rule tests SHALL continue to pass.

至少包含 3 个 scenario：

1. service recommendation for outdated provenance matches pure rule；
2. service recommendation for current metadata matches pure rule；
3. service behavior remains CLI-neutral / no command added。

### 8.4 design.md

必须说明：

- 当前 service-level recommendation 边界；
- pure function 的输入/输出；
- adapter 映射方式；
- 哪些字段需要转换；
- 哪些 service-only 字段保持不变；
- 为什么不接 CLI；
- 为什么不接 persistence；
- test strategy；
- fallback strategy。

### 8.5 review.md

必须作为 implementation gate。

检查：

- 是否只做 adapter；
- 是否不改 CLI；
- 是否不改 templates/configs；
- 是否不改 governance artifacts；
- 是否有 parity tests；
- 是否允许进入实现。

### 8.6 plan.md

必须给 Claude Code 使用。

步骤必须小：

1. 读取现有 service 与 pure rule；
2. 定义 adapter 映射；
3. 修改 service 最小调用；
4. 增加 parity tests；
5. 运行 targeted tests；
6. 运行 full verification；
7. 写报告；
8. 显式 add；
9. commit。

### 8.7 tasks.md

必须包含：

- T1 OpenSpec artifacts；
- T2 inspect service；
- T3 adapter implementation；
- T4 parity tests；
- T5 verification；
- T6 report；
- T7 commit。

### 8.8 verification.md

必须记录真实命令结果。

---

## 9. 实现要求

### 9.1 recommendation.py

允许修改 service-level recommendation，使其在可映射场景下调用：

```text
recommend_lifecycle_action(input) -> LifecycleRecommendation
```

来自：

```text
src/skill_forge/lifecycle/recommendation_rules.py
```

要求：

- 不破坏 service 原有 public API；
- 不改变 CLI；
- 不改变持久化；
- 不引入网络；
- 不引入新依赖；
- 不做大重构；
- 不删除预存 WIP 中的有价值代码；
- 只做 adapter 收敛。

### 9.2 recommendation_rules.py

只允许做最小兼容调整。

允许：

- 增加小型 conversion helper；
- 增加注释；
- 扩展模型字段以支持 service adapter，但必须保持向后兼容；
- 不破坏 Phase 3 现有 15 个测试。

禁止：

- 重写 pure function；
- 加全局状态；
- 访问文件系统；
- 访问网络；
- 引入依赖。

### 9.3 tests

必须增加或调整 parity tests。

测试建议：

```text
tests/test_lifecycle_recommendation.py
tests/test_lifecycle_recommendation_rules.py
```

至少覆盖：

- service outdated provenance path 与 pure function 一致；
- service current metadata path 与 pure function 一致；
- service unknown/new skill path 与 pure function 一致；
- CLI help 不新增命令；
- pure function deterministic tests 仍通过。

---

## 10. 验证要求

必须执行：

```bash
git status --short
git diff --name-only
openspec validate consolidate-lifecycle-recommendation-service --strict
openspec validate --strict --all
uv run pytest tests/test_lifecycle_recommendation_rules.py
uv run pytest tests/test_lifecycle_recommendation.py
uv run pytest
uv run skill-forge --help
python scripts/governance_check.py --quick
python scripts/governance_check.py
```

如果 `tests/test_lifecycle_recommendation.py` 不存在或不适用，必须说明实际测试文件名和原因。

如果命令失败，必须记录：

- 命令；
- 退出码；
- 错误摘要；
- 失败分类：
  - environment issue
  - tooling issue
  - code issue
  - requirement issue；
- 是否阻塞 Phase 5。

---

## 11. 报告要求

必须创建：

```text
docs/00-project/lifecycle-service-adapter-verification-report.md
```

报告必须包含：

- Phase 5 目标；
- 选定 adapter 策略；
- 修改文件列表；
- 禁止路径检查；
- 脏工作树处理；
- OpenSpec change 摘要；
- service adapter 摘要；
- pure function 复用说明；
- parity tests 摘要；
- 验证命令结果；
- governance_check quick/full 结果；
- remaining risks；
- Phase 6 推荐动作；
- 是否建议提交。

---

## 12. 提交要求

禁止：

```bash
git add .
git add -A
```

只能显式 add：

```bash
git add openspec/changes/consolidate-lifecycle-recommendation-service
git add src/skill_forge/lifecycle/recommendation.py
git add src/skill_forge/lifecycle/recommendation_rules.py
git add tests/test_lifecycle_recommendation.py
git add tests/test_lifecycle_recommendation_rules.py
git add docs/00-project/lifecycle-service-adapter-verification-report.md
```

如果某个测试文件没有被修改，不要 add。

建议 commit message：

```bash
git commit -m "refactor: reuse lifecycle recommendation rules in service"
```

---

# 13. 可直接复制给 Codex / Claude Code 的 Prompt

以下内容可直接复制给执行 Agent。

---

## Prompt 开始

Task: Phase 5 - Lifecycle Recommendation Service Adapter

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

Goal:
Consolidate lifecycle recommendation service logic by making the service-level recommendation use the deterministic pure recommendation rule introduced in Phase 3.

This phase is an internal adapter/refactor slice. It must not expand user-facing behavior.

Strict Scope:
You may create or update only:

- openspec/changes/consolidate-lifecycle-recommendation-service/**
- src/skill_forge/lifecycle/recommendation.py
- src/skill_forge/lifecycle/recommendation_rules.py
- tests/test_lifecycle_recommendation.py
- tests/test_lifecycle_recommendation_rules.py
- docs/00-project/lifecycle-service-adapter-verification-report.md

You must not modify:

- scripts/governance_check.py
- tests/test_governance_check.py
- src/skill_forge/cli.py
- other src/skill_forge/** files
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
- openspec/changes/add-skill-lifecycle-recommendation/**
- openspec/changes/add-governance-enforcement-hooks/**
- templates/**
- configs/**
- pyproject.toml
- uv.lock

Dirty worktree rule:
The repository may contain many pre-existing modifications.
Do not reset them.
Do not delete them.
Do not include unrelated files.
Do not use `git add .` or `git add -A`.
Only explicitly stage Phase 5 files.

Required Work:

1. Create OpenSpec change:
   openspec/changes/consolidate-lifecycle-recommendation-service/

   It must include:
   - .openspec.yaml
   - brainstorm.md
   - proposal.md
   - design.md
   - review.md
   - plan.md
   - tasks.md
   - verification.md
   - specs/lifecycle-recommendation-service-adapter/spec.md

2. Inspect existing service-level lifecycle recommendation code and pure recommendation_rules.py.

3. Implement minimal adapter:
   - service-level recommendation should reuse the deterministic pure function where applicable
   - preserve existing public service behavior
   - do not add CLI behavior
   - do not add persistence
   - do not add dependencies
   - do not touch unrelated WIP

4. Add parity tests:
   - service outdated provenance path matches pure function
   - service current metadata path matches pure function
   - service unknown/new skill path matches pure function
   - pure function deterministic tests remain valid
   - CLI help remains unchanged

5. Create report:
   docs/00-project/lifecycle-service-adapter-verification-report.md

Verification:
Run:

- git status --short
- git diff --name-only
- openspec validate consolidate-lifecycle-recommendation-service --strict
- openspec validate --strict --all
- uv run pytest tests/test_lifecycle_recommendation_rules.py
- uv run pytest tests/test_lifecycle_recommendation.py
- uv run pytest
- uv run skill-forge --help
- python scripts/governance_check.py --quick
- python scripts/governance_check.py

If tests/test_lifecycle_recommendation.py does not exist or is not applicable, record the actual test file name and reason.

Commit:
If verification passes, commit only Phase 5 files.

Do not use `git add .`.
Do not use `git add -A`.

Suggested commit message:

refactor: reuse lifecycle recommendation rules in service

Return format:
After completion, return:

- changed files
- forbidden paths changed: yes/no
- dirty worktree handling summary
- adapter strategy
- parity tests summary
- openspec validation result
- pytest result
- CLI smoke test result
- quick governance check result
- full governance check result
- report file path
- commit SHA if committed
- blockers or risks

## Prompt 结束

---

# 14. 用户回传格式

执行完成后，请按下面格式回传：

```text
Phase 5 回传：

- 修改文件列表：
- 是否误改禁止路径：
- 脏工作树如何处理：
- adapter 策略：
- parity tests 摘要：
- openspec validate 结果：
- pytest 结果：
- CLI smoke test 结果：
- quick governance check 结果：
- full governance check 结果：
- 报告文件：
- commit SHA：
- 遇到的问题：
```

---

# 15. Phase 6 预告

Phase 5 完成后，Phase 6 建议处理：

```text
Phase 6 - Dirty Worktree Triage and Change Queue Normalization
```

Phase 6 不应继续实现功能，而应专门清点当前大量 pre-existing WIP：

- 哪些 WIP 已被 Phase 3/5 吸收；
- 哪些 WIP 应拆为后续 changes；
- 哪些 WIP 应丢弃；
- 哪些 specs 已过时；
- 哪些 openspec/changes 应归档、重塑或删除。

Phase 6 的目标是把工作树恢复到可持续演进状态。
