from pathlib import Path

from skill_forge.generator.template_renderer import TemplateRenderer
from skill_forge.models.blueprint import BlueprintGeneratedFile
from skill_forge.models.generated import GeneratedSkillPackage
from skill_forge.models.requirement import SkillRequirement


class SkillPackageExistsError(RuntimeError):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Skill package already exists: {path}")
        self.path = path


class UnsafeGeneratedFilePathError(RuntimeError):
    def __init__(self, path: str) -> None:
        super().__init__(f"Generated file path escapes Skill package: {path}")
        self.path = path


class SkillGenerator:
    def __init__(self, renderer: TemplateRenderer | None = None) -> None:
        self._renderer = renderer or TemplateRenderer()

    def generate(self, requirement: SkillRequirement, output_dir: Path) -> GeneratedSkillPackage:
        package_dir = output_dir.expanduser() / requirement.name
        if package_dir.exists():
            raise SkillPackageExistsError(package_dir)

        package_dir.mkdir(parents=True)
        skill_md_path = package_dir / "SKILL.md"
        skill_md_path.write_text(self._renderer.render_skill_md(requirement), encoding="utf-8")
        references = _write_generated_files(package_dir, requirement.references)
        assets = _write_generated_files(package_dir, requirement.assets)
        scripts = _write_generated_files(package_dir, requirement.scripts)

        return GeneratedSkillPackage(
            name=requirement.name,
            path=package_dir,
            target_platform=requirement.target_platform,
            skill_md_path=skill_md_path,
            references=references,
            assets=assets,
            scripts=scripts,
        )


def _write_generated_files(package_dir: Path, files: list[BlueprintGeneratedFile]) -> dict[str, str]:
    written: dict[str, str] = {}
    package_root = package_dir.resolve()
    for file in files:
        destination = (package_dir / file.path).resolve()
        if not destination.is_relative_to(package_root):
            raise UnsafeGeneratedFilePathError(file.path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(file.content, encoding="utf-8")
        written[file.path] = str(destination)
    return written
