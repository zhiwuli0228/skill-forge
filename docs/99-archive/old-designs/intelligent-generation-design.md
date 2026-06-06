# Intelligent Generation - 设计文档

## 1. 背景与目标

### 1.1 为什么需要智能化

当前 Skill Forge 的生成管道是**规则驱动 + 模板填充**模式：

```
用户需求 → 关键词匹配 → task_type 推断 → Blueprint 填充默认值 → Jinja2 渲染 → 输出
```

这套机制在初期快速验证 product-market fit 阶段非常有效，但存在根本局限：

| 问题 | 影响 |
|------|------|
| 规则无法理解语义 | "Java 服务慢查询定位" 和 "Java bug 定位" 被混为同一 task_type |
| Blueprint 是静态 YAML | 无法根据用户需求的复杂度自动调整生成深度 |
| 模板是固定的 | 所有 task_type 共用同一 SKILL.md 结构，bug-investigation 和 test-generation 产出格式相同 |
| LLM 只做精化 | `--llm` 选项只能修辞已有的字段，无法生成新的 workflow/constraints |
| 无学习机制 | 每次生成都是从零开始，不从历史经验中学习 |

### 1.2 智能性路线的目标

在不失去 Skill Forge 核心价值（确定性、可重现、可审计）的前提下：

1. **质量上限提升**：LLM 生成更精准的 workflow、constraints、quality_gates
2. **理解深度提升**：语义理解用户意图，生成更贴合需求的 Skill
3. **自适应生成**：不同类型/复杂度的 Skill 使用不同生成策略
4. **自我进化**：从 eval 反馈和用户反馈中持续改进生成质量

---

## 2. 核心设计原则

### 2.1 能力分层（Capability Tiering）

**核心洞察**：不是所有智能功能都同等依赖 LLM，也不是所有场景都需要 LLM。

```
Generation Pipeline
     │
     ├── Layer 1: 简单理解  (规则)      ← 0 外部依赖
     │     keyword 匹配、task_type 推断、name 派生
     │
     ├── Layer 2: 语义增强  (轻量 LLM 或规则) ← 可选
     │     意图分类、复杂度判断、领域识别
     │
     ├── Layer 3: 内容生成  (强 LLM)   ← 核心智能
     │     workflow 生成、constraints 提炼、quality_gates 设计
     │
     ├── Layer 4: 质量验证  (规则 + 可选 LLM)
     │     结构验证、内容质量评估
     │
     └── Layer 5: 经验积累  (规则)     ← 0 外部依赖
           eval 反馈 → 规则更新
```

### 2.2 模型无关架构（Model-Agnostic）

通过抽象接口解耦 LLM 实现，让系统可以在多种模型之间切换或降级。

```python
# 能力抽象
class ModelCapability(Enum):
    RULE_MATCHING = auto()
    SEMANTIC_UNDERSTANDING = auto()
    TEXT_GENERATION = auto()
    QUALITY_EVALUATION = auto()

# 模型接口
class LLMClient(ABC):
    @property
    @abstractmethod
    def capabilities(self) -> set[ModelCapability]: ...
    
    @property
    @abstractmethod
    def cost_tier(self) -> str: ...  # "free" | "cheap" | "expensive"
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str: ...

# 可用实现
- LocalRuleEngine       # 纯规则，免费，永不宕机
- OllamaClient         # 本地模型，免费但需硬件
- OpenAICompatibleClient # 云端 API，付费但质量稳定
```

### 2.3 降级链（Fallback Chain）

任何层的失败都应有清晰的降级路径，用户永远不会被阻塞。

```
用户请求
     │
     ├── 尝试 Layer 1 (规则) → 永远成功
     │     └→ 基础生成，保证可用性
     │
     ├── 尝试 Layer 2 (轻量 LLM)
     │     ├→ 成功 → 增强意图理解
     │     └→ 失败 → 回退到 Layer 1 结果
     │
     ├── 尝试 Layer 3 (强 LLM 内容生成)
     │     ├→ 成功 → 使用 LLM 生成的 content
     │     └→ 失败 → 回退到 Blueprint 默认值
     │
     └── 尝试 Layer 4 (质量验证)
           ├→ 成功 → 通过验证
           └→ 失败 → 迭代修复或接受带警告的产出
```

### 2.4 经验积累（Experience Accumulation）

LLM 的输出不应该被遗忘，而应该被提炼成系统知识。

```
Eval 失败案例
     │
     ├── 分析失败模式
     │     "workflow 太泛" / "constraints 不可检查" / "quality_gates 太弱"
     │
     ├── 提炼成规则
     │     "workflow steps must be domain-specific"
     │     "constraints must have verifiable conditions"
     │     "quality_gates must have pass/fail criteria"
     │
     └── 更新到 Experience Store
           未来的规则引擎和 LLM prompt 都使用这些经验
```

---

## 3. 架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Create Pipeline                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User Requirement                                                    │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Intent Analyzer                             │   │
│  │  • Rule-based task_type detection (existing)                   │   │
│  │  • NEW: LLM-powered semantic understanding                    │   │
│  │  • NEW: Complexity scoring                                    │   │
│  │  • NEW: Domain context extraction                             │   │
│  └─────────────────────────────┬────────────────────────────────┘   │
│                                │ EnrichedRequirement               │
│                                ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  Retrieval Augmentation                        │   │
│  │  • Query similar skills from corpus                           │   │
│  │  • Extract useful patterns from similar skills                │   │
│  │  • Provide few-shot examples to generator                     │   │
│  └─────────────────────────────┬────────────────────────────────┘   │
│                                │ RetrievalContext                   │
│                                ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 Capability Router                              │   │
│  │                                                              │   │
│  │  strategy = offline   → RuleEngine only                        │   │
│  │  strategy = lean      → RuleEngine + LLM(workflow)           │   │
│  │  strategy = full      → RuleEngine + LLM(all fields)         │   │
│  │                                                              │   │
│  │  [Checks model availability → selects appropriate path]        │   │
│  └─────────────────────────────┬────────────────────────────────┘   │
│                                │ GenerationStrategy                 │
│                                ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 Content Generator                              │   │
│  │                                                              │   │
│  │  Blueprint (structure guardrails)                              │   │
│  │      │                                                        │   │
│  │      ▼                                                        │   │
│  │  LLM Generate / Rule Generate                                 │   │
│  │      │                                                        │   │
│  │      ▼                                                        │   │
│  │  Template Render                                              │   │
│  └─────────────────────────────┬────────────────────────────────┘   │
│                                │ Generated SKILL.md                 │
│                                ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 Quality Validator                              │   │
│  │                                                              │   │
│  │  Structural Validation (always)                               │   │
│  │      - Section presence, frontmatter, format                  │   │
│  │                                                              │   │
│  │  Content Quality Validation (optional LLM)                     │   │
│  │      - Workflow specificity, constraints verifiability         │   │
│  │      - Domain relevance of generated content                  │   │
│  └─────────────────────────────┬────────────────────────────────┘   │
│                                │ ValidationResult                  │
│                                ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │               Experience Accumulator                           │   │
│  │                                                              │   │
│  │  eval failures → pattern analysis → rules update             │   │
│  │  user feedback → quality signals → experience store            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

Supporting Services:
┌─────────────────────────────────────────────────────────────────────┐
│                       Model Registry                                 │
│  • OpenAICompatibleClient (cloud, expensive, high quality)           │
│  • OllamaClient (local, free, medium quality)                       │
│  • LocalRuleEngine (rules, free, deterministic)                     │
│                                                                      │
│                       Strategy Config                                 │
│  • --strategy offline|lean|full                                     │
│  • SKILL_FORGE_GENERATION_STRATEGY env var                          │
│                                                                      │
│                       Experience Store                               │
│  • ~/.skill-forge/experience/                                      │
│  • Pattern rules derived from eval failures                         │
│  • Learned constraints and quality gates                             │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 关键模块

#### 3.2.1 Intent Analyzer

**输入**：用户需求文本
**输出**：语义丰富的 `EnrichedRequirement`

```python
@dataclass
class EnrichedRequirement:
    # 继承 SkillRequirement 的所有字段
    base: SkillRequirement
    
    # 新增语义理解字段
    complexity: ComplexityLevel  # low / medium / high
    domain_context: str | None
    intent: IntentCategory       # bug-investigation / code-review / etc.
    quality_targets: list[str]   # 用户期望的质量维度
    evidence_required: bool      # 是否需要证据链
    stakeholder_hint: str | None # 隐含用户角色
```

**生成策略**：
- 基础字段（name、task_type）→ 规则引擎（确定性）
- 语义字段（complexity、intent）→ LLM 或规则降级

#### 3.2.2 Retrieval Augmentation

**输入**：EnrichedRequirement
**输出**：相似 Skill 及其模式

```python
@dataclass
class RetrievalContext:
    similar_skills: list[SimilarSkill]
    workflow_patterns: list[str]      # 从相似 Skill 提取的有效 workflow
    constraint_patterns: list[str]     # 从相似 Skill 提取的有效 constraints
    quality_gate_patterns: list[str]   # 从相似 Skill 提取的有效 quality gates
    common_pitfalls: list[str]         # 相似 Skill 中常见的失败模式
```

**关键设计**：检索结果不是直接复制，而是作为生成时的参考上下文。

#### 3.2.3 Capability Router

**输入**：EnrichedRequirement、RetrievalContext
**输出**：选定的生成策略和模型

```python
@dataclass
class GenerationPlan:
    strategy: GenerationStrategy
    model: LLMClient
    fields_to_llm_generate: set[str]  # workflow / constraints / quality_gates
    fields_to_rule_generate: set[str]  # when_to_use / when_not_to_use / etc.
    blueprint_overrides: dict          # 从经验库中学到的 overrides
```

**路由逻辑**：
```
if strategy == "offline":
    model = LocalRuleEngine
    fields_to_llm_generate = {}
elif strategy == "lean":
    model = best_available()  # 优先本地模型
    fields_to_llm_generate = {"workflow"}
elif strategy == "full":
    model = best_available()
    fields_to_llm_generate = {"workflow", "constraints", "quality_gates"}
```

#### 3.2.4 Content Generator

**输入**：GenerationPlan、EnrichedRequirement、RetrievalContext
**输出**：填充好的 SkillRequirement

**生成模式**：

```python
# 字段级生成（示例：workflow）
def generate_workflow(requirement: EnrichedRequirement, context: RetrievalContext, model: LLMClient) -> list[str]:
    prompt = f"""
    Generate a workflow for a {requirement.base.task_type} skill.
    
    Context:
    - Target platform: {requirement.base.target_platform}
    - Language: {requirement.base.language}
    - Domain: {requirement.base.domain}
    - Complexity: {requirement.complexity}
    
    Similar skill workflows (for reference, not copying):
    {context.workflow_patterns}
    
    Common pitfalls to avoid:
    {context.common_pitfalls}
    
    Generate 4-8 specific, actionable workflow steps.
    Return as a JSON array of strings.
    """
    return model.generate(prompt)
```

#### 3.2.5 Quality Validator

**结构验证**（现有实现，保持不变）：
- frontmatter 存在性
- section 完整性
- 格式正确性

**内容质量验证**（新增）：

```python
@dataclass
class ContentQualityCriteria:
    workflow_specificity: float      # workflow 是否具体可执行
    constraint_verifiability: float  # constraints 是否可检查
    quality_gate_clarity: float     # quality_gates 是否有明确通过/失败标准
    domain_relevance: float         # 内容与目标领域的相关性
    overall_score: float

def assess_content_quality(requirement: SkillRequirement, context: RetrievalContext) -> ContentQualityCriteria:
    # 使用规则 + 可选 LLM 评估
    # 返回各项分数和综合分数
```

#### 3.2.6 Experience Accumulator

**输入**：Eval 失败案例、用户反馈、生成质量报告
**输出**：更新经验库

```python
class ExperienceStore:
    def record_eval_failure(self, skill_name: str, failure_type: str, details: str):
        """记录 eval 失败，触发模式分析"""
        
    def record_quality_warning(self, skill_name: str, warning_type: str):
        """记录质量警告"""
        
    def get_generation_hints(self, task_type: str) -> list[GenerationHint]:
        """获取针对特定 task_type 的生成提示"""
        
    def get_constraint_templates(self, task_type: str) -> list[str]:
        """获取针对特定 task_type 的 constraint 模板"""
```

**经验库的存储格式**：
```
~/.skill-forge/experience/
├── patterns/
│   ├── bug-investigation/
│   │   ├── workflow_patterns.yaml   # 从成功案例中提取
│   │   └── common_pitfalls.yaml    # 从失败案例中提取
│   ├── code-review/
│   └── ...
├── constraint_templates/
│   └── {task_type}.yaml
└── quality_thresholds.yaml
```

---

## 4. 数据流

### 4.1 完整生成流程

```
1. user: "Java 存量代码 bug 定位 skill"
         │
2. Intent Analyzer (规则 + 可选 LLM)
         │ EnrichedRequirement(
         │   base: SkillRequirement(...),
         │   complexity: "medium",
         │   domain_context: "legacy-java",
         │   intent: bug-investigation,
         │   evidence_required: true,
         │   stakeholder_hint: "developer"
         │ )
         ▼
3. Retrieval Augmentation
         │ RetrievalContext(
         │   similar_skills: [java-bug-skill, python-debug-skill],
         │   workflow_patterns: ["整理日志证据", "定位代码路径", ...],
         │   common_pitfalls: ["未经验证直接修改代码"],
         │ )
         ▼
4. Capability Router
         │ GenerationPlan(
         │   strategy: full,
         │   model: OpenAICompatibleClient,
         │   fields_to_llm_generate: {workflow, constraints, quality_gates},
         │ )
         ▼
5. Content Generator
         │
         ├── BlueprintRequirementEnricher (填充默认值)
         │
         ├── LLM Generate workflow
         │   prompt: "你是 Skill Forge 助手，为 {intent} 类型 Skill 生成 workflow..."
         │   → ["整理问题现象和日志证据", "定位相关 Java 代码路径", ...]
         │
         ├── LLM Generate constraints
         │   prompt: "为这个 bug investigation skill 生成 constraints..."
         │   → ["根因未明确前不得修改代码", "修复范围应保持小且可验证", ...]
         │
         └── LLM Generate quality_gates
             prompt: "为这个 skill 生成 quality gates..."
             → ["根因必须有日志或代码证据支撑", "修复方案必须附回归测试", ...]
         ▼
6. Template Renderer → SKILL.md
         ▼
7. Quality Validator
         │
         ├── Structural: PASS (section 都存在)
         │
         └── Content: 
             ├── workflow_specificity: 0.85 (具体、可执行)
             ├── constraint_verifiability: 0.90 (可检查)
             ├── quality_gate_clarity: 0.80 (有明确标准)
             └── ContentQualityCriteria(...)
         
         如果内容质量分数低于阈值 → 迭代修复或接受带警告
         ▼
8. Experience Accumulator
         │ eval 结果（如果有）→ 分析失败模式 → 更新经验库
         ▼
9. skill-forge.json + SKILL.md + eval-report.json
```

### 4.2 降级场景

#### 场景 1：完全离线（strategy=offline）

```
用户: "Java bug skill"
         │
Intent Analyzer: (规则引擎，0 外部依赖)
         │ complexity=medium, intent=bug-investigation
         ▼
Retrieval Augmentation: (本地语料库，0 外部依赖)
         │ 找到 2 个相似 Skill
         ▼
Capability Router: (策略=offline)
         │ 选择 LocalRuleEngine
         │ fields_to_llm_generate = {}
         ▼
Content Generator:
         │ Blueprint defaults + 规则生成
         │ 无 LLM 调用
         ▼
Quality Validator: (规则引擎)
         │ structural validation only
         ▼
SKILL.md (确定性产出)
```

用户感知："生成成功，始终可用，不花一分钱"

#### 场景 2：云端 LLM 失败，回退到规则

```
用户: "Java bug skill" (strategy=full)
         │
... (流程同上) ...
         │
Content Generator:
         │
         LLM Generate workflow
         │
         ✗ OpenAI API 失败 (网络错误)
         │
         降级到 Blueprint workflow 默认值
         ▼
Quality Validator:
         │ structural: PASS
         │ content: 警告 (workflow 是通用默认值，非定制)
         ▼
SKILL.md (带警告，但可用)
```

用户感知："生成成功（使用默认 workflow）"

---

## 5. 新增配置项

### 5.1 Generation Strategy

```yaml
# ~/.skill-forge/config.yaml
generation:
  strategy: lean  # offline | lean | full
  
  # offline: 完全不使用 LLM，规则 + 语料库
  # lean:    LLM 仅用于 workflow 生成
  # full:    LLM 用于 workflow、constraints、quality_gates
  
  offline_fallback: true    # LLM 失败时是否降级到规则
  local_model_preferred: true  # 优先使用本地模型

model:
  # 优先级列表，按顺序尝试
  providers:
    - type: local
      name: ollama
      model: llama3.2
      base_url: http://localhost:11434
    - type: cloud
      name: openai
      model: gpt-4o-mini
      base_url: https://api.openai.com/v1
      api_key: ${SKILL_FORGE_LLM_API_KEY}
```

### 5.2 命令行接口

```bash
# 智能生成（使用配置的 strategy）
skill-forge create "Java bug investigation skill"

# 指定 strategy
skill-forge create "xxx" --strategy offline  # 完全离线
skill-forge create "xxx" --strategy lean      # 轻度 LLM
skill-forge create "xxx" --strategy full      # 全力 LLM

# 显式指定 LLM（向后兼容）
skill-forge create "xxx" --llm  # 等于 --strategy lean

# 指定模型
skill-forge create "xxx" --model ollama:llama3.2
skill-forge create "xxx" --model openai:gpt-4o-mini

# 禁用降级（仅 LLM 失败时报错）
skill-forge create "xxx" --no-fallback
```

---

## 6. 实现路径

### Phase 1: 架构基础设施（不改变现有行为）

```
目标：建立模型无关架构，不影响现有生成流程

任务：
1. 定义 ModelCapability enum 和 LLMClient 接口
2. 实现 LocalRuleEngine（封装现有规则逻辑）
3. 实现 OllamaClient（本地模型支持）
4. 实现 ModelRegistry（模型注册和选择）
5. 实现 CapabilityRouter（策略到模型的映射）
6. 建立 ExperienceStore 数据结构

产出：
- src/skill_forge/llm/clients.py (新增)
- src/skill_forge/generation/ 目录 (新增)
- 不改变 create 命令的默认行为
```

### Phase 2: 检索增强生成（RAG）

```
目标：将检索结果融入生成流程

任务：
1. 在 create 流程中集成检索步骤
2. 构建 RetrievalContext（相似 Skill 模式提取）
3. 将 RetrievalContext 注入到 LLM prompt（如果有）
4. 验证 RAG 提升生成质量

产出：
- RetrievalContext 类
- 增强的 create 流程（带 retrieval augmentation）
```

### Phase 3: 分层内容生成

```
目标：实现 LLM 字段级生成，支持降级

任务：
1. 实现字段级生成器（workflow、constraints、quality_gates）
2. 实现降级链（LLM → Blueprint 默认值）
3. 实现 GenerationPlan 和字段路由
4. 添加 --strategy 选项
5. 现有 create 命令变为 --strategy=offline 的快捷方式

产出：
- ContentGenerator 类
- 降级链实现
- --strategy 命令行选项
```

### Phase 4: 内容质量验证

```
目标：验证生成内容的质量，不仅是结构

任务：
1. 定义 ContentQualityCriteria 数据模型
2. 实现内容质量评估规则（workflow 特异性、constraint 可检查性等）
3. 实现 ContentQualityValidator
4. 将内容质量分数纳入 eval-report.json

产出：
- ContentQualityValidator
- 增强的 eval-report.json
```

### Phase 5: 经验积累

```
目标：从反馈中学习，持续改进生成质量

任务：
1. 实现 ExperienceStore
2. 实现 eval 失败模式分析
3. 实现规则自动更新机制
4. 实现经验查询接口（供 Generator 使用）

产出：
- ExperienceStore
- ~/.skill-forge/experience/ 数据结构
```

---

## 7. 向后兼容性

| 变更 | 向后兼容策略 |
|------|-------------|
| `--llm` 选项 | 视为 `--strategy lean` |
| 默认生成行为 | 不变（等同于 `--strategy offline`） |
| skill-forge.json 格式 | 扩展字段，新增 strategy_used |
| Blueprint 格式 | 完全不变 |
| 现有 eval 流程 | 完全不变 |

---

## 8. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| LLM 生成质量不稳定 | 降级链 + Blueprint 作为 fallback |
| LLM API 成本失控 | --strategy 选项 + 本地模型优先 |
| 内容质量难以评估 | 规则 + LLM 双重评估，分数透明 |
| 离线场景完全不可用 | offline 策略保证始终可用 |
| 实现复杂度高 | 分 Phase，每个 Phase 独立可用 |
