from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from acxiom_crm.backend.models.opportunity import Opportunity, OpportunityStageEnum, OpportunityStatusEnum
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from acxiom_crm.backend.services.audit_service import log_action

def get_opportunities(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Opportunity]:
    query = db.query(Opportunity)

    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        query = query.filter(Opportunity.assigned_to == current_user.user_id)

    if customer_id:
        query = query.filter(Opportunity.customer_id == customer_id)

    if search:
        s = f"%{search.strip()}%"
        query = query.join(Customer).filter(
            or_(
                Opportunity.opportunity_name.ilike(s),
                Customer.customer_name.ilike(s),
                Customer.company_name.ilike(s)
            )
        )

    if stage and stage != "All":
        query = query.filter(Opportunity.stage == stage)

    if status and status != "All":
        query = query.filter(Opportunity.status == status)

    return query.order_by(desc(Opportunity.created_at)).offset(offset).limit(limit).all()

def get_opportunity_by_id(db: Session, opportunity_id: int, current_user: User) -> Optional[Opportunity]:
    opp = db.query(Opportunity).filter(Opportunity.opportunity_id == opportunity_id).first()
    if not opp:
        return None
    if current_user.role == RoleEnum.SALES_EXECUTIVE and opp.assigned_to != current_user.user_id:
        return None
    return opp

def create_opportunity(
    db: Session,
    opp_in: OpportunityCreate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> Opportunity:
    # Validate customer existence and permission
    customer = db.query(Customer).filter(Customer.customer_id == opp_in.customer_id).first()
    if not customer:
        raise ValueError(f"Customer with ID {opp_in.customer_id} not found.")

    # Server-side business validations
    if opp_in.amount <= 0:
        raise ValueError("Opportunity Amount must be greater than 0.")
    if opp_in.probability < 0 or opp_in.probability > 100:
        raise ValueError("Probability must be between 0 and 100.")
    if opp_in.expected_close_date < date.today():
        raise ValueError("Expected Close Date cannot be in the past.")

    # Derive status from stage
    status = OpportunityStatusEnum.OPEN
    if opp_in.stage == OpportunityStageEnum.WON:
        status = OpportunityStatusEnum.WON
    elif opp_in.stage == OpportunityStageEnum.LOST:
        status = OpportunityStatusEnum.LOST

    assigned = opp_in.assigned_to
    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        assigned = current_user.user_id

    opportunity = Opportunity(
        opportunity_name=opp_in.opportunity_name.strip(),
        customer_id=opp_in.customer_id,
        lead_id=opp_in.lead_id,
        amount=opp_in.amount,
        stage=opp_in.stage,
        probability=opp_in.probability,
        expected_close_date=opp_in.expected_close_date,
        status=status,
        assigned_to=assigned,
        notes=opp_in.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    log_action(
        db=db,
        action=AuditActionEnum.CREATE,
        entity_name="Opportunity",
        record_id=str(opportunity.opportunity_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        new_value={
            "name": opportunity.opportunity_name,
            "amount": opportunity.amount,
            "stage": opportunity.stage,
            "probability": opportunity.probability,
            "weighted_amount": opportunity.weighted_amount
        },
        details=f"Opportunity created: {opportunity.opportunity_name} (${opportunity.amount:,.2f})",
        ip_address=ip_address
    )
    return opportunity

def update_opportunity(
    db: Session,
    opportunity_id: int,
    opp_in: OpportunityUpdate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> Opportunity:
    opp = get_opportunity_by_id(db, opportunity_id, current_user)
    if not opp:
        raise ValueError("Opportunity not found or access denied.")

    # Business validations
    if opp_in.amount is not None and opp_in.amount <= 0:
        raise ValueError("Opportunity Amount must be greater than 0.")
    if opp_in.probability is not None and (opp_in.probability < 0 or opp_in.probability > 100):
        raise ValueError("Probability must be between 0 and 100.")

    target_stage = opp_in.stage if opp_in.stage is not None else opp.stage
    target_date = opp_in.expected_close_date if opp_in.expected_close_date is not None else opp.expected_close_date

    if target_stage in OpportunityStageEnum.ACTIVE_STAGES:
        if target_date < date.today():
            raise ValueError("Expected Close Date cannot be in the past.")

    old_dict = {
        "amount": opp.amount,
        "stage": opp.stage,
        "probability": opp.probability,
        "expected_close_date": str(opp.expected_close_date),
        "status": opp.status
    }

    if opp_in.opportunity_name is not None:
        opp.opportunity_name = opp_in.opportunity_name.strip()
    if opp_in.amount is not None:
        opp.amount = opp_in.amount
    if opp_in.probability is not None:
        opp.probability = opp_in.probability
    if opp_in.expected_close_date is not None:
        opp.expected_close_date = opp_in.expected_close_date
    if opp_in.notes is not None:
        opp.notes = opp_in.notes

    if opp_in.stage is not None:
        opp.stage = opp_in.stage
        if opp.stage == OpportunityStageEnum.WON:
            opp.status = OpportunityStatusEnum.WON
            opp.probability = 100.0
        elif opp.stage == OpportunityStageEnum.LOST:
            opp.status = OpportunityStatusEnum.LOST
            opp.probability = 0.0
        else:
            opp.status = OpportunityStatusEnum.OPEN

    if opp_in.status is not None:
        opp.status = opp_in.status

    if opp_in.assigned_to is not None and current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
        opp.assigned_to = opp_in.assigned_to

    opp.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(opp)

    new_dict = {
        "amount": opp.amount,
        "stage": opp.stage,
        "probability": opp.probability,
        "expected_close_date": str(opp.expected_close_date),
        "status": opp.status
    }

    log_action(
        db=db,
        action=AuditActionEnum.UPDATE,
        entity_name="Opportunity",
        record_id=str(opp.opportunity_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        old_value=old_dict,
        new_value=new_dict,
        details=f"Opportunity updated: {opp.opportunity_name}",
        ip_address=ip_address
    )
    return opp

def delete_opportunity(
    db: Session,
    opportunity_id: int,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> bool:
    opp = get_opportunity_by_id(db, opportunity_id, current_user)
    if not opp:
        raise ValueError("Opportunity not found or access denied.")

    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        raise PermissionError("Sales Executives cannot delete opportunities.")

    old_dict = {"name": opp.opportunity_name, "amount": opp.amount, "stage": opp.stage}
    db.delete(opp)
    db.commit()

    log_action(
        db=db,
        action=AuditActionEnum.DELETE,
        entity_name="Opportunity",
        record_id=str(opportunity_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        old_value=old_dict,
        details=f"Opportunity deleted: {old_dict['name']}",
        ip_address=ip_address
    )
    return True
