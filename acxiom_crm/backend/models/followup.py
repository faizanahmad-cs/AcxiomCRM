from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from acxiom_crm.backend.database import Base

class FollowUpStatusEnum:
    PLANNED = "Planned"
    COMPLETED = "Completed"
    MISSED = "Missed"
    CANCELLED = "Cancelled"

    ALL = [PLANNED, COMPLETED, MISSED, CANCELLED]

class FollowUpTypeEnum:
    CALL = "Call"
    EMAIL = "Email"
    MEETING = "Meeting"
    DEMO = "Demo"
    TASK = "Task"

    ALL = [CALL, EMAIL, MEETING, DEMO, TASK]

class RelatedTypeEnum:
    CUSTOMER = "Customer"
    LEAD = "Lead"
    OPPORTUNITY = "Opportunity"

    ALL = [CUSTOMER, LEAD, OPPORTUNITY]

class FollowUp(Base):
    __tablename__ = "followups"

    followup_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.opportunity_id"), nullable=True)
    related_type = Column(String(50), nullable=False)  # Customer, Lead, Opportunity
    related_id = Column(Integer, nullable=False)
    followup_date = Column(DateTime, nullable=False)
    followup_type = Column(String(50), default=FollowUpTypeEnum.CALL, nullable=False)
    subject = Column(String(200), nullable=False)
    remarks = Column(Text, nullable=True)
    status = Column(String(50), default=FollowUpStatusEnum.PLANNED, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="followups")
    lead = relationship("Lead", back_populates="followups")
    opportunity = relationship("Opportunity", back_populates="followups")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_followups")

    def is_overdue(self) -> bool:
        if self.status == FollowUpStatusEnum.PLANNED and self.followup_date < datetime.utcnow():
            return True
        return False
