from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from acxiom_crm.backend.database import Base

class RoleEnum:
    ADMIN = "Admin"
    MANAGER = "Manager"
    SALES_EXECUTIVE = "Sales Executive"
    
    ALL = [ADMIN, MANAGER, SALES_EXECUTIVE]

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=RoleEnum.SALES_EXECUTIVE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    failed_login_count = Column(Integer, default=0, nullable=False)
    lockout_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    assigned_customers = relationship("Customer", back_populates="assigned_user", foreign_keys="Customer.assigned_to")
    assigned_leads = relationship("Lead", back_populates="assigned_user", foreign_keys="Lead.assigned_to")
    assigned_opportunities = relationship("Opportunity", back_populates="assigned_user", foreign_keys="Opportunity.assigned_to")
    assigned_followups = relationship("FollowUp", back_populates="assigned_user", foreign_keys="FollowUp.assigned_to")
    assigned_activities = relationship("Activity", back_populates="assigned_user", foreign_keys="Activity.assigned_to")
    audit_logs = relationship("AuditLog", back_populates="user", foreign_keys="AuditLog.user_id")

    def is_locked(self) -> bool:
        if self.lockout_until and self.lockout_until > datetime.utcnow():
            return True
        return False
