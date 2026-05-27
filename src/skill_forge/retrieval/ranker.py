from datetime import datetime, timezone

from skill_forge.models.search import CorpusDocument


AUTHORITY_BOOSTS = {
    "official": 0.12,
    "standard": 0.10,
    "reference": 0.06,
    "community": 0.03,
}


class RankingEngine:
    def score(
        self,
        document: CorpusDocument,
        relevance_score: float,
        *,
        platform: str | None = None,
    ) -> tuple[float, float, float, float, float]:
        authority_boost = AUTHORITY_BOOSTS.get(document.authority_level, 0.02)
        completeness_boost = document.completeness * 0.10
        freshness_boost = self._freshness_boost(document.updated_at)
        platform_boost = 0.08 if platform and document.platform == platform else 0.0
        total = relevance_score + authority_boost + completeness_boost + freshness_boost + platform_boost
        return (
            round(total, 6),
            round(authority_boost, 6),
            round(completeness_boost, 6),
            round(freshness_boost, 6),
            round(platform_boost, 6),
        )

    def _freshness_boost(self, updated_at: str | None) -> float:
        if not updated_at:
            return 0.0
        try:
            parsed = datetime.fromisoformat(updated_at)
        except ValueError:
            return 0.0
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        age_days = max((datetime.now(timezone.utc) - parsed).days, 0)
        if age_days <= 7:
            return 0.04
        if age_days <= 30:
            return 0.02
        return 0.0
