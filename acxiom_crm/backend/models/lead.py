from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from acxiom_crm.backend.database import Base

class LeadStatusEnum:
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    UNQUALIFIED = "Unqualified"
    CONVERTED = "Converted"
    LOST = "Lost"

    ALL = [NEW, CONTACTED, QUALIFIED, UNQUALIFIED, CONVERTED, LOST]

class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_code = Column(String(50), unique=True, index=True, nullable=False)
    lead_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=False, index=True)
    company_name = Column(String(150), nullable=True)
    source = Column(String(50), default="Website", nullable=False)  # Website, Referral, Cold Call, Trade Show, Email Campaign, Other
    status = Column(String(50), default=LeadStatusEnum.NEW, nullable=False)
    priority = Column(String(50), default="Medium", nullable=False)  # Low, Medium, High
    expected_value = Column(Float, default=0.0, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    converted_customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_leads")
    converted_customer = relationship("Customer", foreign_keys=[converted_customer_id])
    followups = relationship("FollowUp", back_populates="lead", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="lead", cascade="all, delete-orphan")
