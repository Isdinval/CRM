from app.services.scoring import compute_score
def test_s(): assert compute_score({"linkedin_activity": "high"})[0] == 15
