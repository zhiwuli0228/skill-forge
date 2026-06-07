from pathlib import Path

from pydantic import BaseModel

from skill_forge.models.collection import CollectionRecord
from skill_forge.models.eval import SkillEvalReport
from skill_forge.models.generated import GenerationProvenanceMetadata


class SkillLibraryEntry(BaseModel):
    name: str
    frontmatter_name: str | None = None
    description: str | None = None
    path: Path
    skill_md_path: Path
    reference_count: int = 0
    asset_count: int = 0
    script_count: int = 0
    provenance: GenerationProvenanceMetadata | None = None
    eval_report: SkillEvalReport | None = None
    collection_record: CollectionRecord | None = None
