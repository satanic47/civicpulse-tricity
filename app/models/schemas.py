from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Channel(str, Enum):
    VOICE = "VOICE"
    WHATSAPP = "WHATSAPP"
    WEB = "WEB"
    SMS = "SMS"

class CivicCategory(str, Enum):
    ROADS_TRAFFIC = "Roads & Traffic"
    WATER_SEWAGE = "Water Supply & Sewage"
    ELECTRICITY_LIGHTING = "Street Lighting & Power"
    SOLID_WASTE = "Sanitation & Waste Management"
    HEALTH_SAFETY = "Public Safety & Health"
    PUBLIC_TRANSIT = "Public Transit & Mobility"
    URBAN_PARKS = "Parks & Green Spaces"
    OTHER = "General Public Infrastructure"

class GrievanceStatus(str, Enum):
    REPORTED = "REPORTED"
    TRIAGED = "TRIAGED"
    SCHEDULED = "SCHEDULED_INSPECTION"
    IN_DPR = "INCLUDED_IN_DPR"
    RESOLVED = "RESOLVED"

class GrievanceCreate(BaseModel):
    raw_input: str = Field(..., description="Raw citizen voice transcript or message")
    channel: Channel = Channel.WEB
    audio_file_name: Optional[str] = None
    citizen_phone: Optional[str] = None
    location_hint: Optional[str] = None

class Grievance(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    channel: Channel
    raw_input: str
    language_detected: str = "English"
    translated_text: str
    category: CivicCategory
    department: str
    location_raw: str
    sector: str
    lat: float
    lng: float
    urgency_score: int = Field(ge=1, le=10)
    sentiment: str
    summary: str
    status: GrievanceStatus = GrievanceStatus.REPORTED
    upvotes: int = 1
    verified_by_ai: bool = True

class PolicyRecommendation(BaseModel):
    id: str
    title: str
    sector_or_ward: str
    category: str
    affected_population: int
    incident_count: int
    priority_score: float
    estimated_cost_inr: float
    recommended_action: str
    dpr_summary: str
    urgency_level: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HotspotCluster(BaseModel):
    cluster_id: str
    sector: str
    category: str
    incident_count: int
    avg_urgency: float
    center_lat: float
    center_lng: float
    summary: str
    sample_grievances: List[str]

class SectorMetric(BaseModel):
    sector: str
    ward_number: Optional[int] = None
    population: int
    total_incidents: int
    open_incidents: int
    infrastructure_health_score: float  # 0 to 100
    dominant_category: str
    allocated_budget_lakhs: float
