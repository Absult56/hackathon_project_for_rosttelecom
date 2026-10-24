from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.models.company import Company
from app.schemas.radar import CompanyOut, RadarAnalyticsOut
from app.core.security import get_current_user

router = APIRouter(prefix="/radar", tags=["Market Radar"])

@router.get(
    "/companies",
    response_model=List[CompanyOut],
    summary="Реальный реестр компаний с фильтрами"
)
def get_companies(
    industry: Optional[str] = Query(None, description="Отрасль (ТЭК, АПК, IT и др.)"),
    min_revenue: Optional[float] = Query(None, description="Минимальная выручка"),
    max_revenue: Optional[float] = Query(None, description="Максимальная выручка"),
    is_rtk_client: Optional[bool] = Query(None, description="Статус: True - клиент, False - лид"),
    white_spot_only: bool = Query(False, description="Только потенциальные белые пятна"),
    db: Session = Depends(get_db),
    # Роут защищен JWT (при необходимости можно временно закомментировать для упрощения тестов фронта)
    user: dict = Depends(get_current_user)
):
    query = db.query(Company)

    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))
    if min_revenue is not None:
        query = query.filter(Company.revenue >= min_revenue)
    if max_revenue is not None:
        query = query.filter(Company.revenue <= max_revenue)
    if is_rtk_client is not None:
        query = query.filter(Company.is_rtk_client == is_rtk_client)
    if white_spot_only:
        query = query.filter(Company.is_white_spot == True)

    return query.all()

@router.get(
    "/analytics",
    response_model=RadarAnalyticsOut,
    summary="Агрегированные данные для графиков и дашбордов"
)
def get_radar_analytics(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    total_companies = db.query(Company).count()
    rtk_clients_count = db.query(Company).filter(Company.is_rtk_client == True).count()
    white_spots_count = db.query(Company).filter(Company.is_white_spot == True).count()

    penetration_rate = round((rtk_clients_count / total_companies * 100), 2) if total_companies > 0 else 0.0

    # Группировка выручки по отраслям
    industry_stats = (
        db.query(Company.industry, func.sum(Company.revenue))
        .group_by(Company.industry)
        .all()
    )
    revenue_by_industry = {industry: (rev or 0.0) for industry, rev in industry_stats}

    return RadarAnalyticsOut(
        total_companies=total_companies,
        rtk_clients_count=rtk_clients_count,
        white_spots_count=white_spots_count,
        penetration_rate=penetration_rate,
        revenue_by_industry=revenue_by_industry
    )