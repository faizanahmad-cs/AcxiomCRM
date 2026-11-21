import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{10,20}$")

class CustomerBase(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=150, description="Customer or organization full name")
    email: str = Field(..., description="Unique contact email")
    phone: str = Field(..., description="Unique phone number")
    company_name: Optional[str] = Field(None, max_length=150)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="Active")  # Active, Inactive, Lead_Converted
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
        valid_statuses = ["Active", "Inactive", "Lead_Converted"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    status: Optional[str] = None
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
        if v is None:
            return None
        valid_statuses = ["Active", "Inactive", "Lead_Converted"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

class CustomerResponse(CustomerBase):
    customer_id: int
    customer_code: str
    created_by: Optional[int] = None
    assigned_user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
