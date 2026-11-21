import streamlit as st
import pandas as pd
from datetime import date, timedelta
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.opportunity import (
    Opportunity, OpportunityStageEnum, OpportunityStatusEnum
)
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from acxiom_crm.backend.services.opportunity_service import (
    get_opportunities, get_opportunity_by_id, create_opportunity, update_opportunity, delete_opportunity
)

def render_opportunity_view(current_user: User):
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">💼 Opportunity Management</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Manage sales pipeline, deal stages, probability, and weighted revenue</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()
    try:
        customers = db.query(Customer).all()
        if current_user.role == RoleEnum.SALES_EXECUTIVE:
            customers = [c for c in customers if c.assigned_to == current_user.user_id]
        customer_options = {c.customer_id: f"{c.customer_code} - {c.customer_name} ({c.company_name or 'Direct'})" for c in customers}

        all_users = db.query(User).filter(User.is_active == True).all()
        user_options = {u.user_id: f"{u.name} ({u.role})" for u in all_users}

        tab_list, tab_create = st.tabs(["📋 Pipeline Deals", "➕ Create New Opportunity"])

        with tab_create:
            st.markdown("##### Register New Sales Opportunity")
            if not customer_options:
                st.warning("You must have at least one registered Customer before creating an Opportunity. Please add a customer first.")
            else:
                with st.form("create_opp_form", clear_on_submit=False):
                    o1, o2 = st.columns(2)
                    with o1:
                        opp_name = st.text_input("Opportunity Name / Title *", placeholder="e.g. Enterprise Cloud Migration")
                        selected_cust = st.selectbox(
                            "Associated Customer *",
                            options=list(customer_options.keys()),
                            format_func=lambda x: customer_options.get(x, str(x))
                        )
                        amount = st.number_input("Deal Amount ($) * (Must be > 0)", min_value=0.0, value=25000.0, step=1000.0)
                        probability = st.slider("Win Probability (%) * (0–100)", min_value=0.0, max_value=100.0, value=25.0, step=5.0)

                    with o2:
                        stage = st.selectbox("Pipeline Stage", OpportunityStageEnum.ALL, index=0)
                        close_date = st.date_input("Expected Close Date *", value=date.today() + timedelta(days=30))
                        assigned_to = None
                        if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                            assigned_to = st.selectbox(
                                "Opportunity Owner / Rep",
                                options=list(user_options.keys()),
                                format_func=lambda x: user_options.get(x, str(x)),
                                index=0 if user_options else None
                            )
                        else:
                            assigned_to = current_user.user_id

                    notes = st.text_area("Deal Description & Value Proposition", placeholder="Scope of deliverables, stakeholders, budget...")
                    submitted = st.form_submit_button("Create Opportunity", type="primary", use_container_width=True)

                    if submitted:
                        # Client-side validation
                        errs = []
                        if not opp_name.strip():
                            errs.append("Opportunity Name is required.")
                        if amount <= 0:
                            errs.append("Opportunity Amount must be greater than 0.")
                        if probability < 0 or probability > 100:
                            errs.append("Probability must be between 0 and 100.")
                        if stage in OpportunityStageEnum.ACTIVE_STAGES and close_date < date.today():
                            errs.append("Expected Close Date cannot be in the past.")

                        if errs:
                            for e in errs:
                                st.error(f"Validation Error: {e}")
                        else:
                            try:
                                opp_in = OpportunityCreate(
                                    opportunity_name=opp_name.strip(),
                                    customer_id=selected_cust,
                                    amount=amount,
                                    stage=stage,
                                    probability=probability,
                                    expected_close_date=close_date,
                                    assigned_to=assigned_to,
                                    notes=notes.strip() if notes else None
                                )
                                created_opp = create_opportunity(db, opp_in, current_user)
                                st.success(f"Opportunity '{created_opp.opportunity_name}' created successfully! (Weighted value: ${created_opp.weighted_amount:,.2f})")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error saving opportunity: {str(ex)}")

        with tab_list:
            f1, f2, f3 = st.columns([3, 2, 2])
            with f1:
                search_term = st.text_input("🔍 Search Opportunities", placeholder="Search by opportunity name or customer...")
            with f2:
                stage_filter = st.selectbox("Filter Stage", ["All"] + OpportunityStageEnum.ALL)
            with f3:
                status_filter = st.selectbox("Filter Status", ["All", "Open", "Won", "Lost"])

            opps = get_opportunities(
                db=db,
                current_user=current_user,
                search=search_term if search_term.strip() else None,
                stage=stage_filter,
                status=status_filter,
                limit=150
            )

            # Summary Bar
            total_val = sum(o.amount for o in opps)
            weighted_val = sum(o.weighted_amount for o in opps)
            s_col1, s_col2, s_col3 = st.columns(3)
            s_col1.metric("Opportunities in View", len(opps))
            s_col2.metric("Total Face Value", f"${total_val:,.2f}")
            s_col3.metric("Weighted Pipeline Value", f"${weighted_val:,.2f}")

            if opps:
                rows = []
                for o in opps:
                    rows.append({
                        "ID": o.opportunity_id,
                        "Opportunity": o.opportunity_name,
                        "Customer": o.customer.customer_name if o.customer else "N/A",
                        "Stage": o.stage,
                        "Amount ($)": f"${o.amount:,.2f}",
                        "Prob (%)": f"{o.probability:.0f}%",
                        "Weighted ($)": f"${o.weighted_amount:,.2f}",
                        "Expected Close": o.expected_close_date.strftime("%Y-%m-%d"),
                        "Status": o.status,
                        "Owner": o.assigned_user.name if o.assigned_user else "Unassigned"
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("##### ✏️ Update Opportunity Stage & Progression")
                opp_ids = [o.opportunity_id for o in opps]
                opp_display = {o.opportunity_id: f"#{o.opportunity_id}: {o.opportunity_name} (${o.amount:,.0f} - {o.stage})" for o in opps}

                selected_opp_id = st.selectbox("Select Opportunity to Update", options=opp_ids, format_func=lambda x: opp_display.get(x, str(x)))
                if selected_opp_id:
                    selected_opp = get_opportunity_by_id(db, selected_opp_id, current_user)
                    if selected_opp:
                        with st.expander(f"📝 Edit: {selected_opp.opportunity_name}", expanded=False):
                            with st.form(f"edit_opp_form_{selected_opp.opportunity_id}"):
                                eo1, eo2 = st.columns(2)
                                with eo1:
                                    e_title = st.text_input("Opportunity Name", value=selected_opp.opportunity_name)
                                    e_amount = st.number_input("Amount ($) * (Must be > 0)", min_value=0.0, value=float(selected_opp.amount), step=1000.0)
                                    e_prob = st.slider("Probability (%)", min_value=0.0, max_value=100.0, value=float(selected_opp.probability), step=5.0)
                                with eo2:
                                    e_stage = st.selectbox("Stage", OpportunityStageEnum.ALL, index=OpportunityStageEnum.ALL.index(selected_opp.stage) if selected_opp.stage in OpportunityStageEnum.ALL else 0)
                                    e_close = st.date_input("Expected Close Date", value=selected_opp.expected_close_date)
                                    e_owner = selected_opp.assigned_to
                                    if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                                        e_owner = st.selectbox(
                                            "Owner",
                                            options=list(user_options.keys()),
                                            format_func=lambda x: user_options.get(x, str(x)),
                                            index=list(user_options.keys()).index(selected_opp.assigned_to) if selected_opp.assigned_to in user_options else 0
                                        )

                                e_notes = st.text_area("Notes", value=selected_opp.notes or "")
                                update_opp_btn = st.form_submit_button("Save Changes", type="primary")

                                if update_opp_btn:
                                    # Client validation
                                    errs = []
                                    if not e_title.strip():
                                        errs.append("Opportunity Name cannot be empty.")
                                    if e_amount <= 0:
                                        errs.append("Opportunity Amount must be greater than 0.")
                                    if e_prob < 0 or e_prob > 100:
                                        errs.append("Probability must be between 0 and 100.")
                                    if e_stage in OpportunityStageEnum.ACTIVE_STAGES and e_close < date.today():
                                        errs.append("Expected Close Date cannot be in the past.")

                                    if errs:
                                        for err in errs:
                                            st.error(err)
                                    else:
                                        try:
                                            opp_update = OpportunityUpdate(
                                                opportunity_name=e_title.strip(),
                                                amount=e_amount,
                                                stage=e_stage,
                                                probability=e_prob,
                                                expected_close_date=e_close,
                                                assigned_to=e_owner,
                                                notes=e_notes.strip() if e_notes else None
                                            )
                                            update_opportunity(db, selected_opp.opportunity_id, opp_update, current_user)
                                            st.success("Opportunity successfully updated!")
                                            st.rerun()
                                        except Exception as ex:
                                            st.error(f"Update failed: {str(ex)}")

                        if current_user.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
                            with st.expander("🗑️ Delete Opportunity", expanded=False):
                                st.warning(f"Permanently delete **{selected_opp.opportunity_name}**?")
                                if st.button(f"Confirm Delete #{selected_opp.opportunity_id}", type="primary"):
                                    try:
                                        delete_opportunity(db, selected_opp.opportunity_id, current_user)
                                        st.success(f"Opportunity #{selected_opp.opportunity_id} deleted.")
                                        st.rerun()
                                    except Exception as ex:
                                        st.error(f"Delete failed: {str(ex)}")
            else:
                st.info("No opportunities found matching your filters.")
    finally:
        db.close()
