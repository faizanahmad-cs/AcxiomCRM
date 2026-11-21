import re
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.lead import Lead, LeadStatusEnum
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.lead import LeadCreate, LeadUpdate, LeadConvertRequest
from acxiom_crm.backend.services.lead_service import (
    get_leads, get_lead_by_id, create_lead, update_lead, delete_lead, convert_lead
)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def render_lead_view(current_user: User):
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">🎯 Lead Management & Conversion</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Capture prospects, nurture opportunities, and execute lead-to-customer conversion workflows</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()
    try:
        all_users = db.query(User).filter(User.is_active == True).all()
        user_options = {u.user_id: f"{u.name} ({u.role})" for u in all_users}

        tab_list, tab_create, tab_convert = st.tabs(["📋 Leads Pipeline", "➕ Capture New Lead", "⚡ Lead Conversion Hub"])

        with tab_create:
            st.markdown("##### Capture New Prospective Lead")
            with st.form("create_lead_form", clear_on_submit=False):
                l_col1, l_col2 = st.columns(2)
                with l_col1:
                    lead_name = st.text_input("Contact / Prospect Name *", placeholder="e.g. Marcus Aurelius")
                    lead_email = st.text_input("Email Address *", placeholder="e.g. marcus@stoictech.com")
                    lead_phone = st.text_input("Phone Number *", placeholder="e.g. 9876543220")
                    lead_company = st.text_input("Company / Organization", placeholder="e.g. Stoic Tech Labs")
                with l_col2:
                    lead_source = st.selectbox("Acquisition Source", ["Website", "Referral", "Cold Call", "Trade Show", "Email Campaign", "Other"])
                    lead_status = st.selectbox("Initial Status", LeadStatusEnum.ALL, index=0)
                    lead_priority = st.selectbox("Priority Level", ["Low", "Medium", "High"], index=1)
                    expected_val = st.number_input("Expected Deal Value ($)", min_value=0.0, value=10000.0, step=1000.0)

                assigned_to = None
                if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                    assigned_to = st.selectbox(
                        "Assign Lead to Rep",
                        options=list(user_options.keys()),
                        format_func=lambda x: user_options.get(x, str(x)),
                        index=0 if user_options else None
                    )
                else:
                    assigned_to = current_user.user_id

                lead_notes = st.text_area("Initial Lead Notes / Requirements", placeholder="Prospect discovery details...")
                submitted = st.form_submit_button("Capture & Save Lead", type="primary", use_container_width=True)

                if submitted:
                    errs = []
                    if not lead_name.strip():
                        errs.append("Lead Name is mandatory.")
                    if not lead_email.strip() or not EMAIL_REGEX.match(lead_email.strip()):
                        errs.append("Enter a valid email address.")
                    digits = re.sub(r"\D", "", lead_phone.strip())
                    if len(digits) < 10 or len(digits) > 15:
                        errs.append("Enter a valid phone number.")

                    if errs:
                        for e in errs:
                            st.error(f"Validation Error: {e}")
                    else:
                        try:
                            lead_in = LeadCreate(
                                lead_name=lead_name.strip(),
                                email=lead_email.strip().lower(),
                                phone=lead_phone.strip(),
                                company_name=lead_company.strip() if lead_company else None,
                                source=lead_source,
                                status=lead_status,
                                priority=lead_priority,
                                expected_value=expected_val,
                                assigned_to=assigned_to,
                                notes=lead_notes.strip() if lead_notes else None
                            )
                            new_lead = create_lead(db, lead_in, current_user)
                            st.success(f"Lead '{new_lead.lead_name}' ({new_lead.lead_code}) created successfully!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error saving lead: {str(ex)}")

        with tab_list:
            f1, f2, f3, f4 = st.columns([3, 2, 2, 2])
            with f1:
                search_term = st.text_input("🔍 Search Leads", placeholder="Search by name, email, phone, company, code...")
            with f2:
                status_filter = st.selectbox("Filter Status", ["All"] + LeadStatusEnum.ALL)
            with f3:
                priority_filter = st.selectbox("Filter Priority", ["All", "High", "Medium", "Low"])
            with f4:
                source_filter = st.selectbox("Filter Source", ["All", "Website", "Referral", "Cold Call", "Trade Show", "Email Campaign", "Other"])

            leads = get_leads(
                db=db,
                current_user=current_user,
                search=search_term if search_term.strip() else None,
                status=status_filter,
                priority=priority_filter,
                source=source_filter,
                limit=150
            )

            st.write(f"Showing **{len(leads)}** lead(s)")
            if leads:
                table_rows = []
                for l in leads:
                    table_rows.append({
                        "ID": l.lead_id,
                        "Code": l.lead_code,
                        "Name": l.lead_name,
                        "Company": l.company_name or "-",
                        "Email": l.email,
                        "Phone": l.phone,
                        "Source": l.source,
                        "Status": l.status,
                        "Priority": l.priority,
                        "Expected Value ($)": f"${l.expected_value:,.2f}",
                        "Assigned Rep": l.assigned_user.name if l.assigned_user else "Unassigned",
                        "Created": l.created_at.strftime("%Y-%m-%d")
                    })
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

                # Edit / Transition / Delete Section
                st.markdown("---")
                st.markdown("##### ✏️ Update Lead Status or Assignee")
                lead_ids = [l.lead_id for l in leads]
                lead_display = {l.lead_id: f"{l.lead_code} - {l.lead_name} ({l.status}) - ${l.expected_value:,.0f}" for l in leads}

                selected_lead_id = st.selectbox("Select Lead to Edit", options=lead_ids, format_func=lambda x: lead_display.get(x, str(x)))
                if selected_lead_id:
                    selected_lead = get_lead_by_id(db, selected_lead_id, current_user)
                    if selected_lead:
                        with st.expander(f"📝 Edit Lead: {selected_lead.lead_name} ({selected_lead.lead_code})", expanded=False):
                            with st.form(f"edit_lead_form_{selected_lead.lead_id}"):
                                el1, el2 = st.columns(2)
                                with el1:
                                    el_name = st.text_input("Lead Name", value=selected_lead.lead_name)
                                    el_email = st.text_input("Email", value=selected_lead.email)
                                    el_phone = st.text_input("Phone", value=selected_lead.phone)
                                    el_company = st.text_input("Company", value=selected_lead.company_name or "")
                                with el2:
                                    el_source = st.selectbox("Source", ["Website", "Referral", "Cold Call", "Trade Show", "Email Campaign", "Other"], index=["Website", "Referral", "Cold Call", "Trade Show", "Email Campaign", "Other"].index(selected_lead.source) if selected_lead.source in ["Website", "Referral", "Cold Call", "Trade Show", "Email Campaign", "Other"] else 0)
                                    el_status = st.selectbox("Status", LeadStatusEnum.ALL, index=LeadStatusEnum.ALL.index(selected_lead.status) if selected_lead.status in LeadStatusEnum.ALL else 0)
                                    el_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(selected_lead.priority) if selected_lead.priority in ["Low", "Medium", "High"] else 1)
                                    el_val = st.number_input("Expected Value ($)", min_value=0.0, value=float(selected_lead.expected_value), step=1000.0)

                                el_notes = st.text_area("Notes", value=selected_lead.notes or "")
                                update_lead_btn = st.form_submit_button("Update Lead", type="primary")

                                if update_lead_btn:
                                    # Business rule: check cannot revert Converted lead
                                    if selected_lead.status == LeadStatusEnum.CONVERTED and el_status != LeadStatusEnum.CONVERTED:
                                        st.error("A Converted lead cannot be reverted to a previous status.")
                                    elif not el_name.strip():
                                        st.error("Lead Name is required.")
                                    elif not EMAIL_REGEX.match(el_email.strip()):
                                        st.error("Enter a valid email address.")
                                    else:
                                        try:
                                            l_update = LeadUpdate(
                                                lead_name=el_name.strip(),
                                                email=el_email.strip(),
                                                phone=el_phone.strip(),
                                                company_name=el_company.strip() if el_company else None,
                                                source=el_source,
                                                status=el_status,
                                                priority=el_priority,
                                                expected_value=el_val,
                                                notes=el_notes.strip() if el_notes else None
                                            )
                                            update_lead(db, selected_lead.lead_id, l_update, current_user)
                                            st.success("Lead updated successfully!")
                                            st.rerun()
                                        except Exception as ex:
                                            st.error(f"Update failed: {str(ex)}")

                        if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                            with st.expander("🗑️ Delete Lead", expanded=False):
                                st.warning(f"Permanently delete lead **{selected_lead.lead_name}** ({selected_lead.lead_code})?")
                                if st.button(f"Confirm Delete {selected_lead.lead_code}", type="primary"):
                                    try:
                                        delete_lead(db, selected_lead.lead_id, current_user)
                                        st.success(f"Lead {selected_lead.lead_code} deleted.")
                                        st.rerun()
                                    except Exception as ex:
                                        st.error(f"Delete failed: {str(ex)}")
            else:
                st.info("No leads found matching your criteria.")

        with tab_convert:
            st.markdown("##### ⚡ Lead Conversion Workflow (Lead → Customer + Opportunity)")
            st.info("Converting a lead creates a Customer record and automatically registers an active sales Opportunity in your pipeline.")

            # Filter only unconverted leads
            unconverted_leads = db.query(Lead).filter(Lead.status.notin_([LeadStatusEnum.CONVERTED, LeadStatusEnum.LOST]))
            if current_user.role == RoleEnum.SALES_EXECUTIVE:
                unconverted_leads = unconverted_leads.filter(Lead.assigned_to == current_user.user_id)
            unconverted_leads = unconverted_leads.all()

            if not unconverted_leads:
                st.success("All active leads have already been converted or qualified!")
            else:
                lead_to_convert_id = st.selectbox(
                    "Select Lead to Convert",
                    options=[l.lead_id for l in unconverted_leads],
                    format_func=lambda x: f"{next(l.lead_code for l in unconverted_leads if l.lead_id == x)}: {next(l.lead_name for l in unconverted_leads if l.lead_id == x)} ({next(l.company_name or 'Personal' for l in unconverted_leads if l.lead_id == x)}) - Expected: ${next(l.expected_value for l in unconverted_leads if l.lead_id == x):,.0f}"
                )
                target_lead = get_lead_by_id(db, lead_to_convert_id, current_user)
                if target_lead:
                    st.markdown(
                        f"""
                        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 14px; margin-bottom: 16px;">
                            <h4 style="margin: 0; color: #f8fafc;">Converting: {target_lead.lead_name}</h4>
                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                                Email: <strong>{target_lead.email}</strong> | Phone: <strong>{target_lead.phone}</strong> | Company: <strong>{target_lead.company_name or 'N/A'}</strong>
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    with st.form("lead_convert_execution_form"):
                        create_opp = st.checkbox("Create New Sales Opportunity for Customer", value=True)
                        co1, co2 = st.columns(2)
                        with co1:
                            opp_title = st.text_input("Opportunity Name", value=f"Deal - {target_lead.company_name or target_lead.lead_name}")
                            opp_amt = st.number_input("Opportunity Amount ($) *", min_value=1.0, value=float(target_lead.expected_value if target_lead.expected_value > 0 else 25000.0), step=1000.0)
                        with co2:
                            opp_close = st.date_input("Expected Close Date *", value=date.today() + timedelta(days=30))
                            opp_rep = target_lead.assigned_to or current_user.user_id

                        convert_btn = st.form_submit_button("🚀 Finalize Lead Conversion", type="primary", use_container_width=True)

                        if convert_btn:
                            # Business rule: expected close date cannot be in the past
                            if opp_close < date.today():
                                st.error("Expected Close Date cannot be in the past.")
                            elif opp_amt <= 0:
                                st.error("Opportunity Amount must be greater than 0.")
                            else:
                                try:
                                    req_data = LeadConvertRequest(
                                        create_opportunity=create_opp,
                                        opportunity_name=opp_title.strip() if opp_title else None,
                                        opportunity_amount=opp_amt,
                                        expected_close_date=opp_close,
                                        assigned_to=opp_rep
                                    )
                                    cust, opp = convert_lead(
                                        db=db,
                                        lead_id=target_lead.lead_id,
                                        convert_data=req_data,
                                        current_user=current_user
                                    )
                                    st.success(f"🎉 Lead successfully converted into Customer '{cust.customer_name}' ({cust.customer_code})!" + (f" and Opportunity '{opp.opportunity_name}'" if opp else ""))
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Conversion failed: {str(ex)}")
    finally:
        db.close()
