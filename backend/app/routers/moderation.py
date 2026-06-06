import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import FlaggedContent
from app.schemas import ScanRequest, ScanResponse
from app.services.classifier import ToxicityClassifier
from app.services.explainability import ExplainabilityLayer

router = APIRouter(prefix="/moderation", tags=["Moderation"])

@router.post("/scan", response_model=ScanResponse, status_code=status.HTTP_200_OK)
def scan_text(request: ScanRequest, db: Session = Depends(get_db)):
    """
    Scans content for multi-level regional toxicity, performs transliteration,
    runs explanation highlighting, and records the event in the database.
    """
    try:
        # Run classification
        raw_result = ToxicityClassifier.classify(request.text)
        
        # Enrich with token highlights
        enriched_result = ExplainabilityLayer.enrich_explanation(raw_result)
        
        # Save to DB if toxic or flagged
        db_entry = FlaggedContent(
            input_text=enriched_result["input_text"],
            processed_text=enriched_result["processed_text"],
            detected_language=enriched_result["detected_language"],
            label=enriched_result["label"],
            confidence=enriched_result["confidence"],
            severity=enriched_result["severity"],
            target_community=enriched_result["target_community"],
            reasoning=enriched_result["reasoning"],
            toxic_phrases=json.dumps(enriched_result["toxic_phrases"]),
            suggested_action=enriched_result["suggested_action"]
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        # Map response
        response_data = ScanResponse(
            id=db_entry.id,
            input_text=db_entry.input_text,
            processed_text=db_entry.processed_text or "",
            detected_language=db_entry.detected_language,
            label=db_entry.label,
            confidence=db_entry.confidence,
            severity=db_entry.severity,
            target_community=db_entry.target_community or "General",
            reasoning=db_entry.reasoning or "",
            toxic_phrases=json.loads(db_entry.toxic_phrases or "[]"),
            highlights=enriched_result["highlights"],
            suggested_action=db_entry.suggested_action,
            timestamp=db_entry.timestamp
        )
        
        return response_data
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification service error: {str(e)}"
        )

@router.get("/logs", response_model=List[ScanResponse])
def get_moderation_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve recent scans and flagged contents.
    """
    logs = db.query(FlaggedContent).order_by(FlaggedContent.timestamp.desc()).limit(limit).all()
    
    response_logs = []
    for log in logs:
        toxic_phrases = json.loads(log.toxic_phrases or "[]")
        highlights = ExplainabilityLayer.get_token_highlights(log.input_text, toxic_phrases)
        
        response_logs.append(ScanResponse(
            id=log.id,
            input_text=log.input_text,
            processed_text=log.processed_text or "",
            detected_language=log.detected_language,
            label=log.label,
            confidence=log.confidence,
            severity=log.severity,
            target_community=log.target_community or "General",
            reasoning=log.reasoning or "",
            toxic_phrases=toxic_phrases,
            highlights=highlights,
            suggested_action=log.suggested_action,
            timestamp=log.timestamp
        ))
    return response_logs

@router.post("/logs/{log_id}/action")
def update_moderator_action(log_id: int, action: str, db: Session = Depends(get_db)):
    """
    Override the system's recommended moderator action.
    """
    log_item = db.query(FlaggedContent).filter(FlaggedContent.id == log_id).first()
    if not log_item:
        raise HTTPException(status_code=404, detail="Log entry not found")
        
    log_item.suggested_action = action
    db.commit()
    return {"message": "Suggested action updated successfully", "new_action": action}
