from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from acxiom_crm.backend.models.opportunity import OpportunityStageEnum, OpportunityStatusEnum

class OpportunityBase(BaseModel):
    opportunity_name: str = Field(..., min_length=2, max_length=150, description="Name or title of opportunity")
    customer_id: int = Field(..., gt=0, description="Associated Customer ID")
    lead_id: Optional[int] = Field(None, gt=0, description="Optional originating Lead ID")
    amount: float = Field(..., description="Deal value in currency (must be > 0)")
    stage: str = Field(default=OpportunityStageEnum.QUALIFICATION)
    probability: float = Field(default=20.0, description="Win probability 0-100%")
    expected_close_date: date = Field(..., description="Anticipated close date (cannot be in the past)")
    status: str = Field(default=OpportunityStatusEnum.OPEN)
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Opportunity Amount must be greater than 0.")
        return round(v, 2)

    @field_validator("probability")
    @classmethod
    def check_probability(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError("Probability must be between 0 and 100.")
        return round(v, 2)

    @field_validator("stage")
    @classmethod
    def check_stage(cls, v: str) -> str:
        if v not in OpportunityStageEnum.ALL:
            raise ValueError(f"Stage must be one of: {', '.join(OpportunityStageEnum.ALL)}")
        return v

    @field_validator("status")
    @classmethod
    def check_status(cls, v: str) -> str:
        if v not in OpportunityStatusEnum.ALL:
            raise ValueError(f"Status must be one of: {', '.join(OpportunityStatusEnum.ALL)}")
        return v

    @model_validator(mode="after")
    def validate_business_rules(self):
        # Expected close date check for active / open opportunities
        if self.stage in OpportunityStageEnum.ACTIVE_STAGES or self.status == OpportunityStatusEnum.OPEN:
            if self.expected_close_date < date.today():
                raise ValueError("Expected Close Date cannot be in the past.")
        return self

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    opportunity_name: Optional[str] = Field(None, min_length=2, max_length=150)
    customer_id: Optional[int] = Field(None, gt=0)
    lead_id: Optional[int] = None
    amount: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[float] = None
    expected_close_date: Optional[date] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Opportunity Amount must be greater than 0.")
        return round(v, 2) if v is not None else None

    @field_validator("probability")
    @classmethod
    def check_probability(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Probability must be between 0 and 100.")
        return round(v, 2) if v is not None else None

    @field_validator("stage")
    @classmethod
    def check_stage(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in OpportunityStageEnum.ALL:
            raise ValueError(f"Stage must be one of: {', '.join(OpportunityStageEnum.ALL)}")
        return v

    @model_validator(mode="after")
    def validate_business_rules(self):
        if self.expected_close_date is not None:
            if self.stage in OpportunityStageEnum.ACTIVE_STAGES or self.status == OpportunityStatusEnum.OPEN:
                if self.expected_close_date < date.today():
                    raise ValueError("Expected Close Date cannot be in the past.")
        return self

class OpportunityResponse(OpportunityBase):
    opportunity_id: int
    customer_name: Optional[str] = None
    assigned_user_name: Optional[str] = None
    weighted_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
