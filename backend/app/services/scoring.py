def compute_score(p: dict) -> tuple[int, dict]:
    dp = 0
    dp += {"none": 0, "low": 5, "medium": 10, "high": 15}.get(p.get("linkedin_activity", "none"), 0)
    dp += {"none": 0, "low": 3, "medium": 6, "high": 10}.get(p.get("instagram_activity", "none"), 0)
    dp += {"none": 0, "basic": 3, "good": 6, "excellent": 10}.get(p.get("website_quality", "none"), 0)
    if (p.get("google_reviews_avg") or 0) >= 4.5 and (p.get("google_reviews_count") or 0) >= 20: dp += 8
    dp = min(dp, 35)
    inf = 0
    if p.get("has_given_keynote"): inf += 15
    if p.get("has_presented_webinar"): inf += 12
    if p.get("teaches_at_university"): inf += 10
    inf += min(len(p.get("publications", [])), 2) * 5
    if len(p.get("conferences", [])) >= 2: inf += 5
    inf = min(inf, 42)
    ps = 0
    np = p.get("num_practitioners", 1)
    if np >= 5: ps = 10
    elif np >= 3: ps = 7
    elif np >= 2: ps = 4
    tech = 0
    if p.get("uses_voice_dictation"): tech += 7
    if p.get("uses_quote_software"): tech += 5
    if p.get("offers_teleconsultation"): tech += 3
    net = 0
    if p.get("part_of_dental_network"): net += 8
    if p.get("member_of_pro_association"): net += 4
    eng = 0
    if p.get("demo_attended"): eng = 10
    elif p.get("email_link_clicked"): eng = 5
    elif p.get("email_opened"): eng = 2
    total = min(dp + inf + ps + tech + net + eng, 100)
    breakdown = {"total": total, "details": {"digital_presence": {"score": dp, "max": 35}, "professional_influence": {"score": inf, "max": 42}, "practice_size": {"score": ps, "max": 10}, "tech_adoption": {"score": tech, "max": 15}, "network": {"score": net, "max": 8}, "saydo_engagement": {"score": eng, "max": 10}}}
    return total, breakdown
def get_tier(score: int, manual_override: str = None) -> str:
    if manual_override: return manual_override
    if score >= 70: return "ambassador"
    if score >= 45: return "champion"
    if score >= 20: return "early_adopter"
    return "standard"
