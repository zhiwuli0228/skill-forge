# Skill Forge Phase 4 任务书：Governance Enforcement Hooks

> 适用仓库：`https://github.com/zhiwuli0228/skill-forge`  
> 前置阶段：  
> - Phase 0 commit: `e541b3bee1eca8795b0258ae69be028f43070d9c`  
> - Phase 1 commit: `a14a4d449a81ac711497692d929b3bbf9835f87d`  
> - Phase 2: Superpowers execution discipline and example change 已完成  
> - Phase 3 feature commit: `44f60fb`  
> - Phase 3 report follow-up commit: `1ace0e9`  
> 阶段目标：Add lightweight governance enforcement hooks  
> 执行对象：Codex 负责方案收敛，Claude Code 负责实现与验证  
> 变更类型：治理门禁工具化，不扩大业务功能

---

## 1. Phase 3 验收结论

Phase 3 已完成第一个真实治理闭环代码切片：

- `add-skill-lifecycle-recommendation` 已切换为 `skill-forge-governance`；
- 补齐 8-artifact 结构；
- 新增 `src/skill_forge/lifecycle/recommendation_rules.py`；
- 新增 `tests/test_lifecycle_recommendation_rules.py`；
- 新增 `docs/00-project/first-governed-change-verification-report.md`；
- `openspec validate add-skill-lifecycle-recommendation --strict` 通过；
- `openspec validate --strict --all` 通过，24 items passed；
- `uv run pytest` 通过，280 tests passed；
- `uv run skill-forge --help` 通过；
- Phase 3 commit:
  - `44f60fb` — `feat: add governed skill lifecycle recommendation slice`
  - `1ace0e9` — `docs: record Phase 3 commit SHA in verification report`

Phase 3 遗留风险：

1. `recommendation_rules.py` 的状态映射规则与预存 service-level `recommendation.py` 存在重复；
2. 预存 WIP 仍然很多，Phase 3 未纳入；
3. 治理规则目前仍主要靠文档和人工纪律，没有本地 enforcement hook。

---

## 2. Phase 4 目标

Phase 4 的目标是把已建立的治理规则转化为**轻量、可重复、本地可执行的检查命令**。

本阶段不做业务功能扩展。

Phase 4 要完成：

1. 新增一个本地治理检查脚本；
2. 将 OpenSpec schema validate、OpenSpec strict validate、pytest、CLI smoke test 组合为一键检查；
3. 增加 example change 验证；
4. 增加 artifact/template/schema 一致性基础检查；
5. 生成 Phase 4 验证报告；
6. 独立提交，不纳入预存 WIP。

---

## 3. 非目标

Phase 4 不做：

- 不改 lifecycle recommendation 业务逻辑；
- 不做 service adapter；
- 不接 CLI command；
- 不处理全部预存 WIP；
- 不修复 pre-existing dirty worktree；
- 不接远端 CI；
- 不强制安装 pre-commit；
- 不修改 OpenSpec schema 结构；
- 不修改 Superpowers 文档；
- 不修改 README；
- 不引入新依赖；
- 不修改 `pyproject.toml` 或 `uv.lock`。

---

## 4. 推荐实现策略

优先使用仓库内轻量脚本，而不是引入依赖。

推荐新增：

```text
scripts/governance_check.py
```

并配套：

```text
docs/00-project/governance-enforcement-verification-report.md
```

如果仓库已有 `scripts/` 目录，使用现有目录。

如果没有 `scripts/` 目录，可以创建。

不要把 Phase 4 做成复杂框架。目标是一个弱 Agent 也能运行的本地检查器。

---

## 5. 允许修改路径

Phase 4 只允许创建或修改：

```text
scripts/governance_check.py
docs/00-project/governance-enforcement-verification-report.md
openspec/changes/add-governance-enforcement-hooks/**
tests/test_governance_check.py
```

说明：

- `openspec/changes/add-governance-enforcement-hooks/**` 用于本阶段 change artifact；
- `tests/test_governance_check.py` 仅用于测试治理检查脚本；
- 如脚本测试不适合使用 pytest，可不新增测试文件，但必须在报告中说明原因。

---

## 6. 禁止修改路径

Phase 4 禁止修改：

```text
src/**
tests/test_lifecycle_recommendation_rules.py
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
templates/**
configs/**
pyproject.toml
uv.lock
```

特别说明：

- `tests/**` 原则上禁止，但允许新增或修改 `tests/test_governance_check.py`；
- 不允许改 Phase 3 的 lifecycle 文件；
- 不允许修正 Phase 3 遗留的 service adapter 重复问题；
- 不允许为了通过检查而修改 schema/config。

---

## 7. 脏工作树控制规则

执行前必须运行：

```bash
git status --short
git diff --name-only
```

必须记录：

- 当前 dirty worktree 中哪些是 pre-existing；
- Phase 4 实际新增或修改哪些文件；
- 是否触碰禁止路径；
- 是否存在未纳入提交的相关文件。

禁止：

```bash
git add .
git add -A
```

只能显式 add Phase 4 文件。

---

## 8. OpenSpec change 要求

创建：

```text
openspec/changes/add-governance-enforcement-hooks/
```

必须使用 `skill-forge-governance` 结构，至少包含：

```text
.openspec.yaml
brainstorm.md
proposal.md
design.md
review.md
plan.md
tasks.md
verification.md
specs/governance-enforcement-hooks/spec.md
```

如果当前 OpenSpec 要求不同结构，按工具要求修正。

### 8.1 brainstorm.md

必须说明：

- 当前问题：治理已有文档和示例，但缺少一键本地检查；
- 方案选项：
  - 只写文档；
  - 增加本地脚本；
  - 直接接 CI / pre-commit；
- 推荐方案：先增加本地脚本；
- 风险：脚本过重、误伤 pre-existing WIP；
- 非目标：不接 CI、不装 pre-commit、不修业务代码。

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

### 8.3 specs/governance-enforcement-hooks/spec.md

必须使用 SHALL 风格。

建议 requirements：

- Governance check SHALL run OpenSpec schema validation when available.
- Governance check SHALL run OpenSpec strict validation.
- Governance check SHALL run CLI smoke test.
- Governance check SHALL run pytest.
- Governance check SHALL validate that the example governance walkthrough remains valid.
- Governance check SHALL report skipped commands with reasons.
- Governance check SHALL not modify repository files.

至少包含 3 个 scenario。

### 8.4 design.md

必须说明：

- 为什么使用本地脚本；
- 脚本如何调用命令；
- 如何处理命令缺失；
- 如何处理退出码；
- 如何避免修改仓库；
- 为什么不在 Phase 4 接 CI；
- 为什么不引入依赖。

### 8.5 review.md

必须作为 implementation gate。

检查：

- scope 是否小；
- 是否不改业务代码；
- 是否不改 schema/config；
- 是否不改 Phase 3 lifecycle；
- 是否有测试和验证；
- 是否允许进入实现。

### 8.6 plan.md

必须给 Claude Code 使用。

要求步骤清晰：

1. 创建 OpenSpec change；
2. 创建 `scripts/governance_check.py`；
3. 可选新增 `tests/test_governance_check.py`；
4. 运行验证；
5. 写报告；
6. 显式 add；
7. commit。

### 8.7 tasks.md

必须包含：

- T1 OpenSpec artifacts；
- T2 governance_check.py；
- T3 script tests；
- T4 command verification；
- T5 report；
- T6 commit。

### 8.8 verification.md

必须记录真实命令结果。

---

## 9. governance_check.py 功能要求

脚本必须满足：

1. 使用 Python 标准库；
2. 不引入新依赖；
3. 不修改仓库文件；
4. 从仓库根目录运行；
5. 输出每个检查项的状态；
6. 汇总最终结果；
7. 任一 required 检查失败时返回非 0；
8. optional 检查命令不存在时可标记 skipped，但必须说明原因；
9. 支持 `--quick` 参数，仅执行较快检查；
10. 默认完整检查。

### 9.1 默认完整检查

默认执行：

```bash
openspec schema validate
openspec validate example-governance-stack-walkthrough --strict
openspec validate add-skill-lifecycle-recommendation --strict
openspec validate --strict --all
uv run skill-forge --help
uv run pytest
```

### 9.2 quick 检查

`--quick` 至少执行：

```bash
openspec validate --strict --all
uv run skill-forge --help
```

可以额外执行 schema validate，但不能执行耗时测试。

### 9.3 输出格式

建议输出类似：

```text
[PASS] openspec schema validate
[PASS] openspec validate example-governance-stack-walkthrough --strict
[PASS] openspec validate add-skill-lifecycle-recommendation --strict
[PASS] openspec validate --strict --all
[PASS] uv run skill-forge --help
[PASS] uv run pytest

Summary: 6 passed, 0 failed, 0 skipped
```

失败时必须显示：

- command；
- exit code；
- stdout/stderr 摘要；
- 是否 required。

### 9.4 命令缺失处理

如果 `openspec` 或 `uv` 不存在：

- 对 required 命令应 fail；
- 对 optional 命令可 skip；
- 必须输出清晰原因。

---

## 10. 测试要求

如新增 `tests/test_governance_check.py`，至少覆盖：

- command list construction；
- quick mode command list；
- result aggregation；
- failed command returns non-zero；
- skipped optional command is reported；
- script does not mutate files。

测试必须避免真的运行全部外部命令，可用 monkeypatch/subprocess mock。

---

## 11. 验证要求

必须执行：

```bash
git status --short
git diff --name-only
openspec validate add-governance-enforcement-hooks --strict
openspec validate --strict --all
uv run pytest
uv run skill-forge --help
python scripts/governance_check.py --quick
python scripts/governance_check.py
```

如果新增了脚本测试，也执行：

```bash
uv run pytest tests/test_governance_check.py
```

如果完整 `python scripts/governance_check.py` 因耗时可接受，必须执行。若环境阻塞，记录原因。

---

## 12. 报告要求

必须创建：

```text
docs/00-project/governance-enforcement-verification-report.md
```

报告必须包含：

- Phase 4 目标；
- 选定实现策略；
- 修改文件列表；
- 禁止路径检查；
- 脏工作树处理；
- OpenSpec change 摘要；
- script 功能摘要；
- test 摘要；
- 验证命令结果；
- quick/full governance check 结果；
- skipped commands and reasons；
- remaining risks；
- Phase 5 推荐动作；
- 是否建议提交。

---

## 13. 提交要求

禁止：

```bash
git add .
git add -A
```

只能显式 add：

```bash
git add openspec/changes/add-governance-enforcement-hooks
git add scripts/governance_check.py
git add tests/test_governance_check.py
git add docs/00-project/governance-enforcement-verification-report.md
```

如果没有新增测试文件，不要 add 不存在路径。

建议 commit message：

```bash
git commit -m "chore: add governance enforcement check"
```

---

# 14. 可直接复制给 Codex / Claude Code 的 Prompt

以下内容可直接复制给执行 Agent。

---

## Prompt 开始

Task: Phase 4 - Add Governance Enforcement Hooks

Repository: https://github.com/zhiwuli0228/skill-forge

Preconditions:
Phase 0 completed: e541b3bee1eca8795b0258ae69be028f43070d9c
Phase 1 completed: a14a4d449a81ac711497692d929b3bbf9835f87d
Phase 2 completed: Superpowers execution discipline and example change are in place
Phase 3 completed:
- 44f60fb feat: add governed skill lifecycle recommendation slice
- 1ace0e9 docs: record Phase 3 commit SHA in verification report

Goal:
Add lightweight local governance enforcement so the governance stack is no longer documentation-only.

This phase must not expand business functionality.

Strict Scope:
You may create or update only:

- scripts/governance_check.py
- tests/test_governance_check.py
- openspec/changes/add-governance-enforcement-hooks/**
- docs/00-project/governance-enforcement-verification-report.md

You must not modify:

- src/**
- tests/test_lifecycle_recommendation_rules.py
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
Only explicitly stage Phase 4 files.

Required Work:

1. Create OpenSpec change:
   openspec/changes/add-governance-enforcement-hooks/

   It must include:
   - .openspec.yaml
   - brainstorm.md
   - proposal.md
   - design.md
   - review.md
   - plan.md
   - tasks.md
   - verification.md
   - specs/governance-enforcement-hooks/spec.md

2. Create scripts/governance_check.py.

   Requirements:
   - standard library only
   - no repository mutation
   - run from repo root
   - default full check
   - support --quick
   - print PASS/FAIL/SKIP per command
   - return non-zero when required checks fail
   - report skipped commands with reasons

   Full mode commands:
   - openspec schema validate
   - openspec validate example-governance-stack-walkthrough --strict
   - openspec validate add-skill-lifecycle-recommendation --strict
   - openspec validate --strict --all
   - uv run skill-forge --help
   - uv run pytest

   Quick mode commands:
   - openspec validate --strict --all
   - uv run skill-forge --help

3. Add tests/test_governance_check.py if practical.

   Cover:
   - command list construction
   - quick mode command list
   - result aggregation
   - failed command returns non-zero
   - skipped optional command is reported
   - script does not mutate files

   Use monkeypatch or subprocess mocking. Do not run full external commands inside unit tests.

4. Create docs/00-project/governance-enforcement-verification-report.md.

   Include:
   - changed files
   - restricted path check
   - dirty worktree handling
   - OpenSpec change summary
   - script summary
   - test summary
   - verification command results
   - quick/full governance check results
   - skipped commands and reasons
   - remaining risks
   - recommended Phase 5

Verification:
Run:

- git status --short
- git diff --name-only
- openspec validate add-governance-enforcement-hooks --strict
- openspec validate --strict --all
- uv run pytest
- uv run skill-forge --help
- python scripts/governance_check.py --quick
- python scripts/governance_check.py

If added:
- uv run pytest tests/test_governance_check.py

Commit:
If validation passes or only documented environment/tooling checks fail, commit only Phase 4 files.

Do not use `git add .`.
Do not use `git add -A`.

Suggested commit message:

chore: add governance enforcement check

Return format:
After completion, return:

- changed files
- forbidden paths changed: yes/no
- dirty worktree handling summary
- governance check script summary
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

# 15. 用户回传格式

执行完成后，请按下面格式回传：

```text
Phase 4 回传：

- 修改文件列表：
- 是否误改禁止路径：
- 脏工作树如何处理：
- governance check 脚本摘要：
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

# 16. Phase 5 预告

Phase 4 完成后，Phase 5 再处理：

```text
Phase 5 - Lifecycle Recommendation Service Adapter
```

Phase 5 目标才是消除 Phase 3 遗留的规则重复：

- 让 service-level recommendation 调用 pure function；
- 增加 parity tests；
- 保持 CLI 行为不变；
- 不接新功能；
- 只做内部收敛。

Phase 5 仍必须走完整 governance stack。
