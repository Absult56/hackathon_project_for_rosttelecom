from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.schemas.invest import InvestProjectOut

router = APIRouter(prefix="/invest", tags=["Invest Navigator"])

MOCK_PROJECTS = [
    {
        "id": 1,
        "title": "Строительство логистического технопарка 'Запад'",
        "investor": "ЛогоПром Инвест",
        "industry": "Логистика",
        "stage": "стройка",
        "budget": 2500000000.0,
        "lat": 55.680000,
        "lon": 37.350000,
        "target_needs": ["fiber_optics", "cctv", "data_center"],
        "event_date": "2025-06-30",
        "description": "Крупный складской хаб класса А, требуется СКС, магистральная оптика и 120 камер."
    },
    {
        "id": 2,
        "title": "Модернизация элеваторного комплекса",
        "investor": "АгроСевер Холдинг",
        "industry": "АПК",
        "stage": "проектирование",
        "budget": 850000000.0,
        "lat": 55.910000,
        "lon": 37.580000,
        "target_needs": ["telephony", "fiber_optics", "access_control"],
        "event_date": "2025-09-15",
        "description": "Автоматизация взвешивания зерна, видеонаблюдение с аналитикой."
    }
]

@router.get("/projects", response_model=List[InvestProjectOut], summary="Список инвестпроектов")
def get_projects(
    stage: Optional[str] = Query(None, description="проектирование, стройка, запуск"),
    industry: Optional[str] = Query(None, description="Отрасль проекта")
):
    results = MOCK_PROJECTS
    if stage:
        results = [p for p in results if p["stage"].lower() == stage.lower()]
    if industry:
        results = [p for p in results if p["industry"].lower() == industry.lower()]
    return results

@router.get("/projects/{project_id}", response_model=InvestProjectOut, summary="Детальная карточка проекта")
def get_project_by_id(project_id: int):
    for p in MOCK_PROJECTS:
        if p["id"] == project_id:
            return p
    raise HTTPException(status_code=404, detail="Инвестпроект не найден")