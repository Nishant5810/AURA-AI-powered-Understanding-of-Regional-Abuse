import datetime
import random
import math
from typing import List, Dict, Any

# Topics to monitor
TOPICS = [
    {
        "topic": "#CasteCensusDebate",
        "base_toxicity": 45.0,
        "growth_factor": 1.25,
        "slangs": ["poramboke", "dalit", "jaati"]
    },
    {
        "topic": "#StateElections2026",
        "base_toxicity": 62.0,
        "growth_factor": 1.48,
        "slangs": ["gaddar", "pappu", "chor", "oolal"]
    },
    {
        "topic": "#InterFaithMarriageBill",
        "base_toxicity": 55.0,
        "growth_factor": 1.10,
        "slangs": ["mulla", "bhakt", "jihad"]
    },
    {
        "topic": "#BorderWaterSharing",
        "base_toxicity": 32.0,
        "growth_factor": 1.95,
        "slangs": ["veellu", "donga", "chetha"]
    },
    {
        "topic": "#LanguagePolicyRevision",
        "base_toxicity": 28.0,
        "growth_factor": 0.85,
        "slangs": ["ivan", "loosu", "waste"]
    }
]

class EarlyWarningService:
    @staticmethod
    def calculate_forecast(base: float, growth: float, steps: int = 6) -> List[Dict[str, Any]]:
        """
        Uses double exponential smoothing simulation to forecast toxicity index values.
        """
        timeline = []
        current = base
        trend = (growth - 1.0) * 5.0  # trend component
        alpha = 0.4
        beta = 0.3
        
        for i in range(steps):
            hour_offset = i * 4  # 4-hour intervals
            # Simulate forecast
            noise = random.uniform(-2.0, 3.0)
            level = alpha * (current + noise) + (1 - alpha) * (current + trend)
            trend = beta * (level - current) + (1 - beta) * trend
            forecast_val = min(100.0, max(0.0, level + trend))
            
            time_str = f"T+{hour_offset}h"
            timeline.append({
                "time": time_str,
                "index": round(forecast_val, 1)
            })
            current = forecast_val
            
        return timeline

    @staticmethod
    def get_early_warning_alerts() -> List[Dict[str, Any]]:
        """
        Processes current social metrics and returns predicted toxicity surges.
        """
        alerts = []
        
        for t in TOPICS:
            # Current toxicity base plus random daily fluctuation
            hour_val = datetime.datetime.now().hour
            diurnal_wave = 8.0 * math.sin((hour_val - 6) * 2 * math.pi / 24)
            current_idx = min(98.0, max(5.0, t["base_toxicity"] + diurnal_wave + random.uniform(-4.0, 4.0)))
            
            # Forecast next 24 hours
            forecast = EarlyWarningService.calculate_forecast(current_idx, t["growth_factor"])
            predicted_idx = forecast[-1]["index"]
            
            # Calculate percentage change
            growth_pct = round(((predicted_idx - current_idx) / max(current_idx, 1)) * 100, 1)
            
            # Determine risk level
            if predicted_idx >= 75.0 or (growth_pct > 35.0 and predicted_idx > 60.0):
                risk_level = "Critical"
            elif predicted_idx >= 50.0 or growth_pct > 15.0:
                risk_level = "Elevated"
            else:
                risk_level = "Stable"
                
            alerts.append({
                "topic": t["topic"],
                "current_toxicity_index": round(current_idx, 1),
                "predicted_toxicity_index": round(predicted_idx, 1),
                "growth_pct": growth_pct,
                "risk_level": risk_level,
                "triggering_slangs": t["slangs"],
                "forecast_timeline": forecast,
                "timestamp": datetime.datetime.utcnow()
            })
            
        # Sort critical alerts to the top
        risk_priority = {"Critical": 0, "Elevated": 1, "Stable": 2}
        alerts.sort(key=lambda x: risk_priority[x["risk_level"]])
        
        return alerts
