from __future__ import annotations

from skill_forge.experience.service import ExperienceStore
from skill_forge.library.manager import SkillLibraryManager
from skill_forge.lifecycle.models import LifecycleEvidence, LifecycleState, LifecycleSummary
from skill_forge.models.generated import GenerationProvenanceMetadata


HEALTHY_QUALITY_THRESHOLD = 90


class LifecycleService:
    def __init__(self, library_manager: SkillLibraryManager, experience_store: ExperienceStore | None = None) -> None:
        self._library_manager = library_manager
        self._experience_store = experience_store

    @property
    def library_manager(self) -> SkillLibraryManager:
        return self._library_manager

    def show(self, skill_name: str) -> LifecycleSummary:
        entry = self._library_manager.show(skill_name)
        return self._build_summary(entry)

    def _build_summary(self, entry) -> LifecycleSummary:
        provenance = entry.provenance
        evidence: list[LifecycleEvidence] = []
        missing_facts: list[str] = []
        applied_experience_rule_ids: list[str] = []
        resolved_experience_rules: list[str] = []

        if provenance is None:
            state: LifecycleState = "unknown"
            reason = "No provenance metadata was found for this Skill package."
            missing_facts.extend(["provenance", "eval-report", "quality metrics", "experience rules"])
            evidence.append(
                LifecycleEvidence(
                    source="package",
                    summary="Skill package exists but lifecycle facts are missing.",
                    details=[str(entry.path)],
                )
            )
            return LifecycleSummary(
                skill_name=entry.name,
                package_path=entry.path,
                state=state,
                reason=reason,
                evidence=evidence,
                missing_facts=missing_facts,
            )

        quality_score = provenance.quality_score
        quality_status = provenance.quality_status
        evidence.append(_provenance_evidence(provenance))

        if provenance.content_quality is not None:
            evidence.append(_quality_evidence(provenance))
        else:
            missing_facts.append("content quality metrics")

        if entry.eval_report is not None:
            report = entry.eval_report
            evidence.append(
                LifecycleEvidence(
                    source="eval-report",
                    summary=f"Eval report: {report.passed}/{report.total} passed, {report.failed} failed.",
                    details=[f"Skill: {report.skill_name}"],
                )
            )
        else:
            missing_facts.append("eval-report")

        if provenance.applied_experience_rule_ids:
            applied_experience_rule_ids = list(provenance.applied_experience_rule_ids)
            experience_evidence = []
            for rule_id in applied_experience_rule_ids:
                rule = self._experience_store.read_rule(rule_id) if self._experience_store is not None else None
                if rule is None:
                    missing_facts.append(f"experience rule {rule_id}")
                    experience_evidence.append(f"{rule_id}: rule definition not found in local experience store")
                    continue
                resolved_experience_rules.append(rule.rule_text)
                experience_evidence.append(
                    f"{rule.id}: {rule.rule_text}"
                    + (f" | priority={rule.priority}" if rule.priority else "")
                )
            evidence.append(
                LifecycleEvidence(
                    source="experience",
                    summary=f"Applied experience rules: {len(applied_experience_rule_ids)}",
                    details=experience_evidence,
                )
            )
        else:
            missing_facts.append("experience-rule usage")

        state, reason = _classify_state(provenance, entry.eval_report)

        return LifecycleSummary(
            skill_name=entry.name,
            package_path=entry.path,
            state=state,
            reason=reason,
            evidence=evidence,
            missing_facts=_dedupe(missing_facts),
            quality_score=quality_score,
            quality_status=quality_status,
            eval_total=entry.eval_report.total if entry.eval_report is not None else None,
            eval_passed=entry.eval_report.passed if entry.eval_report is not None else None,
            eval_failed=entry.eval_report.failed if entry.eval_report is not None else None,
            applied_experience_rule_ids=applied_experience_rule_ids,
            resolved_experience_rules=resolved_experience_rules,
        )


def _classify_state(
    provenance: GenerationProvenanceMetadata,
    eval_report,
) -> tuple[LifecycleState, str]:
    if eval_report is None:
        return "needs-eval", "No eval report is available for this Skill package."
    if eval_report.failed > 0:
        return "regressed", f"Eval report has {eval_report.failed} failing case(s)."
    if provenance.quality_score < HEALTHY_QUALITY_THRESHOLD:
        return "needs-upgrade", f"Quality score {provenance.quality_score}/100 is below the healthy threshold."
    if provenance.quality_status != "valid":
        return "needs-upgrade", f"Quality status is {provenance.quality_status}, so the package is not yet fully healthy."
    return "healthy", "Provenance, quality, and eval signals are all healthy."


def _provenance_evidence(provenance: GenerationProvenanceMetadata) -> LifecycleEvidence:
    details = [
        f"Origin: {provenance.origin_type}",
        f"Generated at: {provenance.generated_at}",
        f"Task type: {provenance.task_type or '-'}",
        f"Target platform: {provenance.target_platform}",
        f"Language: {provenance.language}",
        f"Quality: {provenance.quality_score}/100 ({provenance.quality_status})",
    ]
    if provenance.blueprint_id:
        details.append(f"Blueprint: {provenance.blueprint_id}")
    if provenance.applied_experience_rule_ids:
        details.append(f"Applied experience rules: {', '.join(provenance.applied_experience_rule_ids)}")
    return LifecycleEvidence(
        source="provenance",
        summary="Generation provenance and package metadata are present.",
        details=details,
    )


def _quality_evidence(provenance: GenerationProvenanceMetadata) -> LifecycleEvidence:
    quality = provenance.content_quality
    assert quality is not None
    return LifecycleEvidence(
        source="content-quality",
        summary="Content quality metrics are available.",
        details=[
            f"Workflow specificity: {quality.workflow_specificity:.2f}",
            f"Constraint verifiability: {quality.constraint_verifiability:.2f}",
            f"Quality gate clarity: {quality.quality_gate_clarity:.2f}",
        ],
    )


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        normalized = item.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped
