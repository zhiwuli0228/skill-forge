# Skill 生命周期治理计划与进展跟踪

本文档用于把 Skill Forge 的下一阶段能力整理成三个渐进式 OpenSpec change，目标不是继续增强单次生成，而是把已生成 Skill 变成可运营、可比较、可升级、可回滚的生命周期对象。

它是上游设计与 process 跟踪文档，不是某一个 change 的实现说明。每个 change 都应从这里抽取一个边界清晰、可独立验收的能力切片，再创建 `proposal.md`、`design.md`、`specs/` 和 `tasks.md`。

## 1. 当前基线

当前项目已经具备生命周期治理的关键事实源：

```text
create
  ↓
skill-forge.json
  ↓
show / list / diff
  ↓
eval-report.json
  ↓
upgrade
  ↓
experience rules
```

已具备的基础能力：

1. `skill-forge.json` provenance 记录。
2. `show / list / diff` 的本地库管理。
3. `eval-report.json` 的静态评估结果。
4. `upgrade` 候选生成与比较。
5. 本地 experience rule 记录与应用。

当前主要缺口：

1. 没有统一的生命周期视图来回答“这个 Skill 现在处于什么状态”。
2. 没有确定性的推荐引擎来回答“下一步最应该做什么”。
3. 没有标准化的 promote / rollback 流程来把候选版本转成正式版本。
4. provenance、eval、quality、experience 还只是散落的事实源，没有被整合成运营层。

## 2. 总目标

把 Skill Forge 演进成一个本地的 Skill 生命周期工作台：

```text
生成
  ↓
记录
  ↓
评估
  ↓
推荐
  ↓
升级 / 推广
  ↓
回滚 / 修复
  ↓
经验回流
```

一句话目标：

> 让用户不只是生成 Skill，而是能持续管理 Skill 的版本健康、推广节奏和回退路径。

## 3. 设计原则

1. 优先确定性推荐，不把生命周期判断建立在 LLM 上。
2. 每个 change 必须有单一主要用户行为，避免命令泛化。
3. 所有推荐都要可解释，能追溯到 provenance、eval、quality 或 experience。
4. promote / rollback 必须保留回退路径，不覆盖原始事实源。
5. 先做只读生命周期视图，再做动作型命令。
6. 将生命周期状态视为聚合结果，不在多个命令里复制状态机。

## 4. 能力分层

```text
Layer 3: promote / rollback / release control
Layer 2: deterministic recommendation engine
Layer 1: lifecycle index and status view
Layer 0: existing provenance / eval / upgrade / experience facts
```

下一阶段应优先完成 Layer 1 到 Layer 3。

## 5. 总体依赖

```text
add-skill-lifecycle-index
        |
        v
add-skill-lifecycle-recommendation
        |
        v
add-skill-promotion-and-rollback
```

说明：

1. 生命周期索引先把事实源聚合起来，后续所有推荐都能复用。
2. 推荐引擎应只消费已有事实，不引入新的数据源。
3. promote / rollback 依赖前两层，否则动作没有稳定的依据。

## 6. Change 总览

| 顺序 | Change ID | 状态 | 目标 | 不包含 |
|---:|---|---|---|---|
| 1 | `add-skill-lifecycle-index` | Archived | 聚合 provenance、quality、eval、experience，形成生命周期视图 | 不做 promote / rollback |
| 2 | `add-skill-lifecycle-recommendation` | Archived | 基于确定性规则输出 next best action 和原因 | 不做文件变更 |
| 3 | `add-skill-promotion-and-rollback` | Archived | 提供 promotion / rollback 流程，管理正式版本与候选版本 | 不做远程同步 |

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

### 1. `add-skill-lifecycle-index`

状态：`Archived`

目标：

- 建立单个 Skill 的生命周期索引。
- 聚合 provenance、quality report、eval report、experience rule 使用情况。
- 为后续推荐和动作命令提供统一只读视图。

范围：

- 新增生命周期聚合模型。
- 从 `skill-forge.json`、`eval-report.json`、experience store 读取事实。
- 提供 `skill-forge lifecycle show <skill-name>`。
- 提供基础状态标签，例如 `healthy`、`needs-eval`、`needs-upgrade`、`regressed`。

不包含：

- 不做 promote / rollback。
- 不修改 Skill 内容。
- 不引入 LLM。

用户可见行为：

```bash
skill-forge lifecycle show java-bug-investigation
```

验收标准：

1. 能展示单个 Skill 的生命周期摘要。
2. 能解释摘要来源来自 provenance、eval、quality 和 experience。
3. 缺失部分事实源时仍能给出可读状态。
4. 不影响现有 `show / diff / upgrade`。

主要影响文件：

- `src/skill_forge/lifecycle/`
- `src/skill_forge/library/manager.py`
- `src/skill_forge/cli.py`
- `tests/test_skill_lifecycle.py`

风险：

- 如果聚合字段过多，生命周期视图会变成第二套 metadata 展示。
- 如果状态定义太细，用户很难理解。

### 2. `add-skill-lifecycle-recommendation`

状态：`Archived`

目标：

- 根据生命周期事实源给出确定性 next best action。
- 让用户明确知道当前最该做的是评估、升级、推广还是回滚。

范围：

- 新增确定性推荐引擎。
- 输出推荐动作与原因分解。
- 提供 `skill-forge lifecycle recommend <skill-name>` 或等价能力。
- 支持比较两个版本并标注推荐方向。

不包含：

- 不自动执行动作。
- 不覆盖用户决策。
- 不依赖 LLM。

用户可见行为：

```bash
skill-forge lifecycle recommend java-bug-investigation
skill-forge lifecycle compare java-bug-investigation java-bug-investigation-upgraded
```

验收标准：

1. 推荐结果是确定性的。
2. 推荐结果能解释为什么这么建议。
3. 旧版本和候选版本可以直接对比。
4. 没有 eval 或 provenance 时也能给出保守建议。

主要影响文件：

- `src/skill_forge/lifecycle/`
- `src/skill_forge/cli.py`
- `tests/test_skill_lifecycle.py`

风险：

- 推荐如果太保守，用户看不到价值。
- 推荐如果太激进，会制造错误升级冲动。

### 3. `add-skill-promotion-and-rollback`

状态：`Archived`

目标：

- 把候选版本正式推进为可发布版本。
- 提供回滚到已知好版本的明确路径。

范围：

- 新增 promote 命令或同等流程。
- 新增 rollback 命令或同等流程。
- 明确正式版本、候选版本、已安装版本之间的关系。
- 记录推广动作的 provenance。

不包含：

- 不做远程同步。
- 不做自动发布到外部市场。
- 不替代 upgrade 候选生成。

用户可见行为：

```bash
skill-forge promote java-bug-investigation-upgraded
skill-forge rollback java-bug-investigation --to java-bug-investigation-v2
```

验收标准：

1. 候选版本可以安全推广。
2. 推广前后状态可追踪。
3. 能回滚到前一个已知版本。
4. 推广和回滚都保留原始事实源。

主要影响文件：

- `src/skill_forge/lifecycle/`
- `src/skill_forge/installer/installer.py`
- `src/skill_forge/cli.py`
- `tests/test_skill_lifecycle.py`

风险：

- 如果回滚语义不清，用户会把 promote 当成覆盖写入。
- 如果版本命名没有约束，历史会难以追踪。

## 9. 推荐实施顺序

```text
add-skill-lifecycle-index
  -> add-skill-lifecycle-recommendation
  -> add-skill-promotion-and-rollback
```

理由：

1. 先统一事实源，再做推荐。
2. 先推荐，再做动作，便于校验推荐是否有价值。
3. 只读视图先落地，动作型命令最后落地，风险更低。

## 10. 当前进展记录

- 2026-05-31: Created lifecycle governance plan as `docs/skill_lifecycle_governance_plan.md`.
- 2026-05-31: Defined three phased changes: lifecycle index, lifecycle recommendation, and promote/rollback.
- 2026-05-31: Implemented the first change `add-skill-lifecycle-index` with lifecycle models, read-only service, CLI command, and tests.
- 2026-05-31: Verified with `uv run pytest -q` and `openspec validate "add-skill-lifecycle-index" --strict`.
- 2026-05-31: Archived `add-skill-lifecycle-index`.
- 2026-05-31: Implemented the second change `add-skill-lifecycle-recommendation` with deterministic recommend/compare commands and tests.
- 2026-05-31: Verified with `uv run pytest -q` and `openspec validate "add-skill-lifecycle-recommendation" --strict`.
- 2026-05-31: Archived `add-skill-lifecycle-recommendation`.
- 2026-05-31: Implemented the third change `add-skill-promotion-and-rollback` with local promotion registry, promote/rollback commands, and tests.
- 2026-05-31: Verified with `uv run pytest -q` and `openspec validate "add-skill-promotion-and-rollback" --strict`.
- 2026-05-31: Archived `add-skill-promotion-and-rollback`.
- Remaining: none.

## 11. 文档维护要求

每完成一个 change 后，应检查并更新：

1. 本文档的 Change 总览状态和对应进展记录。
2. `docs/skill_forge_next_evolution_plan.md` 的阶段依赖与状态。
3. `README.md` 和 `README.zh-CN.md` 的用户可见命令。
4. 对应 `openspec/specs/` 主规格。

如果文档冲突，以当前 CLI 行为、已归档 OpenSpec specs 和测试为优先事实源。
