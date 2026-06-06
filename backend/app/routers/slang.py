from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import EmergingSlang
from app.schemas import SlangCreate, SlangResponse, SlangUpdateStatus
from app.services.slang_monitor import SlangMonitorService

router = APIRouter(prefix="/slang", tags=["Slang Monitoring"])

@router.get("/terms", response_model=List[SlangResponse])
def get_emerging_slangs(db: Session = Depends(get_db)):
    """Retrieve all emerging regional slang terms sorted by growth rate."""
    # Seed if empty
    SlangMonitorService.seed_initial_slangs(db)
    return db.query(EmergingSlang).order_by(EmergingSlang.growth_rate.desc()).all()

@router.post("/terms", response_model=SlangResponse)
def add_custom_slang(request: SlangCreate, db: Session = Depends(get_db)):
    """Add a new slang term directly into the monitoring/blocking index."""
    existing = db.query(EmergingSlang).filter(EmergingSlang.term == request.term.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Slang term '{request.term}' is already in the database."
        )
        
    db_slang = EmergingSlang(
        term=request.term.lower().strip(),
        language=request.language,
        definition=request.definition,
        frequency=request.frequency or 1,
        growth_rate=request.growth_rate or 0.0,
        status=request.status or "New"
    )
    db.add(db_slang)
    db.commit()
    db.refresh(db_slang)
    return db_slang

@router.put("/terms/{term_id}", response_model=SlangResponse)
def update_slang_status(term_id: int, payload: SlangUpdateStatus, db: Session = Depends(get_db)):
    """Update status (e.g. approve to 'Blocked' list or transition to 'Monitored')."""
    slang = db.query(EmergingSlang).filter(EmergingSlang.id == term_id).first()
    if not slang:
        raise HTTPException(status_code=404, detail="Slang term not found")
        
    slang.status = payload.status
    db.commit()
    db.refresh(slang)
    return slang

@router.post("/simulate")
def trigger_simulation(db: Session = Depends(get_db)):
    """
    Simulates a time step of incoming social media comment feeds (YouTube, X, Reddit) 
    that dynamically updates the frequency and growth metrics of regional slang.
    """
    updated_count = SlangMonitorService.simulate_social_feed_ingestion(db)
    return {"status": "success", "message": f"Simulated feed step. Updated {updated_count} slang items."}
