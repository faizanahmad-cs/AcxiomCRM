import streamlit as st
from datetime import datetime
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.services.audit_service import log_action

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None
    if "jwt_token" not in st.session_state:
        st.session_state["jwt_token"] = None
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Dashboard"

def set_logged_in_user(user: User, token: str):
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user.user_id
    st.session_state["user_email"] = user.email
    st.session_state["user_name"] = user.name
    st.session_state["user_role"] = user.role
    st.session_state["jwt_token"] = token
    st.session_state["current_page"] = "Dashboard"

def logout():
    user_id = st.session_state.get("user_id")
    email = st.session_state.get("user_email")
    if user_id:
        db = SessionLocal()
        try:
            log_action(
                db=db,
                action=AuditActionEnum.LOGOUT,
                entity_name="Auth",
                record_id=str(user_id),
                user_id=user_id,
                user_email=email,
                details="User logged out via Streamlit interface"
            )
        finally:
            db.close()

    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None
    st.session_state["user_role"] = None
    st.session_state["jwt_token"] = None
    st.session_state["current_page"] = "Dashboard"
    st.rerun()

def get_current_user_object() -> User:
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        return user
    finally:
        db.close()

def render_top_header():
    user_name = st.session_state.get("user_name", "User")
    user_email = st.session_state.get("user_email", "")
    user_role = st.session_state.get("user_role", RoleEnum.SALES_EXECUTIVE)

    role_class = "role-sales"
    if user_role == RoleEnum.ADMIN:
        role_class = "role-admin"
    elif user_role == RoleEnum.MANAGER:
        role_class = "role-manager"

    col_brand, col_user = st.columns([3, 2])
    with col_brand:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
                <div class="acxiom-logo">A</div>
                <div>
                    <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px;">AcxiomCRM</h2>
                    <p style="margin: 0; font-size: 12px; color: #94a3b8;">Enterprise Customer & Sales Lifecycle Platform</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_user:
        u_col, b_col = st.columns([3, 1])
        with u_col:
            st.markdown(
                f"""
                <div style="text-align: right; margin-top: 6px;">
                    <span style="font-weight: 700; color: #f1f5f9; font-size: 14px;">{user_name}</span><br/>
                    <span class="role-badge {role_class}">{user_role}</span>
                    <span style="color: #64748b; font-size: 11px; margin-left: 6px;">{user_email}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with b_col:
            st.write("")
            if st.button("🚪 Logout", key="top_logout_btn", use_container_width=True):
                logout()
    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 6px 0 20px 0;' />", unsafe_allow_html=True)
