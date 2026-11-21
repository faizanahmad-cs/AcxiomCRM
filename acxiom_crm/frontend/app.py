import streamlit as st
import sys
from pathlib import Path

# Ensure root package is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from acxiom_crm.backend.seed_data import seed_database
from acxiom_crm.backend.models.user import RoleEnum
from acxiom_crm.frontend.styles import get_custom_css
from acxiom_crm.frontend.state import (
    init_session_state, get_current_user_object, render_top_header, logout
)
from acxiom_crm.frontend.views import (
    render_login_view,
    render_dashboard_view,
    render_customer_view,
    render_lead_view,
    render_opportunity_view,
    render_followup_view,
    render_activity_view,
    render_user_admin_view,
    render_audit_view,
    render_reports_view,
    render_api_docs_view
)

# Page Configuration
st.set_page_config(
    page_title="AcxiomCRM | Enterprise Sales Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Modern SaaS CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize Session State
init_session_state()

# Ensure Database Seeded
seed_database()

# Authentication Guard
if not st.session_state.get("authenticated", False):
    render_login_view()
else:
    current_user = get_current_user_object()
    if not current_user:
        st.session_state["authenticated"] = False
        st.rerun()

    # Render Persistent Header
    render_top_header()

    # Sidebar Navigation Scoped to Role
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px;">
            <span style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">
                NAVIGATION
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    nav_options = [
        "📊 Dashboard",
        "👥 Customers",
        "🎯 Leads & Conversion",
        "💼 Opportunities",
        "📅 Follow-Ups",
        "⚡ Activities"
    ]

    if current_user.role == RoleEnum.ADMIN:
        nav_options.extend([
            "👤 User & Role Management",
            "📜 Audit Log",
            "📈 Reports & Analytics",
            "🔌 REST API Gateway"
        ])
    elif current_user.role == RoleEnum.MANAGER:
        nav_options.extend([
            "📜 Audit Log",
            "📈 Reports & Analytics",
            "🔌 REST API Gateway"
        ])
    else:  # Sales Executive
        nav_options.extend([
            "📈 Reports & Analytics",
            "🔌 REST API Gateway"
        ])

    selected_nav = st.sidebar.radio(
        "Modules",
        nav_options,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 24px 0 12px 0;' />", unsafe_allow_html=True)

    # Sidebar Quick Info
    st.sidebar.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Logged In As</div>
            <div style="font-size: 13px; font-weight: 700; color: #f8fafc; margin-top: 2px;">{current_user.name}</div>
            <div style="font-size: 11px; color: #38bdf8;">Role: {current_user.role}</div>
            <div style="font-size: 10px; color: #64748b; margin-top: 4px;">{current_user.email}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.sidebar.button("🚪 Logout Session", use_container_width=True):
        logout()

    # Route to Views
    if "Dashboard" in selected_nav:
        render_dashboard_view(current_user)
    elif "Customers" in selected_nav:
        render_customer_view(current_user)
    elif "Leads" in selected_nav:
        render_lead_view(current_user)
    elif "Opportunities" in selected_nav:
        render_opportunity_view(current_user)
    elif "Follow-Ups" in selected_nav:
        render_followup_view(current_user)
    elif "Activities" in selected_nav:
        render_activity_view(current_user)
    elif "User & Role" in selected_nav:
        render_user_admin_view(current_user)
    elif "Audit Log" in selected_nav:
        render_audit_view(current_user)
    elif "Reports" in selected_nav:
        render_reports_view(current_user)
    elif "REST API" in selected_nav:
        render_api_docs_view(current_user)

    # Footer
    st.markdown(
        """
        <div style="margin-top: 50px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06); text-align: center; color: #64748b; font-size: 12px;">
            AcxiomCRM v1.0.0 Enterprise • Secure Role-Based Customer & Sales Management System • Built with Python, Streamlit & FastAPI
        </div>
        """,
        unsafe_allow_html=True
    )
