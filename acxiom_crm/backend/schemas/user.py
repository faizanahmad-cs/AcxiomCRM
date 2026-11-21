import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from acxiom_crm.backend.models.user import RoleEnum
from acxiom_crm.backend.security.password import validate_password_policy

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: str = Field(..., description="Unique email address")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean_v = v.strip().lower()
        if not EMAIL_REGEX.match(clean_v):
            raise ValueError("Enter a valid email address.")
        return clean_v

class UserRegisterRequest(UserBase):
    password: str = Field(..., min_length=8, description="Password adhering to complexity policy")
    role: str = Field(default=RoleEnum.SALES_EXECUTIVE, description="Assigned role")

    @field_validator("password")
    @classmethod
    def check_password_complexity(cls, v: str) -> str:
        valid, msg = validate_password_policy(v)
        if not valid:
            raise ValueError(msg)
        return v

    @field_validator("role")
    @classmethod
    def check_role(cls, v: str) -> str:
        if v not in RoleEnum.ALL:
            raise ValueError(f"Role must be one of: {', '.join(RoleEnum.ALL)}")
        return v

class UserLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean_v = v.strip().lower()
        if not EMAIL_REGEX.match(clean_v):
            raise ValueError("Enter a valid email address.")
        return clean_v

class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("role")
    @classmethod
    def check_role(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in RoleEnum.ALL:
            raise ValueError(f"Role must be one of: {', '.join(RoleEnum.ALL)}")
        return v

class PasswordResetRequest(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password(cls, v: str) -> str:
        valid, msg = validate_password_policy(v)
        if not valid:
            raise ValueError(msg)
        return v

class UserResponse(UserBase):
    user_id: int
    role: str
    is_active: bool
    failed_login_count: int
    lockout_until: Optional[datetime] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
