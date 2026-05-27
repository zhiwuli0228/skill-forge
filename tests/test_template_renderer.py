from skill_forge.generator.template_renderer import TemplateRenderer
from skill_forge.requirement.analyzer import RequirementAnalyzer


def test_renderer_includes_frontmatter_and_standard_sections() -> None:
    requirement = RequirementAnalyzer().analyze("Java bug 定位 skill")

    content = TemplateRenderer().render_skill_md(requirement)

    assert content.startswith("---\nname: java-bug-investigation\n")
    assert "description:" in content
    for section in (
        "## Purpose",
        "## When to use",
        "## When not to use",
        "## Required inputs",
        "## Workflow",
        "## Constraints",
        "## Output format",
        "## Quality gates",
    ):
        assert section in content
