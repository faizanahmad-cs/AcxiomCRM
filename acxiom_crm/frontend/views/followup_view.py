import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta, time
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.followup import (
    FollowUp, FollowUpStatusEnum, FollowUpTypeEnum, RelatedTypeEnum
)
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.lead import Lead
from acxiom_crm.backend.models.opportunity import Opportunity
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.followup import FollowUpCreate, FollowUpUpdate
from acxiom_crm.backend.services.followup_service import (
    get_followups, get_followup_by_id, create_followup, complete_followup, update_followup
)

def render_followup_view(current_user: User):
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">📅 Follow-Up & Task Management</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Schedule client calls, meetings, product demos, and track task compliance</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()
    try:
        all_users = db.query(User).filter(User.is_active == True).all()
        user_options = {u.user_id: f"{u.name} ({u.role})" for u in all_users}

        tab_upcoming, tab_overdue, tab_all, tab_schedule = st.tabs([
            "⏳ Upcoming & Planned",
            "⚠️ Overdue Follow-Ups",
            "📚 Full History & All Statuses",
            "➕ Schedule New Follow-Up"
        ])

        with tab_schedule:
            st.markdown("##### Schedule Client or Prospect Follow-Up")
            with st.form("schedule_followup_form", clear_on_submit=False):
                f_rel_type = st.selectbox("Related To Entity *", [RelatedTypeEnum.CUSTOMER, RelatedTypeEnum.LEAD, RelatedTypeEnum.OPPORTUNITY])

                # Fetch available records for relation
                related_records = {}
                if f_rel_type == RelatedTypeEnum.CUSTOMER:
                    c_query = db.query(Customer)
                    if current_user.role == RoleEnum.SALES_EXECUTIVE:
                        c_query = c_query.filter(Customer.assigned_to == current_user.user_id)
                    related_records = {c.customer_id: f"{c.customer_code} - {c.customer_name} ({c.company_name or 'Direct'})" for c in c_query.all()}
                elif f_rel_type == RelatedTypeEnum.LEAD:
                    l_query = db.query(Lead)
                    if current_user.role == RoleEnum.SALES_EXECUTIVE:
                        l_query = l_query.filter(Lead.assigned_to == current_user.user_id)
                    related_records = {l.lead_id: f"{l.lead_code} - {l.lead_name} ({l.company_name or 'N/A'})" for l in l_query.all()}
                elif f_rel_type == RelatedTypeEnum.OPPORTUNITY:
                    o_query = db.query(Opportunity)
                    if current_user.role == RoleEnum.SALES_EXECUTIVE:
                        o_query = o_query.filter(Opportunity.assigned_to == current_user.user_id)
                    related_records = {o.opportunity_id: f"Deal #{o.opportunity_id}: {o.opportunity_name} (${o.amount:,.0f})" for o in o_query.all()}

                if not related_records:
                    st.warning(f"No accessible {f_rel_type} records found. Please create a {f_rel_type} first.")
                    f_rel_id = None
                else:
                    f_rel_id = st.selectbox(
                        f"Choose {f_rel_type} Record *",
                        options=list(related_records.keys()),
                        format_func=lambda x: related_records.get(x, str(x))
                    )

                c1, c2 = st.columns(2)
                with c1:
                    f_type = st.selectbox("Follow-Up Channel", FollowUpTypeEnum.ALL, index=0)
                    f_date = st.date_input("Scheduled Date * (Cannot be earlier than today)", value=date.today())
                    f_time = st.time_input("Scheduled Time", value=time(10, 0))
                with c2:
                    f_subject = st.text_input("Subject / Meeting Goal *", placeholder="e.g. Discuss RFP proposal & pricing options")
                    f_assigned = None
                    if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                        f_assigned = st.selectbox(
                            "Assigned To Rep",
                            options=list(user_options.keys()),
                            format_func=lambda x: user_options.get(x, str(x)),
                            index=0 if user_options else None
                        )
                    else:
                        f_assigned = current_user.user_id

                f_remarks = st.text_area("Agenda / Context Notes", placeholder="Key discussion points, presentation links...")
                submitted = st.form_submit_button("Confirm & Schedule Follow-Up", type="primary", use_container_width=True)

                if submitted:
                    # Client-side validation
                    errs = []
                    if not f_rel_id:
                        errs.append("A related record must be selected.")
                    if not f_subject.strip():
                        errs.append("Subject is required.")
                    if f_date < date.today():
                        errs.append("Follow-up date cannot be earlier than today.")

                    if errs:
                        for e in errs:
                            st.error(f"Validation Error: {e}")
                    else:
                        scheduled_dt = datetime.combine(f_date, f_time)
                        try:
                            fol_in = FollowUpCreate(
                                related_type=f_rel_type,
                                related_id=f_rel_id,
                                followup_date=scheduled_dt,
                                followup_type=f_type,
                                subject=f_subject.strip(),
                                remarks=f_remarks.strip() if f_remarks else None,
                                status=FollowUpStatusEnum.PLANNED,
                                assigned_to=f_assigned
                            )
                            new_fol = create_followup(db, fol_in, current_user)
                            st.success(f"Follow-up '{new_fol.subject}' scheduled for {scheduled_dt.strftime('%Y-%m-%d %H:%M')}!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error scheduling follow-up: {str(ex)}")

        # Helper renderer for follow-up tables with Complete button
        def display_followups_list(items, title):
            st.markdown(f"##### {title} ({len(items)})")
            if not items:
                st.info(f"No {title.lower()} found.")
                return

            rows = []
            for item in items:
                rel_label = f"{item.related_type} #{item.related_id}"
                if item.related_type == RelatedTypeEnum.CUSTOMER and item.customer:
                    rel_label = f"Customer: {item.customer.customer_name}"
                elif item.related_type == RelatedTypeEnum.LEAD and item.lead:
                    rel_label = f"Lead: {item.lead.lead_name}"
                elif item.related_type == RelatedTypeEnum.OPPORTUNITY and item.opportunity:
                    rel_label = f"Opp: {item.opportunity.opportunity_name}"

                rows.append({
                    "ID": item.followup_id,
                    "Date & Time": item.followup_date.strftime("%Y-%m-%d %H:%M"),
                    "Type": item.followup_type,
                    "Subject": item.subject,
                    "Relation": rel_label,
                    "Status": item.status,
                    "Rep": item.assigned_user.name if item.assigned_user else "N/A",
                    "Remarks": item.remarks or "-"
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Quick Action: Mark Completed
            active_items = [i for i in items if i.status == FollowUpStatusEnum.PLANNED]
            if active_items:
                st.markdown("---")
                st.markdown("##### ✅ Complete or Update Selected Follow-Up")
                item_options = {i.followup_id: f"#{i.followup_id}: {i.subject} ({i.followup_date.strftime('%Y-%m-%d')})" for i in active_items}
                chosen_id = st.selectbox("Select Follow-Up to Action", options=list(item_options.keys()), format_func=lambda x: item_options.get(x, str(x)))

                if chosen_id:
                    chosen_fol = get_followup_by_id(db, chosen_id, current_user)
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        with st.form(f"complete_form_{chosen_id}"):
                            st.markdown(f"**Mark as Completed:** {chosen_fol.subject}")
                            completion_notes = st.text_input("Call/Meeting Outcome Notes", placeholder="e.g. Client agreed to schedule final contract review.")
                            if st.form_submit_button("✅ Mark as Completed", type="primary"):
                                try:
                                    complete_followup(db, chosen_id, completion_notes, current_user)
                                    st.success(f"Follow-up #{chosen_id} marked as completed!")
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Error: {str(ex)}")

                    with act_col2:
                        with st.form(f"reschedule_form_{chosen_id}"):
                            st.markdown(f"**Reschedule:** {chosen_fol.subject}")
                            new_date = st.date_input("New Date", value=date.today() + timedelta(days=2))
                            new_time = st.time_input("New Time", value=time(11, 0))
                            if st.form_submit_button("🔄 Reschedule Follow-Up"):
                                if new_date < date.today():
                                    st.error("Follow-up date cannot be earlier than today.")
                                else:
                                    new_dt = datetime.combine(new_date, new_time)
                                    try:
                                        up_in = FollowUpUpdate(followup_date=new_dt, status=FollowUpStatusEnum.PLANNED)
                                        update_followup(db, chosen_id, up_in, current_user)
                                        st.success(f"Rescheduled to {new_dt.strftime('%Y-%m-%d %H:%M')}")
                                        st.rerun()
                                    except Exception as ex:
                                        st.error(f"Error: {str(ex)}")

        with tab_upcoming:
            upcoming = get_followups(db=db, current_user=current_user, only_upcoming=True)
            display_followups_list(upcoming, "Upcoming Scheduled Follow-Ups")

        with tab_overdue:
            overdue = get_followups(db=db, current_user=current_user, only_overdue=True)
            display_followups_list(overdue, "Overdue Action Items")

        with tab_all:
            all_fol = get_followups(db=db, current_user=current_user)
            display_followups_list(all_fol, "All Follow-Up History & Completed Records")

    finally:
        db.close()
