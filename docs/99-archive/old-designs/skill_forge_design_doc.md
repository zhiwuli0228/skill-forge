# Skill Forge 设计文档

## 1. 项目概述

### 1.1 项目名称

**Skill Forge**

### 1.2 项目定位

Skill Forge 是一个面向 AI 编程 Agent 的 **Skill 设计、生成、校验、缓存、更新与安装工具**。

它的核心目标不是简单生成一个 `SKILL.md`，而是根据用户需求、项目上下文、官方规范和社区最佳实践，生成可直接用于 Codex、opencode、Claude Code 等 Agent 环境的标准化 Skill 包。

### 1.3 一句话定义

> Skill Forge 是一个可交互、可联网更新、可本地缓存、可恢复草稿、可校验输出、可安装到多 Agent 平台的 Skill 生成工作台。

### 1.4 核心问题

当前 Skill 编写存在以下问题：

1. 不同平台的 Skill 写法不完全一致。
2. Skill 模板相对稳定，但最佳实践会持续变化。
3. 用户通常无法一次性描述清楚适合当前项目的 Skill。
4. 手写 Skill 容易遗漏触发条件、使用边界、输出格式和质量检查。
5. 直接让 LLM 生成 `SKILL.md`，结果不稳定、不可追溯、不可复用。
6. 项目级 Skill 需要结合当前项目约束，例如 `AGENTS.md`、`.opencode/`、`openspec/`、README、项目规则等。

### 1.5 设计目标

Skill Forge 需要满足以下目标：

1. 支持交互式创建 Skill。
2. 支持根据项目上下文生成项目级 Skill。
3. 支持联网更新官方和社区 Skill 资料。
4. 支持本地分层缓存：原文、清洗文本、摘要、结构化模式。
5. 支持生成标准化 Skill 包，而不是只生成 Markdown 字符串。
6. 支持生成后自动校验。
7. 支持安装到目标 Agent 平台的目录。
8. 支持草稿保存和恢复。
9. 支持离线模式、强制刷新和缓存过期提示。
10. 支持后续接入 LLM，但第一版不能强依赖 LLM。

---

## 2. 技术选型

### 2.1 编程语言

使用：

```text
Python 3.11+
```

### 2.2 第一阶段技术栈

| 能力 | 选型 | 说明 |
|---|---|---|
| CLI 框架 | Typer | 命令行入口清晰，类型友好 |
| 交互式问答 | Questionary | 支持选择、确认、文本输入 |
| 终端输出 | Rich | 美化表格、状态、结果展示 |
| 数据模型 | Pydantic | 结构化需求、草稿、配置、校验结果 |
| 配置解析 | PyYAML / pydantic-settings | 配置文件管理 |
| 模板渲染 | Jinja2 | 生成 `SKILL.md` 和辅助文件 |
| HTTP 请求 | httpx | 联网拉取文档、GitHub 内容 |
| HTML 文本提取 | trafilatura / readability-lxml | 提取网页正文 |
| Markdown frontmatter | python-frontmatter | 解析和校验 `SKILL.md` |
| 本地数据库 | SQLite | 保存元数据、摘要、索引信息 |
| 简单检索 | scikit-learn TF-IDF | MVP 检索，不依赖向量数据库 |
| 单元测试 | pytest | 模块测试 |

### 2.3 第一版暂不引入

第一版不引入以下能力：

1. Web UI。
2. 多用户服务。
3. 后台常驻进程。
4. 默认定时联网。
5. 强依赖 LLM。
6. 复杂向量数据库。
7. 插件市场。
8. 自动提交 Git。

---

## 3. 产品形态

### 3.1 CLI 优先

Skill Forge 第一阶段以 CLI 工具形式提供。

命令名称：

```bash
skill-forge
```

### 3.2 核心命令

```bash
skill-forge init
skill-forge update
skill-forge search "<query>"
skill-forge create "<requirement>"
skill-forge create --interactive
skill-forge resume <draft-id>
skill-forge validate <skill-path>
skill-forge install <skill-name> --target <codex|opencode|claude> --scope <project|user>
```

### 3.3 推荐使用方式

快速生成：

```bash
skill-forge create "Java 存量代码 bug 定位 skill"
```

交互式生成：

```bash
skill-forge create "Java 存量代码 bug 定位 skill" --interactive
```

结合当前项目生成：

```bash
skill-forge create "OpenSpec change 创建前需求分析 skill" --project . --interactive
```

强制联网刷新后生成：

```bash
skill-forge create "harness design review skill" --refresh
```

离线生成：

```bash
skill-forge create "git commit workflow skill" --offline
```

---

## 4. 总体架构

### 4.1 架构分层

```text
skill-forge
├── cli                  # 命令行入口层
├── config               # 配置管理层
├── requirement          # 用户需求解析层
├── interaction          # 交互式向导层
├── project_context      # 项目上下文读取层
├── research             # 联网资料更新层
├── corpus               # 本地资料库层
├── retrieval            # 检索与排序层
├── generator            # Skill 生成层
├── validator            # Skill 校验层
├── installer            # 平台安装层
└── storage              # 文件与数据库存储层
```

### 4.2 逻辑流程

```text
用户输入需求
   ↓
需求解析 Requirement Analyzer
   ↓
交互式补全 Interaction Wizard
   ↓
项目上下文读取 Project Context Reader
   ↓
本地资料库检索 Corpus Retriever
   ↓
最佳实践排序 Ranking Engine
   ↓
Skill 生成 Generator
   ↓
Skill 校验 Validator
   ↓
输出 Skill 包
   ↓
可选安装 Installer
```

### 4.3 数据流

```text
User Requirement
   → SkillDraftState
   → SkillRequirement
   → RetrievedSkillExamples
   → GeneratedSkillPackage
   → ValidationResult
   → InstalledSkill
```

---

## 5. 项目目录设计

### 5.1 源码目录

```text
skill-forge/
├── pyproject.toml
├── README.md
├── configs/
│   └── sources.yaml
├── templates/
│   ├── common/
│   │   ├── SKILL.md.j2
│   │   └── reference-checklist.md.j2
│   ├── codex/
│   │   └── SKILL.md.j2
│   ├── opencode/
│   │   └── SKILL.md.j2
│   └── claude/
│       └── SKILL.md.j2
├── src/
│   └── skill_forge/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── constants.py
│       ├── exceptions.py
│       ├── models/
│       │   ├── requirement.py
│       │   ├── draft.py
│       │   ├── source.py
│       │   ├── corpus.py
│       │   ├── generated.py
│       │   └── validation.py
│       ├── requirement/
│       │   └── analyzer.py
│       ├── interaction/
│       │   └── wizard.py
│       ├── project_context/
│       │   ├── reader.py
│       │   └── summarizer.py
│       ├── research/
│       │   ├── updater.py
│       │   ├── web_fetcher.py
│       │   ├── github_client.py
│       │   └── extractor.py
│       ├── corpus/
│       │   ├── store.py
│       │   ├── normalizer.py
│       │   └── indexer.py
│       ├── retrieval/
│       │   ├── retriever.py
│       │   └── ranker.py
│       ├── generator/
│       │   ├── skill_generator.py
│       │   ├── template_renderer.py
│       │   └── platform_adapter.py
│       ├── validator/
│       │   └── skill_validator.py
│       ├── installer/
│       │   └── installer.py
│       └── storage/
│           ├── paths.py
│           ├── sqlite_store.py
│           └── file_store.py
└── tests/
    ├── test_requirement_analyzer.py
    ├── test_wizard.py
    ├── test_store.py
    ├── test_retriever.py
    ├── test_generator.py
    ├── test_validator.py
    └── test_installer.py
```

### 5.2 本地数据目录

```text
~/.skill-forge/
├── config.yaml
├── corpus/
│   ├── raw/
│   ├── normalized/
│   ├── summaries/
│   └── patterns/
├── db/
│   └── skill_forge.sqlite
├── index/
│   ├── tfidf.pkl
│   └── metadata.json
├── drafts/
│   └── <draft-id>.json
├── output/
│   └── <skill-name>/
└── logs/
```

---

## 6. 核心模块设计

## 6.1 CLI 模块

### 6.1.1 职责

CLI 模块负责：

1. 定义命令入口。
2. 接收用户参数。
3. 调用核心服务。
4. 展示执行结果。
5. 处理用户可见错误。

### 6.1.2 命令定义

#### init

```bash
skill-forge init
```

职责：

1. 创建 `~/.skill-forge/` 目录。
2. 创建默认配置文件。
3. 创建 SQLite 数据库。
4. 初始化默认模板。
5. 检查本地环境。

#### update

```bash
skill-forge update
```

职责：

1. 读取 `sources.yaml`。
2. 拉取官方文档和社区资料。
3. 清洗内容。
4. 保存原始和清洗文本。
5. 写入元数据。
6. 更新检索索引。

#### search

```bash
skill-forge search "bug investigation"
```

职责：

1. 从本地资料库检索相关 Skill 样例。
2. 展示名称、来源、摘要、评分。
3. 支持 `--top-k` 参数。

#### create

```bash
skill-forge create "<requirement>" [--interactive] [--project .] [--refresh] [--offline]
```

职责：

1. 解析需求。
2. 检查缓存过期状态。
3. 可选联网更新。
4. 可选进入交互式补全。
5. 可选读取项目上下文。
6. 检索参考资料。
7. 生成 Skill 包。
8. 校验输出。
9. 输出生成路径。

#### resume

```bash
skill-forge resume <draft-id>
```

职责：

1. 读取草稿状态。
2. 从上次中断步骤继续交互。
3. 最终生成 Skill。

#### validate

```bash
skill-forge validate <skill-path>
```

职责：

1. 校验 Skill 目录结构。
2. 校验 `SKILL.md` frontmatter。
3. 校验必需章节。
4. 输出校验结果。

#### install

```bash
skill-forge install <skill-name> --target opencode --scope project
```

职责：

1. 查找本地生成的 Skill 包。
2. 根据目标平台计算安装路径。
3. 拷贝 Skill 目录。
4. 可选覆盖已有 Skill。
5. 输出安装结果。

---

## 6.2 Requirement Analyzer 模块

### 6.2.1 职责

将用户自然语言需求解析为结构化 `SkillRequirement`。

### 6.2.2 输入示例

```text
我需要一个用于 Java 存量代码 bug 定位的 skill，要求先分析日志，再读代码，不能直接修改代码，要输出根因、修复方案和测试建议。
```

### 6.2.3 输出示例

```json
{
  "name": "java-bug-investigation",
  "domain": "software-engineering",
  "task_type": "bug-investigation",
  "target_platform": "opencode",
  "language": "zh-CN",
  "description": "用于根据日志、堆栈和源码定位 Java 存量服务问题",
  "when_to_use": [
    "用户提供错误日志、异常堆栈或问题现象",
    "需要分析 Java 服务运行时问题",
    "需要定位存量代码中的缺陷"
  ],
  "when_not_to_use": [
    "新功能设计",
    "大规模重构",
    "没有证据的直接代码修改"
  ],
  "constraints": [
    "先分析日志和证据",
    "再阅读相关源码",
    "未定位根因前不要修改代码"
  ],
  "expected_outputs": [
    "Symptom",
    "Evidence",
    "Root Cause",
    "Fix Plan",
    "Test Plan",
    "Risks"
  ]
}
```

### 6.2.4 MVP 实现策略

MVP 不依赖 LLM，使用规则解析：

1. 根据关键词识别领域。
2. 根据关键词识别任务类型。
3. 根据固定映射生成默认 name。
4. 提取“要求”“必须”“不要”“输出”等后续短语。
5. 无法识别的字段留给交互式向导补全。

### 6.2.5 后续增强

后续可增加：

```bash
skill-forge create "xxx" --llm
```

通过 LLM 生成更准确的结构化需求。

---

## 6.3 Interaction Wizard 模块

### 6.3.1 职责

交互式补全 Skill 需求，避免用户一次性输入不完整导致 Skill 不适配项目。

### 6.3.2 设计原则

1. 不做问卷地狱。
2. 已经自动识别的信息只让用户确认。
3. 只追问缺失或高风险字段。
4. 每一步都保存草稿。
5. 支持中断后恢复。

### 6.3.3 交互步骤

```text
1. 确认 Skill 名称
2. 确认目标平台
3. 确认使用场景
4. 确认不适用场景
5. 确认输入信息
6. 确认执行流程
7. 确认输出格式
8. 确认质量检查
9. 确认是否读取项目上下文
10. 确认是否生成 references/assets/scripts
```

### 6.3.4 草稿保存

每次回答后保存到：

```text
~/.skill-forge/drafts/<draft-id>.json
```

### 6.3.5 草稿状态

草稿状态包括：

```text
draft
in_progress
ready_to_generate
generated
installed
```

---

## 6.4 Project Context Reader 模块

### 6.4.1 职责

读取当前项目中会影响 Skill 生成的上下文文件。

### 6.4.2 默认读取文件

```text
AGENTS.md
CLAUDE.md
README.md
.opencode/
.claude/
.agents/
openspec/
config.yaml
project.md
```

### 6.4.3 读取策略

1. 只读取文本文件。
2. 跳过大文件、二进制文件、构建产物。
3. 默认限制总字符数。
4. 对项目上下文生成摘要。
5. 将摘要作为 Skill 约束来源，而不是直接把全部项目内容塞入生成器。

### 6.4.4 输出

```json
{
  "project_name": "diagnosis-tool",
  "detected_agent_tools": ["opencode", "openspec"],
  "detected_rules": [
    "must use OpenSpec change workflow",
    "must not modify unrelated files",
    "must include tests"
  ],
  "context_summary": "当前项目使用 opencode 和 OpenSpec，要求需求变更先 proposal，再 design/spec，再实现和验证。"
}
```

---

## 6.5 Research Updater 模块

### 6.5.1 职责

联网更新官方和社区 Skill 资料。

### 6.5.2 资料源配置

文件：

```text
configs/sources.yaml
```

示例：

```yaml
sources:
  - name: openai-codex-skills-docs
    type: docs
    url: https://developers.openai.com/codex/skills
    authority_level: official
    enabled: true

  - name: openai-skills-github
    type: github
    url: https://github.com/openai/skills
    authority_level: official
    enabled: true

  - name: anthropic-agent-skills-docs
    type: docs
    url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
    authority_level: official
    enabled: true

  - name: anthropic-skills-github
    type: github
    url: https://github.com/anthropics/skills
    authority_level: official
    enabled: true

  - name: agent-skills-standard
    type: docs
    url: https://agentskills.io/home
    authority_level: standard
    enabled: true

  - name: opencode-skills-docs
    type: docs
    url: https://opencode.ai/docs/skills/
    authority_level: official
    enabled: true
```

### 6.5.3 更新流程

```text
1. 读取 sources.yaml
2. 对每个 source 判断是否启用
3. 拉取内容
4. 计算 content hash
5. 如果内容未变化，跳过解析
6. 如果内容变化，保存 raw
7. 清洗成 normalized markdown
8. 抽取 Skill 样例或模式
9. 生成摘要
10. 更新 SQLite
11. 重建检索索引
```

### 6.5.4 网络失败策略

1. 单个源失败不影响整体更新。
2. 记录失败原因。
3. 更新完成后展示失败列表。
4. 如果所有源失败，返回非零退出码。

---

## 6.6 Corpus Store 模块

### 6.6.1 职责

管理本地 Skill 资料库。

### 6.6.2 缓存原则

采用分层缓存：

```text
原始内容 raw：保存
清洗文本 normalized：保存
摘要 summary：保存
结构化模式 patterns：保存
元数据 metadata：保存
```

### 6.6.3 为什么不只保存摘要

摘要适合检索，但会丢失模板细节、frontmatter、目录结构、脚本引用和完整约束。

### 6.6.4 为什么不只保存全文

全文噪声大，检索慢，不利于快速排序。

### 6.6.5 存储策略

```text
全文存文件系统
摘要和元数据存 SQLite
检索索引单独保存
```

---

## 6.7 Retrieval & Ranking 模块

### 6.7.1 职责

从本地资料库中检索与用户需求相关的 Skill 样例，并排序。

### 6.7.2 MVP 检索方式

使用 TF-IDF：

1. 对 summary 和 normalized content 建立索引。
2. 查询时根据用户需求检索 top-k。
3. 返回候选 Skill 样例。

### 6.7.3 排序维度

| 维度 | 权重建议 | 说明 |
|---|---:|---|
| 来源权威性 | 0.35 | 官方文档和官方仓库优先 |
| 文本相关性 | 0.25 | 与用户需求匹配程度 |
| 内容完整度 | 0.15 | 是否包含 description/workflow/output |
| 更新时间 | 0.10 | 最近更新优先 |
| 平台匹配 | 0.10 | 与目标平台一致优先 |
| 社区信号 | 0.05 | stars/forks 等 |

### 6.7.4 输出

```json
[
  {
    "name": "skill-creator",
    "source": "openai-skills-github",
    "platform": "codex",
    "summary": "用于创建高质量 skill 的官方 skill",
    "score": 0.91
  }
]
```

---

## 6.8 Generator 模块

### 6.8.1 职责

根据结构化需求、项目上下文、检索结果和目标平台模板生成 Skill 包。

### 6.8.2 生成内容

最小生成内容：

```text
<skill-name>/
└── SKILL.md
```

增强生成内容：

```text
<skill-name>/
├── SKILL.md
├── references/
│   └── checklist.md
└── assets/
    └── output-template.md
```

### 6.8.3 `SKILL.md` 标准章节

```markdown
---
name: example-skill
description: Use this skill when ... Do not use it when ...
---

# Example Skill

## Purpose

## When to use

## When not to use

## Required inputs

## Workflow

## Constraints

## Output format

## Quality gates
```

### 6.8.4 生成策略

MVP 使用模板生成：

1. Jinja2 模板填充。
2. 根据目标平台调整 frontmatter 和路径提示。
3. 根据 task_type 注入默认 workflow。
4. 根据项目上下文注入 constraints。
5. 根据检索样例补充 best practices。

### 6.8.5 后续 LLM 增强

后续增加：

```bash
skill-forge create "xxx" --llm
```

LLM 只负责增强草稿，不直接绕过校验器。

---

## 6.9 Validator 模块

### 6.9.1 职责

对生成的 Skill 包进行静态校验。

### 6.9.2 校验项

| 校验项 | 级别 | 说明 |
|---|---|---|
| Skill 目录存在 | error | 必须 |
| `SKILL.md` 存在 | error | 必须 |
| frontmatter 存在 | error | 必须 |
| `name` 存在 | error | 必须 |
| `description` 存在 | error | 必须 |
| description 非空 | error | 必须 |
| description 足够具体 | warning | 推荐 |
| `Purpose` 存在 | warning | 推荐 |
| `When to use` 存在 | warning | 推荐 |
| `When not to use` 存在 | warning | 推荐 |
| `Workflow` 存在 | warning | 推荐 |
| `Output format` 存在 | warning | 推荐 |
| `Quality gates` 存在 | warning | 推荐 |

### 6.9.3 校验结果

```json
{
  "ok": true,
  "errors": [],
  "warnings": [
    "description could be more specific"
  ]
}
```

---

## 6.10 Installer 模块

### 6.10.1 职责

将生成好的 Skill 安装到目标 Agent 平台目录。

### 6.10.2 支持目标平台

#### opencode

项目级：

```text
<project>/.opencode/skills/<skill-name>/SKILL.md
```

用户级：

```text
~/.config/opencode/skills/<skill-name>/SKILL.md
```

#### Claude Code

用户级：

```text
~/.claude/skills/<skill-name>/SKILL.md
```

项目级可兼容：

```text
<project>/.claude/skills/<skill-name>/SKILL.md
```

#### Codex

Codex 路径通过配置文件指定：

```yaml
platforms:
  codex:
    user_skills_path: "~/.codex/skills"
```

### 6.10.3 覆盖策略

默认不覆盖已有 Skill。

如果已存在：

```text
Skill already exists: .opencode/skills/java-bug-investigation
Overwrite? [y/N]
```

支持：

```bash
skill-forge install java-bug-investigation --target opencode --scope project --force
```

---

## 7. 数据模型设计

## 7.1 SkillRequirement

```python
class SkillRequirement(BaseModel):
    name: str
    description: str
    domain: str | None = None
    task_type: str | None = None
    target_platform: str = "opencode"
    language: str = "zh-CN"
    when_to_use: list[str] = []
    when_not_to_use: list[str] = []
    required_inputs: list[str] = []
    workflow: list[str] = []
    constraints: list[str] = []
    expected_outputs: list[str] = []
    quality_gates: list[str] = []
    references_needed: bool = False
    scripts_needed: bool = False
    assets_needed: bool = False
```

## 7.2 SkillDraftState

```python
class SkillDraftState(BaseModel):
    draft_id: str
    requirement: SkillRequirement
    current_step: str
    status: str = "draft"
    project_path: str | None = None
    project_context_summary: str | None = None
    selected_examples: list[str] = []
    created_at: datetime
    updated_at: datetime
```

## 7.3 SkillSource

```python
class SkillSource(BaseModel):
    name: str
    type: str
    url: str
    authority_level: str
    enabled: bool = True
    last_checked_at: datetime | None = None
```

## 7.4 SkillExample

```python
class SkillExample(BaseModel):
    id: str
    name: str
    source_name: str
    platform: str | None = None
    description: str | None = None
    summary: str | None = None
    full_content_path: str
    tags: list[str] = []
    quality_score: float = 0.0
```

## 7.5 GeneratedSkillPackage

```python
class GeneratedSkillPackage(BaseModel):
    name: str
    path: str
    target_platform: str
    skill_md_path: str
    references: dict[str, str] = {}
    assets: dict[str, str] = {}
    scripts: dict[str, str] = {}
```

## 7.6 ValidationResult

```python
class ValidationIssue(BaseModel):
    level: str
    code: str
    message: str


class ValidationResult(BaseModel):
    ok: bool
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
```

---

## 8. SQLite 表设计

## 8.1 sources

```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    authority_level TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    last_checked_at TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

## 8.2 documents

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    raw_path TEXT,
    normalized_path TEXT,
    content_hash TEXT,
    fetched_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(source_id) REFERENCES sources(id)
);
```

## 8.3 skill_examples

```sql
CREATE TABLE skill_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    name TEXT,
    description TEXT,
    platform TEXT,
    full_content_path TEXT,
    summary TEXT,
    tags TEXT,
    quality_score REAL DEFAULT 0,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(document_id) REFERENCES documents(id)
);
```

## 8.4 skill_patterns

```sql
CREATE TABLE skill_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    source_example_id INTEGER,
    confidence REAL DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY(source_example_id) REFERENCES skill_examples(id)
);
```

## 8.5 drafts

```sql
CREATE TABLE drafts (
    id TEXT PRIMARY KEY,
    state_path TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT
);
```

---

## 9. 配置设计

## 9.1 用户配置

路径：

```text
~/.skill-forge/config.yaml
```

示例：

```yaml
update:
  mode: manual
  stale_after_days: 7
  check_on_create: true
  auto_update_on_create: false

create:
  default_target: opencode
  default_language: zh-CN
  output_dir: ~/.skill-forge/output
  interactive_by_default: false

retrieval:
  top_k: 5
  use_tfidf: true

platforms:
  opencode:
    user_skills_path: ~/.config/opencode/skills
  claude:
    user_skills_path: ~/.claude/skills
  codex:
    user_skills_path: ~/.codex/skills
```

## 9.2 资料源配置

路径：

```text
configs/sources.yaml
```

支持用户覆盖：

```text
~/.skill-forge/sources.yaml
```

---

## 10. 更新策略设计

### 10.1 默认策略

默认手动更新：

```bash
skill-forge update
```

### 10.2 create 时缓存过期提示

当用户执行：

```bash
skill-forge create "xxx"
```

如果距离上次 update 超过 `stale_after_days`，提示：

```text
本地 Skill 资料库已 12 天未更新。是否现在联网更新？ [y/N]
```

### 10.3 强制更新

```bash
skill-forge create "xxx" --refresh
```

### 10.4 离线模式

```bash
skill-forge create "xxx" --offline
```

离线模式不检查网络，只使用本地模板和缓存。

### 10.5 定时更新

第一版不默认实现定时任务。

后续可增加：

```bash
skill-forge schedule enable --weekly
skill-forge schedule disable
```

---

## 11. Skill 生成模板设计

### 11.1 通用 SKILL.md 模板

```jinja2
---
name: {{ requirement.name }}
description: {{ requirement.description }}
---

# {{ title }}

## Purpose

{{ purpose }}

## When to use

{% for item in requirement.when_to_use %}
- {{ item }}
{% endfor %}

## When not to use

{% for item in requirement.when_not_to_use %}
- {{ item }}
{% endfor %}

## Required inputs

{% for item in requirement.required_inputs %}
- {{ item }}
{% endfor %}

## Workflow

{% for step in requirement.workflow %}
{{ loop.index }}. {{ step }}
{% endfor %}

## Constraints

{% for item in requirement.constraints %}
- {{ item }}
{% endfor %}

## Output format

```text
{% for item in requirement.expected_outputs %}
## {{ item }}
{% endfor %}
```

## Quality gates

{% for item in requirement.quality_gates %}
- {{ item }}
{% endfor %}
```

### 11.2 description 生成规则

description 必须同时表达：

1. 什么时候使用。
2. 什么时候不要使用。
3. 目标任务边界。

推荐格式：

```text
Use this skill when <trigger condition>. Do not use it for <excluded scenarios>.
```

中文 Skill 也建议 frontmatter description 使用英文，以提高不同 Agent 的匹配稳定性。

---

## 12. 典型运行流程

### 12.1 快速生成流程

```bash
skill-forge create "Java bug 定位 skill"
```

流程：

```text
1. 解析用户需求
2. 使用默认 target=opencode
3. 检查缓存是否过期
4. 检索本地资料库
5. 生成 Skill
6. 校验 Skill
7. 输出路径
```

### 12.2 交互式项目生成流程

```bash
skill-forge create "OpenSpec change 创建前分析 skill" --project . --interactive
```

流程：

```text
1. 解析用户需求
2. 创建 draft-id
3. 读取项目上下文
4. 进入交互式确认
5. 保存草稿状态
6. 检索相关 Skill 样例
7. 生成 Skill 包
8. 校验结果
9. 用户确认是否安装
10. 安装到 .opencode/skills/
```

---

## 13. 子模块拆分建议

为了让 Codex 高质量实现，建议按以下子模块拆分。

## 13.1 Module 1：项目骨架与 CLI 初始化

### 目标

完成基础项目结构和 CLI 命令框架。

### 范围

1. 创建 `pyproject.toml`。
2. 配置 Typer CLI。
3. 实现 `init` 命令。
4. 创建默认目录。
5. 创建默认配置文件。
6. 创建空 SQLite 数据库。

### 验收标准

```bash
skill-forge --help
skill-forge init
```

执行成功，并生成：

```text
~/.skill-forge/config.yaml
~/.skill-forge/db/skill_forge.sqlite
~/.skill-forge/corpus/
~/.skill-forge/drafts/
~/.skill-forge/output/
```

---

## 13.2 Module 2：数据模型与配置管理

### 目标

实现核心 Pydantic 模型和配置加载。

### 范围

1. `SkillRequirement`
2. `SkillDraftState`
3. `SkillSource`
4. `SkillExample`
5. `GeneratedSkillPackage`
6. `ValidationResult`
7. `AppConfig`
8. 配置默认值和用户覆盖逻辑。

### 验收标准

1. 单元测试覆盖模型默认值。
2. 能读取 `~/.skill-forge/config.yaml`。
3. 缺失配置时能使用默认值。

---

## 13.3 Module 3：Requirement Analyzer

### 目标

实现基于规则的用户需求解析。

### 范围

1. 输入自然语言。
2. 识别 skill name。
3. 识别 domain。
4. 识别 task_type。
5. 提取 constraints。
6. 提取 expected_outputs。
7. 生成默认 when_to_use / when_not_to_use。

### 验收标准

输入：

```text
我需要一个用于 Java 存量代码 bug 定位的 skill，要求先分析日志，再读代码，不能直接修改代码，要输出根因、修复方案和测试建议。
```

能生成合理的结构化结果。

---

## 13.4 Module 4：交互式向导与草稿恢复

### 目标

支持 `create --interactive` 和 `resume <draft-id>`。

### 范围

1. 实现交互式确认。
2. 每一步保存 draft。
3. 支持恢复草稿。
4. 支持跳过已完成步骤。
5. 支持最终进入生成阶段。

### 验收标准

1. 中断后可以通过 `resume` 恢复。
2. 草稿 JSON 内容完整。
3. 交互不会重复追问已确认字段。

---

## 13.5 Module 5：Skill 模板生成器

### 目标

基于模板生成 Skill 包。

### 范围

1. Jinja2 渲染。
2. 生成 `SKILL.md`。
3. 可选生成 `references/checklist.md`。
4. 支持 target platform 参数。
5. 输出到 `~/.skill-forge/output/<skill-name>/`。

### 验收标准

```bash
skill-forge create "Java bug 定位 skill"
```

生成：

```text
~/.skill-forge/output/java-bug-investigation/SKILL.md
```

---

## 13.6 Module 6：Skill Validator

### 目标

实现 Skill 静态校验。

### 范围

1. 检查目录。
2. 检查 `SKILL.md`。
3. 检查 frontmatter。
4. 检查 name / description。
5. 检查推荐章节。
6. 输出 error / warning。

### 验收标准

```bash
skill-forge validate ~/.skill-forge/output/java-bug-investigation
```

输出校验结果。

---

## 13.7 Module 7：Installer

### 目标

支持安装 Skill 到 opencode / claude / codex 路径。

### 范围

1. 计算安装路径。
2. 支持 project/user scope。
3. 复制目录。
4. 避免默认覆盖。
5. 支持 `--force`。

### 验收标准

```bash
skill-forge install java-bug-investigation --target opencode --scope project
```

生成：

```text
./.opencode/skills/java-bug-investigation/SKILL.md
```

---

## 13.8 Module 8：Research Updater 与 Corpus Store

### 目标

支持联网更新和本地资料库缓存。

### 范围

1. 读取 `sources.yaml`。
2. 拉取 docs source。
3. 拉取 GitHub source。
4. 保存 raw。
5. 生成 normalized。
6. 保存 SQLite 元数据。
7. 计算 content hash。
8. 未变化内容跳过。

### 验收标准

```bash
skill-forge update
```

可以更新资料库并写入 SQLite。

---

## 13.9 Module 9：Search / Retrieval

### 目标

支持本地资料库搜索。

### 范围

1. 构建 TF-IDF 索引。
2. 支持 `search` 命令。
3. 返回 top-k 结果。
4. 展示来源、摘要和评分。

### 验收标准

```bash
skill-forge search "bug investigation"
```

能返回相关资料。

---

## 13.10 Module 10：Project Context Reader

### 目标

支持读取项目上下文，并注入生成流程。

### 范围

1. 扫描项目规则文件。
2. 读取 AGENTS.md / README.md / openspec 等。
3. 跳过大文件和二进制。
4. 生成简单摘要。
5. 将摘要转为 constraints。

### 验收标准

```bash
skill-forge create "OpenSpec change skill" --project . --interactive
```

生成 Skill 中包含项目约束。

---

## 14. 开发阶段规划

## Phase 1：本地生成闭环

目标：无网络、无 LLM，也能完整生成、校验、安装 Skill。

包含模块：

1. Module 1：项目骨架与 CLI 初始化
2. Module 2：数据模型与配置管理
3. Module 3：Requirement Analyzer
4. Module 5：Skill 模板生成器
5. Module 6：Skill Validator
6. Module 7：Installer

验收：

```bash
skill-forge init
skill-forge create "Java bug 定位 skill"
skill-forge validate ~/.skill-forge/output/java-bug-investigation
skill-forge install java-bug-investigation --target opencode --scope project
```

## Phase 2：交互式生成

包含模块：

1. Module 4：交互式向导与草稿恢复
2. 完善 create 流程

验收：

```bash
skill-forge create "Java bug 定位 skill" --interactive
skill-forge resume <draft-id>
```

## Phase 3：联网更新和本地资料库

包含模块：

1. Module 8：Research Updater 与 Corpus Store
2. Module 9：Search / Retrieval

验收：

```bash
skill-forge update
skill-forge search "agent skill"
```

## Phase 4：项目上下文增强

包含模块：

1. Module 10：Project Context Reader
2. 生成器注入项目约束

验收：

```bash
skill-forge create "OpenSpec change skill" --project . --interactive
```

## Phase 5：生成质量增强

可选增强：

1. LLM 需求解析。
2. LLM 草稿润色。
3. 更复杂的 ranking。
4. 更完整的 Skill pattern 抽取。

---

## 15. Codex 实现总 Prompt

下面是可以直接给 Codex / opencode 的总任务描述。

```text
You are implementing a Python CLI project named Skill Forge.

Goal:
Build a local-first CLI tool that helps users generate high-quality Agent Skills for Codex, opencode, Claude Code, and compatible AI coding agents.

Core product idea:
Skill Forge is not a one-shot markdown generator. It is an interactive, cache-aware, updateable, resumable, and validated Skill design workspace.

Technical stack:
- Python 3.11+
- Typer for CLI
- Questionary for interactive prompts
- Rich for terminal output
- Pydantic for data models
- Jinja2 for templates
- httpx for network fetching
- SQLite for local metadata storage
- pytest for tests

Core commands:
- skill-forge init
- skill-forge update
- skill-forge search "<query>"
- skill-forge create "<requirement>"
- skill-forge create --interactive
- skill-forge resume <draft-id>
- skill-forge validate <skill-path>
- skill-forge install <skill-name> --target <codex|opencode|claude> --scope <project|user>

MVP constraints:
- Do not require LLM in the first version.
- Do not implement Web UI.
- Do not implement default background scheduled update.
- Do not introduce unnecessary dependencies.
- Use templates instead of hardcoding generated markdown in business logic.
- Keep modules small and testable.
- Add pytest tests for each module.
- Code should be in English.
- Add concise Chinese comments only where logic is complex.

Required phases:
1. Implement project skeleton, CLI, init command, config, and SQLite initialization.
2. Implement data models and config loading.
3. Implement rule-based requirement analyzer.
4. Implement template-based Skill generator.
5. Implement Skill validator.
6. Implement installer for opencode, Claude, and configurable Codex path.
7. Implement interactive wizard and draft resume.
8. Implement research updater and local corpus store.
9. Implement search/retrieval.
10. Implement project context reader.

Quality requirements:
- Every module must have unit tests.
- Generated Skill must include SKILL.md.
- SKILL.md must include frontmatter with name and description.
- Generated Skill should include Purpose, When to use, When not to use, Required inputs, Workflow, Constraints, Output format, and Quality gates.
- Validator must report errors and warnings separately.
- Installer must not overwrite existing skills unless --force is provided.
```

---

## 16. 关键验收标准

### 16.1 最小可用验收

以下命令必须成功：

```bash
skill-forge init
skill-forge create "Java 存量代码 bug 定位 skill"
skill-forge validate ~/.skill-forge/output/java-bug-investigation
skill-forge install java-bug-investigation --target opencode --scope project
```

### 16.2 交互式验收

```bash
skill-forge create "OpenSpec change 创建前需求分析 skill" --interactive
```

必须能够：

1. 自动解析初始需求。
2. 让用户确认关键字段。
3. 保存 draft。
4. 中断后 resume。
5. 生成 Skill。

### 16.3 联网更新验收

```bash
skill-forge update
skill-forge search "skill creator"
```

必须能够：

1. 读取资料源配置。
2. 拉取至少一个 docs source。
3. 保存 raw 和 normalized 内容。
4. 写入 SQLite。
5. search 能检索到内容。

### 16.4 项目上下文验收

```bash
skill-forge create "bug investigation skill" --project . --interactive
```

生成的 Skill 必须能体现项目约束，例如：

1. 不做无关重构。
2. 遵守项目已有开发流程。
3. 保留测试要求。
4. 优先小范围修改。

---

## 17. 风险与约束

### 17.1 风险：交互过多导致用户疲劳

解决方案：

1. 自动解析优先。
2. 只确认关键字段。
3. 支持默认值。
4. 支持快速模式。

### 17.2 风险：联网资料质量不稳定

解决方案：

1. 官方源优先。
2. 社区源默认关闭。
3. 保存来源和更新时间。
4. 使用评分机制。

### 17.3 风险：生成 Skill 不稳定

解决方案：

1. 模板生成优先。
2. LLM 只作为增强。
3. 所有输出必须经过 validator。

### 17.4 风险：项目上下文过大

解决方案：

1. 只读规则类文件。
2. 限制文件大小。
3. 生成摘要后注入。
4. 不直接把整个项目塞入生成器。

### 17.5 风险：覆盖用户已有 Skill

解决方案：

1. 默认不覆盖。
2. 需要 `--force`。
3. 覆盖前可备份。

---

## 18. 当前增强能力与后续扩展方向

### 18.1 可选 LLM 增强

当前已支持：

```bash
skill-forge create "xxx" --llm
```

支持：

1. 更准确的需求解析。
2. 更自然的 workflow 生成。
3. 优化 description、constraints、expected outputs 和 quality gates。
4. LLM 输出仍必须经过 validator 和质量报告。

后续可继续增强：

1. 自动修复 validator warning。
2. 更细粒度的隐私和项目上下文发送策略。

### 18.2 Skill 质量评分

当前已支持生成后质量报告。后续可继续扩展评分维度：

1. 触发条件清晰度。
2. 使用边界完整度。
3. workflow 可执行性。
4. output format 稳定性。
5. quality gates 完整度。

### 18.3 Skill 库管理与版本管理

当前已支持：

```bash
skill-forge list
skill-forge show <skill-name>
skill-forge diff <skill-a> <skill-b>
```

后续可增加：

```bash
skill-forge upgrade <skill-name>
```

### 18.4 Web UI

后续可增加：

```text
FastAPI + React
```

用于可视化编辑 Skill。

### 18.5 多平台导出

支持：

```bash
skill-forge export <skill-name> --target codex
skill-forge export <skill-name> --target claude
skill-forge export <skill-name> --target opencode
```

---

## 19. 最终结论

Skill Forge 的第一版应该坚持以下原则：

1. **Python CLI 优先。**
2. **本地优先，不强依赖 LLM。**
3. **模板生成优先，保证稳定性。**
4. **交互式补全，保证适配项目。**
5. **分层缓存，保证可追溯。**
6. **手动更新为主，避免后台复杂度。**
7. **validator 必须存在，保证输出质量。**
8. **installer 必须存在，保证生成结果真正落地。**

最终，这个项目不是一个普通 Markdown 生成器，而是一个面向 AI Agent 工程化的 **Skill Capability Factory**。
