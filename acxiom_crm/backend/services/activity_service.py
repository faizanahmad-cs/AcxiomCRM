from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from acxiom_crm.backend.models.activity import Activity, ActivityTypeEnum
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.schemas.activity import ActivityCreate
from acxiom_crm.backend.services.audit_service import log_action

def get_activities(
    db: Session,
    current_user: User,
    customer_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    activity_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Activity]:
    query = db.query(Activity)

    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        query = query.filter(Activity.assigned_to == current_user.user_id)

    if customer_id:
        query = query.filter(Activity.customer_id == customer_id)
    if lead_id:
        query = query.filter(Activity.lead_id == lead_id)
    if activity_type and activity_type != "All":
        query = query.filter(Activity.activity_type == activity_type)

    return query.order_by(desc(Activity.activity_date)).offset(offset).limit(limit).all()

def create_activity(
    db: Session,
    activity_in: ActivityCreate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> Activity:
    assigned = activity_in.assigned_to
    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        assigned = current_user.user_id

    activity = Activity(
        activity_type=activity_in.activity_type,
        subject=activity_in.subject.strip(),
        description=activity_in.description,
        activity_date=activity_in.activity_date or datetime.utcnow(),
        customer_id=activity_in.customer_id,
        lead_id=activity_in.lead_id,
        opportunity_id=activity_in.opportunity_id,
        assigned_to=assigned,
        status=activity_in.status,
        created_at=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    log_action(
        db=db,
        action=AuditActionEnum.CREATE,
        entity_name="Activity",
        record_id=str(activity.activity_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=f"Activity logged: [{activity.activity_type}] {activity.subject}",
        ip_address=ip_address
    )
    return activity
