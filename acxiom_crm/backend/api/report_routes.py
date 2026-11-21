from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from acxiom_crm.backend.database import get_db
from acxiom_crm.backend.models.user import User
from acxiom_crm.backend.services.report_service import get_dashboard_kpis, get_chart_data
from acxiom_crm.backend.api.deps import get_current_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/pipeline")
def get_pipeline_report(
    date_filter: str = Query("All Time", description="Today, This Week, This Month, All Time"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    kpis = get_dashboard_kpis(
        db=db,
        current_user=current_user,
        date_filter=date_filter,
        custom_start=start_date,
        custom_end=end_date
    )
    chart_data = get_chart_data(
        db=db,
        current_user=current_user,
        date_filter=date_filter,
        custom_start=start_date,
        custom_end=end_date
    )
    return {
        "kpis": kpis,
        "charts": chart_data
    }
