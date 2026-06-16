from app.database import SessionLocal
from app.models.orthodontist import Orthodontist
from app.services.scoring import compute_score, get_tier
def seed():
    db = SessionLocal()
    for i in range(20):
        email = f"o{i}@test.com"
        if not db.query(Orthodontist).filter(Orthodontist.email == email).first():
            p = Orthodontist(first_name=f"O{i}", last_name="T", email=email, practice_name="P", city="C", department="75", region="R", practice_type="solo")
            p.prospect_score, _ = compute_score({"practice_type": "solo"})
            p.tier = get_tier(p.prospect_score)
            db.add(p)
    db.commit()
seed()
