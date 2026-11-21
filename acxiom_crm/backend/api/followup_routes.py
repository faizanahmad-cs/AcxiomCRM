from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from acxiom_crm.backend.database import get_db
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.followup import FollowUpCreate, FollowUpUpdate, FollowUpResponse
from acxiom_crm.backend.services.followup_service import (
    get_followups, get_followup_by_id, create_followup, update_followup, complete_followup
)
from acxiom_crm.backend.api.deps import get_current_user, get_client_ip, require_role

router = APIRouter(prefix="/api/followups", tags=["Follow-Ups"])

def to_followup_response(f) -> FollowUpResponse:
    assigned_name = f.assigned_user.name if f.assigned_user else None
    rel_name = None
    if f.related_type == "Customer" and f.customer:
        rel_name = f.customer.customer_name
    elif f.related_type == "Lead" and f.lead:
        rel_name = f.lead.lead_name
    elif f.related_type == "Opportunity" and f.opportunity:
        rel_name = f.opportunity.opportunity_name

    return FollowUpResponse(
        followup_id=f.followup_id,
        customer_id=f.customer_id,
        lead_id=f.lead_id,
        opportunity_id=f.opportunity_id,
        related_type=f.related_type,
        related_id=f.related_id,
        followup_date=f.followup_date,
        followup_type=f.followup_type,
        subject=f.subject,
        remarks=f.remarks,
        status=f.status,
        assigned_to=f.assigned_to,
        assigned_user_name=assigned_name,
        related_name=rel_name,
        is_overdue=f.is_overdue(),
        created_at=f.created_at,
        completed_at=f.completed_at
    )

@router.get("", response_model=List[FollowUpResponse])
def list_followups(
    status_filter: Optional[str] = Query(None, alias="status"),
    followup_type: Optional[str] = None,
    related_type: Optional[str] = None,
    only_upcoming: bool = False,
    only_overdue: bool = False,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = get_followups(
        db=db,
        current_user=current_user,
        status=status_filter,
        followup_type=followup_type,
        related_type=related_type,
        only_upcoming=only_upcoming,
        only_overdue=only_overdue,
        limit=limit,
        offset=offset
    )
    return [to_followup_response(f) for f in items]

@router.post("", response_model=FollowUpResponse, status_code=status.HTTP_201_CREATED)
def create_new_followup(
    followup_in: FollowUpCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        item = create_followup(
            db=db,
            followup_in=followup_in,
            current_user=current_user,
            ip_address=ip
        )
        return to_followup_response(item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{followup_id}", response_model=FollowUpResponse)
def get_followup(
    followup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = get_followup_by_id(db=db, followup_id=followup_id, current_user=current_user)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow-up not found or unauthorized.")
    return to_followup_response(item)

@router.put("/{followup_id}", response_model=FollowUpResponse)
def update_existing_followup(
    followup_id: int,
    followup_in: FollowUpUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    try:
        item = update_followup(
            db=db,
            followup_id=followup_id,
            followup_in=followup_in,
            current_user=current_user,
            ip_address=ip
        )
        return to_followup_response(item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{followup_id}/complete", response_model=FollowUpResponse)
def mark_followup_completed(
    followup_id: int,
    remarks: Optional[str] = None,
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request) if request else "127.0.0.1"
    try:
        item = complete_followup(
            db=db,
            followup_id=followup_id,
            remarks=remarks,
            current_user=current_user,
            ip_address=ip
        )
        return to_followup_response(item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
