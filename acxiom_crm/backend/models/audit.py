from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from acxiom_crm.backend.database import Base

class AuditActionEnum:
    LOGIN = "Login"
    FAILED_LOGIN = "Failed_Login"
    LOGOUT = "Logout"
    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"
    STATUS_CHANGE = "Status_Change"
    STAGE_CHANGE = "Stage_Change"
    CONVERT = "Convert"
    ROLE_CHANGE = "Role_Change"
    LOCKOUT = "Lockout"
    UNLOCK = "Unlock"
    PASSWORD_RESET = "Password_Reset"

    ALL = [
        LOGIN, FAILED_LOGIN, LOGOUT, CREATE, UPDATE, DELETE,
        STATUS_CHANGE, STAGE_CHANGE, CONVERT, ROLE_CHANGE,
        LOCKOUT, UNLOCK, PASSWORD_RESET
    ]

class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    user_email = Column(String(150), nullable=True)
    action = Column(String(100), nullable=False)
    entity_name = Column(String(100), nullable=False)  # User, Customer, Lead, Opportunity, FollowUp, Activity, Auth
    record_id = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(50), default="127.0.0.1", nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")
