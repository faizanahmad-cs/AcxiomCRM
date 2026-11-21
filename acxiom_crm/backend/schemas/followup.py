from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from acxiom_crm.backend.models.followup import FollowUpStatusEnum, FollowUpTypeEnum, RelatedTypeEnum

class FollowUpBase(BaseModel):
    related_type: str = Field(..., description="Customer, Lead, or Opportunity")
    related_id: int = Field(..., gt=0, description="ID of the related record")
    followup_date: datetime = Field(..., description="Scheduled date & time of follow-up")
    followup_type: str = Field(default=FollowUpTypeEnum.CALL)
    subject: str = Field(..., min_length=2, max_length=200)
    remarks: Optional[str] = None
    status: str = Field(default=FollowUpStatusEnum.PLANNED)
    assigned_to: int = Field(..., gt=0, description="User ID responsible for follow-up")

    @field_validator("related_type")
    @classmethod
    def check_related_type(cls, v: str) -> str:
        if v not in RelatedTypeEnum.ALL:
            raise ValueError(f"Related type must be one of: {', '.join(RelatedTypeEnum.ALL)}")
        return v

    @field_validator("followup_type")
    @classmethod
    def check_followup_type(cls, v: str) -> str:
        if v not in FollowUpTypeEnum.ALL:
            raise ValueError(f"Follow-up type must be one of: {', '.join(FollowUpTypeEnum.ALL)}")
        return v

    @field_validator("status")
    @classmethod
    def check_status(cls, v: str) -> str:
        if v not in FollowUpStatusEnum.ALL:
            raise ValueError(f"Status must be one of: {', '.join(FollowUpStatusEnum.ALL)}")
        return v

    @model_validator(mode="after")
    def validate_followup_date(self):
        # Follow-up date cannot be earlier than today for new or planned follow-ups
        if self.status == FollowUpStatusEnum.PLANNED:
            if self.followup_date.date() < date.today():
                raise ValueError("Follow-up date cannot be earlier than today.")
        return self

class FollowUpCreate(FollowUpBase):
    pass

class FollowUpUpdate(BaseModel):
    followup_date: Optional[datetime] = None
    followup_type: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=2, max_length=200)
    remarks: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None

    @field_validator("followup_type")
    @classmethod
    def check_followup_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in FollowUpTypeEnum.ALL:
            raise ValueError(f"Follow-up type must be one of: {', '.join(FollowUpTypeEnum.ALL)}")
        return v

    @field_validator("status")
    @classmethod
    def check_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in FollowUpStatusEnum.ALL:
            raise ValueError(f"Status must be one of: {', '.join(FollowUpStatusEnum.ALL)}")
        return v

    @model_validator(mode="after")
    def validate_followup_date(self):
        if self.followup_date is not None and self.status == FollowUpStatusEnum.PLANNED:
            if self.followup_date.date() < date.today():
                raise ValueError("Follow-up date cannot be earlier than today.")
        return self

class FollowUpResponse(FollowUpBase):
    followup_id: int
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    assigned_user_name: Optional[str] = None
    related_name: Optional[str] = None
    is_overdue: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
