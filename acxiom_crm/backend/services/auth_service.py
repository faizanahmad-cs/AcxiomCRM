from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from acxiom_crm.backend.config import settings
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.security.password import hash_password, verify_password, validate_password_policy
from acxiom_crm.backend.security.jwt import create_access_token
from acxiom_crm.backend.services.audit_service import log_action

class AuthenticationError(Exception):
    pass

class AccountLockedError(Exception):
    def __init__(self, message: str, lockout_until: datetime):
        super().__init__(message)
        self.lockout_until = lockout_until

def authenticate_user(db: Session, email: str, password: str, ip_address: str = "127.0.0.1") -> Tuple[User, str]:
    """
    Authenticate user by email and password with automatic lockout protection.
    Returns (user, token) on success.
    Raises AccountLockedError or AuthenticationError on failure.
    """
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        # Unknown email attempt
        log_action(
            db=db,
            action=AuditActionEnum.FAILED_LOGIN,
            entity_name="Auth",
            user_email=email,
            details=f"Failed login attempt for unknown email from {ip_address}",
            ip_address=ip_address
        )
        raise AuthenticationError("Invalid email or password.")

    # Check if account is active
    if not user.is_active:
        log_action(
            db=db,
            action=AuditActionEnum.FAILED_LOGIN,
            entity_name="Auth",
            user_id=user.user_id,
            user_email=user.email,
            details="Login attempted on inactive account",
            ip_address=ip_address
        )
        raise AuthenticationError("Account has been deactivated. Please contact an Administrator.")

    # Check lockout
    now = datetime.utcnow()
    if user.lockout_until:
        if user.lockout_until > now:
            remaining = int((user.lockout_until - now).total_seconds() / 60) + 1
            log_action(
                db=db,
                action=AuditActionEnum.FAILED_LOGIN,
                entity_name="Auth",
                user_id=user.user_id,
                user_email=user.email,
                details=f"Login attempt on locked account. Locked for {remaining} more minute(s).",
                ip_address=ip_address
            )
            raise AccountLockedError(
                f"Account is temporarily locked due to repeated failed login attempts. Try again in {remaining} minute(s) or contact an Admin.",
                lockout_until=user.lockout_until
            )
        else:
            # Lockout period expired - unlock automatically
            user.lockout_until = None
            user.failed_login_count = 0
            db.commit()

    # Verify password
    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        remaining_attempts = max(0, settings.MAX_FAILED_LOGIN_ATTEMPTS - user.failed_login_count)

        if user.failed_login_count >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.lockout_until = now + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            db.commit()
            log_action(
                db=db,
                action=AuditActionEnum.LOCKOUT,
                entity_name="User",
                record_id=str(user.user_id),
                user_id=user.user_id,
                user_email=user.email,
                details=f"Account locked for {settings.LOCKOUT_DURATION_MINUTES} minutes after {user.failed_login_count} failed attempts",
                ip_address=ip_address
            )
            raise AccountLockedError(
                f"Account locked! Maximum failed attempts ({settings.MAX_FAILED_LOGIN_ATTEMPTS}) reached. Account locked for {settings.LOCKOUT_DURATION_MINUTES} minutes.",
                lockout_until=user.lockout_until
            )
        else:
            db.commit()
            log_action(
                db=db,
                action=AuditActionEnum.FAILED_LOGIN,
                entity_name="Auth",
                user_id=user.user_id,
                user_email=user.email,
                details=f"Failed password attempt ({user.failed_login_count}/{settings.MAX_FAILED_LOGIN_ATTEMPTS})",
                ip_address=ip_address
            )
            raise AuthenticationError(
                f"Invalid email or password. {remaining_attempts} attempt(s) remaining before lockout."
            )

    # Password correct! Reset failure counters
    user.failed_login_count = 0
    user.lockout_until = None
    user.last_login_at = now
    db.commit()

    # Generate JWT token
    token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email, "role": user.role}
    )

    log_action(
        db=db,
        action=AuditActionEnum.LOGIN,
        entity_name="Auth",
        record_id=str(user.user_id),
        user_id=user.user_id,
        user_email=user.email,
        details=f"User successfully logged in as {user.role}",
        ip_address=ip_address
    )

    return user, token

def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str = RoleEnum.SALES_EXECUTIVE,
    created_by_user: Optional[User] = None,
    ip_address: str = "127.0.0.1"
) -> User:
    """Register a new user with validation and audit logging."""
    email_clean = email.strip().lower()

    # Check duplicate email
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise ValueError(f"User with email '{email_clean}' already exists.")

    # Validate password complexity
    valid_pass, msg = validate_password_policy(password)
    if not valid_pass:
        raise ValueError(msg)

    if role not in RoleEnum.ALL:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {', '.join(RoleEnum.ALL)}")

    new_user = User(
        name=name.strip(),
        email=email_clean,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
        failed_login_count=0,
        lockout_until=None,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_action(
        db=db,
        action=AuditActionEnum.CREATE,
        entity_name="User",
        record_id=str(new_user.user_id),
        user_id=created_by_user.user_id if created_by_user else new_user.user_id,
        user_email=created_by_user.email if created_by_user else new_user.email,
        new_value={"name": new_user.name, "email": new_user.email, "role": new_user.role},
        details=f"New user registered: {new_user.email} ({new_user.role})",
        ip_address=ip_address
    )

    return new_user

def unlock_user_account(db: Session, user_id: int, admin_user: User, ip_address: str = "127.0.0.1") -> User:
    """Admin unlock for locked user account."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError("User not found.")
    
    user.lockout_until = None
    user.failed_login_count = 0
    db.commit()

    log_action(
        db=db,
        action=AuditActionEnum.UNLOCK,
        entity_name="User",
        record_id=str(user.user_id),
        user_id=admin_user.user_id,
        user_email=admin_user.email,
        details=f"Admin unlocked user account {user.email}",
        ip_address=ip_address
    )
    return user
