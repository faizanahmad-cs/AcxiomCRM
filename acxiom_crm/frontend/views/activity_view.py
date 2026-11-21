import streamlit as st
import pandas as pd
from datetime import datetime
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.activity import Activity, ActivityTypeEnum
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.lead import Lead
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.activity import ActivityCreate
from acxiom_crm.backend.services.activity_service import get_activities, create_activity

def render_activity_view(current_user: User):
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">⚡ Client Activities & Touchpoints</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Log phone conversations, client meetings, email threads, and task notes</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()
    try:
        tab_timeline, tab_log = st.tabs(["📜 Activity Timeline", "➕ Log New Interaction"])

        with tab_log:
            st.markdown("##### Log Client Communication or Task")
            customers = db.query(Customer).all()
            leads = db.query(Lead).all()
            if current_user.role == RoleEnum.SALES_EXECUTIVE:
                customers = [c for c in customers if c.assigned_to == current_user.user_id]
                leads = [l for l in leads if l.assigned_to == current_user.user_id]

            with st.form("log_activity_form"):
                col1, col2 = st.columns(2)
                with col1:
                    act_type = st.selectbox("Interaction Channel", ActivityTypeEnum.ALL, index=0)
                    subject = st.text_input("Subject / Title *", placeholder="e.g. Discussed Q3 contract expansion")
                with col2:
                    rel_target = st.radio("Link to Record", ["Customer", "Lead", "General Task"], horizontal=True)
                    target_cust_id = None
                    target_lead_id = None

                    if rel_target == "Customer":
                        cust_opts = {c.customer_id: f"{c.customer_code} - {c.customer_name}" for c in customers}
                        if cust_opts:
                            target_cust_id = st.selectbox("Select Customer", options=list(cust_opts.keys()), format_func=lambda x: cust_opts.get(x, str(x)))
                        else:
                            st.caption("No customers available.")
                    elif rel_target == "Lead":
                        lead_opts = {l.lead_id: f"{l.lead_code} - {l.lead_name}" for l in leads}
                        if lead_opts:
                            target_lead_id = st.selectbox("Select Lead", options=list(lead_opts.keys()), format_func=lambda x: lead_opts.get(x, str(x)))
                        else:
                            st.caption("No leads available.")

                desc = st.text_area("Interaction Notes / Summary", placeholder="Detailed meeting minutes, agreements, key takeaways...")
                submitted = st.form_submit_button("Record Activity Entry", type="primary", use_container_width=True)

                if submitted:
                    if not subject.strip():
                        st.error("Subject is required.")
                    else:
                        try:
                            act_in = ActivityCreate(
                                activity_type=act_type,
                                subject=subject.strip(),
                                description=desc.strip() if desc else None,
                                customer_id=target_cust_id,
                                lead_id=target_lead_id,
                                assigned_to=current_user.user_id,
                                status="Completed"
                            )
                            create_activity(db, act_in, current_user)
                            st.success(f"Activity '{subject}' successfully logged!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error logging activity: {str(ex)}")

        with tab_timeline:
            filter_type = st.selectbox("Filter Activity Type", ["All"] + ActivityTypeEnum.ALL)
            activities = get_activities(db=db, current_user=current_user, activity_type=filter_type)

            st.write(f"Showing **{len(activities)}** recorded activity entries")
            if activities:
                rows = []
                for a in activities:
                    target_str = "General"
                    if a.customer:
                        target_str = f"Customer: {a.customer.customer_name}"
                    elif a.lead:
                        target_str = f"Lead: {a.lead.lead_name}"

                    rows.append({
                        "Date": a.activity_date.strftime("%Y-%m-%d %H:%M"),
                        "Channel": a.activity_type,
                        "Subject": a.subject,
                        "Associated To": target_str,
                        "Rep": a.assigned_user.name if a.assigned_user else "N/A",
                        "Notes": a.description or "-"
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No activities recorded yet.")
    finally:
        db.close()
