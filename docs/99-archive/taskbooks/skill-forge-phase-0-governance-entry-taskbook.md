# Skill Forge Phase 0 治理入口建设任务书

> 适用仓库：`https://github.com/zhiwuli0228/skill-forge`  
> 阶段目标：Phase 0 - Establish Governance Entry Points  
> 执行对象：Codex 或 Claude Code  
> 变更类型：治理入口建设，不涉及业务代码实现

---

## 1. 背景

`skill-forge` 不是普通 Python CLI 项目，而是后续用于生成、管理、验证和演进 AI Agent Skills 的基础工具。

该项目未来需要承载：

- OpenSpec 变更生命周期管理；
- SuperSpec 风格的规格、设计、任务治理；
- Superpowers 风格的 Agent 执行纪律；
- 项目级 AI Harness 编程规范；
- Codex、Claude Code、opencode 等不同 Agent 的协作入口。

当前仓库虽然已有 README、CLAUDE.md、docs、openspec、src、tests 等基础资产，但缺少完整的治理入口和 Agent 分工约束。若继续直接演进功能，后续容易出现修改范围失控、上下文不一致、治理资产分散、变更不可追踪等问题。

本阶段只建立治理入口，不接入 schema，不改业务代码。

---

## 2. Phase 0 目标

本阶段目标是建立最小可用的治理入口，使所有 Agent 在进入项目后能够明确：

1. 项目定位；
2. 必读文件顺序；
3. Codex、Claude Code、opencode 的职责边界；
4. OpenSpec / SuperSpec / Superpowers / Harness 的分层关系；
5. 修改范围控制规则；
6. 验证前置和证据记录要求；
7. 后续 Phase 1 接入 OpenSpec + SuperSpec schema 的准备条件。

---

## 3. 本阶段允许修改的文件

只能创建或更新以下文件：

```text
AGENTS.md
CODEX.md
CLAUDE.md
OPENCODE.md
SUPERPOWERS.md
README.md
README.zh-CN.md
docs/00-project/governance-bootstrap-report.md
```

---

## 4. 本阶段禁止修改的文件或目录

禁止修改以下路径：

```text
src/**
tests/**
templates/**
configs/**
openspec/**
pyproject.toml
uv.lock
```

说明：

- Phase 0 暂不修改 `openspec/`；
- Phase 0 暂不修改业务代码；
- Phase 0 暂不调整测试；
- Phase 0 暂不变更依赖；
- Phase 0 暂不调整 Skill 模板。

---

## 5. 必须创建或更新的内容

### 5.1 AGENTS.md

`AGENTS.md` 是所有 AI Agent 的总入口。

必须包含以下内容：

#### 项目定位

说明 `skill-forge` 是一个 local-first Skill 生成与 AI Harness 治理工具，而不是普通脚本项目。

#### 必读顺序

必须定义以下读取顺序：

1. `AGENTS.md`
2. 工具专属入口：
   - Codex 读取 `CODEX.md`
   - Claude Code 读取 `CLAUDE.md`
   - opencode 读取 `OPENCODE.md`
3. 涉及执行纪律时读取 `SUPERPOWERS.md`
4. 涉及项目上下文时读取 `README.md` 和现有 docs

#### Agent 分工

必须明确：

- Codex：需求分析、brainstorm、OpenSpec/SuperSpec 变更规划、设计文档、plan.md、任务拆分；
- Claude Code：实现、测试、验证、证据记录、按需准备 commit；
- opencode：备用实现 Agent，只能在严格范围内执行小修改；
- Superpowers：执行纪律，不是项目权威来源。

#### 通用规则

必须包含：

- 非平凡变更优先走 OpenSpec；
- 不得静默扩大修改范围；
- 不得依赖聊天历史作为唯一事实来源；
- 不得进行机会主义重构；
- 完成前必须验证；
- 验证失败必须记录原因；
- 发现需求不清或范围过大时必须停止并报告。

---

### 5.2 CODEX.md

`CODEX.md` 是 Codex 的专属入口。

必须说明 Codex 的职责是设计与计划，而不是默认直接实现。

必须包含：

- 需求分析；
- brainstorm；
- OpenSpec/SuperSpec change 规划；
- proposal/spec/design/tasks/plan.md 草案；
- 实现任务拆分；
- 风险识别；
- 文件范围定义；
- 验证策略定义。

必须明确禁止：

- 未授权的大范围实现；
- 未经确认的重构；
- 跳过 OpenSpec 直接改复杂功能；
- 只依赖聊天上下文，不读取仓库文件。

---

### 5.3 CLAUDE.md

`CLAUDE.md` 是 Claude Code 的实现入口。

如果仓库中已经存在 `CLAUDE.md`，必须保留其中有价值的内容，例如：

- 项目概览；
- 常用命令；
- 代码结构；
- CLI 入口；
- 核心数据流；
- 本地工作区说明。

但需要升级为实现端治理入口。

必须包含：

- 实现前读取 `AGENTS.md`；
- 按 `plan.md` 和 `tasks.md` 执行；
- 只修改授权范围内文件；
- 不做机会主义重构；
- 实现后运行验证；
- 记录验证证据；
- 仅在用户要求时准备 commit；
- 失败时输出 BLOCKED 或明确失败原因。

---

### 5.4 OPENCODE.md

`OPENCODE.md` 是 opencode 备用执行入口。

必须强调 opencode 更容易受到上下文压缩和范围扩散影响，因此规则要更严格。

必须包含：

- 严格文件范围；
- 小 diff 优先；
- 禁止全仓重写；
- 禁止顺手重构；
- 上下文不足时停止；
- 修改前先列出预期文件；
- 修改后必须列出实际文件；
- 与预期不一致时必须报告。

---

### 5.5 SUPERPOWERS.md

`SUPERPOWERS.md` 定义本项目如何使用 Superpowers。

必须明确：

```text
OpenSpec owns lifecycle.
SuperSpec-style artifacts own structured change assets.
Superpowers owns execution discipline.
Project Harness owns Skill Forge-specific constraints.
```

必须说明 Superpowers 不是项目权威来源，而是执行纪律来源。

必须包含阶段映射：

- brainstorm：问题澄清、方案候选、风险识别；
- writing plans：实现前计划；
- executing plans：按计划执行；
- test-driven development：行为变更时优先测试；
- systematic debugging：缺陷修复时必须定位根因；
- verification before completion：完成前必须验证；
- subagent-driven development：仅大任务使用；
- using git worktrees：仅隔离大变更时使用。

---

### 5.6 README.md 和 README.zh-CN.md

只允许添加一个简短的治理入口章节。

不要重写 README。

新增章节建议标题：

英文：

```text
Governance Entry Points
```

中文：

```text
治理入口
```

内容只需要指向：

- `AGENTS.md`
- `CODEX.md`
- `CLAUDE.md`
- `OPENCODE.md`
- `SUPERPOWERS.md`

并说明：

- 非平凡变更应先阅读治理入口；
- 后续将接入 OpenSpec + SuperSpec + Superpowers；
- 当前 README 仍是用户入口，治理文件是 Agent 入口。

---

### 5.7 governance-bootstrap-report.md

必须创建：

```text
docs/00-project/governance-bootstrap-report.md
```

报告必须包含：

- 本阶段目标；
- 修改文件列表；
- 禁止修改路径检查结果；
- 实际执行的验证命令；
- 跳过的命令和原因；
- 当前剩余风险；
- Phase 1 推荐动作；
- 是否建议提交。

---

## 6. 验证要求

执行以下命令，能执行的必须执行：

```bash
git diff --stat
git diff --name-only
uv run skill-forge --help
uv run pytest
```

如果命令失败或环境不支持，不要隐瞒，必须在报告中记录：

- 命令原文；
- 错误摘要；
- 判断是代码问题、环境问题还是工具缺失；
- 是否阻塞 Phase 0。

---

## 7. 完成标准

Phase 0 完成必须满足：

- `AGENTS.md` 存在；
- `CODEX.md` 存在；
- `CLAUDE.md` 存在；
- `OPENCODE.md` 存在；
- `SUPERPOWERS.md` 存在；
- README 已添加治理入口章节；
- README.zh-CN 已添加治理入口章节；
- `docs/00-project/governance-bootstrap-report.md` 存在；
- 未修改任何禁止路径；
- 验证结果已记录；
- Phase 1 后续动作已写入报告。

---

## 8. 建议 commit message

如果验证通过，或者只有明确记录的环境阻塞，可以提交：

```bash
git add .
git commit -m "docs: establish governance entry points"
```

---

# 9. 可直接复制给 Codex / Claude Code 的 Prompt

以下内容可直接复制给执行 Agent。

---

## Prompt 开始

Task: Phase 0 - Establish Skill Forge Governance Entry Points

Repository: https://github.com/zhiwuli0228/skill-forge

Goal:
Establish the first layer of governance entry points for Skill Forge.

Skill Forge is not a generic Python CLI tool. It is intended to become a local-first Skill generation and AI Harness governance tool. Future evolution must be controlled by OpenSpec + SuperSpec + Superpowers + project-level Harness rules.

This phase only creates or updates governance entry files. Do not modify runtime code.

Strict Scope:
You may create or update only:

- AGENTS.md
- CODEX.md
- CLAUDE.md
- OPENCODE.md
- SUPERPOWERS.md
- README.md
- README.zh-CN.md
- docs/00-project/governance-bootstrap-report.md

You must not modify:

- src/**
- tests/**
- templates/**
- configs/**
- openspec/**
- pyproject.toml
- uv.lock

Required Work:

1. Create or update AGENTS.md as the universal AI Agent entry point.
   It must define:
   - Skill Forge positioning
   - required reading order
   - Codex / Claude Code / opencode role split
   - strict modification boundary rules
   - OpenSpec-first rule for non-trivial changes
   - no silent scope expansion
   - no reliance on chat history as the only source of truth
   - verification-before-completion rule

2. Create or update CODEX.md.
   Define Codex as the design and planning agent.
   Codex responsibilities:
   - requirement analysis
   - brainstorm
   - OpenSpec/SuperSpec change planning
   - design document generation
   - plan.md generation
   - task decomposition
   Codex must not perform broad implementation unless explicitly authorized.

3. Create or update CLAUDE.md.
   Preserve useful existing content if CLAUDE.md already exists.
   Upgrade it into the Claude Code implementation entry.
   Claude Code responsibilities:
   - implementation
   - tests
   - verification
   - evidence collection
   - commit preparation only when requested
   Claude Code must follow scoped plans and must not perform opportunistic refactors.

4. Create OPENCODE.md.
   Define opencode fallback execution rules:
   - strict file scope
   - avoid full-repository rewrites
   - avoid broad refactors
   - stop when context is insufficient
   - prefer minimal diffs
   - preserve existing behavior unless explicitly changed

5. Create SUPERPOWERS.md.
   Define Superpowers as execution discipline, not project authority.
   Explain:
   - OpenSpec owns lifecycle
   - SuperSpec-style artifacts own structured change assets
   - Superpowers owns execution discipline
   - Project Harness owns Skill Forge-specific constraints

   Include phase mappings:
   - brainstorm: clarify problem and options
   - writing plans: before implementation
   - executing plans: during implementation
   - test-driven development: when behavior changes
   - systematic debugging: for defects
   - verification before completion: always required
   - subagent/worktree usage: only for large work

6. Update README.md and README.zh-CN.md.
   Only add a short governance entry section.
   Do not rewrite the whole README.
   The section should point readers to:
   - AGENTS.md
   - CODEX.md
   - CLAUDE.md
   - OPENCODE.md
   - SUPERPOWERS.md

7. Create docs/00-project/governance-bootstrap-report.md.
   The report must include:
   - changed files
   - unchanged restricted areas
   - verification commands executed
   - skipped commands and reasons
   - remaining risks
   - recommended next phase

Verification:
Run these commands if available:

- git diff --stat
- git diff --name-only
- uv run skill-forge --help
- uv run pytest

If a command cannot run, record the exact reason in the report.

Completion Criteria:
Phase 0 is complete only if:

- all five agent entry files exist
- README files point to governance entry files
- no forbidden paths were changed
- governance-bootstrap-report.md exists
- verification result is recorded

Commit:
If validation passes or only documented environment-blocked checks fail, create a local commit:

git add .
git commit -m "docs: establish governance entry points"

Return format:
After completion, return:

- changed files
- forbidden paths changed: yes/no
- verification results
- report file path
- commit SHA if committed
- blockers or risks

## Prompt 结束

---

# 10. 用户回传格式

执行完成后，请按下面格式回传：

```text
Phase 0 回传：

- 修改文件列表：
- 是否误改 src/tests/templates/configs/openspec/pyproject.toml/uv.lock：
- 验证命令结果：
- 报告文件：
- commit SHA：
- 遇到的问题：
```

---

# 11. Phase 1 预告

Phase 0 完成后，下一阶段是：

```text
Phase 1 - Introduce OpenSpec + SuperSpec Governance Schema
```

Phase 1 才会修改：

```text
openspec/config.yaml
openspec/schemas/skill-forge-governance/**
docs/03-openspec/**
```

Phase 1 仍然不修改业务代码。
