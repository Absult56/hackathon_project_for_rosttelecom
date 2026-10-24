from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.invest_project import InvestProject
from app.schemas.invest import InvestProjectOut
from app.core.security import get_current_user

router = APIRouter(prefix="/invest", tags=["Invest Navigator"])

@router.get(
    "/projects",
    response_model=List[InvestProjectOut],
    summary="Реестр инвестпроектов и строек с таймлайном"
)
def get_invest_projects(
    stage: Optional[str] = Query(None, description="Стадия: проектирование, стройка, ввод в эксплуатацию"),
    industry: Optional[str] = Query(None, description="Отрасль проекта"),
    needs: Optional[str] = Query(None, description="Потребность (например: fiber_optics, cctv)"),
    date_from: Optional[str] = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Конечная дата (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    query = db.query(InvestProject)

    if stage:
        query = query.filter(InvestProject.stage.ilike(f"%{stage}%"))
    if industry:
        query = query.filter(InvestProject.industry.ilike(f"%{industry}%"))
    if needs:
        query = query.filter(InvestProject.target_needs.ilike(f"%{needs}%"))
    if date_from:
        query = query.filter(InvestProject.event_date >= date_from)
    if date_to:
        query = query.filter(InvestProject.event_date <= date_to)

    return query.all()

@router.get(
    "/projects/{project_id}",
    response_model=InvestProjectOut,
    summary="Карточка инвестпроекта (для перехода в Калькулятор)"
)
def get_invest_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    project = db.query(InvestProject).filter(InvestProject.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Инвестпроект с ID {project_id} не найден"
        )
    return project