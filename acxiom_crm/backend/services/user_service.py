from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.security.password import hash_password, validate_password_policy
from acxiom_crm.backend.services.audit_service import log_action

def get_all_users(db: Session) -> List[User]:
    return db.query(User).order_by(User.role, User.name).all()

def update_user_profile(
    db: Session,
    user_id: int,
    name: Optional[str],
    role: Optional[str],
    is_active: Optional[bool],
    admin_user: User,
    ip_address: str = "127.0.0.1"
) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError("User not found.")

    old_state = {"name": user.name, "role": user.role, "is_active": user.is_active}

    if name:
        user.name = name.strip()
    if role and role in RoleEnum.ALL:
        if user.role != role:
            log_action(
                db=db,
                action=AuditActionEnum.ROLE_CHANGE,
                entity_name="User",
                record_id=str(user.user_id),
                user_id=admin_user.user_id,
                user_email=admin_user.email,
                old_value={"role": user.role},
                new_value={"role": role},
                details=f"User {user.email} role changed from {user.role} to {role}",
                ip_address=ip_address
            )
            user.role = role
    if is_active is not None:
        user.is_active = is_active

    db.commit()
    db.refresh(user)

    log_action(
        db=db,
        action=AuditActionEnum.UPDATE,
        entity_name="User",
        record_id=str(user.user_id),
        user_id=admin_user.user_id,
        user_email=admin_user.email,
        old_value=old_state,
        new_value={"name": user.name, "role": user.role, "is_active": user.is_active},
        details=f"User updated: {user.email}",
        ip_address=ip_address
    )
    return user

def admin_reset_password(
    db: Session,
    user_id: int,
    new_password: str,
    admin_user: User,
    ip_address: str = "127.0.0.1"
) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError("User not found.")

    valid, msg = validate_password_policy(new_password)
    if not valid:
        raise ValueError(msg)

    user.password_hash = hash_password(new_password)
    user.failed_login_count = 0
    user.lockout_until = None
    db.commit()

    log_action(
        db=db,
        action=AuditActionEnum.PASSWORD_RESET,
        entity_name="User",
        record_id=str(user.user_id),
        user_id=admin_user.user_id,
        user_email=admin_user.email,
        details=f"Admin reset password for user {user.email}",
        ip_address=ip_address
    )
    return user
