import re
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from acxiom_crm.backend.models.lead import LeadStatusEnum

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{10,20}$")

class LeadBase(BaseModel):
    lead_name: str = Field(..., min_length=2, max_length=150, description="Lead contact or prospect name")
    email: str = Field(..., description="Prospect email address")
    phone: str = Field(..., description="Prospect phone number")
    company_name: Optional[str] = Field(None, max_length=150)
    source: str = Field(default="Website", max_length=50)
    status: str = Field(default=LeadStatusEnum.NEW)
    priority: str = Field(default="Medium")
    expected_value: float = Field(default=0.0, ge=0.0, description="Expected deal value (must be >= 0)")
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("email")
    @classmethod
    def check_email_format(cls, v: str) -> str:
        clean_v = v.strip().lower()
        if not EMAIL_REGEX.match(clean_v):
            raise ValueError("Enter a valid email address.")
        return clean_v

    @field_validator("phone")
    @classmethod
    def check_phone_format(cls, v: str) -> str:
        clean_v = v.strip()
        digits = re.sub(r"\D", "", clean_v)
        if len(digits) < 10 or len(digits) > 15 or not PHONE_REGEX.match(clean_v):
            raise ValueError("Enter a valid phone number.")
        return clean_v

    @field_validator("status")
    @classmethod
    def check_status(cls, v: str) -> str:
        if v not in LeadStatusEnum.ALL:
            raise ValueError(f"Lead status must be one of: {', '.join(LeadStatusEnum.ALL)}")
        return v

    @field_validator("priority")
    @classmethod
    def check_priority(cls, v: str) -> str:
        valid_priorities = ["Low", "Medium", "High"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    lead_name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    expected_value: Optional[float] = Field(None, ge=0.0)
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("email")
    @classmethod
    def check_email_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean_v = v.strip().lower()
        if not EMAIL_REGEX.match(clean_v):
            raise ValueError("Enter a valid email address.")
        return clean_v

    @field_validator("phone")
    @classmethod
    def check_phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean_v = v.strip()
        digits = re.sub(r"\D", "", clean_v)
        if len(digits) < 10 or len(digits) > 15 or not PHONE_REGEX.match(clean_v):
            raise ValueError("Enter a valid phone number.")
        return clean_v

    @field_validator("status")
    @classmethod
    def check_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in LeadStatusEnum.ALL:
            raise ValueError(f"Lead status must be one of: {', '.join(LeadStatusEnum.ALL)}")
        return v

class LeadConvertRequest(BaseModel):
    create_opportunity: bool = True
    opportunity_name: Optional[str] = None
    opportunity_amount: Optional[float] = None
    expected_close_date: Optional[date] = None
    assigned_to: Optional[int] = None

class LeadResponse(LeadBase):
    lead_id: int
    lead_code: str
    created_by: Optional[int] = None
    converted_customer_id: Optional[int] = None
    assigned_user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
