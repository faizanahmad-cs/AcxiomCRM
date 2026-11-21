from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from acxiom_crm.backend.models.customer import Customer
from acxiom_crm.backend.models.lead import Lead, LeadStatusEnum
from acxiom_crm.backend.models.opportunity import Opportunity, OpportunityStageEnum, OpportunityStatusEnum
from acxiom_crm.backend.models.followup import FollowUp, FollowUpStatusEnum
from acxiom_crm.backend.models.activity import Activity
from acxiom_crm.backend.models.user import User, RoleEnum

def get_date_range(filter_type: str, custom_start: Optional[date] = None, custom_end: Optional[date] = None):
    today = date.today()
    if filter_type == "Today":
        start = today
        end = today
    elif filter_type == "This Week":
        start = today - timedelta(days=today.weekday())
        end = today
    elif filter_type == "This Month":
        start = today.replace(day=1)
        end = today
    elif filter_type == "Custom Range" and custom_start and custom_end:
        start = custom_start
        end = custom_end
    else:  # "All Time"
        start = None
        end = None
    return start, end

def get_dashboard_kpis(
    db: Session,
    current_user: User,
    date_filter: str = "All Time",
    custom_start: Optional[date] = None,
    custom_end: Optional[date] = None
) -> Dict[str, Any]:
    start_date, end_date = get_date_range(date_filter, custom_start, custom_end)
    now = datetime.utcnow()

    cust_q = db.query(Customer)
    lead_q = db.query(Lead)
    opp_q = db.query(Opportunity)
    fol_q = db.query(FollowUp)

    # Scoping
    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        cust_q = cust_q.filter(Customer.assigned_to == current_user.user_id)
        lead_q = lead_q.filter(Lead.assigned_to == current_user.user_id)
        opp_q = opp_q.filter(Opportunity.assigned_to == current_user.user_id)
        fol_q = fol_q.filter(FollowUp.assigned_to == current_user.user_id)

    # Apply date filters based on created_at or close date
    if start_date:
        start_dt = datetime.combine(start_date, datetime.min.time())
        cust_q = cust_q.filter(Customer.created_at >= start_dt)
        lead_q = lead_q.filter(Lead.created_at >= start_dt)
        opp_q = opp_q.filter(Opportunity.created_at >= start_dt)
        fol_q = fol_q.filter(FollowUp.followup_date >= start_dt)
    if end_date:
        end_dt = datetime.combine(end_date, datetime.max.time())
        cust_q = cust_q.filter(Customer.created_at <= end_dt)
        lead_q = lead_q.filter(Lead.created_at <= end_dt)
        opp_q = opp_q.filter(Opportunity.created_at <= end_dt)
        fol_q = fol_q.filter(FollowUp.followup_date <= end_dt)

    total_customers = cust_q.count()
    total_leads = lead_q.count()
    open_leads = lead_q.filter(Lead.status.notin_([LeadStatusEnum.CONVERTED, LeadStatusEnum.LOST, LeadStatusEnum.UNQUALIFIED])).count()
    
    total_opportunities = opp_q.count()
    open_opportunities = opp_q.filter(Opportunity.status == OpportunityStatusEnum.OPEN).count()
    won_opportunities = opp_q.filter(Opportunity.status == OpportunityStatusEnum.WON).count()
    lost_opportunities = opp_q.filter(Opportunity.status == OpportunityStatusEnum.LOST).count()

    # Sum pipeline value (Open opportunities)
    open_opps = opp_q.filter(Opportunity.status == OpportunityStatusEnum.OPEN).all()
    total_pipeline_val = sum(o.amount for o in open_opps)
    weighted_pipeline_val = sum(o.weighted_amount for o in open_opps)

    # Won revenue
    won_opps = opp_q.filter(Opportunity.status == OpportunityStatusEnum.WON).all()
    total_won_revenue = sum(o.amount for o in won_opps)

    # Follow-ups
    pending_followups = fol_q.filter(FollowUp.status == FollowUpStatusEnum.PLANNED).count()
    overdue_followups = fol_q.filter(
        FollowUp.status == FollowUpStatusEnum.PLANNED,
        FollowUp.followup_date < now
    ).count()

    # Conversion rate
    conversion_rate = round((lead_q.filter(Lead.status == LeadStatusEnum.CONVERTED).count() / max(1, total_leads)) * 100, 1)

    return {
        "total_customers": total_customers,
        "total_leads": total_leads,
        "open_leads": open_leads,
        "total_opportunities": total_opportunities,
        "open_opportunities": open_opportunities,
        "won_opportunities": won_opportunities,
        "lost_opportunities": lost_opportunities,
        "total_pipeline_value": round(total_pipeline_val, 2),
        "weighted_pipeline_value": round(weighted_pipeline_val, 2),
        "total_won_revenue": round(total_won_revenue, 2),
        "pending_followups": pending_followups,
        "overdue_followups": overdue_followups,
        "conversion_rate": conversion_rate
    }

def get_chart_data(
    db: Session,
    current_user: User,
    date_filter: str = "All Time",
    custom_start: Optional[date] = None,
    custom_end: Optional[date] = None
) -> Dict[str, Any]:
    start_date, end_date = get_date_range(date_filter, custom_start, custom_end)

    lead_q = db.query(Lead)
    opp_q = db.query(Opportunity)

    if current_user.role == RoleEnum.SALES_EXECUTIVE:
        lead_q = lead_q.filter(Lead.assigned_to == current_user.user_id)
        opp_q = opp_q.filter(Opportunity.assigned_to == current_user.user_id)

    if start_date:
        start_dt = datetime.combine(start_date, datetime.min.time())
        lead_q = lead_q.filter(Lead.created_at >= start_dt)
        opp_q = opp_q.filter(Opportunity.created_at >= start_dt)
    if end_date:
        end_dt = datetime.combine(end_date, datetime.max.time())
        lead_q = lead_q.filter(Lead.created_at <= end_dt)
        opp_q = opp_q.filter(Opportunity.created_at <= end_dt)

    leads = lead_q.all()
    opps = opp_q.all()

    # 1. Lead Status Distribution
    status_counts = {}
    for st in LeadStatusEnum.ALL:
        status_counts[st] = 0
    for l in leads:
        status_counts[l.status] = status_counts.get(l.status, 0) + 1

    # 2. Opportunity Pipeline by Stage
    stage_data = {
        OpportunityStageEnum.QUALIFICATION: {"count": 0, "value": 0.0, "weighted": 0.0},
        OpportunityStageEnum.PROPOSAL: {"count": 0, "value": 0.0, "weighted": 0.0},
        OpportunityStageEnum.NEGOTIATION: {"count": 0, "value": 0.0, "weighted": 0.0},
        OpportunityStageEnum.WON: {"count": 0, "value": 0.0, "weighted": 0.0},
        OpportunityStageEnum.LOST: {"count": 0, "value": 0.0, "weighted": 0.0},
    }
    for o in opps:
        if o.stage in stage_data:
            stage_data[o.stage]["count"] += 1
            stage_data[o.stage]["value"] += o.amount
            stage_data[o.stage]["weighted"] += o.weighted_amount

    # 3. Monthly Sales / Outcomes (Past 6 months)
    monthly_sales = {}
    for i in range(5, -1, -1):
        m_date = date.today().replace(day=1) - timedelta(days=i * 30)
        m_key = m_date.strftime("%b %Y")
        monthly_sales[m_key] = {"Won": 0.0, "Pipeline": 0.0}

    for o in opps:
        m_key = o.created_at.strftime("%b %Y")
        if m_key in monthly_sales:
            if o.stage == OpportunityStageEnum.WON:
                monthly_sales[m_key]["Won"] += o.amount
            else:
                monthly_sales[m_key]["Pipeline"] += o.amount

    # 4. Lead Source Breakdown
    source_counts = {}
    for l in leads:
        src = l.source or "Unknown"
        source_counts[src] = source_counts.get(src, 0) + 1

    return {
        "lead_status_distribution": status_counts,
        "opportunity_stages": stage_data,
        "monthly_sales": monthly_sales,
        "lead_sources": source_counts
    }
