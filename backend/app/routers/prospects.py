from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import date, datetime
import csv, io, uuid
from fastapi.responses import StreamingResponse
from ..database import get_db
from ..models.orthodontist import Orthodontist
from ..schemas.orthodontist import ProspectCreate, ProspectUpdate, ProspectSummary, ProspectDetail, ProspectListResponse
from ..services.scoring import compute_score, get_tier
router = APIRouter(prefix="/prospects", tags=["prospects"])
@router.get("", response_model=ProspectListResponse)
def get_prospects(tier: Optional[str]=None, region: Optional[str]=None, department: Optional[str]=None, contact_status: Optional[str]=None, practice_type: Optional[str]=None, part_of_dental_network: Optional[bool]=None, assigned_to: Optional[str]=None, page: int=Query(1, ge=1), page_size: int=Query(50, ge=1, le=200), db: Session=Depends(get_db)):
    q = db.query(Orthodontist)
    if tier: q = q.filter(Orthodontist.tier == tier)
    if region: q = q.filter(Orthodontist.region == region)
    if department: q = q.filter(Orthodontist.department == department)
    if contact_status: q = q.filter(Orthodontist.contact_status == contact_status)
    if practice_type: q = q.filter(Orthodontist.practice_type == practice_type)
    if part_of_dental_network is not None: q = q.filter(Orthodontist.part_of_dental_network == part_of_dental_network)
    if assigned_to: q = q.filter(Orthodontist.assigned_to == assigned_to)
    total = q.count()
    items = q.order_by(desc(Orthodontist.prospect_score)).offset((page-1)*page_size).limit(page_size).all()
    return {"items": [ProspectSummary.model_validate(i) for i in items], "total": total, "page": page, "page_size": page_size, "pages": (total+page_size-1)//page_size}
@router.get("/export/csv")
def export(db: Session=Depends(get_db)):
    prospects = db.query(Orthodontist).all()
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(["id", "last_name", "first_name", "email"])
    for p in prospects: writer.writerow([p.id, p.last_name, p.first_name, p.email])
    return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8-sig')), media_type="text/csv; charset=utf-8-sig", headers={"Content-Disposition": f"attachment; filename=prospects.csv"})
@router.post("", response_model=ProspectDetail, status_code=201)
def create(p_in: ProspectCreate, db: Session=Depends(get_db)):
    if db.query(Orthodontist).filter(Orthodontist.email == p_in.email).first(): raise HTTPException(409, "Email exists")
    data = p_in.model_dump()
    s, _ = compute_score(data)
    t = get_tier(s, data.get("manual_tier_override"))
    db_p = Orthodontist(**data, prospect_score=s, tier=t)
    db.add(db_p); db.commit(); db.refresh(db_p)
    res = ProspectDetail.model_validate(db_p)
    _, res.score_breakdown = compute_score(data)
    return res
@router.get("/{id}", response_model=ProspectDetail)
def get_p(id: uuid.UUID, db: Session=Depends(get_db)):
    db_p = db.query(Orthodontist).filter(Orthodontist.id == id).first()
    if not db_p: raise HTTPException(404)
    res = ProspectDetail.model_validate(db_p)
    _, res.score_breakdown = compute_score({c.name: getattr(db_p, c.name) for c in db_p.__table__.columns})
    return res
@router.patch("/{id}", response_model=ProspectDetail)
def update_p(id: uuid.UUID, p_in: ProspectUpdate, db: Session=Depends(get_db)):
    db_p = db.query(Orthodontist).filter(Orthodontist.id == id).first()
    if not db_p: raise HTTPException(404)
    for k, v in p_in.model_dump(exclude_unset=True).items(): setattr(db_p, k, v)
    full = {c.name: getattr(db_p, c.name) for c in db_p.__table__.columns}
    db_p.prospect_score, _ = compute_score(full)
    db_p.tier = get_tier(db_p.prospect_score, db_p.manual_tier_override)
    db.commit(); db.refresh(db_p)
    res = ProspectDetail.model_validate(db_p)
    _, res.score_breakdown = compute_score(full)
    return res
@router.delete("/{id}", status_code=204)
def delete_p(id: uuid.UUID, db: Session=Depends(get_db)):
    db_p = db.query(Orthodontist).filter(Orthodontist.id == id).first()
    if db_p: db.delete(db_p); db.commit()
    return Response(status_code=204)
