from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.company import Company
from app.models.invest_project import InvestProject
from app.services.export_service import generate_companies_csv, generate_projects_csv
from app.core.security import get_current_user

router = APIRouter(prefix="/export", tags=["Export Engine (CSV/CRM)"])

@router.get(
    "/companies/csv",
    summary="Выгрузка реестра компаний в CSV"
)
def export_companies_to_csv(
    industry: Optional[str] = Query(None),
    is_rtk_client: Optional[bool] = Query(None),
    white_spot_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(Company)
    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))
    if is_rtk_client is not None:
        query = query.filter(Company.is_rtk_client == is_rtk_client)
    if white_spot_only:
        query = query.filter(Company.is_white_spot == True)

    companies = query.all()
    csv_bytes = generate_companies_csv(companies)

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="rtk_companies_export.csv"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@router.get(
    "/projects/csv",
    summary="Выгрузка реестра инвестпроектов в CSV (Закрывает требование жюри)"
)
def export_projects_to_csv(
    stage: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(InvestProject)
    if stage:
        query = query.filter(InvestProject.stage.ilike(f"%{stage}%"))
    if industry:
        query = query.filter(InvestProject.industry.ilike(f"%{industry}%"))

    projects = query.all()
    csv_bytes = generate_projects_csv(projects)

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="rtk_projects_export.csv"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )