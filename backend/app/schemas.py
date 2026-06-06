from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Scanning Schemas
class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to scan for toxicity")

class ToxicPhrase(BaseModel):
    phrase: str
    category: str
    severity: str

class HighlightToken(BaseModel):
    text: str
    is_toxic: bool

class ScanResponse(BaseModel):
    id: Optional[int] = None
    input_text: str
    processed_text: str
    detected_language: str
    label: str
    confidence: float  # e.g., 0.965 for 96.5%
    severity: str  # "High", "Medium", "Low", "None"
    target_community: str
    reasoning: str
    toxic_phrases: List[str] = []
    highlights: List[HighlightToken] = []
    suggested_action: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

# Slang Schemas
class SlangCreate(BaseModel):
    term: str
    language: str
    definition: Optional[str] = None
    frequency: Optional[int] = 1
    growth_rate: Optional[float] = 0.0
    status: Optional[str] = "New"

class SlangUpdateStatus(BaseModel):
    status: str  # "New", "Monitored", "Blocked"

class SlangResponse(BaseModel):
    id: int
    term: str
    language: str
    definition: Optional[str] = None
    frequency: int
    growth_rate: float
    status: str
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True

# Analytics Schemas
class CategoryMetric(BaseModel):
    category: str
    count: int

class CommunityRiskMetric(BaseModel):
    community: str
    count: int
    severity_distribution: dict  # {"High": count, "Medium": count, ...}

class LanguageMetric(BaseModel):
    language: str
    toxic_count: int
    non_toxic_count: int

class StateHeatmapMetric(BaseModel):
    state: str
    language: str
    intensity: float  # toxicity level scale 0-100
    toxic_count: int

class DashboardAnalyticsResponse(BaseModel):
    total_scans: int
    toxic_scans: int
    toxicity_rate: float  # percentage
    by_category: List[CategoryMetric]
    by_language: List[LanguageMetric]
    by_community: List[CommunityRiskMetric]
    state_heatmap: List[StateHeatmapMetric]
    hourly_trends: List[dict]  # [{"hour": "10:00", "count": 12}, ...]

# Early Warning Schemas
class EarlyWarningAlert(BaseModel):
    topic: str
    current_toxicity_index: float  # 0 to 100
    predicted_toxicity_index: float  # 0 to 100
    growth_pct: float
    risk_level: str  # "Critical", "Elevated", "Stable"
    triggering_slangs: List[str]
    forecast_timeline: List[dict]  # [{"time": "T+1h", "index": 45}, ...]
    timestamp: datetime
