from fastapi import APIRouter, status
from typing import List
from app.schemas import EarlyWarningAlert
from app.services.early_warning import EarlyWarningService

router = APIRouter(prefix="/warning", tags=["Early Warning System"])

@router.get("/alerts", response_model=List[EarlyWarningAlert], status_code=status.HTTP_200_OK)
def get_early_warning_alerts():
    """
    Returns predictive alerts highlighting topics with high risk of escalating regional toxicity.
    """
    return EarlyWarningService.get_early_warning_alerts()
