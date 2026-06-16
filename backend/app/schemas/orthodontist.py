import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Literal, Dict
from datetime import datetime, date
PracticeType = Literal["solo", "group", "clinic", "hospital"]
ActivityLevel = Literal["none", "low", "medium", "high"]
WebsiteQuality = Literal["none", "basic", "good", "excellent"]
Source = Literal["linkedin", "referral", "event", "cold_email", "inbound", "other"]
ContactStatus = Literal["not_contacted", "contacted", "demo_done", "proposal_sent", "negotiation", "closed_won", "closed_lost"]
Tier = Literal["ambassador", "champion", "early_adopter", "standard"]
class ProspectBase(BaseModel):
    first_name: str; last_name: str; email: EmailStr; phone: Optional[str] = None; rpps_number: Optional[str] = Field(None, pattern=r'^\d{11}$'); years_of_experience: Optional[int] = Field(None, ge=0, le=60); installation_year: Optional[int] = Field(None, ge=1960, le=datetime.now().year)
    practice_name: str; city: str; department: str = Field(..., pattern=r'^\d{2}$|^2[AB]$|^97[1-6]$'); region: str; practice_type: PracticeType; num_practitioners: int = 1; num_secretaries: int = 0; active_patients_estimate: Optional[int] = None; current_software: Optional[str] = None
    uses_quote_software: bool = False; uses_voice_dictation: bool = False; offers_teleconsultation: bool = False; member_of_pro_association: bool = False; pro_association_name: Optional[str] = None; part_of_dental_network: bool = False; dental_network_name: Optional[str] = None
    linkedin_url: Optional[str] = None; linkedin_followers: Optional[int] = None; linkedin_activity: ActivityLevel = "none"; instagram_url: Optional[str] = None; instagram_followers: Optional[int] = None; instagram_activity: ActivityLevel = "none"; website_url: Optional[str] = None; website_quality: WebsiteQuality = "none"; google_reviews_count: Optional[int] = None; google_reviews_avg: Optional[float] = None
    has_presented_webinar: bool = False; has_given_keynote: bool = False; conferences: List[str] = []; publications: List[str] = []; teaches_at_university: bool = False; university_name: Optional[str] = None
    source: Source = "other"; assigned_to: Optional[str] = None; contact_status: ContactStatus = "not_contacted"; contact_date: Optional[date] = None; next_follow_up: Optional[date] = None; email_opened: bool = False; email_link_clicked: bool = False; demo_attended: bool = False; notes: Optional[str] = None; manual_tier_override: Optional[Tier] = None
    @field_validator('conferences', 'publications')
    @classmethod
    def validate_lists(cls, v, info):
        if len(v) > 20: raise ValueError('Max 20 items')
        limit = 200 if info.field_name == 'conferences' else 300
        for item in v:
            if len(item) > limit: raise ValueError(f'Item max {limit} chars')
        return v
    @model_validator(mode='after')
    def check_req(self) -> 'ProspectBase':
        if self.part_of_dental_network and not self.dental_network_name: raise ValueError('dental_network_name required')
        if self.member_of_pro_association and not self.pro_association_name: raise ValueError('pro_association_name required')
        if self.teaches_at_university and not self.university_name: raise ValueError('university_name required')
        return self
class ProspectCreate(ProspectBase): pass
class ProspectUpdate(ProspectBase):
    first_name: Optional[str] = None; last_name: Optional[str] = None; email: Optional[EmailStr] = None; practice_name: Optional[str] = None; city: Optional[str] = None; department: Optional[str] = None; region: Optional[str] = None; practice_type: Optional[PracticeType] = None; num_practitioners: Optional[int] = None
class ProspectSummary(BaseModel):
    id: uuid.UUID; first_name: str; last_name: str; email: str; city: str; region: str; department: str; practice_name: str; practice_type: str; num_practitioners: int; contact_status: str; assigned_to: Optional[str] = None; next_follow_up: Optional[date] = None; prospect_score: int; tier: str; manual_tier_override: Optional[str] = None; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class ScoreDetail(BaseModel): score: int; max: int
class ScoreBreakdown(BaseModel): total: int; details: Dict[str, ScoreDetail]
class ProspectDetail(ProspectBase):
    id: uuid.UUID; created_at: datetime; updated_at: datetime; prospect_score: int; tier: str; score_breakdown: Optional[ScoreBreakdown] = None
    model_config = ConfigDict(from_attributes=True)
class ProspectListResponse(BaseModel): items: List[ProspectSummary]; total: int; page: int; page_size: int; pages: int
