from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from acxiom_crm.backend.database import get_db
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.lead import LeadCreate, LeadUpdate, LeadConvertRequest, LeadResponse
from acxiom_crm.backend.schemas.customer import CustomerResponse
from acxiom_crm.backend.schemas.opportunity import OpportunityResponse
from acxiom_crm.backend.services.lead_service import (
    get_leads, get_lead_by_id, create_lead, update_lead, delete_lead, convert_lead
)
from acxiom_crm.backend.api.deps import get_current_user, get_client_ip, require_role

router = APIRouter(prefix="/api/leads", tags=["Leads"])

def to_lead_response(l) -> LeadResponse:
    assigned_name = l.assigned_user.name if l.assigned_user else None
    return LeadResponse(
        lead_id=l.lead_id,
        lead_code=l.lead_code,
        lead_name=l.lead_name,
        email=l.email,
        phone=l.phone,
        company_name=l.company_name,
        source=l.source,
        status=l.status,
        priority=l.priority,
        expected_value=l.expected_value,
        assigned_to=l.assigned_to,
        created_by=l.created_by,
        converted_customer_id=l.converted_customer_id,
        assigned_user_name=assigned_name,
        notes=l.notes,
        created_at=l.created_at,
        updated_at=l.updated_at
    )

@router.get("", response_model=List[LeadResponse])
def list_leads(
    search: Optional[str] = Query(None, description="Search by name, email, phone, company, code"),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leads = get_leads(
        db=db,
        current_user=current_user,
        search=search,
        status=status_filter,
        priority=priority,
        source=source,
        limit=limit,
        offset=offset
    )
    return [to_lead_response(l) for l in leads]

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_new_lead(
    lead_in: LeadCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        lead = create_lead(
            db=db,
            lead_in=lead_in,
            current_user=current_user,
            ip_address=ip
        )
        return to_lead_response(lead)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lead = get_lead_by_id(db=db, lead_id=lead_id, current_user=current_user)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found or unauthorized.")
    return to_lead_response(lead)

@router.put("/{lead_id}", response_model=LeadResponse)
def update_existing_lead(
    lead_id: int,
    lead_in: LeadUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        lead = update_lead(
            db=db,
            lead_id=lead_id,
            lead_in=lead_in,
            current_user=current_user,
            ip_address=ip
        )
        return to_lead_response(lead)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.post("/{lead_id}/convert")
def convert_lead_endpoint(
    lead_id: int,
    convert_data: LeadConvertRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        customer, opp = convert_lead(
            db=db,
            lead_id=lead_id,
            convert_data=convert_data,
            current_user=current_user,
            ip_address=ip
        )
        return {
            "message": "Lead converted successfully.",
            "customer_id": customer.customer_id,
            "customer_code": customer.customer_code,
            "opportunity_id": opp.opportunity_id if opp else None
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{lead_id}", status_code=status.HTTP_200_OK)
def remove_lead(
    lead_id: int,
    request: Request,
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER])),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        delete_lead(
            db=db,
            lead_id=lead_id,
            current_user=current_user,
            ip_address=ip
        )
        return {"message": f"Lead #{lead_id} successfully deleted."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
