from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from acxiom_crm.backend.database import get_db
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.audit import AuditLogResponse
from acxiom_crm.backend.services.audit_service import get_audit_logs
from acxiom_crm.backend.api.deps import require_role

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    user_email: Optional[str] = None,
    action: Optional[str] = None,
    entity_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER])),
    db: Session = Depends(get_db)
):
    logs = get_audit_logs(
        db=db,
        user_email=user_email,
        action=action,
        entity_name=entity_name,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    return [AuditLogResponse.model_validate(log) for log in logs]
