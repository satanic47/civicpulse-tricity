from typing import List, Dict, Any
from app.core.gemini_engine import GeminiCivicEngine
from app.core.geocoding import TRICITY_SECTORS

class PolicyRecommender:
    """
    Municipal Policy & Capital Project Recommender.
    Converts aggregated citizen feedback + census demographic data into
    actionable government project recommendations with ROI and budget estimates.
    """

    def __init__(self, gemini_engine: GeminiCivicEngine):
        self.gemini = gemini_engine

    def generate_all_recommendations(self, grievances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Group by (sector, category)
        clusters = {}
        for g in grievances:
            key = (g.get("sector", "Sector 17"), g.get("category", "Roads & Traffic"))
            if key not in clusters:
                clusters[key] = []
            clusters[key].append(g)

        recommendations = []
        rec_id = 1

        for (sector, category), items in clusters.items():
            if len(items) >= 2 or any(i.get("urgency_score", 0) >= 8 for i in items):
                meta = TRICITY_SECTORS.get(sector, {"population": 25000, "ward": 1})
                rec = self.gemini.generate_policy_recommendation(sector, category, items, meta)
                rec["id"] = f"DPR-CH-2026-{rec_id:03d}"
                recommendations.append(rec)
                rec_id += 1

        # Sort by priority score descending
        recommendations.sort(key=lambda r: r.get("priority_score", 0), reverse=True)
        return recommendations
