import datetime
import random
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import FlaggedContent, RegionalTrend
from app.schemas import (
    DashboardAnalyticsResponse, CategoryMetric, LanguageMetric, 
    CommunityRiskMetric, StateHeatmapMetric
)
from app.services.slang_monitor import SlangMonitorService

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])

@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Computes telemetry aggregates for safety managers and visual panels."""
    
    
    # 1. Total Scans and Toxicity Counts
    # To simulate non-toxic scans, we take real logs + a multiplier
    toxic_count = db.query(FlaggedContent).filter(FlaggedContent.label != "Non-Toxic").count()
    total_scans = toxic_count + 124  # simulated benign traffic count
    
    # 2. Count by Category
    category_data = db.query(
        FlaggedContent.label, func.count(FlaggedContent.id)
    ).group_by(FlaggedContent.label).all()
    by_category = [CategoryMetric(category=row[0], count=row[1]) for row in category_data]
    
    # 3. Count by Language
    # Fetch from trends table for state accuracy
    trends = db.query(RegionalTrend).all()
    lang_map = {}
    for t in trends:
        if t.language not in lang_map:
            lang_map[t.language] = {"toxic": 0, "nontoxic": 0}
        lang_map[t.language]["toxic"] += t.toxic_count
        lang_map[t.language]["nontoxic"] += t.non_toxic_count
        
    by_language = [
        LanguageMetric(language=k, toxic_count=v["toxic"], non_toxic_count=v["nontoxic"])
        for k, v in lang_map.items()
    ]
    
    # 4. Community Risk Distributions
    community_data = db.query(
        FlaggedContent.target_community, FlaggedContent.severity, func.count(FlaggedContent.id)
    ).group_by(FlaggedContent.target_community, FlaggedContent.severity).all()
    
    community_metrics = {}
    for comm, sev, count in community_data:
        if comm not in community_metrics:
            community_metrics[comm] = {"count": 0, "distribution": {"High": 0, "Medium": 0, "Low": 0}}
        community_metrics[comm]["count"] += count
        community_metrics[comm]["distribution"][sev] = count
        
    by_community = [
        CommunityRiskMetric(
            community=k, count=v["count"], severity_distribution=v["distribution"]
        ) for k, v in community_metrics.items()
    ]
    
    # 5. State Heatmap Data
    state_heatmap = []
    for t in trends:
        total = t.toxic_count + t.non_toxic_count
        intensity = (t.toxic_count / max(total, 1)) * 100.0
        state_heatmap.append(StateHeatmapMetric(
            state=t.state,
            language=t.language,
            intensity=round(intensity, 1),
            toxic_count=t.toxic_count
        ))
        
    # 6. Hourly Spikes Trend (mocked list based on last 6 hours)
    hourly_trends = []
    now = datetime.datetime.now()
    for i in range(6):
        hour_time = now - datetime.timedelta(hours=(5 - i))
        hour_str = hour_time.strftime("%H:00")
        hourly_trends.append({
            "hour": hour_str,
            "count": random.randint(15, 65)
        })
        
    toxicity_rate = round((toxic_count / max(total_scans, 1)) * 100, 1)

    return DashboardAnalyticsResponse(
        total_scans=total_scans,
        toxic_scans=toxic_count,
        toxicity_rate=toxicity_rate,
        by_category=by_category,
        by_language=by_language,
        by_community=by_community,
        state_heatmap=state_heatmap,
        hourly_trends=hourly_trends
    )
