import re
import streamlit as st
import pandas as pd
from datetime import datetime
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.customer import CustomerCreate, CustomerUpdate
from acxiom_crm.backend.services.customer_service import (
    get_customers, get_customer_by_id, create_customer, update_customer, delete_customer
)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{10,20}$")

def render_customer_view(current_user: User):
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">👥 Customer Management</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Manage client master data, contacts, and account interactions</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()
    try:
        all_users = db.query(User).filter(User.is_active == True).all()
        user_options = {u.user_id: f"{u.name} ({u.role})" for u in all_users}

        # Action bar & Tabs
        tab_list, tab_create, tab_details = st.tabs(["📋 Customer Directory", "➕ Add New Customer", "🔍 Customer Details & History"])

        with tab_create:
            st.markdown("##### Register New Customer")
            with st.form("create_customer_form", clear_on_submit=False):
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    cust_name = st.text_input("Customer / Contact Name *", placeholder="e.g. John Henderson")
                    email = st.text_input("Business Email *", placeholder="e.g. john@company.com")
                    phone = st.text_input("Direct Phone *", placeholder="e.g. 9876543210")
                    company = st.text_input("Company Name", placeholder="e.g. Global Logistics Inc.")
                with c_col2:
                    address = st.text_input("Street Address", placeholder="e.g. 100 Main St")
                    city = st.text_input("City", placeholder="e.g. Chicago")
                    state = st.text_input("State / Province", placeholder="e.g. Illinois")
                    status_val = st.selectbox("Account Status", ["Active", "Inactive", "Lead_Converted"], index=0)

                assigned_to = None
                if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                    assigned_to = st.selectbox(
                        "Assigned Sales Executive",
                        options=list(user_options.keys()),
                        format_func=lambda x: user_options.get(x, str(x)),
                        index=0 if user_options else None
                    )
                else:
                    assigned_to = current_user.user_id

                notes = st.text_area("Account Notes / Preferences", placeholder="Client requirements, history, contract notes...")

                submitted = st.form_submit_button("Save & Register Customer", type="primary", use_container_width=True)

                if submitted:
                    # Client-side validation
                    errs = []
                    if not cust_name.strip():
                        errs.append("Customer Name is required.")
                    if not email.strip():
                        errs.append("Email is required.")
                    elif not EMAIL_REGEX.match(email.strip()):
                        errs.append("Enter a valid email address.")
                    
                    if not phone.strip():
                        errs.append("Phone is required.")
                    else:
                        digits = re.sub(r"\D", "", phone.strip())
                        if len(digits) < 10 or len(digits) > 15:
                            errs.append("Enter a valid phone number.")

                    if errs:
                        for e in errs:
                            st.error(f"Validation Error: {e}")
                    else:
                        try:
                            cust_in = CustomerCreate(
                                customer_name=cust_name.strip(),
                                email=email.strip().lower(),
                                phone=phone.strip(),
                                company_name=company.strip() if company else None,
                                address=address.strip() if address else None,
                                city=city.strip() if city else None,
                                state=state.strip() if state else None,
                                status=status_val,
                                assigned_to=assigned_to,
                                notes=notes.strip() if notes else None
                            )
                            new_c = create_customer(
                                db=db,
                                customer_in=cust_in,
                                current_user=current_user,
                                ip_address="127.0.0.1"
                            )
                            st.success(f"Customer '{new_c.customer_name}' ({new_c.customer_code}) created successfully!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error saving customer: {str(ex)}")

        with tab_list:
            # Search & Filter controls
            scol1, scol2, scol3 = st.columns([3, 2, 2])
            with scol1:
                search_term = st.text_input("🔍 Search Customers", placeholder="Search by name, email, phone, company, or code...")
            with scol2:
                status_filter = st.selectbox("Filter Status", ["All", "Active", "Inactive", "Lead_Converted"])
            with scol3:
                all_cities = sorted(list(set([c.city for c in db.query(Customer.city).filter(Customer.city != None).all() if c[0]])))
                city_filter = st.selectbox("Filter City", ["All"] + all_cities)

            customers = get_customers(
                db=db,
                current_user=current_user,
                search=search_term if search_term.strip() else None,
                status=status_filter,
                city=city_filter,
                limit=150
            )

            st.write(f"Showing **{len(customers)}** customer record(s)")

            if customers:
                table_data = []
                for c in customers:
                    table_data.append({
                        "ID": c.customer_id,
                        "Code": c.customer_code,
                        "Name": c.customer_name,
                        "Company": c.company_name or "-",
                        "Email": c.email,
                        "Phone": c.phone,
                        "City": c.city or "-",
                        "Status": c.status,
                        "Assigned Rep": c.assigned_user.name if c.assigned_user else "Unassigned",
                        "Created": c.created_at.strftime("%Y-%m-%d")
                    })
                df_cust = pd.DataFrame(table_data)
                st.dataframe(df_cust, use_container_width=True, hide_index=True)

                # Edit / Delete Section
                st.markdown("---")
                st.markdown("##### ✏️ Manage Selected Customer")
                cust_ids = [c.customer_id for c in customers]
                cust_display = {c.customer_id: f"{c.customer_code} - {c.customer_name} ({c.company_name or 'N/A'})" for c in customers}

                selected_id = st.selectbox(
                    "Choose Customer to Edit / Remove",
                    options=cust_ids,
                    format_func=lambda x: cust_display.get(x, str(x))
                )

                if selected_id:
                    selected_c = get_customer_by_id(db, selected_id, current_user)
                    if selected_c:
                        edit_expander = st.expander(f"📝 Edit Information for {selected_c.customer_name}", expanded=False)
                        with edit_expander:
                            with st.form(f"edit_cust_form_{selected_c.customer_id}"):
                                ec1, ec2 = st.columns(2)
                                with ec1:
                                    e_name = st.text_input("Customer Name", value=selected_c.customer_name)
                                    e_email = st.text_input("Email", value=selected_c.email)
                                    e_phone = st.text_input("Phone", value=selected_c.phone)
                                    e_company = st.text_input("Company", value=selected_c.company_name or "")
                                with ec2:
                                    e_city = st.text_input("City", value=selected_c.city or "")
                                    e_state = st.text_input("State", value=selected_c.state or "")
                                    e_status = st.selectbox("Status", ["Active", "Inactive", "Lead_Converted"], index=["Active", "Inactive", "Lead_Converted"].index(selected_c.status) if selected_c.status in ["Active", "Inactive", "Lead_Converted"] else 0)
                                    e_assigned = selected_c.assigned_to
                                    if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                                        e_assigned = st.selectbox(
                                            "Assigned To",
                                            options=list(user_options.keys()),
                                            format_func=lambda x: user_options.get(x, str(x)),
                                            index=list(user_options.keys()).index(selected_c.assigned_to) if selected_c.assigned_to in user_options else 0
                                        )

                                e_notes = st.text_area("Notes", value=selected_c.notes or "")
                                update_submit = st.form_submit_button("Update Customer Details", type="primary")

                                if update_submit:
                                    # Client validation
                                    errs = []
                                    if not e_name.strip():
                                        errs.append("Customer Name cannot be empty.")
                                    if not EMAIL_REGEX.match(e_email.strip()):
                                        errs.append("Enter a valid email address.")
                                    digits = re.sub(r"\D", "", e_phone.strip())
                                    if len(digits) < 10 or len(digits) > 15:
                                        errs.append("Enter a valid phone number.")

                                    if errs:
                                        for err in errs:
                                            st.error(err)
                                    else:
                                        try:
                                            update_in = CustomerUpdate(
                                                customer_name=e_name.strip(),
                                                email=e_email.strip(),
                                                phone=e_phone.strip(),
                                                company_name=e_company.strip() if e_company else None,
                                                city=e_city.strip() if e_city else None,
                                                state=e_state.strip() if e_state else None,
                                                status=e_status,
                                                assigned_to=e_assigned,
                                                notes=e_notes.strip() if e_notes else None
                                            )
                                            update_customer(db, selected_c.customer_id, update_in, current_user)
                                            st.success("Customer successfully updated!")
                                            st.rerun()
                                        except Exception as ex:
                                            st.error(f"Update failed: {str(ex)}")

                        # Delete action (Admin / Manager only)
                        if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                            with st.expander("🗑️ Delete Customer", expanded=False):
                                st.warning(f"Are you sure you want to permanently delete **{selected_c.customer_name}** ({selected_c.customer_code})? This will also remove associated opportunities.")
                                confirm_del = st.checkbox(f"Confirm deletion of {selected_c.customer_code}", key=f"del_chk_{selected_c.customer_id}")
                                if st.button(f"Permanently Delete {selected_c.customer_code}", type="primary", disabled=not confirm_del):
                                    try:
                                        delete_customer(db, selected_c.customer_id, current_user)
                                        st.success(f"Customer {selected_c.customer_code} deleted successfully.")
                                        st.rerun()
                                    except Exception as ex:
                                        st.error(f"Delete failed: {str(ex)}")
            else:
                st.info("No customers found matching the search criteria.")

        with tab_details:
            st.markdown("##### 🔍 360-Degree Customer Detail View")
            all_c = get_customers(db=db, current_user=current_user, limit=200)
            if not all_c:
                st.info("No customer records available.")
            else:
                detail_id = st.selectbox(
                    "Select Customer to inspect",
                    options=[c.customer_id for c in all_c],
                    format_func=lambda x: f"{next(c.customer_code for c in all_c if c.customer_id == x)} - {next(c.customer_name for c in all_c if c.customer_id == x)}",
                    key="detail_cust_select"
                )
                cust_obj = get_customer_by_id(db, detail_id, current_user)
                if cust_obj:
                    # Customer Details Card
                    d1, d2, d3 = st.columns(3)
                    with d1:
                        st.markdown(f"**Customer Code:** `{cust_obj.customer_code}`")
                        st.markdown(f"**Full Name:** {cust_obj.customer_name}")
                        st.markdown(f"**Company:** {cust_obj.company_name or 'N/A'}")
                    with d2:
                        st.markdown(f"**Email:** {cust_obj.email}")
                        st.markdown(f"**Phone:** {cust_obj.phone}")
                        st.markdown(f"**Location:** {cust_obj.city or '-'}, {cust_obj.state or '-'}")
                    with d3:
                        st.markdown(f"**Status:** `{cust_obj.status}`")
                        st.markdown(f"**Assigned Rep:** {cust_obj.assigned_user.name if cust_obj.assigned_user else 'Unassigned'}")
                        st.markdown(f"**Client Since:** {cust_obj.created_at.strftime('%Y-%m-%d')}")

                    if cust_obj.notes:
                        st.info(f"**Account Notes:** {cust_obj.notes}")

                    st.markdown("---")
                    st.markdown("##### 💼 Associated Opportunities")
                    if cust_obj.opportunities:
                        opp_rows = [{
                            "Opportunity": o.opportunity_name,
                            "Amount ($)": f"${o.amount:,.2f}",
                            "Stage": o.stage,
                            "Probability": f"{o.probability}%",
                            "Weighted Value": f"${o.weighted_amount:,.2f}",
                            "Expected Close": o.expected_close_date.strftime("%Y-%m-%d"),
                            "Status": o.status
                        } for o in cust_obj.opportunities]
                        st.dataframe(pd.DataFrame(opp_rows), use_container_width=True, hide_index=True)
                    else:
                        st.caption("No opportunities registered for this customer.")

                    st.markdown("##### 📅 Scheduled Follow-Ups")
                    if cust_obj.followups:
                        fol_rows = [{
                            "Date & Time": f.followup_date.strftime("%Y-%m-%d %H:%M"),
                            "Type": f.followup_type,
                            "Subject": f.subject,
                            "Status": f.status,
                            "Remarks": f.remarks or "-"
                        } for f in cust_obj.followups]
                        st.dataframe(pd.DataFrame(fol_rows), use_container_width=True, hide_index=True)
                    else:
                        st.caption("No follow-ups recorded.")

                    st.markdown("##### 📋 Activity History")
                    if cust_obj.activities:
                        act_rows = [{
                            "Date": a.activity_date.strftime("%Y-%m-%d %H:%M"),
                            "Type": a.activity_type,
                            "Subject": a.subject,
                            "Description": a.description or "-"
                        } for a in cust_obj.activities]
                        st.dataframe(pd.DataFrame(act_rows), use_container_width=True, hide_index=True)
                    else:
                        st.caption("No activities recorded.")
    finally:
        db.close()
