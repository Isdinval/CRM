from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..database import get_db
from ..models.orthodontist import Orthodontist
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
@router.get("/stats")
def stats(db: Session=Depends(get_db)):
    total = db.query(Orthodontist).count()
    tiers = {t: c for t, c in db.query(Orthodontist.tier, func.count(Orthodontist.id)).group_by(Orthodontist.tier).all()}
    for t in ["ambassador", "champion", "early_adopter", "standard"]: tiers.setdefault(t, 0)
    return {"total": total, "by_tier": tiers, "by_contact_status": {}, "by_region": [], "avg_score": 0, "top10": []}
