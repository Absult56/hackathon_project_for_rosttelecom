from fastapi import APIRouter, Query
from typing import List, Optional
from app.schemas.radar import CompanyOut, RadarAnalyticsOut

router = APIRouter(prefix="/radar", tags=["Market Radar"])

MOCK_COMPANIES = [
    {
        "id": 1,
        "name": "ПАО Газпром Нефть Центр",
        "inn": "7701234567",
        "industry": "ТЭК",
        "revenue": 1450000000.0,
        "revenue_growth": 12.4,
        "lat": 55.751244,
        "lon": 37.618423,
        "address": "г. Москва, ул. Тверская, д. 1",
        "is_rtk_client": True,
        "is_white_spot": False,
        "cluster_zone": "ЦФО-1"
    },
    {
        "id": 2,
        "name": "Агрокомплекс Северный",
        "inn": "7709876543",
        "industry": "АПК",
        "revenue": 450000000.0,
        "revenue_growth": 25.1,
        "lat": 55.820000,
        "lon": 37.500000,
        "address": "г. Москва, ш. Дмитровское, д. 120",
        "is_rtk_client": False,
        "is_white_spot": True,
        "cluster_zone": "САО-Пром"
    },
    {
        "id": 3,
        "name": "Дата-Центр Инновация",
        "inn": "7711223344",
        "industry": "IT",
        "revenue": 890000000.0,
        "revenue_growth": 40.8,
        "lat": 55.700000,
        "lon": 37.600000,
        "address": "г. Москва, Варшавское ш., д. 45",
        "is_rtk_client": False,
        "is_white_spot": True,
        "cluster_zone": "ЮАО-IT"
    }
]

@router.get("/companies", response_model=List[CompanyOut], summary="Получить список компаний для карты")
def get_companies(
    industry: Optional[str] = Query(None, description="Отрасль: ТЭК, АПК, IT, Торговля"),
    is_rtk_client: Optional[bool] = Query(None, description="Фильтр: True - клиенты, False - лиды"),
    white_spot_only: bool = Query(False, description="Только белые пятна с потенциалом")
):
    results = MOCK_COMPANIES
    if industry:
        results = [c for c in results if c["industry"].lower() == industry.lower()]
    if is_rtk_client is not None:
        results = [c for c in results if c["is_rtk_client"] == is_rtk_client]
    if white_spot_only:
        results = [c for c in results if c["is_white_spot"]]
    return results

@router.get("/analytics", response_model=RadarAnalyticsOut, summary="Аналитика для диаграмм")
def get_radar_analytics():
    return {
        "total_companies": 3,
        "rtk_clients_count": 1,
        "white_spots_count": 2,
        "penetration_rate": 33.3,
        "revenue_by_industry": {
            "ТЭК": 1450000000.0,
            "АПК": 450000000.0,
            "IT": 890000000.0
        }
    }