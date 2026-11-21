import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from acxiom_crm.backend.models.audit import AuditLog

def log_action(
    db: Session,
    action: str,
    entity_name: str,
    record_id: Optional[str] = None,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = "127.0.0.1"
) -> AuditLog:
    """Safely record an append-only audit event without storing sensitive information."""
    
    # Sanitize and serialize old/new values
    def sanitize(val):
        if val is None:
            return None
        if isinstance(val, dict):
            # Strip passwords and secrets
            safe_dict = {}
            for k, v in val.items():
                if "password" in k.lower() or "secret" in k.lower() or "token" in k.lower():
                    safe_dict[k] = "[REDACTED]"
                else:
                    safe_dict[k] = str(v)
            return json.dumps(safe_dict)
        return str(val)

    audit_entry = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        entity_name=entity_name,
        record_id=str(record_id) if record_id is not None else None,
        old_value=sanitize(old_value),
        new_value=sanitize(new_value),
        details=details,
        timestamp=datetime.utcnow(),
        ip_address=ip_address
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry

def get_audit_logs(
    db: Session,
    user_email: Optional[str] = None,
    action: Optional[str] = None,
    entity_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    query = db.query(AuditLog)
    if user_email:
        query = query.filter(AuditLog.user_email.ilike(f"%{user_email}%"))
    if action and action != "All":
        query = query.filter(AuditLog.action == action)
    if entity_name and entity_name != "All":
        query = query.filter(AuditLog.entity_name == entity_name)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        # Include full day for end_date
        query = query.filter(AuditLog.timestamp <= end_date + timedelta(days=1))
    
    return query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()
