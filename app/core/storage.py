import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.gemini_engine import GeminiCivicEngine
from app.core.geocoding import resolve_sector, get_all_sector_metadata
from app.core.hotspot_engine import HotspotEngine
from app.core.policy_recommender import PolicyRecommender

class GrievanceStore:
    def __init__(self, data_file: str = "app/data/grievances_db.json", seed_file: str = "app/data/initial_grievances.json"):
        self.data_file = data_file
        self.seed_file = seed_file
        self.gemini = GeminiCivicEngine()
        self.recommender = PolicyRecommender(self.gemini)
        self.grievances: List[Dict[str, Any]] = []
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.grievances = json.load(f)
                    return
            except Exception:
                pass

        if os.path.exists(self.seed_file):
            try:
                with open(self.seed_file, "r", encoding="utf-8") as f:
                    self.grievances = json.load(f)
                    self._save_data()
                    return
            except Exception:
                pass
        self.grievances = []

    def _save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.grievances, f, indent=2, ensure_ascii=False)

    def get_all(self, sector: Optional[str] = None, category: Optional[str] = None, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        results = self.grievances
        if sector:
            results = [g for g in results if g.get("sector") == sector]
        if category:
            results = [g for g in results if g.get("category") == category]
        if channel:
            results = [g for g in results if g.get("channel") == channel]
        return results

    def get_by_id(self, grievance_id: str) -> Optional[Dict[str, Any]]:
        for g in self.grievances:
            if g.get("id") == grievance_id:
                return g
        return None

    def add_grievance(self, raw_input: str, channel: str = "WEB", audio_file: Optional[str] = None, location_hint: Optional[str] = None) -> Dict[str, Any]:
        # 1. AI Analysis & Categorization
        ai_meta = self.gemini.analyze_grievance(raw_input, channel=channel)
        
        # 2. Geocoding & Sector resolution
        geo_text = f"{raw_input} {location_hint or ''}"
        geo_meta = resolve_sector(geo_text)

        new_id = f"INC-2026-{100 + len(self.grievances) + 1}"
        record = {
            "id": new_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "channel": channel,
            "raw_input": raw_input,
            "audio_file": audio_file,
            "language_detected": ai_meta.get("language_detected", "English"),
            "translated_text": ai_meta.get("translated_text", raw_input),
            "category": ai_meta.get("category", "General Public Infrastructure"),
            "department": ai_meta.get("department", "Municipal Corporation Chandigarh"),
            "location_raw": ai_meta.get("location_raw", geo_meta.get("sector", "Chandigarh")),
            "sector": geo_meta.get("sector", "Sector 17"),
            "lat": geo_meta.get("lat", 30.7398),
            "lng": geo_meta.get("lng", 76.7827),
            "urgency_score": ai_meta.get("urgency_score", 5),
            "sentiment": ai_meta.get("sentiment", "neutral"),
            "summary": ai_meta.get("summary", "Citizen infrastructure grievance reported."),
            "status": "TRIAGED",
            "upvotes": 1,
            "verified_by_ai": True
        }

        self.grievances.insert(0, record)
        self._save_data()
        return record

    def upvote(self, grievance_id: str) -> Optional[Dict[str, Any]]:
        for g in self.grievances:
            if g.get("id") == grievance_id:
                g["upvotes"] = g.get("upvotes", 1) + 1
                self._save_data()
                return g
        return None

    def update_status(self, grievance_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        for g in self.grievances:
            if g.get("id") == grievance_id:
                g["status"] = new_status
                self._save_data()
                return g
        return None

    def get_hotspots(self) -> List[Dict[str, Any]]:
        return HotspotEngine.compute_hotspots(self.grievances)

    def get_sector_metrics(self) -> List[Dict[str, Any]]:
        return HotspotEngine.compute_sector_metrics(self.grievances, get_all_sector_metadata())

    def get_policy_recommendations(self) -> List[Dict[str, Any]]:
        return self.recommender.generate_all_recommendations(self.grievances)
