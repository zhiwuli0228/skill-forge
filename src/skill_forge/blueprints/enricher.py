from skill_forge.blueprints.loader import BlueprintLoader
from skill_forge.blueprints.loader import LoadedBlueprint
from skill_forge.models.blueprint import BlueprintGeneratedFile, SkillBlueprint
from skill_forge.models.requirement import SkillRequirement


class BlueprintRequirementEnricher:
    def __init__(self, loader: BlueprintLoader | None = None) -> None:
        self._loader = loader or BlueprintLoader()

    def enrich(self, requirement: SkillRequirement, *, blueprint_id: str | None = None) -> SkillRequirement:
        record = self._loader.get_record(blueprint_id) if blueprint_id else self._loader.find_record_by_task_type(requirement.task_type)
        if record is None:
            return requirement

        return merge_loaded_blueprint_defaults(requirement, record)


def merge_loaded_blueprint_defaults(requirement: SkillRequirement, record: LoadedBlueprint) -> SkillRequirement:
    return merge_blueprint_defaults(requirement, record.blueprint, source=record.source)


def merge_blueprint_defaults(requirement: SkillRequirement, blueprint: SkillBlueprint, *, source: str | None = None) -> SkillRequirement:
    data = requirement.model_dump()
    for field_name in (
        "when_to_use",
        "when_not_to_use",
        "required_inputs",
        "workflow",
        "constraints",
        "expected_outputs",
        "quality_gates",
    ):
        data[field_name] = merge_list_values(data[field_name], getattr(blueprint, field_name))
    for field_name in ("references", "assets", "scripts"):
        data[field_name] = merge_generated_files(data[field_name], getattr(blueprint, field_name))
    data["references_needed"] = data["references_needed"] or bool(data["references"])
    data["assets_needed"] = data["assets_needed"] or bool(data["assets"])
    data["scripts_needed"] = data["scripts_needed"] or bool(data["scripts"])
    data["applied_blueprint_id"] = blueprint.id
    data["applied_blueprint_source"] = source
    return SkillRequirement.model_validate(data)


def merge_list_values(primary: list[str], defaults: list[str]) -> list[str]:
    merged = list(primary)
    seen = {item.casefold() for item in merged}
    for item in defaults:
        key = item.casefold()
        if key not in seen:
            merged.append(item)
            seen.add(key)
    return merged


def merge_generated_files(primary: list, defaults: list[BlueprintGeneratedFile]) -> list:
    merged = list(primary)
    seen = {item["path"].casefold() if isinstance(item, dict) else item.path.casefold() for item in merged}
    for item in defaults:
        key = item.path.casefold()
        if key not in seen:
            merged.append(item)
            seen.add(key)
    return merged
