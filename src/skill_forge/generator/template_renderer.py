from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from skill_forge.models.requirement import SkillRequirement


class TemplateRenderer:
    def __init__(self, template_root: Path | None = None) -> None:
        root = template_root or Path(__file__).resolve().parents[3] / "templates"
        self._environment = Environment(
            loader=FileSystemLoader(root),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )

    def render_skill_md(self, requirement: SkillRequirement) -> str:
        template = self._environment.get_template("common/SKILL.md.j2")
        return template.render(requirement=requirement, title=self._title(requirement.name), purpose=requirement.description)

    def _title(self, name: str) -> str:
        return " ".join(part.capitalize() for part in name.split("-"))
