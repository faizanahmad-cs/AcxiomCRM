import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.schemas.customer import CustomerCreate, CustomerUpdate
from acxiom_crm.backend.services.audit_service import log_action

def generate_customer_code(db: Session) -> str:
    count = db.query(Customer).count()
    return f"CUST-{(count + 1):04d}"

def get_customers(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Customer]:
    query = db.query(Customer)

    # Role-based scoping
    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        query = query.filter(Customer.assigned_to == current_user.user_id)

    # Search filter (name, email, phone, company)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Customer.customer_name.ilike(s),
                Customer.email.ilike(s),
                Customer.phone.ilike(s),
                Customer.company_name.ilike(s),
                Customer.customer_code.ilike(s)
            )
        )

    if status and status != "All":
        query = query.filter(Customer.status == status)

    if city and city != "All":
        query = query.filter(Customer.city == city)

    return query.order_by(desc(Customer.created_at)).offset(offset).limit(limit).all()

def get_customer_by_id(db: Session, customer_id: int, current_user: User) -> Optional[Customer]:
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return None
    # Authorization check
    if current_user.role == RoleEnum.SALES_EXECUTIVE and customer.assigned_to != current_user.user_id:
        return None
    return customer

def create_customer(
    db: Session,
    customer_in: CustomerCreate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> Customer:
    email_clean = customer_in.email.strip().lower()
    clean_phone = re.sub(r"\D", "", customer_in.phone)

    # Check email uniqueness
    existing_email = db.query(Customer).filter(Customer.email == email_clean).first()
    if existing_email:
        raise ValueError(f"Customer with email '{email_clean}' already exists.")

    # Check phone uniqueness
    existing_phone = db.query(Customer).filter(Customer.phone == customer_in.phone.strip()).first()
    if existing_phone:
        raise ValueError(f"Customer with phone '{customer_in.phone.strip()}' already exists.")

    assigned = customer_in.assigned_to
    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        assigned = current_user.user_id  # Sales Exec always assigns to self

    customer = Customer(
        customer_code=generate_customer_code(db),
        customer_name=customer_in.customer_name.strip(),
        email=email_clean,
        phone=customer_in.phone.strip(),
        company_name=customer_in.company_name.strip() if customer_in.company_name else None,
        address=customer_in.address.strip() if customer_in.address else None,
        city=customer_in.city.strip() if customer_in.city else None,
        state=customer_in.state.strip() if customer_in.state else None,
        status=customer_in.status,
        assigned_to=assigned,
        created_by=current_user.user_id,
        notes=customer_in.notes,
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
        new_value={
            "customer_code": customer.customer_code,
            "name": customer.customer_name,
            "email": customer.email,
            "phone": customer.phone,
            "status": customer.status
        },
        details=f"Customer created: {customer.customer_name} ({customer.customer_code})",
        ip_address=ip_address
    )
    return customer

def update_customer(
    db: Session,
    customer_id: int,
    customer_in: CustomerUpdate,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> Customer:
    customer = get_customer_by_id(db, customer_id, current_user)
    if not customer:
        raise ValueError("Customer not found or access denied.")

    old_dict = {
        "name": customer.customer_name,
        "email": customer.email,
        "phone": customer.phone,
        "status": customer.status,
        "assigned_to": customer.assigned_to
    }

    # If updating email, check uniqueness
    if customer_in.email is not None:
        new_email = customer_in.email.strip().lower()
        if new_email != customer.email:
            existing = db.query(Customer).filter(Customer.email == new_email).first()
            if existing:
                raise ValueError(f"Customer with email '{new_email}' already exists.")
            customer.email = new_email

    # If updating phone, check uniqueness
    if customer_in.phone is not None:
        new_phone = customer_in.phone.strip()
        if new_phone != customer.phone:
            existing = db.query(Customer).filter(Customer.phone == new_phone).first()
            if existing:
                raise ValueError(f"Customer with phone '{new_phone}' already exists.")
            customer.phone = new_phone

    if customer_in.customer_name is not None:
        customer.customer_name = customer_in.customer_name.strip()
    if customer_in.company_name is not None:
        customer.company_name = customer_in.company_name.strip()
    if customer_in.address is not None:
        customer.address = customer_in.address.strip()
    if customer_in.city is not None:
        customer.city = customer_in.city.strip()
    if customer_in.state is not None:
        customer.state = customer_in.state.strip()
    if customer_in.status is not None:
        customer.status = customer_in.status
    if customer_in.notes is not None:
        customer.notes = customer_in.notes

    if customer_in.assigned_to is not None and current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
        customer.assigned_to = customer_in.assigned_to

    customer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(customer)

    new_dict = {
        "name": customer.customer_name,
        "email": customer.email,
        "phone": customer.phone,
        "status": customer.status,
        "assigned_to": customer.assigned_to
    }

    log_action(
        db=db,
        action=AuditActionEnum.UPDATE,
        entity_name="Customer",
        record_id=str(customer.customer_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        old_value=old_dict,
        new_value=new_dict,
        details=f"Customer updated: {customer.customer_name}",
        ip_address=ip_address
    )
    return customer

def delete_customer(
    db: Session,
    customer_id: int,
    current_user: User,
    ip_address: str = "127.0.0.1"
) -> bool:
    customer = get_customer_by_id(db, customer_id, current_user)
    if not customer:
        raise ValueError("Customer not found or access denied.")

    # Sales Execs cannot delete customers, only Admin/Manager
    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        raise PermissionError("Sales Executives are not authorized to delete customers.")

    old_dict = {"name": customer.customer_name, "code": customer.customer_code}
    db.delete(customer)
    db.commit()

    log_action(
        db=db,
        action=AuditActionEnum.DELETE,
        entity_name="Customer",
        record_id=str(customer_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        old_value=old_dict,
        details=f"Customer deleted: {old_dict['name']} ({old_dict['code']})",
        ip_address=ip_address
    )
    return True
