# Intelligent Generation 能力路线图

本文档用于跟踪 Skill Forge 从"当前 LLM 精化能力"演进到"智能生成高质量 Skills"的需求拆分、OpenSpec change 规划和实施进展。

## 1. 背景

当前 `--llm` 选项的能力：

```
用户需求
  ↓
RequirementAnalyzer（规则匹配）
  ↓
RequirementLLMRefiner（仅精化已有字段）
  ↓
BlueprintRequirementEnricher（蓝图默认值填充）
  ↓
ProjectContextEnricher（可选项目约束注入）
  ↓
SkillGenerator + Jinja2
  ↓
SkillValidator + GenerationQualityReport
```

LLM 当前运行点在蓝图 enrichment 之前。它已经允许返回 `workflow`、`constraints`、`quality_gates` 等列表字段，但当前 prompt 语义仍偏"精化 requirement"，缺少面向核心字段的生成型指令、字段级来源记录、字段级失败回退和内容质量对照。

核心缺口：

1. LLM 缺少稳定的 workflow/constraints/quality_gates 生成路径和字段级 fallback
2. 默认行为是纯规则，用户不知道何时应该用 LLM
3. 现有质量分主要来自 validator warning/error，不能充分衡量内容是否更具体、更可检查
4. 检索结果不能融入生成流程
5. 没有从 eval 反馈中学习的机制

## 2. 总目标

将 Skill Forge 演进为**语义理解驱动的智能 Skill 生成工厂**：

```
用户需求（可能模糊、简短）
  ↓
语义理解层 — 意图分类、复杂度判断、领域识别
  ↓
检索增强层 — 从相似 Skill 提取模式作为参考
  ↓
内容生成层 — LLM 生成定制化 workflow/constraints/quality_gates
  ↓
质量验证层 — 结构校验 + 内容质量评估
  ↓
经验积累层 — 从 eval 反馈中提炼规则
```

## 3. 设计原则

1. **验证驱动**：每个 change 必须有明确的验证问题，答案"无显著差异"则停止
2. **最小增量**：每个 change 独立交付、独立验证、独立回退
3. **降级链内置**：任何 LLM 失败都有回退路径，用户永远不被阻塞
4. **0配置优先**：用户不需要理解策略、模型等概念
5. **先数据后结构**：不预设 Experience Store，等数据积累后再提炼

## 4. 能力分层

```
Layer 5: 经验积累（eval 反馈 → 规则更新）
Layer 4: 检索增强（RAG — 相似 Skill 模式注入）
Layer 3: 内容质量评估（workflow 特异性、constraint 可检查性）
Layer 2: 智能降级（自动检测 + 回退）
Layer 1: LLM 字段级生成（workflow/constraints/quality_gates）
Layer 0: 现有精化能力（description 等字段）
```

## 5. 总体依赖

```
add-llm-field-generation
  ├── 内置最小内容质量基线（用于验证 LLM 收益）
  ├── dd-content-quality-rules（扩展为完整规则体系）
  │       |
  │       v
  │  add-retrieval-augmentation
  │       |
  │       v
  │  add-experience-accumulation
  |
  v
add-intelligent-fallback（需先证明 LLM 字段生成有收益）
```

说明：

- `add-llm-field-generation` 是所有后续 change 的基础
- `add-llm-field-generation` 内必须包含最小内容质量基线，至少覆盖 workflow 特异性、constraints 可检查性、quality gates 明确性
- `add-intelligent-fallback` 必须等变更 1 的对照验证完成后再做，避免在 LLM 价值未证明前改变默认行为
- `dd-content-quality-rules` 可在变更 1 后扩展为完整规则体系；如果实现时希望先做质量工具，也可以把它作为变更 1 的前置支撑
- `add-retrieval-augmentation` 需要变更 1 + 语料库质量达标
- `add-experience-accumulation` 需要变更 1 + 变更 2 + 足够样本量

## 6. Change 总览

| 顺序 | Change ID | 优先级 | 状态 | 目标 | 不包含 |
|---:|---|---|---|---|---|
| 1 | `add-llm-field-generation` | P0 | Archived | LLM 可生成 workflow/constraints/quality_gates，并内置最小内容质量基线 | 不引入 strategy/model 选项 |
| 2 | `dd-content-quality-rules` | P1 | Implemented | 规则化内容质量评估（不用 LLM） | 不做自动修复 |
| 3 | `add-intelligent-fallback` | P1 | Archived | 在 LLM 收益验证后自动检测 LLM 可用性，默认智能选择 | 不引入 --strategy 选项 |
| 4 | `add-retrieval-augmentation` | P2 | Implemented | RAG — 相似 Skill 模式注入生成 | 不替换 TF-IDF |
| 5 | `add-experience-accumulation` | P3 | Proposed | 从 eval 反馈中提炼模式改进生成 | 不做远程同步 |

状态建议值：

- `Not started`
- `Proposed`
- `Implementing`
- `Implemented`
- `Verified`
- `Archived`
- `Blocked`

## 7. 推荐实施顺序

### 第一批（P0 + P1，可并行）

```
add-llm-field-generation（含最小内容质量基线）
  │
  ├── dd-content-quality-rules（扩展验证工具）
  │
  └── add-intelligent-fallback（依赖 1 的收益验证）
```

理由：

1. 变更 1 是核心增量，直接提升生成质量
2. 最小内容质量基线必须随变更 1 一起交付，否则无法判断 LLM 是否真的更智能
3. 完整内容质量规则可以随后扩展，用于更稳定地验证后续 RAG/经验能力
4. 智能降级涉及默认行为变更，应在 LLM 字段生成被证明有收益后再实施

### 第二批（P2，需要数据支撑）

```
add-retrieval-augmentation（依赖 1 + 语料库质量）
```

前提条件：语料库中有 ≥ 10 个高质量 Skill 样本

### 第三批（P3，需要数据积累）

```
add-experience-accumulation（依赖 1 + 2 + 样本量）
```

前提条件：≥ 50 个生成样本的 eval 结果和内容质量数据

**建议：先只做第一批，验证 LLM 生成确实比规则好，再决定后续节奏。**

如果变更 1 的验证结果显示 LLM 生成质量没有显著提升，应停止后续方向。

## 8. Change 详情

### 1. `add-llm-field-generation`

状态：`Implemented`

目标：

- 让 LLM 能为 Skill 的核心内容字段（workflow、constraints、quality_gates）**生成**定制化内容，而非仅精化已有字段
- 将 LLM 运行点调整到 Blueprint enrichment 之后，使蓝图默认值既可作为生成上下文，也可作为字段级 fallback

范围：

- 扩展 `RequirementLLMRefiner` 的能力，从"精化"升级为"基于用户需求、蓝图默认值和项目上下文生成核心字段"
- LLM 可生成的字段：`workflow`、`constraints`、`quality_gates`
- LLM 仍可精化的字段：`description`、`when_to_use`、`when_not_to_use`、`expected_outputs`
- 单字段格式错误时只回退该字段，不让整个生成失败
- 整体 LLM 请求失败时回退到非 LLM 路径，继续使用蓝图 enrichment 后的 requirement
- 在 `skill-forge.json` provenance 中记录 LLM 生成、回退、可选精化了哪些字段
- 加入最小内容质量评估，至少覆盖 workflow 特异性、constraints 可检查性、quality gates 明确性

不包含：

- 不引入 `--strategy` 选项
- 不引入 `OllamaClient`
- 不引入 Intent Analyzer（保持现有 `RequirementAnalyzer`）
- 不引入 RAG
- 不引入 Experience Store
- 不引入完整 Content Quality Validator（仅实现变更 1 验证所需的最小内容质量基线）

用户可见行为：

```bash
# 与现有 --llm 完全一致，行为增强但接口不变
skill-forge create "Java 存量代码慢查询定位 skill" --llm
```

与现有 `--llm` 的区别：

| 方面 | 当前 `--llm` | 变更1后 `--llm` |
|------|-------------|----------------|
| 工作模式 | 精化已有字段 | 精化 + 生成新内容 |
| LLM 运行点 | 蓝图 enrichment 之前 | 蓝图 enrichment 之后 |
| workflow | 可返回但缺少生成型 prompt 和字段 fallback | 基于需求 + 蓝图默认值生成或改写 |
| constraints | 可返回但缺少生成型 prompt 和字段 fallback | 基于需求 + 蓝图默认值生成或改写 |
| quality_gates | 可返回但缺少生成型 prompt 和字段 fallback | 基于需求 + 蓝图默认值生成或改写 |
| 无蓝图时 | LLM 精化规则分析结果 | LLM 生成完整核心字段 |
| 失败回退 | 响应错误会中断 `--llm` | 单字段回退；整体请求失败回退到非 LLM 路径 |

目标流程：

```
RequirementAnalyzer
  ↓
BlueprintRequirementEnricher
  ↓
ProjectContextEnricher（如传入 --project）
  ↓
RequirementLLMRefiner（生成/改写字段，字段级 fallback）
  ↓
SkillGenerator
```

prompt 要求：

- 从"refine requirement"改为"generate task-specific Skill requirement fields"
- 要求 JSON object；列表字段必须是字符串数组
- 不接受 Markdown 包裹内容作为最终字段值；如果模型返回 fenced JSON，可解析后仍必须按字段类型校验
- 未知字段忽略；已知字段类型错误只回退该字段

provenance 扩展：

```json
{
  "llm_enabled": true,
  "llm_generated_fields": ["workflow", "constraints", "quality_gates"],
  "llm_fallback_fields": [],
  "llm_refined_fields": ["description", "when_to_use"],
  "content_quality": {
    "workflow_specificity": 0.82,
    "constraint_verifiability": 0.74,
    "quality_gate_clarity": 0.70
  }
}
```

验收标准：

1. `create --llm` 的 LLM 生成内容与规则生成内容对比时，最小内容质量分 LLM 版本 ≥ 规则版本
2. LLM 生成失败时自动回退到蓝图默认值，生成仍然成功
3. 无蓝图时 LLM 仍能生成完整内容
4. provenance 记录哪些字段由 LLM 生成、哪些回退
5. 不传 `--llm` 时行为完全不变
6. 现有测试全部通过
7. 现有 0-100 `GenerationQualityReport` 结构分不得作为唯一验收依据

验证问题：**同一需求，`--llm` 生成 vs 纯规则生成，质量分差异多少？**

如果答案是"没有显著差异"，应停止智能生成路线，而不是继续投入变更 2-5。

主要影响文件：

- `src/skill_forge/llm/refiner.py`
- `src/skill_forge/cli.py`
- `src/skill_forge/models/generated.py`
- `src/skill_forge/models/quality.py`
- `tests/test_llm_refiner.py`
- `tests/test_cli.py`
- `tests/test_generation_quality_report.py`

风险：

- LLM 生成内容的格式不可控（可能不是列表、可能混入 markdown）→ 需要字段级结构化校验和 fallback
- 生成质量不稳定 → 变更 1 必须包含最小内容质量基线，不能只依赖 validator warning/error

---

### 2. `dd-content-quality-rules`

状态：`Implemented`

依赖：`add-llm-field-generation`

目标：

- 在变更 1 的最小内容质量基线基础上，扩展完整的规则化内容质量评估（不依赖 LLM）
- 为后续 RAG、经验积累和 `show` 展示提供稳定质量信号

范围：

- 定义内容质量维度：workflow 特异性、constraint 可检查性、quality_gate 明确性
- 每个维度用规则评估（不用 LLM），给出 0-1 分数
- 评估结果纳入 `GenerationQualityReport`
- 评估结果写入 `skill-forge.json` provenance

不包含：

- 不用 LLM 做内容质量评估
- 不引入 Experience Store
- 不自动修复低质量内容

评估规则示例：

```python
# workflow 特异性
def assess_workflow_specificity(workflow: list[str]) -> float:
    """
    评分维度:
    - 每个步骤是否包含动词 (0.3)
    - 每个步骤是否提及具体对象/工具 (0.3)
    - 步骤间是否有逻辑衔接词 (0.2)
    - 是否避免泛化表述 ("处理问题" vs "定位慢查询SQL执行计划") (0.2)
    """

# constraint 可检查性
def assess_constraint_verifiability(constraints: list[str]) -> float:
    """
    评分维度:
    - 是否包含可检查的条件 ("根因必须有日志证据" vs "需要仔细分析")
    - 是否包含否定约束 ("不得" / "不能" / "不要") (0.3)
    - 是否包含量化标准 (0.2)
    """

# quality_gate 明确性
def assess_quality_gate_clarity(gates: list[str]) -> float:
    """
    评分维度:
    - 是否有明确的通过/失败标准 (0.5)
    - 是否可自动化检查 (0.3)
    - 是否与 workflow 步骤对应 (0.2)
    """
```

provenance 扩展：

```json
{
  "content_quality": {
    "workflow_specificity": 0.85,
    "constraint_verifiability": 0.72,
    "quality_gate_clarity": 0.60
  }
}
```

验收标准：

1. LLM 生成的 Skill 在内容质量各维度上 ≥ 规则生成的 Skill
2. 规则生成的 Skill 在内容质量上有可改进空间（基准分不为 1.0）
3. 评估分数稳定可测（同一输入多次评估分数一致）
4. 评估结果不影响生成成功/失败（纯信息性）
5. `show` 命令展示内容质量分数

验证问题：**内容质量分数与人工判断的相关性如何？**

主要影响文件：

- `src/skill_forge/validator/skill_validator.py`
- `src/skill_forge/models/quality.py`
- `src/skill_forge/models/generated.py`
- `src/skill_forge/library/manager.py`
- `tests/test_skill_validator.py`
- `tests/test_generation_quality_report.py`

风险：

- 规则评估可能过于机械 — "包含动词"不一定等于"步骤具体"
- 评分维度可能需要多次调整才能与人工判断对齐

---

### 3. `add-intelligent-fallback`

状态：`Proposed`

依赖：`add-llm-field-generation` 的对照验证通过

目标：

- 让系统**自动判断**是否使用 LLM，用户不需要理解策略概念
- 默认行为变为：LLM 可用则用，不可用则纯规则

范围：

- 首版自动检测只要求本地 LLM 配置存在；网络 probe 必须短超时、可跳过，并且不能让无配置用户变慢
- `create` 默认行为变为：如果 LLM 可用则自动使用，不可用则纯规则
- 保留 `--llm` 为显式启用（强制使用 LLM，不可用时报错）
- 保留 `--no-llm` 为显式禁用（强制不使用 LLM）

不包含：

- 不引入 `--strategy` 选项
- 不引入模型优先级列表
- 不引入 `OllamaClient`

用户可见行为：

```bash
# 自动选择（推荐）— LLM 可用则用，不可用则不用
skill-forge create "Java 存量代码慢查询定位 skill"

# 显式启用 — LLM 不可用时报错
skill-forge create "Java 存量代码慢查询定位 skill" --llm

# 显式禁用 — 保证纯规则生成
skill-forge create "Java 存量代码慢查询定位 skill" --no-llm
```

自动检测逻辑：

```
if --llm 传入:
    强制使用 LLM，不可用则报错
elif --no-llm 传入:
    强制不使用 LLM
else:
    检测 SKILL_FORGE_LLM_API_KEY 是否配置
    and 可选短超时 API endpoint probe（可跳过）
    → 可用: 使用 LLM（字段级降级回退）
    → 不可用或未配置: 纯规则生成
```

验收标准：

1. 无任何 LLM 配置时，`create` 默认走纯规则，无报错
2. 有 LLM 配置且可用时，`create` 默认使用 LLM
3. `--llm` 在 LLM 不可用时给出清晰错误
4. `--no-llm` 始终走纯规则
5. 自动检测不增加明显的延迟（probe 超时 < 2s）
6. README、README.zh-CN 和 release note 明确说明默认行为变化

验证问题：**自动检测是否正确判断 LLM 可用性？降级是否无缝？**

主要影响文件：

- `src/skill_forge/cli.py`
- `src/skill_forge/llm/refiner.py`
- `tests/test_cli.py`
- `tests/test_llm_refiner.py`

风险：

- 默认行为从"纯规则"变为"可能用 LLM" — 这是一个行为变更，需要在 release note 中明确说明
- 自动 probe 可能增加首次创建的延迟

---

### 4. `add-retrieval-augmentation`

状态：`Proposed`

依赖：`add-llm-field-generation` + 语料库质量达标

目标：

- 在生成时利用语料库中相似 Skill 的模式作为**参考上下文**，提升 LLM 生成质量

前提条件：语料库中有足够多的高质量 Skill 样本（≥ 10 个）

范围：

- 在 `create --llm` 流程中，生成前先搜索语料库获取相似 Skill
- 从相似 Skill 中提取 workflow/constraints/quality_gates 模式
- 将提取的模式作为 LLM prompt 的参考上下文
- 在 provenance 中记录是否使用了 RAG 上下文

不包含：

- 不替换 TF-IDF 检索为向量检索
- 不引入语义 reranker
- 不自动从 RAG 结果复制内容（仅作为参考）

用户可见行为：

无新增命令或选项。`create --llm` 的生成质量提升是隐性收益。

数据流：

```
用户需求
  ↓
搜索语料库 → 相似 Skill 列表
  ↓
提取模式:
  - workflow_patterns: ["定位代码路径", "整理日志证据", ...]
  - constraint_patterns: ["根因未明确前不得修改代码", ...]
  - quality_gate_patterns: ["根因必须有日志或代码证据支撑", ...]
  ↓
注入 LLM prompt:
  "参考以下模式，为用户需求生成更贴合的 workflow/constraints/quality_gates"
  ↓
LLM 生成（参考上下文 + 用户需求）
  ↓
回退检查 + provenance 记录
```

验收标准：

1. 有 RAG 上下文时 LLM 生成质量 ≥ 无 RAG 上下文时
2. 语料库为空时不影响生成（跳过 RAG 步骤）
3. RAG 搜索失败时不阻塞生成
4. provenance 记录 RAG 使用情况和参考的 Skill 名称

验证问题：**有 RAG vs 无 RAG，LLM 生成质量差异多少？**

如果答案是"没有显著差异"，应停止 RAG 方向。

主要影响文件：

- `src/skill_forge/llm/refiner.py`
- `src/skill_forge/retrieval/retriever.py`
- `tests/test_llm_refiner.py`

风险：

- 语料库质量不足时 RAG 提供噪声而非信号 — 需要前置质量门槛
- 相似度搜索可能返回不相关的结果 — 需要 relevance 阈值
- prompt 长度增加可能影响 LLM 输出质量

---

### 5. `add-experience-accumulation`

状态：`Proposed`

依赖：`dd-content-quality-rules` + 样本量积累

目标：

- 从 eval 结果和内容质量评估中**提炼模式**，持续改进生成质量

前提条件：积累了足够多的 eval 结果和内容质量分数（≥ 50 个生成样本）

范围：

- 分析 eval 失败模式，提炼常见问题
- 分析内容质量低分维度，生成针对性改进规则
- 将提炼的规则注入到 RequirementAnalyzer 或 LLM prompt 中
- 经验存储在 `~/.skill-forge/experience/` 目录

不包含：

- 不自动修改蓝图
- 不用 LLM 做模式提炼
- 不做远程经验同步

验收标准：

1. 经验规则能提升特定 task_type 的生成质量分
2. 经验积累是增量的 — 新规则不破坏旧规则的改进效果
3. 经验规则可解释 — 能查看某条规则是从哪些失败案例中提炼的
4. 清空经验目录后生成行为回退到无经验状态

验证问题：**有经验 vs 无经验，生成质量差异多少？**

如果答案是"没有显著差异"，应停止经验积累方向。

主要影响文件：

- 新增 `src/skill_forge/experience/` 模块
- `src/skill_forge/requirement/analyzer.py`
- `src/skill_forge/llm/refiner.py`
- `tests/test_experience.py`（新增）

风险：

- 经验规则可能过拟合少量样本
- 规则冲突时优先级不明确

---

## 9. 与 V1 方案的对照

| V1 概念 | V2 处理 | 理由 |
|---------|---------|------|
| 5层能力分层 | 取消 — 实际为 6 层但有前置条件 | Layer 2与3边界模糊，5层过度设计 |
| Intent Analyzer | 不独立引入 — 保持现有 RequirementAnalyzer | 规则分析够用，等有数据再说 |
| Capability Router | 不引入 — 用自动检测+降级替代 | 用户不需要理解策略概念 |
| `--strategy` 选项 | 不引入 — 用 `--llm`/`--no-llm`/自动检测 | 减少认知负担 |
| `--model` 选项 | 不引入 — 保持现有 OpenAI 兼容客户端 | 先验证价值，再增加灵活性 |
| OllamaClient | 不引入 | 硬件依赖，非核心 |
| ModelRegistry | 不引入 | 当前只有一种模型实现，不需要注册 |
| Retrieval Augmentation | 变更 4 — 有前置条件，可能推迟 | 语料库质量不足时 RAG 是噪声 |
| ContentQualityValidator | 变更 1 内置最小基线，变更 2 扩展完整规则 | 先支撑 LLM 收益验证，再做完整质量体系 |
| Experience Store | 变更 5 — 有前置条件，很可能推迟 | 先有数据再建结构 |
| 降级链 | 保留 — 每个变更都内置降级 | 这是 V1 最好的设计 |

## 10. 向后兼容性

| 变更 | 向后兼容策略 |
|------|-------------|
| 变更 1 | `--llm` 接口不变，行为增强；不传 `--llm` 行为完全不变 |
| 变更 2 | 纯增量 — 新增评估维度，不改变已有评分逻辑 |
| 变更 3 | 默认行为从"纯规则"变为"自动检测" — 这是行为变更，需 README 和 release note |
| 变更 4 | 纯增量 — RAG 是可选增强，不影响非 LLM 路径 |
| 变更 5 | 纯增量 — 经验规则是可选注入，清空后回退到无经验 |

## 11. 验证策略

每个变更都需要回答一个核心问题：

| 变更 | 验证问题 | 通过标准 |
|------|---------|---------|
| 1 | LLM 生成 vs 规则生成，最小内容质量分差异多少？ | LLM ≥ 规则，且结构分不退化 |
| 2 | 内容质量分数与人工判断相关性如何？ | 人工抽检一致性 |
| 3 | 自动检测是否正确？降级是否无缝？ | 无配置零延迟；probe < 2s |
| 4 | 有 RAG vs 无 RAG，质量差异多少？ | RAG ≥ 无 RAG |
| 5 | 有经验 vs 无经验，质量差异多少？ | 经验 ≥ 无经验 |

**如果任何变更的答案是"没有显著差异"，应该停止该方向，而不是继续投入。**

## 12. 文档维护说明

每个 OpenSpec change 归档后，应检查并更新：

1. `README.md` 和 `README.zh-CN.md`：用户可见命令、当前范围、配置和示例
2. `docs/skill_generation_roadmap.md`：change 状态、验证命令、遗留问题和下一阶段建议
3. `docs/skill_forge_next_evolution_plan.md`：长期设计文档中的能力分层和依赖关系

如果 README、roadmap、CLI help 之间出现冲突，以当前 CLI 行为和已归档主规格为优先事实源，再同步其他文档。

## 13. 进展记录

- 2026-05-29: Created OpenSpec change artifacts at `openspec/changes/add-llm-field-generation/`: `proposal.md`, `design.md`, delta specs for `llm-assisted-generation`, `local-skill-generation`, `generation-quality-report`, and `tasks.md`.
- 2026-05-29: Validated the proposal with `openspec validate "add-llm-field-generation" --strict`.
- 2026-05-29: Implemented `add-llm-field-generation`: LLM field generation now runs after blueprint/project-context enrichment, supports field-level fallback/provenance, and records deterministic content quality metrics.
- 2026-05-29: Verified with `uv run pytest tests/test_llm_refiner.py tests/test_cli.py tests/test_generation_quality_report.py tests/test_skill_generator.py`, `uv run pytest`, `openspec validate "add-llm-field-generation" --strict`, and `openspec validate --all --strict`.
- 2026-05-29: Archived via `openspec archive "add-llm-field-generation" --yes`; synced modified `generation-quality-report`, `llm-assisted-generation`, and `local-skill-generation` specs, archived as `openspec/changes/archive/2026-05-28-add-llm-field-generation/`.
- 2026-05-29: Created OpenSpec change artifacts at `openspec/changes/add-intelligent-fallback/`: `proposal.md`, `design.md`, delta specs for `intelligent-generation-fallback`, `llm-assisted-generation`, `local-skill-generation`, and `tasks.md`.
- 2026-05-29: Validated the proposal with `openspec validate "add-intelligent-fallback" --strict`.
- 2026-05-29: Implemented `add-intelligent-fallback`: `create` now auto-selects configured LLM generation, supports `--no-llm`, keeps `--llm` strict, and records LLM mode/selection/fallback reason in provenance.
- 2026-05-29: Verified with `uv run pytest tests/test_llm_refiner.py tests/test_cli.py`, `uv run pytest`, `openspec validate "add-intelligent-fallback" --strict`, and `openspec validate --all --strict`.
- 2026-05-29: Archived via `openspec archive "add-intelligent-fallback" --yes`; synced new `intelligent-generation-fallback` spec and modified `llm-assisted-generation` and `local-skill-generation` specs, archived as `openspec/changes/archive/2026-05-28-add-intelligent-fallback/`.
- 2026-05-29: Created OpenSpec change artifacts at `openspec/changes/dd-content-quality-rules/`: `proposal.md`, `design.md`, delta specs for `content-quality-rules`, `generation-quality-report`, `skill-library-management`, and `tasks.md`.
- 2026-05-29: Validated the proposal with `openspec validate "dd-content-quality-rules" --strict`.
- 2026-05-29: Implemented `dd-content-quality-rules`: content quality rules now explicitly score workflow specificity, constraint verifiability, and quality gate clarity with deterministic local signals while preserving informational-only report status behavior.
- 2026-05-29: Verified with `uv run pytest tests/test_generation_quality_report.py tests/test_cli.py -q` and `openspec validate "dd-content-quality-rules" --strict`.
- 2026-05-29: Created OpenSpec change artifacts at `openspec/changes/add-retrieval-augmentation/`: `proposal.md`, `design.md`, delta specs for `llm-assisted-generation`, `local-skill-generation`, `search-retrieval`, `generation-quality-report`, and `tasks.md`.
- 2026-05-29: Validated the proposal with `openspec validate "add-retrieval-augmentation" --strict`.
- 2026-05-29: Implemented `add-retrieval-augmentation`: LLM-assisted generation can now gather quality-gated TF-IDF references, extract compact workflow/constraint/quality-gate patterns, inject them as guidance, and record retrieval augmentation provenance.
- 2026-05-29: Verified with `uv run pytest tests/test_search_retrieval.py tests/test_llm_refiner.py tests/test_cli.py tests/test_generation_quality_report.py -q`, `uv run pytest -q`, `openspec validate "add-retrieval-augmentation" --strict`, and `openspec validate --all --strict`.
- 2026-05-29: Created OpenSpec change artifacts at `openspec/changes/add-experience-accumulation/`: `proposal.md`, `design.md`, delta specs for `experience-accumulation`, `skill-evaluation`, `generation-quality-report`, `llm-assisted-generation`, `local-skill-generation`, and `tasks.md`.
- 2026-05-29: Validated the proposal with `openspec validate "add-experience-accumulation" --strict`.
- Next step: archive completed implemented changes when ready, then apply `add-experience-accumulation` after enough eval and content-quality samples exist.
