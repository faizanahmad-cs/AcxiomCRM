from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from acxiom_crm.backend.database import get_db
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.schemas.user import UserLoginRequest, UserRegisterRequest, UserResponse, TokenResponse
from acxiom_crm.backend.services.auth_service import authenticate_user, register_user, AccountLockedError, AuthenticationError
from acxiom_crm.backend.services.audit_service import log_action
from acxiom_crm.backend.api.deps import get_current_user, get_client_ip, require_role

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = get_client_ip(request)
    try:
        user, token = authenticate_user(
            db=db,
            email=login_data.email,
            password=login_data.password,
            ip_address=ip
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    reg_data: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN]))  # Admin only can register/assign roles directly
):
    ip = get_client_ip(request)
    try:
        new_user = register_user(
            db=db,
            name=reg_data.name,
            email=reg_data.email,
            password=reg_data.password,
            role=reg_data.role,
            created_by_user=current_user,
            ip_address=ip
        )
        return UserResponse.model_validate(new_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT if "already exists" in str(e).lower() else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = get_client_ip(request)
    log_action(
        db=db,
        action=AuditActionEnum.LOGOUT,
        entity_name="Auth",
        record_id=str(current_user.user_id),
        user_id=current_user.user_id,
        user_email=current_user.email,
        details="User logged out session",
        ip_address=ip
    )
    return {"message": "Logged out successfully."}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
