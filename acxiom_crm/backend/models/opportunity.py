from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from acxiom_crm.backend.database import Base

class OpportunityStageEnum:
    QUALIFICATION = "Qualification"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"

    ACTIVE_STAGES = [QUALIFICATION, PROPOSAL, NEGOTIATION]
    ALL = [QUALIFICATION, PROPOSAL, NEGOTIATION, WON, LOST]

class OpportunityStatusEnum:
    OPEN = "Open"
    WON = "Won"
    LOST = "Lost"

    ALL = [OPEN, WON, LOST]

class Opportunity(Base):
    __tablename__ = "opportunities"

    opportunity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    opportunity_name = Column(String(150), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=True)
    amount = Column(Float, nullable=False)
    stage = Column(String(50), default=OpportunityStageEnum.QUALIFICATION, nullable=False)
    probability = Column(Float, default=20.0, nullable=False)  # 0 to 100
    expected_close_date = Column(Date, nullable=False)
    status = Column(String(50), default=OpportunityStatusEnum.OPEN, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="opportunities")
    lead = relationship("Lead")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_opportunities")
    followups = relationship("FollowUp", back_populates="opportunity", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="opportunity", cascade="all, delete-orphan")

    @property
    def weighted_amount(self) -> float:
        return round((self.amount or 0.0) * (self.probability or 0.0) / 100.0, 2)
