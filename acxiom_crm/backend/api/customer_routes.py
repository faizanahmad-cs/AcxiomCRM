from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from acxiom_crm.backend.database import get_db
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from acxiom_crm.backend.services.customer_service import (
    get_customers, get_customer_by_id, create_customer, update_customer, delete_customer
)
from acxiom_crm.backend.api.deps import get_current_user, get_client_ip, require_role

router = APIRouter(prefix="/api/customers", tags=["Customers"])

def to_customer_response(c) -> CustomerResponse:
    assigned_name = c.assigned_user.name if c.assigned_user else None
    return CustomerResponse(
        customer_id=c.customer_id,
        customer_code=c.customer_code,
        customer_name=c.customer_name,
        email=c.email,
        phone=c.phone,
        company_name=c.company_name,
        address=c.address,
        city=c.city,
        state=c.state,
        status=c.status,
        assigned_to=c.assigned_to,
        created_by=c.created_by,
        assigned_user_name=assigned_name,
        notes=c.notes,
        created_at=c.created_at,
        updated_at=c.updated_at
    )

@router.get("", response_model=List[CustomerResponse])
def list_customers(
    search: Optional[str] = Query(None, description="Search by name, email, phone, company, code"),
    status_filter: Optional[str] = Query(None, alias="status"),
    city: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    customers = get_customers(
        db=db,
        current_user=current_user,
        search=search,
        status=status_filter,
        city=city,
        limit=limit,
        offset=offset
    )
    return [to_customer_response(c) for c in customers]

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_new_customer(
    customer_in: CustomerCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        cust = create_customer(
            db=db,
            customer_in=customer_in,
            current_user=current_user,
            ip_address=ip
        )
        return to_customer_response(cust)
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cust = get_customer_by_id(db=db, customer_id=customer_id, current_user=current_user)
    if not cust:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found or unauthorized.")
    return to_customer_response(cust)

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_existing_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        cust = update_customer(
            db=db,
            customer_id=customer_id,
            customer_in=customer_in,
            current_user=current_user,
            ip_address=ip
        )
        return to_customer_response(cust)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.delete("/{customer_id}", status_code=status.HTTP_200_OK)
def remove_customer(
    customer_id: int,
    request: Request,
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER])),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        delete_customer(
            db=db,
            customer_id=customer_id,
            current_user=current_user,
            ip_address=ip
        )
        return {"message": f"Customer #{customer_id} successfully deleted."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
