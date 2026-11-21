from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from acxiom_crm.backend.models.lead import Lead, LeadStatusEnum
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.opportunity import Opportunity, OpportunityStageEnum, OpportunityStatusEnum
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.schemas.lead import LeadCreate, LeadUpdate, LeadConvertRequest
from acxiom_crm.backend.services.customer_service import generate_customer_code
from acxiom_crm.backend.services.audit_service import log_action

def generate_lead_code(db: Session) -> str:
    count = db.query(Lead).count()
    return f"LEAD-{(count + 1):04d}"

def get_leads(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Lead]:
    query = db.query(Lead)

    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        query = query.filter(Lead.assigned_to == current_user.user_id)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Lead.lead_name.ilike(s),
                Lead.email.ilike(s),
                Lead.phone.ilike(s),
                Lead.company_name.ilike(s),
                Lead.lead_code.ilike(s)
            )
        )

    if status and status != "All":
        query = query.filter(Lead.status == status)

    if priority and priority != "All":
        query = query.filter(Lead.priority == priority)

    if source and source != "All":
        query = query.filter(Lead.source == source)

    return query.order_by(desc(Lead.created_at)).offset(offset).limit(limit).all()

def get_lead_by_id(db: Session, lead_id: int, current_user: User) -> Optional[Lead]:
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        return None
    if current_user.role == RoleEnum.SALES_EXECUTIVE and lead.assigned_to != current_user.user_id:
        return None
    return lead

def create_lead(
    db: Session,
    lead_in: LeadCreate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> Lead:
    assigned = lead_in.assigned_to
    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        assigned = current_user.user_id

    lead = Lead(
        lead_code=generate_lead_code(db),
        lead_name=lead_in.lead_name.strip(),
        email=lead_in.email.strip().lower(),
        phone=lead_in.phone.strip(),
        company_name=lead_in.company_name.strip() if lead_in.company_name else None,
        source=lead_in.source,
        status=lead_in.status,
        priority=lead_in.priority,
        expected_value=lead_in.expected_value,
        assigned_to=assigned,
        created_by=current_user.user_id,
        notes=lead_in.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    log_action(
        db=db,
        action=AuditActionEnum.CREATE,
        entity_name="Lead",
        record_id=str(lead.lead_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        new_value={
            "lead_code": lead.lead_code,
            "name": lead.lead_name,
            "status": lead.status,
            "priority": lead.priority,
            "expected_value": lead.expected_value
        },
        details=f"Lead created: {lead.lead_name} ({lead.lead_code})",
        ip_address=ip_address
    )
    return lead

def update_lead(
    db: Session,
    lead_id: int,
    lead_in: LeadUpdate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> Lead:
    lead = get_lead_by_id(db, lead_id, current_user)
    if not lead:
        raise ValueError("Lead not found or access denied.")

    # Status transition rules
    if lead_in.status is not None:
        if lead.status == LeadStatusEnum.CONVERTED and lead_in.status != LeadStatusEnum.CONVERTED:
            raise ValueError("A Converted lead cannot be reverted to a previous status.")

    old_dict = {
        "status": lead.status,
        "priority": lead.priority,
        "assigned_to": lead.assigned_to,
        "expected_value": lead.expected_value
    }

    if lead_in.lead_name is not None:
        lead.lead_name = lead_in.lead_name.strip()
    if lead_in.email is not None:
        lead.email = lead_in.email.strip().lower()
    if lead_in.phone is not None:
        lead.phone = lead_in.phone.strip()
    if lead_in.company_name is not None:
        lead.company_name = lead_in.company_name.strip()
    if lead_in.source is not None:
        lead.source = lead_in.source
    if lead_in.status is not None:
        lead.status = lead_in.status
    if lead_in.priority is not None:
        lead.priority = lead_in.priority
    if lead_in.expected_value is not None:
        lead.expected_value = lead_in.expected_value
    if lead_in.notes is not None:
        lead.notes = lead_in.notes

    if lead_in.assigned_to is not None and current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
        lead.assigned_to = lead_in.assigned_to

    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)

    new_dict = {
        "status": lead.status,
        "priority": lead.priority,
        "assigned_to": lead.assigned_to,
        "expected_value": lead.expected_value
    }

    log_action(
        db=db,
        action=AuditActionEnum.UPDATE,
        entity_name="Lead",
        record_id=str(lead.lead_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        old_value=old_dict,
        new_value=new_dict,
        details=f"Lead updated: {lead.lead_name}",
        ip_address=ip_address
    )
    return lead

def convert_lead(
    db: Session,
    lead_id: int,
    convert_data: LeadConvertRequest,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> Tuple[Customer, Optional[Opportunity]]:
    """
    Lead conversion workflow:
    1. Validate lead exists and is not already converted.
    2. Check if customer exists; if not, create Customer.
    3. Optionally create Opportunity for customer with business validation.
    4. Mark Lead as Converted and link converted_customer_id.
    5. Record AuditLog entry.
    """
    lead = get_lead_by_id(db, lead_id, current_user)
    if not lead:
        raise ValueError("Lead not found or access denied.")

    if lead.status == LeadStatusEnum.CONVERTED:
        raise ValueError(f"Lead '{lead.lead_name}' has already been converted.")

    # Find or create customer
    customer = db.query(Customer).filter(
        or_(Customer.email == lead.email, Customer.phone == lead.phone)
    ).first()

    if not customer:
        customer = Customer(
            customer_code=generate_customer_code(db),
            customer_name=lead.lead_name,
            email=lead.email,
            phone=lead.phone,
            company_name=lead.company_name,
            status="Lead_Converted",
            assigned_to=lead.assigned_to or current_user.user_id,
            created_by=current_user.user_id,
            notes=f"Converted from Lead #{lead.lead_code}. Original notes: {lead.notes or ''}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

        log_action(
            db=db,
            action=AuditActionEnum.CREATE,
            entity_name="Customer",
            record_id=str(customer.customer_id),
            user_id=current_user.user_id,
            user_email=current_user.email,
            details=f"Created customer '{customer.customer_name}' via lead conversion",
            ip_address=ip_address
        )

    opportunity = None
    if convert_data.create_opportunity:
        opp_amount = convert_data.opportunity_amount if (convert_data.opportunity_amount and convert_data.opportunity_amount > 0) else (lead.expected_value if lead.expected_value > 0 else 5000.0)
        opp_name = convert_data.opportunity_name.strip() if convert_data.opportunity_name else f"Deal - {customer.company_name or customer.customer_name}"
        opp_close_date = convert_data.expected_close_date or (date.today() + timedelta(days=30))

        # Enforce business rules
        if opp_close_date < date.today():
            raise ValueError("Expected Close Date cannot be in the past.")

        opportunity = Opportunity(
            opportunity_name=opp_name,
            customer_id=customer.customer_id,
            lead_id=lead.lead_id,
            amount=opp_amount,
            stage=OpportunityStageEnum.QUALIFICATION,
            probability=25.0,
            expected_close_date=opp_close_date,
            status=OpportunityStatusEnum.OPEN,
            assigned_to=convert_data.assigned_to or lead.assigned_to or current_user.user_id,
            notes=f"Opportunity automatically created via lead conversion for Lead {lead.lead_code}",
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
            new_value={"amount": opportunity.amount, "stage": opportunity.stage, "customer": customer.customer_name},
            details=f"Created opportunity '{opportunity.opportunity_name}' via lead conversion",
            ip_address=ip_address
        )

    # Update lead status
    lead.status = LeadStatusEnum.CONVERTED
    lead.converted_customer_id = customer.customer_id
    lead.updated_at = datetime.utcnow()
    db.commit()

    log_action(
        db=db,
        action=AuditActionEnum.CONVERT,
        entity_name="Lead",
        record_id=str(lead.lead_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=f"Lead {lead.lead_code} converted to Customer {customer.customer_code}" + (f" and Opportunity #{opportunity.opportunity_id}" if opportunity else ""),
        ip_address=ip_address
    )

    return customer, opportunity

def delete_lead(
    db: Session,
    lead_id: int,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> bool:
    lead = get_lead_by_id(db, lead_id, current_user)
    if not lead:
        raise ValueError("Lead not found or access denied.")

    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        raise PermissionError("Sales Executives cannot delete leads.")

    old_dict = {"name": lead.lead_name, "code": lead.lead_code}
    db.delete(lead)
    db.commit()

    log_action(
        db=db,
        action=AuditActionEnum.DELETE,
        entity_name="Lead",
        record_id=str(lead_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        old_value=old_dict,
        details=f"Lead deleted: {old_dict['name']} ({old_dict['code']})",
        ip_address=ip_address
    )
    return True
