from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from skill_forge.models.eval import EVAL_REPORT_FILENAME, SkillEvalReport
from skill_forge.models.experience import (
    AppliedExperienceRuleContext,
    ExperienceDerivationResult,
    ExperienceRule,
    ExperienceRuleEvidence,
)
from skill_forge.models.generated import PROVENANCE_METADATA_FILENAME, GenerationProvenanceMetadata
from skill_forge.models.quality import ContentQualityMetrics
from skill_forge.models.requirement import SkillRequirement


MIN_SAMPLE_COUNT = 3
MIN_REPEATED_EVIDENCE_COUNT = 2
LOW_QUALITY_THRESHOLD = 0.6


@dataclass(frozen=True)
class _PackageSnapshot:
    name: str
    path: Path
    provenance: GenerationProvenanceMetadata | None
    eval_report: SkillEvalReport | None


class ExperienceStore:
    def __init__(self, experience_dir: Path) -> None:
        self._experience_dir = experience_dir.expanduser()

    @property
    def experience_dir(self) -> Path:
        return self._experience_dir

    def list_rules(self) -> list[ExperienceRule]:
        if not self._experience_dir.exists():
            return []

        rules: list[ExperienceRule] = []
        for path in sorted(self._experience_dir.glob(f"*{path_suffix()}"), key=lambda item: item.name.lower()):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                rules.append(ExperienceRule.model_validate(data))
            except (OSError, json.JSONDecodeError, ValidationError):
                continue
        return sorted(rules, key=_rule_sort_key)

    def read_rule(self, rule_id: str) -> ExperienceRule | None:
        path = self._experience_dir / f"{rule_id}{path_suffix()}"
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ExperienceRule.model_validate(data)
        except (OSError, json.JSONDecodeError, ValidationError):
            return None

    def write_rule(self, rule: ExperienceRule) -> Path:
        self._experience_dir.mkdir(parents=True, exist_ok=True)
        path = self._experience_dir / f"{rule.id}{path_suffix()}"
        path.write_text(rule.model_dump_json(indent=2), encoding="utf-8")
        return path

    def write_rules(self, rules: list[ExperienceRule]) -> list[Path]:
        return [self.write_rule(rule) for rule in rules]

    def clear(self) -> None:
        if not self._experience_dir.exists():
            return
        for path in self._experience_dir.glob(f"*{path_suffix()}"):
            if path.is_file():
                path.unlink()


class ExperienceService:
    def __init__(self, store: ExperienceStore) -> None:
        self._store = store

    @property
    def store(self) -> ExperienceStore:
        return self._store

    def list_rules(self) -> list[ExperienceRule]:
        return self._store.list_rules()

    def derive_from_output_dir(self, output_dir: Path, *, rebuild: bool = True) -> ExperienceDerivationResult:
        snapshots = self._collect_snapshots(output_dir)
        result = self._derive_from_snapshots(snapshots)
        if rebuild:
            self._store.clear()
        if result.rules:
            self._store.write_rules(result.rules)
        return result

    def apply_to_requirement(self, requirement: SkillRequirement) -> tuple[SkillRequirement, AppliedExperienceRuleContext]:
        selected_rules = self.select_applicable_rules(requirement, self.list_rules())
        if not selected_rules:
            return requirement, AppliedExperienceRuleContext(
                used=False,
                task_type=requirement.task_type,
                language=requirement.language,
                target_platform=requirement.target_platform,
            )

        updated = requirement.model_copy(deep=True)
        summaries: list[str] = []
        applied_ids: list[str] = []
        for rule in selected_rules:
            applied_ids.append(rule.id)
            summaries.append(_rule_summary(rule))
            updated.workflow = _merge_guidance(updated.workflow, rule.workflow_guidance)
            updated.constraints = _merge_guidance(updated.constraints, rule.constraint_guidance)
            updated.quality_gates = _merge_guidance(updated.quality_gates, rule.quality_gate_guidance)

        return updated, AppliedExperienceRuleContext(
            used=True,
            task_type=requirement.task_type,
            language=requirement.language,
            target_platform=requirement.target_platform,
            rule_ids=applied_ids,
            rule_summaries=summaries,
        )

    def build_llm_context(self, requirement: SkillRequirement) -> AppliedExperienceRuleContext:
        _, context = self.apply_to_requirement(requirement)
        return context

    def select_applicable_rules(self, requirement: SkillRequirement, rules: list[ExperienceRule]) -> list[ExperienceRule]:
        if not requirement.task_type:
            return []

        matches = [
            rule
            for rule in rules
            if rule.task_type == requirement.task_type
            and _scope_matches(rule.language, requirement.language)
            and _scope_matches(rule.target_platform, requirement.target_platform)
        ]
        return sorted(matches, key=_rule_selection_key)

    def _collect_snapshots(self, output_dir: Path) -> list[_PackageSnapshot]:
        if not output_dir.exists():
            return []

        snapshots: list[_PackageSnapshot] = []
        for path in sorted(output_dir.iterdir(), key=lambda item: item.name.lower()):
            if not path.is_dir() or not (path / "SKILL.md").is_file():
                continue
            provenance = _read_provenance(path)
            eval_report = _read_eval_report(path)
            snapshots.append(
                _PackageSnapshot(
                    name=path.name,
                    path=path,
                    provenance=provenance,
                    eval_report=eval_report,
                )
            )
        return snapshots

    def _derive_from_snapshots(self, snapshots: list[_PackageSnapshot]) -> ExperienceDerivationResult:
        grouped: dict[tuple[str, str | None, str | None], list[_PackageSnapshot]] = {}
        skipped_packages: list[str] = []
        evidence_count = 0

        for snapshot in snapshots:
            provenance = snapshot.provenance
            if provenance is None or not provenance.task_type:
                skipped_packages.append(snapshot.name)
                continue
            key = (
                provenance.task_type,
                _normalize_scope_value(provenance.language),
                _normalize_scope_value(provenance.target_platform),
            )
            grouped.setdefault(key, []).append(snapshot)

        rules: list[ExperienceRule] = []
        for (task_type, language, target_platform), group in sorted(
            grouped.items(),
            key=lambda item: (item[0][0], item[0][1] or "", item[0][2] or ""),
        ):
            if len(group) < MIN_SAMPLE_COUNT:
                continue
            rules.extend(_derive_eval_rules(task_type, language, target_platform, group))
            rules.extend(_derive_quality_rules(task_type, language, target_platform, group))

        for rule in rules:
            evidence_count += len(rule.evidence)

        return ExperienceDerivationResult(
            rules=sorted(rules, key=_rule_sort_key),
            scanned_packages=len(snapshots),
            skipped_packages=skipped_packages,
            evidence_count=evidence_count,
        )


def path_suffix() -> str:
    return ".json"


def _read_provenance(path: Path) -> GenerationProvenanceMetadata | None:
    metadata_path = path / PROVENANCE_METADATA_FILENAME
    if not metadata_path.is_file():
        return None
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        return GenerationProvenanceMetadata.model_validate(data)
    except (OSError, json.JSONDecodeError, ValidationError):
        return None


def _read_eval_report(path: Path) -> SkillEvalReport | None:
    report_path = path / EVAL_REPORT_FILENAME
    if not report_path.is_file():
        return None
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        return SkillEvalReport.model_validate(data)
    except (OSError, json.JSONDecodeError, ValidationError):
        return None


def _derive_eval_rules(
    task_type: str,
    language: str | None,
    target_platform: str | None,
    group: list[_PackageSnapshot],
) -> list[ExperienceRule]:
    by_pattern: dict[tuple[str, str], list[ExperienceRuleEvidence]] = {}
    latest_generated_at = _latest_generated_at(group)
    for snapshot in group:
        provenance = snapshot.provenance
        report = snapshot.eval_report
        if provenance is None or report is None or report.failed == 0:
            continue
        for result in report.results:
            if result.passed:
                continue
            for assertion in result.assertions:
                if assertion.passed:
                    continue
                pattern = (
                    assertion.assertion,
                    _normalize_message(assertion.message),
                )
                by_pattern.setdefault(pattern, []).append(
                    ExperienceRuleEvidence(
                        source_package=snapshot.name,
                        source_kind="eval-failure",
                        task_type=task_type,
                        language=language,
                        target_platform=target_platform,
                        case_id=result.case_id,
                        assertion=assertion.assertion,
                        message=assertion.message,
                    )
                )

    rules: list[ExperienceRule] = []
    for (assertion, message), evidence in sorted(by_pattern.items(), key=lambda item: item[0]):
        unique_packages = {item.source_package for item in evidence}
        if len(unique_packages) < MIN_REPEATED_EVIDENCE_COUNT:
            continue
        guidance = _eval_guidance(assertion, message)
        rule_text = f"For {task_type}, address repeated eval failures for {assertion}: {message}"
        rules.append(
            _build_rule(
                task_type=task_type,
                language=language,
                target_platform=target_platform,
                priority=80,
                rule_text=rule_text,
                workflow_guidance=guidance["workflow"],
                constraint_guidance=guidance["constraints"],
                quality_gate_guidance=guidance["quality_gates"],
                evidence=evidence,
                derived_at=latest_generated_at,
            )
        )
    return rules


def _derive_quality_rules(
    task_type: str,
    language: str | None,
    target_platform: str | None,
    group: list[_PackageSnapshot],
) -> list[ExperienceRule]:
    dimension_evidence: dict[str, list[ExperienceRuleEvidence]] = {}
    latest_generated_at = _latest_generated_at(group)
    for snapshot in group:
        provenance = snapshot.provenance
        quality = provenance.content_quality if provenance is not None else None
        if provenance is None or quality is None:
            continue
        for dimension, score in _quality_dimensions(quality).items():
            if score >= LOW_QUALITY_THRESHOLD:
                continue
            dimension_evidence.setdefault(dimension, []).append(
                ExperienceRuleEvidence(
                    source_package=snapshot.name,
                    source_kind="quality-dimension",
                    task_type=task_type,
                    language=language,
                    target_platform=target_platform,
                    quality_dimension=dimension,
                    score=score,
                )
            )

    rules: list[ExperienceRule] = []
    for dimension, evidence in sorted(dimension_evidence.items(), key=lambda item: item[0]):
        unique_packages = {item.source_package for item in evidence}
        if len(unique_packages) < MIN_REPEATED_EVIDENCE_COUNT:
            continue
        guidance = _quality_guidance(dimension)
        rule_text = f"For {task_type}, improve {dimension.replace('_', ' ')} based on repeated low scores."
        rules.append(
            _build_rule(
                task_type=task_type,
                language=language,
                target_platform=target_platform,
                priority=50,
                rule_text=rule_text,
                workflow_guidance=guidance["workflow"],
                constraint_guidance=guidance["constraints"],
                quality_gate_guidance=guidance["quality_gates"],
                evidence=evidence,
                derived_at=latest_generated_at,
            )
        )
    return rules


def _build_rule(
    *,
    task_type: str,
    language: str | None,
    target_platform: str | None,
    priority: int,
    rule_text: str,
    workflow_guidance: list[str],
    constraint_guidance: list[str],
    quality_gate_guidance: list[str],
    evidence: list[ExperienceRuleEvidence],
    derived_at: str,
) -> ExperienceRule:
    payload = {
        "task_type": task_type,
        "language": language,
        "target_platform": target_platform,
        "priority": priority,
        "rule_text": rule_text,
        "workflow_guidance": workflow_guidance,
        "constraint_guidance": constraint_guidance,
        "quality_gate_guidance": quality_gate_guidance,
        "evidence": [item.model_dump(mode="json") for item in sorted(evidence, key=_evidence_sort_key)],
        "derived_at": derived_at,
    }
    payload["id"] = _rule_id(payload)
    return ExperienceRule.model_validate(payload)


def _rule_id(payload: dict[str, Any]) -> str:
    normalized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"experience-{digest}"


def _rule_selection_key(rule: ExperienceRule) -> tuple[int, int, str]:
    specificity = sum(1 for value in (rule.language, rule.target_platform) if value is not None)
    return (-specificity, -rule.priority, rule.id)


def _evidence_sort_key(item: ExperienceRuleEvidence) -> tuple[str, str | None, str | None]:
    return (item.source_package, item.case_id or "", item.assertion or "")


def _scope_matches(rule_value: str | None, requirement_value: str | None) -> bool:
    if rule_value is None:
        return True
    if requirement_value is None:
        return False
    return rule_value.casefold() == requirement_value.casefold()


def _normalize_scope_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized or normalized.casefold() == "unknown":
        return None
    return normalized


def _normalize_message(message: str) -> str:
    return " ".join(message.strip().casefold().split())


def _latest_generated_at(group: list[_PackageSnapshot]) -> str:
    generated_at_values = [
        snapshot.provenance.generated_at
        for snapshot in group
        if snapshot.provenance is not None and snapshot.provenance.generated_at.strip()
    ]
    return sorted(generated_at_values)[-1] if generated_at_values else "1970-01-01T00:00:00Z"


def _quality_dimensions(quality: ContentQualityMetrics) -> dict[str, float]:
    return {
        "workflow_specificity": quality.workflow_specificity,
        "constraint_verifiability": quality.constraint_verifiability,
        "quality_gate_clarity": quality.quality_gate_clarity,
    }


def _eval_guidance(assertion: str, message: str) -> dict[str, list[str]]:
    if assertion == "required_sections":
        section = message.rsplit(":", 1)[-1].strip()
        return {
            "workflow": [f"Confirm the {section} section before finishing the Skill."],
            "constraints": [f"Do not complete the Skill until the {section} section is present."],
            "quality_gates": [f"Pass only when the {section} section is included."],
        }
    if assertion == "required_constraints":
        constraint = message.rsplit(":", 1)[-1].strip()
        return {
            "workflow": [f"Check that the constraint '{constraint}' is satisfied during drafting."],
            "constraints": [constraint],
            "quality_gates": [f"Pass only when the constraint '{constraint}' is satisfied."],
        }
    if assertion == "forbidden_phrases":
        phrase = message.rsplit(":", 1)[-1].strip()
        return {
            "workflow": [f"Review the draft to avoid the phrase '{phrase}'."],
            "constraints": [f"Do not use the phrase '{phrase}' in generated content."],
            "quality_gates": [f"Pass only when the phrase '{phrase}' is absent."],
        }
    return {
        "workflow": [f"Address repeated {assertion} failures before completion."],
        "constraints": [f"Do not ignore repeated {assertion} failures."],
        "quality_gates": [f"Pass only when repeated {assertion} failures are resolved."],
    }


def _quality_guidance(dimension: str) -> dict[str, list[str]]:
    if dimension == "workflow_specificity":
        return {
            "workflow": ["Make workflow steps concrete, task-specific, and ordered."],
            "constraints": ["Avoid generic workflow wording that does not describe observable actions."],
            "quality_gates": ["Pass only when the workflow describes concrete actions and sequencing."],
        }
    if dimension == "constraint_verifiability":
        return {
            "workflow": ["Express constraints as observable checks with clear evidence."],
            "constraints": ["Use testable, observable constraints instead of vague advice."],
            "quality_gates": ["Pass only when constraints can be verified from the output or evidence."],
        }
    return {
        "workflow": ["State explicit quality gates with pass/fail criteria."],
        "constraints": ["Avoid vague quality gate language that cannot be checked directly."],
        "quality_gates": ["Pass only when the gate criteria are explicit and testable."],
    }


def _merge_guidance(existing: list[str], guidance: list[str]) -> list[str]:
    merged = list(existing)
    seen = {item.casefold() for item in merged}
    for item in guidance:
        key = item.casefold()
        if key not in seen:
            merged.append(item)
            seen.add(key)
    return merged


def _rule_summary(rule: ExperienceRule) -> str:
    parts = [rule.rule_text]
    if rule.workflow_guidance:
        parts.append(f"workflow: {rule.workflow_guidance[0]}")
    if rule.constraint_guidance:
        parts.append(f"constraints: {rule.constraint_guidance[0]}")
    if rule.quality_gate_guidance:
        parts.append(f"quality gates: {rule.quality_gate_guidance[0]}")
    return " | ".join(parts)


def _rule_sort_key(rule: ExperienceRule) -> tuple[str, int, str]:
    return (rule.task_type, -rule.priority, rule.id)
