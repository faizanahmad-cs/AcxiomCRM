from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from acxiom_crm.backend.models.followup import FollowUp, FollowUpStatusEnum, FollowUpTypeEnum, RelatedTypeEnum
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.lead import Lead
from acxiom_crm.backend.models.opportunity import Opportunity
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.schemas.followup import FollowUpCreate, FollowUpUpdate
from acxiom_crm.backend.services.audit_service import log_action

def get_followups(
    db: Session,
    current_user: User,
    status: Optional[str] = None,
    followup_type: Optional[str] = None,
    related_type: Optional[str] = None,
    only_upcoming: bool = False,
    only_overdue: bool = False,
    limit: int = 100,
    offset: int = 0
) -> List[FollowUp]:
    query = db.query(FollowUp)

    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        query = query.filter(FollowUp.assigned_to == current_user.user_id)

    now = datetime.utcnow()

    if status and status != "All":
        query = query.filter(FollowUp.status == status)

    if followup_type and followup_type != "All":
        query = query.filter(FollowUp.followup_type == followup_type)

    if related_type and related_type != "All":
        query = query.filter(FollowUp.related_type == related_type)

    if only_upcoming:
        query = query.filter(
            FollowUp.status == FollowUpStatusEnum.PLANNED,
            FollowUp.followup_date >= now
        )
    elif only_overdue:
        query = query.filter(
            FollowUp.status == FollowUpStatusEnum.PLANNED,
            FollowUp.followup_date < now
        )

    return query.order_by(asc(FollowUp.followup_date)).offset(offset).limit(limit).all()

def get_followup_by_id(db: Session, followup_id: int, current_user: User) -> Optional[FollowUp]:
    item = db.query(FollowUp).filter(FollowUp.followup_id == followup_id).first()
    if not item:
        return None
    if current_user.role == RoleEnum.SALES_EXECUTIVE and item.assigned_to != current_user.user_id:
        return None
    return item

def create_followup(
    db: Session,
    followup_in: FollowUpCreate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> FollowUp:
    # Server-side business rule: date cannot be earlier than today for new/planned
    if followup_in.status == FollowUpStatusEnum.PLANNED:
        if followup_in.followup_date.date() < date.today():
            raise ValueError("Follow-up date cannot be earlier than today.")

    cust_id = None
    lead_id = None
    opp_id = None

    # Validate relation
    if followup_in.related_type == RelatedTypeEnum.CUSTOMER:
        rel = db.query(Customer).filter(Customer.customer_id == followup_in.related_id).first()
        if not rel:
            raise ValueError(f"Customer #{followup_in.related_id} not found.")
        cust_id = rel.customer_id
    elif followup_in.related_type == RelatedTypeEnum.LEAD:
        rel = db.query(Lead).filter(Lead.lead_id == followup_in.related_id).first()
        if not rel:
            raise ValueError(f"Lead #{followup_in.related_id} not found.")
        lead_id = rel.lead_id
    elif followup_in.related_type == RelatedTypeEnum.OPPORTUNITY:
        rel = db.query(Opportunity).filter(Opportunity.opportunity_id == followup_in.related_id).first()
        if not rel:
            raise ValueError(f"Opportunity #{followup_in.related_id} not found.")
        opp_id = rel.opportunity_id
        cust_id = rel.customer_id

    assigned = followup_in.assigned_to
    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        assigned = current_user.user_id

    followup = FollowUp(
        customer_id=cust_id,
        lead_id=lead_id,
        opportunity_id=opp_id,
        related_type=followup_in.related_type,
        related_id=followup_in.related_id,
        followup_date=followup_in.followup_date,
        followup_type=followup_in.followup_type,
        subject=followup_in.subject.strip(),
        remarks=followup_in.remarks,
        status=followup_in.status,
        assigned_to=assigned,
        created_at=datetime.utcnow()
    )
    db.add(followup)
    db.commit()
    db.refresh(followup)

    log_action(
        db=db,
        action=AuditActionEnum.CREATE,
        entity_name="FollowUp",
        record_id=str(followup.followup_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        new_value={
            "subject": followup.subject,
            "type": followup.followup_type,
            "date": str(followup.followup_date),
            "related": f"{followup.related_type} #{followup.related_id}"
        },
        details=f"Follow-up scheduled: {followup.subject} for {followup.followup_date.strftime('%Y-%m-%d %H:%M')}",
        ip_address=ip_address
    )
    return followup

def complete_followup(
    db: Session,
    followup_id: int,
    remarks: Optional[str],
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> FollowUp:
    item = get_followup_by_id(db, followup_id, current_user)
    if not item:
        raise ValueError("Follow-up not found or access denied.")

    old_status = item.status
    item.status = FollowUpStatusEnum.COMPLETED
    item.completed_at = datetime.utcnow()
    if remarks:
        item.remarks = (item.remarks or "") + f"\n[Completed on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}]: {remarks}"
    db.commit()
    db.refresh(item)

    log_action(
        db=db,
        action=AuditActionEnum.STATUS_CHANGE,
        entity_name="FollowUp",
        record_id=str(item.followup_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        old_value={"status": old_status},
        new_value={"status": item.status},
        details=f"Follow-up marked completed: {item.subject}",
        ip_address=ip_address
    )
    return item

def update_followup(
    db: Session,
    followup_id: int,
    followup_in: FollowUpUpdate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> FollowUp:
    item = get_followup_by_id(db, followup_id, current_user)
    if not item:
        raise ValueError("Follow-up not found or access denied.")

    if followup_in.followup_date is not None:
        target_status = followup_in.status or item.status
        if target_status == FollowUpStatusEnum.PLANNED and followup_in.followup_date.date() < date.today():
            raise ValueError("Follow-up date cannot be earlier than today.")
        item.followup_date = followup_in.followup_date

    if followup_in.subject is not None:
        item.subject = followup_in.subject.strip()
    if followup_in.followup_type is not None:
        item.followup_type = followup_in.followup_type
    if followup_in.remarks is not None:
        item.remarks = followup_in.remarks
    if followup_in.status is not None:
        item.status = followup_in.status
        if item.status == FollowUpStatusEnum.COMPLETED and not item.completed_at:
            item.completed_at = datetime.utcnow()
    if followup_in.assigned_to is not None and current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
        item.assigned_to = followup_in.assigned_to

    db.commit()
    db.refresh(item)

    log_action(
        db=db,
        action=AuditActionEnum.UPDATE,
        entity_name="FollowUp",
        record_id=str(item.followup_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=f"Follow-up updated: {item.subject}",
        ip_address=ip_address
    )
    return item
