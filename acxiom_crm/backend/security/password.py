import re
from datetime import datetime, timedelta
import bcrypt
from acxiom_crm.backend.config import settings

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def validate_password_policy(password: str) -> tuple[bool, str]:
    """
    Validate password complexity:
    - Min 8 chars
    - 1 uppercase letter
    - 1 lowercase letter
    - 1 digit
    - 1 special character
    """
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long."
    if settings.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if settings.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter (a-z)."
    if settings.REQUIRE_DIGIT and not re.search(r"\d", password):
        return False, "Password must contain at least one number (0-9)."
    if settings.REQUIRE_SPECIAL_CHAR and not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character (!@#$%^&* etc.)."
    return True, "Password meets all policy requirements."
