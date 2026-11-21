from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from acxiom_crm.backend.models.activity import ActivityTypeEnum

class ActivityBase(BaseModel):
    activity_type: str = Field(default=ActivityTypeEnum.NOTE)
    subject: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    activity_date: datetime = Field(default_factory=datetime.utcnow)
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    assigned_to: int = Field(..., gt=0)
    status: str = Field(default="Completed")

    @field_validator("activity_type")
    @classmethod
    def check_activity_type(cls, v: str) -> str:
        if v not in ActivityTypeEnum.ALL:
            raise ValueError(f"Activity type must be one of: {', '.join(ActivityTypeEnum.ALL)}")
        return v

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    activity_id: int
    assigned_user_name: Optional[str] = None
    customer_name: Optional[str] = None
    lead_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
