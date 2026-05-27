from skill_forge.models.project_context import ProjectContextInput, ProjectContextSummary


TOOL_PATTERNS = (
    ("openspec", ("openspec", "open spec")),
    ("opencode", ("opencode", ".opencode")),
    ("claude", ("claude", ".claude", "CLAUDE.md")),
    ("codex", ("codex", ".codex")),
    ("agents", ("AGENTS.md", ".agents", "agent instructions")),
)

RULE_PATTERNS = (
    (
        "Use the OpenSpec change workflow for requirement changes.",
        ("openspec", "proposal", "design", "spec", "change"),
    ),
    (
        "Run or preserve relevant tests for implementation changes.",
        ("test", "pytest", "unit test", "verification"),
    ),
    (
        "Avoid unrelated modifications outside the requested task.",
        ("unrelated", "do not modify", "avoid unrelated", "scope"),
    ),
    (
        "Keep implementation changes small and aligned with existing project patterns.",
        ("small", "focused", "existing pattern", "minimal"),
    ),
)


class ProjectContextSummarizer:
    def summarize(self, context: ProjectContextInput) -> ProjectContextSummary:
        haystack = "\n".join([file.relative_path + "\n" + file.content for file in context.files])
        haystack_lower = haystack.lower()

        tools = [
            tool
            for tool, patterns in TOOL_PATTERNS
            if any(pattern.lower() in haystack_lower for pattern in patterns)
            or any(pattern in file.relative_path for pattern in patterns for file in context.files)
        ]
        rules = [
            rule
            for rule, patterns in RULE_PATTERNS
            if all(pattern in haystack_lower for pattern in patterns[:1])
            or any(pattern in haystack_lower for pattern in patterns)
        ]

        detected_tools = _dedupe(tools)
        detected_rules = _dedupe(rules)
        derived_constraints = [f"Project constraint: {rule}" for rule in detected_rules]
        if detected_tools:
            derived_constraints.append(f"Project context: detected agent tooling includes {', '.join(detected_tools)}.")

        summary_text = self._summary_text(detected_tools, detected_rules)
        return ProjectContextSummary(
            project_path=context.project_path,
            detected_tools=detected_tools,
            detected_rules=detected_rules,
            summary_text=summary_text,
            derived_constraints=derived_constraints,
        )

    def _summary_text(self, tools: list[str], rules: list[str]) -> str:
        if not tools and not rules:
            return "No explicit project agent tooling or workflow rules detected."
        parts: list[str] = []
        if tools:
            parts.append(f"Detected agent tooling: {', '.join(tools)}.")
        if rules:
            parts.append(f"Detected project rules: {'; '.join(rules)}")
        return " ".join(parts)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result
