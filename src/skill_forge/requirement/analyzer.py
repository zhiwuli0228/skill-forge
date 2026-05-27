import re

from skill_forge.models.requirement import SkillRequirement


_CJK_PUNCTUATION = "，。；、："


class RequirementAnalyzer:
    def analyze(self, text: str, *, target_platform: str = "opencode", language: str = "zh-CN") -> SkillRequirement:
        normalized = text.strip()
        if not normalized:
            raise ValueError("Requirement cannot be empty.")

        is_java_bug = self._is_java_bug_investigation(normalized)
        task_type = self._derive_task_type(normalized, is_java_bug=is_java_bug)
        name = self._derive_task_name(normalized, task_type, is_java_bug=is_java_bug)
        domain = "software-engineering" if task_type or self._contains_any(normalized, ["code", "代码", "bug", "日志"]) else None

        if is_java_bug:
            return SkillRequirement(
                name=name,
                description=(
                    "Use this skill when investigating Java service bugs from logs, stack traces, "
                    "or source code. Do not use it for new feature design or broad refactoring."
                ),
                domain=domain,
                task_type=task_type,
                target_platform=target_platform,
                language=language,
                when_to_use=[
                    "用户提供错误日志、异常堆栈或问题现象",
                    "需要分析 Java 服务运行时问题",
                    "需要定位存量代码中的缺陷",
                ],
                when_not_to_use=[
                    "新功能设计",
                    "大规模重构",
                    "没有证据的直接代码修改",
                ],
                required_inputs=[
                    "错误日志、异常堆栈或问题现象",
                    "相关源码路径或模块线索",
                    "复现步骤或触发条件",
                ],
                workflow=[
                    "先整理问题现象、日志和堆栈证据",
                    "根据证据定位相关 Java 代码路径",
                    "阅读最小相关代码并建立因果链",
                    "输出根因、修复方案、测试建议和风险",
                ],
                constraints=[
                    "先分析日志和证据",
                    "再阅读相关源码",
                    "未定位根因前不要修改代码",
                    "避免无关重构",
                ],
                expected_outputs=["Symptom", "Evidence", "Root Cause", "Fix Plan", "Test Plan", "Risks"],
                quality_gates=[
                    "根因必须由日志、堆栈或代码证据支撑",
                    "修复方案必须保持范围小且可验证",
                    "测试建议必须覆盖复现路径和回归风险",
                ],
            )

        constraints = self._extract_constraints(normalized)
        expected_outputs = self._extract_expected_outputs(normalized)
        title = self._human_title(name)
        return SkillRequirement(
            name=name,
            description=f"Use this skill when working on {title}. Do not use it when the request lacks enough context.",
            domain=domain,
            task_type=task_type,
            target_platform=target_platform,
            language=language,
            when_to_use=[f"用户需要处理：{normalized}"],
            when_not_to_use=["需求目标不明确", "缺少必要上下文", "任务明显超出该 Skill 边界"],
            required_inputs=["用户需求描述", "相关上下文或约束", "期望输出"],
            workflow=[
                "确认用户目标和边界",
                "收集必要上下文和约束",
                "按步骤执行任务",
                "输出结果、依据和后续建议",
            ],
            constraints=constraints or ["不要臆造缺失信息", "不做超出用户需求范围的修改或建议"],
            expected_outputs=expected_outputs or ["Summary", "Findings", "Recommendations", "Next Steps"],
            quality_gates=[
                "输出必须回应用户原始需求",
                "关键结论必须有依据",
                "风险和不确定性必须明确说明",
            ],
        )

    def _derive_task_type(self, text: str, *, is_java_bug: bool) -> str | None:
        if is_java_bug or self._contains_any(text, ["bug", "定位", "根因"]):
            return "bug-investigation"
        if self._is_openspec_change(text):
            return "openspec-change"
        if self._is_test_generation(text):
            return "test-generation"
        if self._is_code_review(text):
            return "code-review"
        return None

    def _derive_task_name(self, text: str, task_type: str | None, *, is_java_bug: bool) -> str:
        if is_java_bug:
            return "java-bug-investigation"
        match task_type:
            case "code-review":
                return "code-review"
            case "test-generation":
                return "test-generation"
            case "openspec-change":
                return "openspec-change"
            case _:
                return self._derive_name(text)

    def _is_java_bug_investigation(self, text: str) -> bool:
        return self._contains_any(text, ["Java", "java"]) and self._contains_any(text, ["bug", "定位", "根因", "日志"])

    def _is_code_review(self, text: str) -> bool:
        return self._contains_any(
            text,
            [
                "code review",
                "review code",
                "review",
                "pr review",
                "pull request",
                "代码审查",
                "代码评审",
                "审查代码",
                "review 代码",
            ],
        )

    def _is_test_generation(self, text: str) -> bool:
        return self._contains_any(
            text,
            [
                "test generation",
                "generate tests",
                "write tests",
                "unit test",
                "pytest",
                "测试生成",
                "生成测试",
                "测试编写",
                "编写测试",
            ],
        )

    def _is_openspec_change(self, text: str) -> bool:
        return self._contains_any(text, ["openspec"]) and self._contains_any(
            text,
            ["change", "proposal", "spec", "tasks", "archive", "变更", "提案", "规格", "归档", "分析"],
        )

    def _derive_name(self, text: str) -> str:
        ascii_words = re.findall(r"[A-Za-z0-9]+", text.lower())
        if ascii_words:
            words = [word for word in ascii_words if word not in {"a", "an", "the", "skill"}][:5]
            if words:
                if words[-1] != "skill":
                    words.append("skill")
                return "-".join(words)

        mappings = [
            ("日志", "log"),
            ("分析", "analysis"),
            ("需求", "requirement"),
            ("创建", "creation"),
            ("生成", "generation"),
            ("测试", "testing"),
            ("定位", "investigation"),
            ("修复", "fix"),
        ]
        words = [slug for keyword, slug in mappings if keyword in text]
        if not words:
            words = ["custom"]
        if words[-1] != "skill":
            words.append("skill")
        return "-".join(dict.fromkeys(words))

    def _extract_constraints(self, text: str) -> list[str]:
        constraints: list[str] = []
        for marker in ("要求", "必须", "不能", "不要"):
            if marker in text:
                fragment = text.split(marker, 1)[1]
                fragment = re.split(r"[。.;]", fragment, maxsplit=1)[0]
                parts = [part.strip(_CJK_PUNCTUATION + " ") for part in re.split(r"，|,|；|;", fragment)]
                constraints.extend(part for part in parts if part)
        return list(dict.fromkeys(constraints))

    def _extract_expected_outputs(self, text: str) -> list[str]:
        if "输出" not in text:
            return []
        fragment = text.split("输出", 1)[1]
        fragment = re.split(r"[。.;]", fragment, maxsplit=1)[0]
        parts = [part.strip(_CJK_PUNCTUATION + " ") for part in re.split(r"，|,|、|和|及", fragment)]
        return [self._normalize_output_label(part) for part in parts if part]

    def _normalize_output_label(self, label: str) -> str:
        mapping = {
            "根因": "Root Cause",
            "修复方案": "Fix Plan",
            "测试建议": "Test Plan",
            "风险": "Risks",
            "总结": "Summary",
        }
        return mapping.get(label, label)

    def _contains_any(self, text: str, needles: list[str]) -> bool:
        lowered = text.lower()
        return any(needle.lower() in lowered for needle in needles)

    def _human_title(self, name: str) -> str:
        return name.replace("-", " ")
