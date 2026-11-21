from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from acxiom_crm.backend.database import get_db
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityResponse
from acxiom_crm.backend.services.opportunity_service import (
    get_opportunities, get_opportunity_by_id, create_opportunity, update_opportunity, delete_opportunity
)
from acxiom_crm.backend.api.deps import get_current_user, get_client_ip, require_role

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])

def to_opportunity_response(o) -> OpportunityResponse:
    assigned_name = o.assigned_user.name if o.assigned_user else None
    cust_name = o.customer.customer_name if o.customer else None
    return OpportunityResponse(
        opportunity_id=o.opportunity_id,
        opportunity_name=o.opportunity_name,
        customer_id=o.customer_id,
        lead_id=o.lead_id,
        amount=o.amount,
        stage=o.stage,
        probability=o.probability,
        expected_close_date=o.expected_close_date,
        status=o.status,
        assigned_to=o.assigned_to,
        customer_name=cust_name,
        assigned_user_name=assigned_name,
        weighted_amount=o.weighted_amount,
        notes=o.notes,
        created_at=o.created_at,
        updated_at=o.updated_at
    )

@router.get("", response_model=List[OpportunityResponse])
def list_opportunities(
    search: Optional[str] = Query(None, description="Search by name or customer name"),
    stage: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    customer_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    opps = get_opportunities(
        db=db,
        current_user=current_user,
        search=search,
        stage=stage,
        status=status_filter,
        customer_id=customer_id,
        limit=limit,
        offset=offset
    )
    return [to_opportunity_response(o) for o in opps]

@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_new_opportunity(
    opp_in: OpportunityCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        opp = create_opportunity(
            db=db,
            opp_in=opp_in,
            current_user=current_user,
            ip_address=ip
        )
        return to_opportunity_response(opp)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    opp = get_opportunity_by_id(db=db, opportunity_id=opportunity_id, current_user=current_user)
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found or unauthorized.")
    return to_opportunity_response(opp)

@router.put("/{opportunity_id}", response_model=OpportunityResponse)
def update_existing_opportunity(
    opportunity_id: int,
    opp_in: OpportunityUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        opp = update_opportunity(
            db=db,
            opportunity_id=opportunity_id,
            opp_in=opp_in,
            current_user=current_user,
            ip_address=ip
        )
        return to_opportunity_response(opp)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.delete("/{opportunity_id}", status_code=status.HTTP_200_OK)
def remove_opportunity(
    opportunity_id: int,
    request: Request,
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER])),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        delete_opportunity(
            db=db,
            opportunity_id=opportunity_id,
            current_user=current_user,
            ip_address=ip
        )
        return {"message": f"Opportunity #{opportunity_id} successfully deleted."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
