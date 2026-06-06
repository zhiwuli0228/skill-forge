# Intelligent Generation V2 — 设计文档

## 1. V1 评审结论与改版动机

V1 方案（`docs/intelligent-generation-design.md`）的问题诊断准确，但实施范围过大：

| 问题 | 影响 |
|------|------|
| 5个Phase、6个新概念同时引入 | 依赖链长，无法增量验证 |
| Layer 2（语义增强）与 Layer 3（内容生成）边界模糊 | 实际坍缩为一层 |
| Experience Store 先建仓库再找货源 | 空转等待数据 |
| RAG 依赖低质量语料 | 引入噪声而非信号 |
| `--strategy`/`--model`/`--no-fallback` 增加用户认知负担 | 违背"生成一个 Skill 应该简单"的原则 |

**V2 核心思路：砍到最小可验证增量，每个概念独立交付、独立验证。**

---

## 2. 设计原则

1. **一次只引入一个新概念** — 每个变更可独立验证、独立回退
2. **先有数据再建结构** — 不预设 Experience Store，等 eval 数据积累后再提炼
3. **0配置智能降级** — 用户不需要理解策略和模型，系统自动选择最优路径
4. **LLM 是可选增强，不是必需依赖** — 任何时刻断网断 LLM，系统仍然可用
5. **质量可度量** — 每个变更都要有基准对比：LLM 生成 vs 规则生成，质量分差多少

---

## 3. 当前基线

非 LLM 路径：

```
用户需求
  ↓
RequirementAnalyzer（规则匹配）
  ↓
BlueprintRequirementEnricher（蓝图默认值填充）
  ↓
ProjectContextEnricher（项目约束注入）
  ↓
SkillGenerator + Jinja2（模板渲染）
  ↓
SkillValidator（结构校验）
  ↓
GenerationQualityReport（质量评分）
  ↓
install / list / show / diff / eval / upgrade
```

`--llm` 路径的实际运行点不同：

```
用户需求
  ↓
RequirementAnalyzer（规则匹配）
  ↓
RequirementLLMRefiner（精化 requirement）
  ↓
BlueprintRequirementEnricher（蓝图默认值填充）
  ↓
ProjectContextEnricher（可选项目约束注入）
  ↓
SkillGenerator + Jinja2
```

LLM 当前已经允许返回 `workflow`、`constraints`、`quality_gates` 等字段，但 prompt 仍是"refine requirement"语义；缺少生成型 prompt、字段级 provenance、字段级失败回退和内容质量对照。因此缺口不是"字段完全不能生成"，而是"缺少稳定的核心字段生成机制"。

---

## 4. 变更拆分

```
变更1: LLM字段级内容生成（含最小内容质量基线）
        ├── 变更2: 内容质量评估规则
        │       ↓
        │   变更4: 检索增强生成（RAG）
        │       ↓
        │   变更5: 经验积累
        ↓
变更3: 智能降级与自动策略选择（需先验证 LLM 收益）
```

每个变更的边界、验收标准和依赖关系如下。

---

## 5. 变更详情

### 变更1: LLM 字段级内容生成

**目标**：让 LLM 能在蓝图 enrichment 之后，为 Skill 的核心内容字段（workflow、constraints、quality_gates）生成或改写定制化内容，并在失败时按字段回退到蓝图默认值。

**范围**：

- 将 `--llm` 运行点调整到 `BlueprintRequirementEnricher` 之后，使蓝图默认内容可作为 LLM 输入和 fallback
- 扩展现有 `RequirementLLMRefiner` 的能力，从"精化"升级为"生成 task-specific Skill requirement fields"
- LLM 可生成的字段：`workflow`、`constraints`、`quality_gates`
- LLM 仍可精化的字段：`description`、`when_to_use`、`when_not_to_use`、`expected_outputs`
- 单字段格式错误时只回退该字段，不让整个生成失败
- 整体 LLM 请求失败时回退到非 LLM 路径，不阻塞用户
- 在 `skill-forge.json` provenance 中记录 LLM 生成、回退、可选精化了哪些字段
- 加入最小内容质量评估，用于对比 LLM 版本和纯规则版本

**不包含**：

- 不引入 `--strategy` 选项
- 不引入 `OllamaClient`（保持现有 OpenAI 兼容客户端）
- 不引入 Intent Analyzer（保持现有 `RequirementAnalyzer`）
- 不引入 RAG
- 不引入 Experience Store
- 不引入完整 Content Quality Validator（变更1只做验证所需的最小内容质量基线）

**用户可见行为**：

```bash
# 与现有 --llm 完全一致，行为增强但接口不变
skill-forge create "Java 存量代码慢查询定位 skill" --llm
```

**与现有 `--llm` 的区别**：

| 方面 | 当前 `--llm` | 变更1后 `--llm` |
|------|-------------|----------------|
| 工作模式 | 精化已有字段 | 精化 + 生成新内容 |
| LLM 运行点 | 蓝图 enrichment 之前 | 蓝图 enrichment 之后 |
| workflow | 可返回但缺少生成型 prompt 和字段 fallback | 基于需求 + 蓝图默认值生成或改写 |
| constraints | 可返回但缺少生成型 prompt 和字段 fallback | 基于需求 + 蓝图默认值生成或改写 |
| quality_gates | 可返回但缺少生成型 prompt 和字段 fallback | 基于需求 + 蓝图默认值生成或改写 |
| 无蓝图时 | LLM 精化规则分析结果 | LLM 生成完整内容 |
| 失败回退 | 响应错误会中断 `--llm` | 单字段回退；整体请求失败回退到非 LLM 路径 |

**生成逻辑**：

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

对于每个可生成字段（workflow / constraints / quality_gates）：

  if 蓝图提供了默认值:
      prompt = "基于以下蓝图默认值和用户需求，生成更贴合的 {field}"
      input  = 蓝图默认值 + 用户需求 + 项目上下文
  else:
      prompt = "基于用户需求，生成 {field}"
      input  = 用户需求 + 项目上下文

  result = llm.generate(prompt, input)

  if result 有效:
      使用 LLM 生成结果
      provenance.llm_generated_fields.append(field)
  else:
      使用蓝图默认值（如有）或留空
      provenance.llm_fallback_fields.append(field)
```

**prompt 与解析要求**：

- prompt 从"refine requirement"改为"generate task-specific Skill requirement fields"
- 返回 JSON object；列表字段必须是字符串数组
- 不接受 Markdown 包裹内容作为最终字段值；如果模型返回 fenced JSON，可解析后仍必须按字段类型校验
- 未知字段忽略；已知字段类型错误只回退该字段

**provenance 扩展**：

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

**验收标准**：

1. `create --llm` 的 LLM 生成内容与规则生成内容对比时，最小内容质量分 LLM 版本 ≥ 规则版本
2. LLM 生成失败时自动回退到蓝图默认值，生成仍然成功
3. 无蓝图时 LLM 仍能生成完整内容
4. provenance 记录哪些字段由 LLM 生成、哪些回退
5. 不传 `--llm` 时行为完全不变
6. 现有测试全部通过
7. 现有 0-100 `GenerationQualityReport` 结构分不得作为唯一验收依据

**主要影响文件**：

- `src/skill_forge/llm/refiner.py` — 扩展为字段级生成
- `src/skill_forge/cli.py` — 调整 `--llm` 路径
- `src/skill_forge/models/generated.py` — provenance 字段扩展
- `src/skill_forge/models/quality.py` — 最小内容质量分
- `tests/test_llm_refiner.py`
- `tests/test_cli.py`
- `tests/test_generation_quality_report.py`

**风险**：

- LLM 生成内容的格式不可控（可能不是列表、可能混入 markdown）→ 需要字段级结构化校验和 fallback
- 生成质量不稳定 → 变更1必须包含最小内容质量基线，不能只依赖 validator warning/error

---

### 变更2: 内容质量评估规则

**目标**：在变更1的最小内容质量基线基础上，扩展完整的规则化内容质量评估（不依赖 LLM）。

**依赖**：变更1

**范围**：

- 定义内容质量维度：workflow 特异性、constraint 可检查性、quality_gate 明确性
- 每个维度用规则评估（不用 LLM），给出 0-1 分数
- 评估结果纳入 `GenerationQualityReport`
- 评估结果写入 `skill-forge.json` provenance

**不包含**：

- 不用 LLM 做内容质量评估
- 不引入 Experience Store
- 不自动修复低质量内容

**评估规则示例**：

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

def assess_quality_gate_clarity(gates: list[str]) -> float:
    """
    评分维度:
    - 是否有明确的通过/失败标准 (0.5)
    - 是否可自动化检查 (0.3)
    - 是否与 workflow 步骤对应 (0.2)
    """
```

**provenance 扩展**：

```json
{
  "content_quality": {
    "workflow_specificity": 0.85,
    "constraint_verifiability": 0.72,
    "quality_gate_clarity": 0.60
  }
}
```

**验收标准**：

1. LLM 生成的 Skill 在内容质量各维度上 ≥ 规则生成的 Skill
2. 规则生成的 Skill 在内容质量上有可改进空间（基准分不为 1.0）
3. 评估分数稳定可测（同一输入多次评估分数一致）
4. 评估结果不影响生成成功/失败（纯信息性）
5. `show` 命令展示内容质量分数

**主要影响文件**：

- `src/skill_forge/validator/skill_validator.py` — 新增内容质量规则
- `src/skill_forge/models/quality.py` — 内容质量模型
- `src/skill_forge/models/generated.py` — provenance 扩展
- `src/skill_forge/library/manager.py` — 展示质量分数
- `src/skill_forge/cli.py`
- `tests/test_skill_validator.py`
- `tests/test_generation_quality_report.py`

**风险**：

- 规则评估可能过于机械 — "包含动词"不一定等于"步骤具体"
- 评分维度可能需要多次调整才能与人工判断对齐

---

### 变更3: 智能降级与自动策略选择

**目标**：在 LLM 字段生成收益被验证后，让系统自动判断是否使用 LLM，用户不需要理解策略概念。

**依赖**：变更1的对照验证通过

**范围**：

- 首版自动检测只要求本地 LLM 配置存在；网络 probe 必须短超时、可跳过，并且不能让无配置用户变慢
- `create` 默认行为变为：如果 LLM 可用则自动使用，不可用则纯规则
- 保留 `--llm` 为显式启用（强制使用 LLM，不可用时报错）
- 保留 `--no-llm` 为显式禁用（强制不使用 LLM）
- 移除对 `--strategy` 的需求

**不包含**：

- 不引入 `--strategy` 选项
- 不引入模型优先级列表
- 不引入 `OllamaClient`

**用户可见行为**：

```bash
# 自动选择 — LLM 可用则用，不可用则不用
skill-forge create "Java 存量代码慢查询定位 skill"

# 显式启用 — LLM 不可用时报错
skill-forge create "Java 存量代码慢查询定位 skill" --llm

# 显式禁用 — 保证纯规则生成
skill-forge create "Java 存量代码慢查询定位 skill" --no-llm
```

**自动检测逻辑**：

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

**验收标准**：

1. 无任何 LLM 配置时，`create` 默认走纯规则，无报错
2. 有 LLM 配置且可用时，`create` 默认使用 LLM
3. `--llm` 在 LLM 不可用时给出清晰错误
4. `--no-llm` 始终走纯规则
5. 自动检测不增加明显的延迟（probe 超时 < 2s）
6. README、README.zh-CN 和 release note 明确说明默认行为变化

**主要影响文件**：

- `src/skill_forge/cli.py` — 默认行为变更
- `src/skill_forge/llm/refiner.py` — 可用性检测
- `src/skill_forge/config.py` — 可选配置
- `tests/test_cli.py`
- `tests/test_llm_refiner.py`

**风险**：

- 默认行为从"纯规则"变为"可能用 LLM" — 这是一个行为变更，需要在 README 和 release note 中明确说明
- 自动 probe 可能增加首次创建的延迟

---

### 变更4: 检索增强生成（RAG）

**目标**：在生成时利用语料库中相似 Skill 的模式作为参考上下文，提升 LLM 生成质量。

**依赖**：变更1 + 语料库质量达标（需先评估）

**前提条件**：语料库中有足够多的高质量 Skill 样本。当前语料库内容以文档为主，不适合直接做 RAG — 需要先用变更1积累一批 LLM 生成的高质量 Skill，或人工标注现有语料中的高质量条目。

**范围**：

- 在 `create --llm` 流程中，生成前先搜索语料库获取相似 Skill
- 从相似 Skill 中提取 workflow/constraints/quality_gates 模式
- 将提取的模式作为 LLM prompt 的参考上下文
- 在 provenance 中记录是否使用了 RAG 上下文

**不包含**：

- 不替换 TF-IDF 检索为向量检索
- 不引入语义 reranker
- 不自动从 RAG 结果复制内容（仅作为参考）

**用户可见行为**：

无新增命令或选项。`create --llm` 的生成质量提升是隐性收益。

**数据流**：

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

**验收标准**：

1. 有 RAG 上下文时 LLM 生成质量 ≥ 无 RAG 上下文时
2. 语料库为空时不影响生成（跳过 RAG 步骤）
3. RAG 搜索失败时不阻塞生成
4. provenance 记录 RAG 使用情况和参考的 Skill 名称

**主要影响文件**：

- `src/skill_forge/llm/refiner.py` — 注入 RAG 上下文
- `src/skill_forge/retrieval/retriever.py` — 模式提取接口
- `src/skill_forge/models/generated.py` — provenance 扩展
- `tests/test_llm_refiner.py`

**风险**：

- 语料库质量不足时 RAG 提供噪声而非信号 — 需要前置质量门槛
- 相似度搜索可能返回不相关的结果 — 需要 relevance 阈值
- prompt 长度增加可能影响 LLM 输出质量

**实施前置条件**：

在实施此变更前，应先回答：

> 当前语料库中有多少条目可以被视为"高质量 Skill 样本"？

如果答案 < 10，应先积累样本，再实施 RAG。

---

### 变更5: 经验积累

**目标**：从 eval 结果和内容质量评估中提炼模式，持续改进生成质量。

**依赖**：变更2（需要内容质量评估数据）+ 变更1（需要足够的生成样本量）

**前提条件**：积累了足够多的 eval 结果和内容质量分数（建议 ≥ 50 个生成样本）。

**范围**：

- 分析 eval 失败模式，提炼常见问题
- 分析内容质量低分维度，生成针对性改进规则
- 将提炼的规则注入到 RequirementAnalyzer 或 LLM prompt 中
- 经验存储在 `~/.skill-forge/experience/` 目录

**不包含**：

- 不自动修改蓝图
- 不用 LLM 做模式提炼
- 不做远程经验同步

**验收标准**：

1. 经验规则能提升特定 task_type 的生成质量分
2. 经验积累是增量的 — 新规则不破坏旧规则的改进效果
3. 经验规则可解释 — 能查看某条规则是从哪些失败案例中提炼的
4. 清空经验目录后生成行为回退到无经验状态

**主要影响文件**：

- 新增 `src/skill_forge/experience/` 模块
- `src/skill_forge/requirement/analyzer.py` — 注入经验规则
- `src/skill_forge/llm/refiner.py` — 注入经验提示
- `tests/test_experience.py`（新增）

**风险**：

- 经验规则可能过拟合少量样本
- 规则冲突时优先级不明确

**实施前置条件**：

在实施此变更前，应确认：

> 已积累 ≥ 50 个生成样本的 eval 结果和内容质量数据。

如果数据不足，此变更应推迟。

---

## 6. 变更依赖图

```
变更1: LLM字段级内容生成
  ├── 最小内容质量基线
  ├── 变更2: 内容质量评估
  │       │
  │       ▼
  │  变更4: RAG（需语料库质量达标）
  │       │
  │       ▼
  │  变更5: 经验积累（需 ≥50 样本）
  │
  ▼
变更3: 智能降级（需先证明 LLM 字段生成有收益）
```

变更2 可在变更1后扩展质量体系；变更3 必须等变更1的收益验证完成后再改变默认行为。

---

## 7. 实施优先级与节奏

| 顺序 | 变更 | 预期工作量 | 前置条件 | 价值 |
|------|------|-----------|---------|------|
| 1 | LLM字段级内容生成 | 中 | 无 | **核心增量** — 直接提升生成质量，并用最小质量基线验证收益 |
| 2 | 内容质量评估规则 | 中 | 变更1 | 量化改进 — 知道 LLM 到底好了多少 |
| 3 | 智能降级与自动策略选择 | 小 | 变更1收益验证通过 | 降低使用门槛 — 用户不需要知道 LLM |
| 4 | RAG | 中 | 变更1 + 语料库质量 | 锦上添花 — 依赖数据，可能推迟 |
| 5 | 经验积累 | 大 | 变更2 + 样本量 | 长期收益 — 依赖数据，很可能推迟 |

**建议：先只做变更1，验证 LLM 生成确实比规则生成好，再决定后续节奏。**

如果变更1的验证结果显示 LLM 生成质量没有显著提升，那整个智能生成路线都需要重新评估，而不是继续投入变更2-5。

---

## 8. 向后兼容性

| 变更 | 向后兼容策略 |
|------|-------------|
| 变更1 | `--llm` 接口不变，行为增强；不传 `--llm` 行为完全不变 |
| 变更2 | 纯增量 — 新增评估维度，不改变已有评分逻辑 |
| 变更3 | 默认行为从"纯规则"变为"自动检测" — 这是行为变更，需 README 和 release note |
| 变更4 | 纯增量 — RAG 是可选增强，不影响非 LLM 路径 |
| 变更5 | 纯增量 — 经验规则是可选注入，清空后回退到无经验 |

---

## 9. 验证策略

每个变更都需要回答一个核心问题：

**变更1**: 同一需求，`--llm` 生成 vs 纯规则生成，最小内容质量分差异多少？
**变更2**: 内容质量分数与人工判断的相关性如何？
**变更3**: 自动检测是否正确判断 LLM 可用性？降级是否无缝？
**变更4**: 有 RAG vs 无 RAG，LLM 生成质量差异多少？
**变更5**: 有经验 vs 无经验，生成质量差异多少？

如果任何变更的答案是"没有显著差异"，应该停止该方向，而不是继续投入。

---

## 10. 与 V1 方案的对照

| V1 概念 | V2 处理 | 理由 |
|---------|---------|------|
| 5层能力分层 | 取消 — 实际为3层（规则→LLM生成→验证） | Layer 2与3边界模糊，5层过度设计 |
| Intent Analyzer | 不独立引入 — 保持现有 RequirementAnalyzer | 规则分析够用，等有数据再说 |
| Capability Router | 不引入 — 用自动检测+降级替代 | 用户不需要理解策略概念 |
| `--strategy` 选项 | 不引入 — 用 `--llm`/`--no-llm`/自动检测 | 减少认知负担 |
| `--model` 选项 | 不引入 — 保持现有 OpenAI 兼容客户端 | 先验证价值，再增加灵活性 |
| OllamaClient | 不引入 | 硬件依赖，非核心 |
| ModelRegistry | 不引入 | 当前只有一种模型实现，不需要注册 |
| Retrieval Augmentation | 变更4 — 有前置条件，可能推迟 | 语料库质量不足时 RAG 是噪声 |
| ContentQualityValidator | 变更1内置最小基线，变更2扩展完整规则 | 先支撑 LLM 收益验证，再做完整质量体系 |
| Experience Store | 变更5 — 有前置条件，很可能推迟 | 先有数据再建结构 |
| 降级链 | 保留 — 每个变更都内置降级 | 这是 V1 最好的设计 |
