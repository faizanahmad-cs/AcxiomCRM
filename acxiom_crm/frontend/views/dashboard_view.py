import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.followup import FollowUp, FollowUpStatusEnum
from acxiom_crm.backend.services.report_service import get_dashboard_kpis, get_chart_data

def render_dashboard_view(current_user: User):
    # Top banner / Filter bar
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">
                    {'👑 Executive Overview' if current_user.role == RoleEnum.ADMIN else ('👔 Management Pipeline' if current_user.role == RoleEnum.MANAGER else '💼 My Sales Workspace')}
                </h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">
                    Real-time pipeline metrics, performance indicators & revenue intelligence
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Date filter controls
    fcol1, fcol2, fcol3 = st.columns([2, 2, 4])
    with fcol1:
        date_filter = st.selectbox(
            "📅 Date Horizon",
            ["All Time", "Today", "This Week", "This Month", "Custom Range"],
            index=0
        )
    custom_start = None
    custom_end = None
    if date_filter == "Custom Range":
        with fcol2:
            custom_start = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        with fcol3:
            custom_end = st.date_input("End Date", value=date.today())

    db = SessionLocal()
    try:
        kpis = get_dashboard_kpis(
            db=db,
            current_user=current_user,
            date_filter=date_filter,
            custom_start=custom_start,
            custom_end=custom_end
        )
        charts = get_chart_data(
            db=db,
            current_user=current_user,
            date_filter=date_filter,
            custom_start=custom_start,
            custom_end=custom_end
        )

        # Urgent Overdue Follow-ups Notification
        if kpis["overdue_followups"] > 0:
            st.markdown(
                f"""
                <div class="overdue-banner">
                    <span style="font-size: 20px;">⚠️</span>
                    <div>
                        <strong>Attention Needed:</strong> You have <strong>{kpis['overdue_followups']}</strong> overdue follow-up task(s). 
                        Please review and reschedule or mark them completed.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # KPI Metric Cards Row 1: Pipeline & Revenue
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Total Pipeline Value</div>
                    <div class="kpi-value">${kpis['total_pipeline_value']:,.2f}</div>
                    <div class="kpi-sub">Weighted: <strong>${kpis['weighted_pipeline_value']:,.2f}</strong></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with k2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Closed Won Revenue</div>
                    <div class="kpi-value" style="color: #4ade80;">${kpis['total_won_revenue']:,.2f}</div>
                    <div class="kpi-sub">{kpis['won_opportunities']} Won Deals</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with k3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Open Opportunities</div>
                    <div class="kpi-value" style="color: #60a5fa;">{kpis['open_opportunities']}</div>
                    <div class="kpi-sub">Total Deals: {kpis['total_opportunities']} | Lost: {kpis['lost_opportunities']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with k4:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Lead Conversion Rate</div>
                    <div class="kpi-value" style="color: #c084fc;">{kpis['conversion_rate']}%</div>
                    <div class="kpi-sub">{kpis['open_leads']} Open of {kpis['total_leads']} Total Leads</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        # KPI Metric Cards Row 2: Customer & Follow-up Operations
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("👥 Total Customers", kpis["total_customers"])
        with c2:
            st.metric("🎯 Total Leads", kpis["total_leads"], delta=f"{kpis['open_leads']} Active")
        with c3:
            st.metric("📅 Pending Follow-Ups", kpis["pending_followups"])
        with c4:
            st.metric("⚠️ Overdue Follow-Ups", kpis["overdue_followups"], delta_color="inverse")

        st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 24px 0;' />", unsafe_allow_html=True)

        # Interactive Plotly Charts Row
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("##### 🎯 Lead Status Distribution")
            lead_dist = charts["lead_status_distribution"]
            df_leads = pd.DataFrame(list(lead_dist.items()), columns=["Status", "Count"])
            # Filter zero counts if table is large, or keep for complete visibility
            color_map = {
                "New": "#3b82f6",
                "Contacted": "#f59e0b",
                "Qualified": "#10b981",
                "Unqualified": "#6b7280",
                "Converted": "#8b5cf6",
                "Lost": "#ef4444"
            }
            fig_leads = px.pie(
                df_leads,
                names="Status",
                values="Count",
                hole=0.45,
                color="Status",
                color_discrete_map=color_map
            )
            fig_leads.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                font=dict(color="#94a3b8")
            )
            st.plotly_chart(fig_leads, use_container_width=True)

        with chart_col2:
            st.markdown("##### 💼 Opportunity Pipeline by Stage")
            opp_stages = charts["opportunity_stages"]
            stages_list = list(opp_stages.keys())
            stage_values = [opp_stages[s]["value"] for s in stages_list]
            stage_counts = [opp_stages[s]["count"] for s in stages_list]
            
            fig_pipe = go.Figure(data=[
                go.Bar(
                    name="Pipeline Value ($)",
                    x=stages_list,
                    y=stage_values,
                    marker_color=["#3b82f6", "#06b6d4", "#f59e0b", "#10b981", "#ef4444"],
                    text=[f"${v:,.0f} ({c})" for v, c in zip(stage_values, stage_counts)],
                    textposition="auto"
                )
            ])
            fig_pipe.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
                font=dict(color="#94a3b8"),
                yaxis=dict(title="Value ($)", gridcolor="rgba(255,255,255,0.06)"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
            )
            st.plotly_chart(fig_pipe, use_container_width=True)

        # Monthly Sales and Acquisition Row
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            st.markdown("##### 📈 Monthly Sales & Pipeline Trend")
            ms = charts["monthly_sales"]
            months = list(ms.keys())
            won_vals = [ms[m]["Won"] for m in months]
            pipe_vals = [ms[m]["Pipeline"] for m in months]

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(x=months, y=pipe_vals, name="Open Pipeline", marker_color="#3b82f6"))
            fig_trend.add_trace(go.Bar(x=months, y=won_vals, name="Closed Won", marker_color="#10b981"))
            fig_trend.update_layout(
                barmode="stack",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
                font=dict(color="#94a3b8"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)")
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with row2_col2:
            st.markdown("##### 🌐 Lead Acquisition Sources")
            src_data = charts["lead_sources"]
            df_src = pd.DataFrame(list(src_data.items()), columns=["Source", "Leads"]).sort_values(by="Leads", ascending=True)
            fig_src = px.bar(
                df_src,
                x="Leads",
                y="Source",
                orientation="h",
                color="Leads",
                color_continuous_scale="Blues"
            )
            fig_src.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
                font=dict(color="#94a3b8"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
            )
            st.plotly_chart(fig_src, use_container_width=True)

        # Urgent / Upcoming Follow-Ups Quick Section
        st.markdown("##### ⚡ Upcoming & Action-Required Follow-Ups")
        now = datetime.utcnow()
        urgent_query = db.query(FollowUp).filter(FollowUp.status == FollowUpStatusEnum.PLANNED)
        if current_user.role == RoleEnum.SALES_EXECUTIVE:
            urgent_query = urgent_query.filter(FollowUp.assigned_to == current_user.user_id)
        
        urgent_list = urgent_query.order_by(FollowUp.followup_date.asc()).limit(5).all()

        if urgent_list:
            rows = []
            for item in urgent_list:
                is_ov = item.followup_date < now
                rows.append({
                    "ID": item.followup_id,
                    "Date & Time": item.followup_date.strftime("%Y-%m-%d %H:%M"),
                    "Type": item.followup_type,
                    "Subject": item.subject,
                    "Relation": f"{item.related_type} #{item.related_id}",
                    "Status": "⚠️ OVERDUE" if is_ov else "Planned",
                    "Assigned": item.assigned_user.name if item.assigned_user else "N/A"
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.success("🎉 No pending follow-ups right now. You are completely caught up!")

    finally:
        db.close()
