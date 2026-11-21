from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from acxiom_crm.backend.database import Base

class ActivityTypeEnum:
    CALL = "Call"
    MEETING = "Meeting"
    EMAIL = "Email"
    TASK = "Task"
    NOTE = "Note"

    ALL = [CALL, MEETING, EMAIL, TASK, NOTE]

class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_type = Column(String(50), default=ActivityTypeEnum.NOTE, nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    activity_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.opportunity_id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(String(50), default="Completed", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="activities")
    lead = relationship("Lead", back_populates="activities")
    opportunity = relationship("Opportunity", back_populates="activities")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_activities")
