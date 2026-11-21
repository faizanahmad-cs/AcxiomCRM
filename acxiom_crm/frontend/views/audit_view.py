import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditActionEnum
from acxiom_crm.backend.services.audit_service import get_audit_logs

def render_audit_view(current_user: User):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
        st.error("⛔ Access Denied: Security Audit Logs are restricted to Administrators and Managers.")
        return

    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">📜 Security & Operations Audit Trail</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Append-only regulatory audit log recording logins, data mutations, role changes, and lockout events</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()
    try:
        # Filter controls
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            action_filter = st.selectbox("Action Type", ["All"] + AuditActionEnum.ALL)
        with c2:
            entity_filter = st.selectbox("Entity / Module", ["All", "User", "Customer", "Lead", "Opportunity", "FollowUp", "Activity", "Auth"])
        with c3:
            user_search = st.text_input("Filter by User Email", placeholder="e.g. admin@")
        with c4:
            days_back = st.selectbox("Timeframe", ["All Records", "Last 24 Hours", "Last 7 Days", "Last 30 Days"])

        start_dt = None
        if days_back == "Last 24 Hours":
            start_dt = datetime.utcnow() - timedelta(days=1)
        elif days_back == "Last 7 Days":
            start_dt = datetime.utcnow() - timedelta(days=7)
        elif days_back == "Last 30 Days":
            start_dt = datetime.utcnow() - timedelta(days=30)

        logs = get_audit_logs(
            db=db,
            user_email=user_search.strip() if user_search.strip() else None,
            action=action_filter,
            entity_name=entity_filter,
            start_date=start_dt,
            limit=250
        )

        st.write(f"Showing **{len(logs)}** audit log entries")

        if logs:
            table_rows = []
            for l in logs:
                table_rows.append({
                    "Timestamp (UTC)": l.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Action": l.action,
                    "Entity": l.entity_name,
                    "Record ID": l.record_id or "-",
                    "User": l.user_email or "System / Anonymous",
                    "Details": l.details or "-",
                    "Old Value": l.old_value or "-",
                    "New Value": l.new_value or "-",
                    "IP Address": l.ip_address or "127.0.0.1"
                })

            df_logs = pd.DataFrame(table_rows)
            st.dataframe(df_logs, use_container_width=True, hide_index=True)

            # Export to CSV
            csv_data = df_logs.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export Audit Log to CSV",
                data=csv_data,
                file_name=f"acxiom_crm_audit_log_{date.today()}.csv",
                mime="text/csv",
                type="secondary"
            )
        else:
            st.info("No audit log records found for the selected criteria.")
    finally:
        db.close()
