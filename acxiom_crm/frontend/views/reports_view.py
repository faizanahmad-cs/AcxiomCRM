import streamlit as st
import pandas as pd
from datetime import date
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.lead import Lead, LeadStatusEnum
from acxiom_crm.backend.models.opportunity import Opportunity, OpportunityStageEnum, OpportunityStatusEnum
from acxiom_crm.backend.models.followup import FollowUp, FollowUpStatusEnum
from acxiom_crm.backend.models.activity import Activity
from acxiom_crm.backend.models.user import User, RoleEnum

def render_reports_view(current_user: User):
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">📈 Enterprise Reports & Business Analytics</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Generate, inspect, filter, and export CRM performance and pipeline compliance datasets</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()
    try:
        report_choice = st.selectbox(
            "Select Reporting Domain",
            [
                "📊 Pipeline & Revenue Forecast Report",
                "🎯 Lead Acquisition & Conversion Report",
                "👥 Customer Master Account Report",
                "📅 Follow-Up Compliance & SLA Report",
                "🏆 Sales Outcome & Win/Loss Velocity Report",
                "⚡ Team Activity & Rep Performance Report"
            ]
        )

        st.markdown("---")

        if report_choice.startswith("📊 Pipeline"):
            st.markdown("#### 📊 Sales Pipeline & Weighted Forecast Report")
            opp_q = db.query(Opportunity)
            if current_user.role == RoleEnum.SALES_EXECUTIVE:
                opp_q = opp_q.filter(Opportunity.assigned_to == current_user.user_id)
            opps = opp_q.all()

            if opps:
                rows = []
                for o in opps:
                    rows.append({
                        "Opportunity": o.opportunity_name,
                        "Customer": o.customer.customer_name if o.customer else "N/A",
                        "Stage": o.stage,
                        "Status": o.status,
                        "Amount ($)": o.amount,
                        "Probability (%)": o.probability,
                        "Weighted Value ($)": o.weighted_amount,
                        "Close Date": o.expected_close_date.strftime("%Y-%m-%d"),
                        "Owner": o.assigned_user.name if o.assigned_user else "Unassigned"
                    })
                df = pd.DataFrame(rows)

                # Summary KPIs
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Deals", len(df))
                col2.metric("Total Face Value", f"${df['Amount ($)'].sum():,.2f}")
                col3.metric("Total Weighted Pipeline", f"${df['Weighted Value ($)'].sum():,.2f}")

                st.dataframe(df, use_container_width=True, hide_index=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Pipeline Report to CSV", data=csv, file_name=f"pipeline_report_{date.today()}.csv", mime="text/csv")
            else:
                st.info("No opportunity data available.")

        elif report_choice.startswith("🎯 Lead"):
            st.markdown("#### 🎯 Lead Acquisition & Conversion Report")
            lead_q = db.query(Lead)
            if current_user.role == RoleEnum.SALES_EXECUTIVE:
                lead_q = lead_q.filter(Lead.assigned_to == current_user.user_id)
            leads = lead_q.all()

            if leads:
                rows = []
                for l in leads:
                    rows.append({
                        "Lead Code": l.lead_code,
                        "Lead Name": l.lead_name,
                        "Company": l.company_name or "-",
                        "Source": l.source,
                        "Status": l.status,
                        "Priority": l.priority,
                        "Expected Value ($)": l.expected_value,
                        "Converted Customer": l.converted_customer.customer_name if l.converted_customer else "-",
                        "Assigned Rep": l.assigned_user.name if l.assigned_user else "Unassigned",
                        "Created Date": l.created_at.strftime("%Y-%m-%d")
                    })
                df = pd.DataFrame(rows)

                total = len(df)
                converted = len(df[df["Status"] == LeadStatusEnum.CONVERTED])
                rate = (converted / total * 100) if total > 0 else 0

                c1, c2, c3 = st.columns(3)
                c1.metric("Total Captured Leads", total)
                c2.metric("Converted to Customers", converted)
                c3.metric("Conversion Rate", f"{rate:.1f}%")

                st.dataframe(df, use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Lead Report to CSV", data=csv, file_name=f"lead_report_{date.today()}.csv", mime="text/csv")
            else:
                st.info("No lead data available.")

        elif report_choice.startswith("👥 Customer"):
            st.markdown("#### 👥 Customer Master Account Report")
            cust_q = db.query(Customer)
            if current_user.role == RoleEnum.SALES_EXECUTIVE:
                cust_q = cust_q.filter(Customer.assigned_to == current_user.user_id)
            customers = cust_q.all()

            if customers:
                rows = []
                for c in customers:
                    rows.append({
                        "Code": c.customer_code,
                        "Customer Name": c.customer_name,
                        "Company": c.company_name or "-",
                        "Email": c.email,
                        "Phone": c.phone,
                        "City": c.city or "-",
                        "State": c.state or "-",
                        "Status": c.status,
                        "Assigned Rep": c.assigned_user.name if c.assigned_user else "Unassigned",
                        "Created Date": c.created_at.strftime("%Y-%m-%d")
                    })
                df = pd.DataFrame(rows)
                st.metric("Total Managed Customer Accounts", len(df))
                st.dataframe(df, use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Customer Report to CSV", data=csv, file_name=f"customer_report_{date.today()}.csv", mime="text/csv")
            else:
                st.info("No customer data available.")

        elif report_choice.startswith("📅 Follow-Up"):
            st.markdown("#### 📅 Follow-Up Compliance & SLA Report")
            fol_q = db.query(FollowUp)
            if current_user.role == RoleEnum.SALES_EXECUTIVE:
                fol_q = fol_q.filter(FollowUp.assigned_to == current_user.user_id)
            followups = fol_q.all()

            if followups:
                rows = []
                for f in followups:
                    rows.append({
                        "ID": f.followup_id,
                        "Date & Time": f.followup_date.strftime("%Y-%m-%d %H:%M"),
                        "Channel": f.followup_type,
                        "Subject": f.subject,
                        "Relation": f"{f.related_type} #{f.related_id}",
                        "Status": f.status,
                        "Is Overdue": "YES" if f.is_overdue() else "NO",
                        "Rep": f.assigned_user.name if f.assigned_user else "Unassigned",
                        "Completed Date": f.completed_at.strftime("%Y-%m-%d %H:%M") if f.completed_at else "-"
                    })
                df = pd.DataFrame(rows)
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Follow-Ups", len(df))
                c2.metric("Completed Tasks", len(df[df["Status"] == FollowUpStatusEnum.COMPLETED]))
                c3.metric("Overdue Items", len(df[df["Is Overdue"] == "YES"]))

                st.dataframe(df, use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Follow-Up Report to CSV", data=csv, file_name=f"followup_report_{date.today()}.csv", mime="text/csv")
            else:
                st.info("No follow-up records found.")

        elif report_choice.startswith("🏆 Sales"):
            st.markdown("#### 🏆 Sales Outcome & Win/Loss Velocity Report")
            opp_q = db.query(Opportunity)
            if current_user.role == RoleEnum.SALES_EXECUTIVE:
                opp_q = opp_q.filter(Opportunity.assigned_to == current_user.user_id)
            opps = opp_q.all()

            won = [o for o in opps if o.stage == OpportunityStageEnum.WON]
            lost = [o for o in opps if o.stage == OpportunityStageEnum.LOST]
            closed_total = len(won) + len(lost)
            win_rate = (len(won) / closed_total * 100) if closed_total > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Closed Won Deals", len(won))
            c2.metric("Won Revenue", f"${sum(o.amount for o in won):,.2f}")
            c3.metric("Closed Lost Deals", len(lost))
            c4.metric("Win Rate %", f"{win_rate:.1f}%")

            outcome_rows = [{
                "Deal Name": o.opportunity_name,
                "Customer": o.customer.customer_name if o.customer else "-",
                "Outcome": o.stage,
                "Deal Amount ($)": o.amount,
                "Rep": o.assigned_user.name if o.assigned_user else "Unassigned",
                "Closed Date": o.expected_close_date.strftime("%Y-%m-%d")
            } for o in (won + lost)]
            if outcome_rows:
                df = pd.DataFrame(outcome_rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Win/Loss Report to CSV", data=csv, file_name=f"win_loss_report_{date.today()}.csv", mime="text/csv")
            else:
                st.info("No closed deals recorded yet.")

        elif report_choice.startswith("⚡ Team Activity"):
            st.markdown("#### ⚡ Team Activity & Rep Performance Report")
            act_q = db.query(Activity)
            if current_user.role == RoleEnum.SALES_EXECUTIVE:
                act_q = act_q.filter(Activity.assigned_to == current_user.user_id)
            acts = act_q.all()

            if acts:
                rows = [{
                    "Date": a.activity_date.strftime("%Y-%m-%d %H:%M"),
                    "Type": a.activity_type,
                    "Subject": a.subject,
                    "Rep": a.assigned_user.name if a.assigned_user else "Unassigned",
                    "Status": a.status
                } for a in acts]
                df = pd.DataFrame(rows)
                st.metric("Total Activities Logged", len(df))
                st.dataframe(df, use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Activity Report to CSV", data=csv, file_name=f"activity_report_{date.today()}.csv", mime="text/csv")
            else:
                st.info("No activities logged.")

    finally:
        db.close()
